# MMC-01 RUNLOG

Every run, including abandoned ones. Protocol deviations are written here, not
corrected silently.

---

## 2026-11-17 — Run 0: prerequisites, data freeze, sealed ground truth

**Prerequisite (protocol section 10, "before any of this"): CAMR STRING threshold
correction.** Not issued, and no longer issuable. The user reports the JCO CCI
revision was never submitted and they emailed the editor to withdraw it, so no
corrected version of CAMR will appear. **Consequence for MMC-01:** CAMR must not
be cited as a published source in this manuscript, and the "700 is primary
because it is what the CAMR code executed" justification in protocol section 6
loses its referent. The 700 primary arm is retained, but its justification is
restated as a free-standing choice (700 is STRING's "high confidence" cutoff),
not as inheritance from CAMR. Logged as a protocol deviation.

**Deviation 2: DrugBank omitted.** DrugBank requires a licensed download that
cannot be obtained unattended. Target assembly will run on DGIdb alone, per user
decision. Per-drug target counts and the resulting coverage gap are reported, and
Gate 1 (>=12 of 16 protectants mapped in the LCC) remains the test of whether
this is sufficient.

**Data sources frozen** (section 3). Downloaded once, hashed, stored in
`data/raw/` with `PROVENANCE.json`:

| source | bytes | sha256 (first 16) |
|---|---|---|
| STRING v12.0 links (9606) | 83,164,437 | 3e22f32572211aa3 |
| STRING v12.0 info | 1,970,090 | 144de4b0d98c6a7d |
| STRING v12.0 aliases | 19,777,800 | b65f730b993ed0c1 |
| DGIdb interactions | 12,178,745 | 08af778126a4f22a |
| HGNC complete set | 17,007,798 | 6df77ac3cbaeb86a |

**Sealed ground truth built and sealed** (section 8), before modules and before
the graph, as the order of operations requires.

- `sealed/CODING_RULES.md` written **before** the pair table was assembled.
- `sealed/outcomes.json` sha256 `16a1bf84d9369805e773bf2cc0dc624db0816865fc906c9d451826d2cf53fb50`
- `sealed/OUTCOMES_HASH.txt` committed at the same time.

### Findings from building the ground truth

These are properties of the evidence base, established before any graph existed.

1. **M3 and M4 yield zero evaluable pairs.** No completed prospective randomised
   cardioprotection trial was identified against VEGF-pathway inhibitor cardiac
   dysfunction, or against proteasome-inhibitor cardiac dysfunction. The
   inferential part of the study can only draw pairs from M1 and M2.

2. **13 evaluable pairs**, so Gate 2 (>=8) passes on count.

3. **The primary comparison is 4 POSITIVE vs 3 NULL** after the pre-specified
   exclusion of 6 MIXED pairs.

4. **The pre-specified primary test cannot attain significance.** Computed
   combinatorially from group sizes alone, with no z-scores involved
   (`src/attainable_p.py` equivalent, run 2026-11-17):

   | scenario | POS | NULL | min attainable Wilcoxon p | min attainable Fisher p | can reach 0.05 |
   |---|---|---|---|---|---|
   | PRIMARY as specified | 4 | 3 | 0.0571 | 0.0286 | Wilcoxon NO, Fisher YES |
   | Sensitivity 3a: MIXED->NULL | 4 | 9 | 0.0028 | 0.0014 | YES |
   | Sensitivity 3b: MIXED->POSITIVE | 10 | 3 | 0.0070 | 0.0035 | YES |
   | Sensitivity 4: drop surrogate-only | 3 | 3 | 0.1000 | 0.1000 | NO |

   The two-sided exact Wilcoxon rank-sum named as the primary test in section 9
   has a floor of p = 0.0571 at these group sizes. It cannot return p < 0.05
   however perfectly the hypothesis holds. The co-primary Fisher test on the
   binary 2x2 can, but only under complete separation (p = 0.0286). Sensitivity
   analysis 4 cannot reach significance at all.

5. **Outcome code is perfectly confounded with module identity.** All 4 POSITIVE
   pairs are M1; all 3 NULL pairs are M2. The primary comparison is therefore
   entirely between-module. Any difference in proximity z-score between POSITIVE
   and NULL pairs is indistinguishable from a difference between the M1 and M2
   modules themselves (their size, degree distribution and interactome coverage).
   This is a structural identifiability failure, not a power problem, and no
   increase in sample size within this design would remove it.

### Integrity note

The protocol's ordering (build outcomes first, then modules) means the analyst
who builds the modules has already seen the outcomes. The seal protects the
graph and the metric; it does not blind module construction. Finding 5 makes this
concrete and material: knowing that POSITIVE == M1 and NULL == M2 is exactly the
knowledge that could bias how M1 and M2 gene sets are drawn. Recorded as an open
issue before module construction begins. No modules have been built yet.

**Status: paused before module construction, pending a decision on findings 4 and 5.**

---

## 2026-11-17 — Run 1: modules, graph, proximity, Gates 0/1/3/4, commitment

**Modules built blind.** Per the decision recorded above, module construction was
delegated to a builder given only the section 4 rules and the index agents, with
no access to `sealed/`, to this RUNLOG, or to the analysis conversation. It never
looked up a cardioprotective drug.

| module | seed sources | declared | two-source | HGNC-mapped | in LCC700 | mapping loss |
|---|---|---|---|---|---|---|
| M1 anthracycline | 7 | 34 | 34 | 34 | 34 | 0.000 |
| M2 anti-HER2 | 13 | 15 | 15 | 15 | 15 | 0.000 |
| M3 VEGF-pathway | 8 | 14 | 14 | 14 | **13** | 0.000 |
| M4 proteasome | 7 | 15 | 15 | 15 | 15 | 0.000 |

`config/modules.yaml` sha256 `95f84b7b46e8d3ae08afe8d0b03ba1913c7c3906f315b5e2f060d8ccf8ba2c65`.
All 35 seed-source entries were independently re-verified against Europe PMC by
PMID: every one is a real, review-typed article with a matching year. Zero
fabricated references. One review (PMID 41189010) seeds both M1 and M2; recorded
because M1 vs M2 is the comparison of interest.

**Known weaknesses in module construction, recorded and NOT repaired:**
- M3 reached only 13 genes in the LCC, below the section 4 minimum of 15.
- Section 4 rule 4 (resolve overlaps by majority of seed sources) is biased by
  unequal source counts: M2 had 13 reviews and M3 had 8, so shared signalling
  nodes migrated systematically to M2 (AKT1, MAPK1, EGFR), and NOS3 — endothelial
  nitric oxide synthase, named in M3's own core biology — was an exact 4-4 tie and
  was dropped from both modules. This is a flaw in the protocol's rule, found by
  executing it. It was not corrected, because correcting it after seeing the
  module contents is a degree of freedom the protocol forbids.
- No proteasome subunit gene is in M4. Across all seven M4 reviews only PSMB10 is
  ever written as a symbol (once). PSMB5 appears nowhere. Adding it would have
  been fabrication.

**Commitment written (protocol 2.2).** `results/predictions.json` sha256
`56018d7324ebf2543f850f11e4669cab4124a2d35f03349a3c55e0f2a34ee63a`, 64 pairs
(16 protectants x 4 modules) at STRING 700, seed 20261117, 1000 permutations.
25 of 64 predicted "matched" at the pre-specified z < -1.0 cutoff.
`sealed/` has not been read.

### Gate results (STRING 700, pre-unsealing)

| gate | verdict | numbers |
|---|---|---|
| 0 module viability | **CONDITIONAL** | M3 = 13 genes (< 15); 3 of 4 modules survive |
| 1 target coverage | **CONDITIONAL** | 16/16 protectants mapped; median direction coverage 0.42 (< 0.5) |
| 3 positive control | **PASS** | dexrazoxane-M1 z = -2.651; top-quartile cutoff -1.602; 4.7th percentile of 64 |
| 4 negative control | **FAIL** (pair-counting) / CONDITIONAL (drug-counting) | 2 violations, both levothyroxine: M2 z = -2.645, M3 z = -3.125 |

**Gate 3 passed decisively.** The method recovers the single clearest case in its
own domain. Dexrazoxane against the anthracycline module sits in the most extreme
5% of all 64 computed z-scores.

**Gate 4 failed, and the failure is informative.** Both violations are the same
drug. Levothyroxine has **no gene in common** with M2 or M3, yet scores z = -2.65
and -3.13 against them, and is negative against all four modules. Its DGIdb
targets are dominated by broad transcriptional regulators — THRA, THRB, PPARG,
NFE2L2, AHR — plus the core cardiac transcription factor NKX2-5. The degree-matched
null corrects for how many edges a gene has, but not for a transcription factor's
regulatory reach, so a drug acting on cardiac transcription scores "close" to any
cardiac module. The other four controls (loratadine, omeprazole, montelukast,
ranitidine) are clean.

**Protocol ambiguity, flagged not resolved.** Section 7 says "No negative-control
drug may score in the top quartile against any module. One violation is
CONDITIONAL... two or more is FAIL." Whether a violation is a drug or a
drug-module pair was not specified, and the two readings give FAIL and CONDITIONAL
respectively. Both are reported in `results/gates.json`; the stricter reading is
carried as the headline. The choice was not pre-specified and is disclosed.

**Also recorded:** levothyroxine met the section 5 selection criterion as written
(no cardioprotective mechanism, no cardio-oncology trial) but is not
pharmacologically inert in the heart. That is a flaw in the negative-control set,
discovered by execution. It was not swapped out.

**Status: Gate 4 FAIL. Under section 7 a FAIL stops the study. Paused before
unsealing, pending a decision.**

---

## 2026-11-17 — Run 2: sensitivity arms, figures, exploratory robustness

**Decision recorded:** Gate 4 FAIL was honoured. `sealed/outcomes.json` was NOT
opened. Gate 2 was not run. No outcome has ever entered the analysis, and the
commitment hash plus the untouched seal are the evidence.

**All arms reported (rule 2.4).** Gate 3 and Gate 4 recomputed at every threshold
under both the primary metric and the secondary S_AB:

| arm | cutoff | dexrazoxane-M1 | percentile | Gate 3 | Gate 4 (pair) | Gate 4 (drug) | violating controls |
|---|---|---|---|---|---|---|---|
| 400 / z | -1.299 | -1.689 | 12.5% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |
| 400 / S_AB | 0.192 | 0.198 | 28.1% | **FAIL** | FAIL | FAIL | levothyroxine, loratadine, omeprazole |
| **700 / z (primary)** | -1.602 | **-2.651** | **4.7%** | **PASS** | **FAIL** | CONDITIONAL | levothyroxine |
| 700 / S_AB | 0.284 | 0.234 | 15.6% | PASS | FAIL | CONDITIONAL | loratadine |
| 900 / z | -1.170 | -3.432 | **0.0%** | PASS | FAIL | FAIL | levothyroxine, loratadine, ranitidine |
| 900 / S_AB | 0.377 | 0.117 | 7.8% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |

Gate 3 passes in 5 of 6 arms and sharpens monotonically with interactome
confidence (12.5% -> 4.7% -> 0.0%): on the highest-confidence graph dexrazoxane-M1
is the single most proximal of all 64 pairs. It fails only under S_AB at 400.
**Gate 4 never passes in any arm under either metric.**

**Figures written** to `results/figures/`: fig1 proximity heatmap (protectants and
negative controls on one colour scale), fig2 Gate 3 with every pair plotted
individually across all three arms, fig3 Gate 4 specificity. Fig 3 replaces the
protocol's leave-one-out stability plot, which is not applicable because no
primary statistic was computed.

### EXPLORATORY (rule 2.3 — cannot change any recorded verdict)

Leave-one-target-out, STRING 700, same seed:

- **Gate 3 is carried by TOP2B.** Removing TOP2B alone moves dexrazoxane-M1 from
  z = -2.651 to -0.764 (delta +1.887); no other target shifts it by more than
  0.66. TOP2B is the established mediator of anthracycline cardiotoxicity and
  dexrazoxane's own target, and its degree is only 15, so this is not a hub
  artefact. The positive control passes for the mechanistically correct reason.
- **The Gate 4 breach is distributed, not attributable to one gene.** The largest
  single-target effect for levothyroxine is +0.461 (NOX3) against M2 and +0.508
  (AHR) against M3. Every leave-one-out still leaves z below -2.1. Excluding any
  one "bad" target would not repair specificity.
- **Module-selectivity index** (exploratory, z for a module minus the mean z for
  the other three): dexrazoxane-M1 is the most selective pair in the panel at
  -2.97, ahead of atorvastatin-M1 at -2.27. Dexrazoxane is not merely close to
  M1, it is close to M1 and to nothing else (M2 +0.46, M3 +0.29, M4 +0.20).
- M3 dominates the selectivity ranking generally, consistent with its small size
  (13 genes in the LCC) inflating closest-distance proximity.

**Status: analysis complete. Study stopped at Gate 4 as section 7 requires.
Seal intact.**

---

## 2026-11-17 — Run 3: corrected headline, expanded controls, submission draft

**Correction to the Run 2 interpretation.** The first manuscript draft led with
"the method fails its own negative control". That framing was wrong and the draft
has been withdrawn (`paper/MMC01_manuscript.md` deleted; retained in git history).

An exploratory calibration check showed Gate 4 was mis-specified, not failed in
substance. A top quartile holds 25% of values by construction, so five of the
twenty negative-control pairs would be expected inside it under exchangeability.
Two were observed at the primary arm. Across arms the controls were in fact
FARTHER from the modules than the cardioprotectants (permutation two-sided
p = 0.0027 at 400, p = 0.0168 at 700, p = 0.152 at 900). The gate demanded zero
overlap between two distributions that overlap by construction.

**The recorded Gate 4 verdict is unchanged and remains FAIL.** It was
pre-specified, it executed, and it is reported as it fell. The calibration
analysis is exploratory and changes interpretation only.

**Expanded control set (exploratory).** 100 DGIdb drugs with 3-60 LCC targets
sampled at random (seed 20261117), all study drugs excluded, giving 400
background drug-module pairs. Cardioprotectants are significantly closer to the
cardiotoxicity modules than this background: median z -0.722 vs -0.361, mean
-0.855 vs -0.362, permutation two-sided p = 0.0022. Only 16.8% of background
pairs fall inside the protectant top quartile against 25% expected. The test is
conservative: background drugs were not screened for cardiac activity, so any
cardioactive drug among them works against the difference.

**Submission draft built** for Cardiovascular Toxicology (Springer) as a Research
Article: `paper/MMC01_CardiovascTox_ResearchArticle.md` and
`paper/MMC01_CardiovascularToxicology_submission.docx`. Journal is hybrid and
states "There are no Page Charges for accepted articles", so the subscription
route carries no fee. Framing moved from methods-critique to mechanism-first,
leading with the dexrazoxane-TOP2B result. 3,672 body words (limit ~10,000),
232-word abstract (limit 150-250), 6 keywords (limit 4-6), 42 references,
3 figures plus the required Graphical Abstract.

`src/verify_numbers.py` audits 49 quantitative and formatting claims against the
result files and the seal; all pass. It caught one real transcription error
(control median at STRING 900 written as -0.057, actual -0.058), now fixed.

**Outstanding before submission (author items):**
- Institutional e-mail address. The journal requires at least one among the
  authors and asks for it from the corresponding author; a personal relay
  address will not satisfy this.
- Affiliation and ORCID.
- AI-assistance declaration is drafted in Methods section 2.8 per Springer policy
  and must be confirmed by the author.
- Suggested reviewers with institutional e-mail addresses (optional but helpful).
- Decide whether to deposit the repository publicly and add the link to the Data
  and Code Availability statements.

---

## 2026-11-17 — Run 4: public release and submission package

**Authorship completed.** Rugved Parmar, Md Fahim, Adam Budzikowski, all SUNY
Downstate Health Sciences University, Brooklyn, New York, USA. Corresponding
author rugved.parmar@downstate.edu. ORCIDs are entered at the submission portal
and are deliberately NOT placeheld in the manuscript; fabricating identifiers for
named individuals is not acceptable. No reviewers suggested, by author decision.

**Repository made public:** https://github.com/Rugved3-droid/mmc01

Publishing required rewriting history: three cached shortest-path matrices
(352 MB, 236 MB, 128 MB) exceeded GitHub's hard 100 MB per-file limit and the
push would have been rejected. `git filter-branch` removed `data/dist` from all
commits; `.git` fell from 194 MB to 5.7 MB. A full bundle backup was taken first
at `D:\mmc01_backup_before_rewrite.bundle` (151 MB), so the rewrite is reversible.

**Seal provenance survived the rewrite intact.** `sealed/outcomes.json` still
appears in exactly one commit, `334709b`, with its original hash — the rewrite
touched only later commits that contained `data/dist`. The claim in the paper's
Data Availability statement therefore still verifies as written:
`git log --oneline -- sealed/outcomes.json` returns a single commit.

**Figure resolution corrected.** Figures were regenerated at 600 dpi; the journal
requires 600 dpi for combination art and the previous 220 dpi output would have
failed production.

**Submission package** assembled at `paper/submission/`:
Manuscript.docx, CoverLetter.docx, GraphicalAbstract.png, Fig1.png, Fig2.png,
Fig3.png (4.9 MB total). Manuscript is 3,797 body words, 232-word abstract,
6 keywords, 42 references, 3 tables, 3 figures plus the Graphical Abstract.
`verify_numbers.py` passes all 49 checks including seal integrity.

**Known residual:** commits before this run carry the author's Apple private-relay
e-mail address in their git metadata, now public. It is a relay address rather
than a personal one, and was left in place because changing it would alter commit
`334709b` and break the seal-provenance claim.

**Author items remaining before submission:**
- ORCIDs for all three authors (entered in the portal).
- Confirmation from Md Fahim and Adam Budzikowski that they approve submission
  and that the Author Contributions statement accurately describes their roles;
  the journal treats submission as implying this.
- Confirmation of the AI-assistance declaration in Methods 2.8.
