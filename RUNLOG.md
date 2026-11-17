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
