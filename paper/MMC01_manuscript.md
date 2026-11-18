# A pre-specified network-proximity criterion recovers the one established cardioprotection mechanism but fails its own negative control

**MMC-01 — Mechanism-Matched Cardioprotection.** Pre-registered methods study, stopped at a pre-specified gate.

Rugved Parmar

---

## Abstract

**Background.** Network proximity between a drug's targets and a disease module is widely used to propose drug repurposing. Whether it can identify *mechanism-matched* cardioprotection — a protectant whose targets sit near the molecular module of a specific cardiotoxicity — has not been tested under pre-registration.

**Methods.** We pre-specified, before any data were read, a protocol fixing the interactome (STRING v12.0, human), the confidence grid (400/700/900, primary 700), the metric (closest-distance proximity with a 1000-permutation degree-matched null), the binary cutoff (z < −1.0), the candidate drug list (16 cardioprotectants tested in prospective cardio-oncology trials), five negative-control drugs, and four cardiotoxicity modules (anthracycline, anti-HER2, VEGF-pathway, proteasome-inhibitor) seeded from published mechanism reviews under a two-source-per-gene rule. Trial outcomes were extracted, coded and **sealed by SHA-256 before the interactome was built**, and module construction was delegated to a builder with no access to them. Four gates were evaluated before unsealing. Gate 3 required the positive control, dexrazoxane against the anthracycline module, to fall in the top quartile of all proximity z-scores; Gate 4 required no negative-control drug to do so.

**Results.** Gate 3 **passed**: dexrazoxane–M1 reached z = −2.651 at STRING 700, the 4.7th percentile of all 64 protectant–module pairs, and passed in 5 of 6 threshold-by-metric arms, sharpening monotonically with interactome confidence (12.5th → 4.7th → 0.0th percentile at 400 → 700 → 900). Exploratory leave-one-target-out showed the signal is carried by TOP2B (Δz = +1.887 on removal), the established mediator of anthracycline cardiotoxicity and dexrazoxane's own target. Gate 4 **failed**: levothyroxine, which shares no gene with either module, reached z = −2.645 against anti-HER2 and −3.125 against VEGF-pathway, and Gate 4 did not pass in **any** of the six arms. The breach was distributed across levothyroxine's 16 targets, with no single gene accounting for more than Δz = +0.51.

**Conclusions.** The criterion is sensitive but not specific. It recovers the one cardioprotection pair the field agrees on, and does so through the correct gene, yet it cannot exclude drugs with no mechanistic relationship to the module. Because a Gate 4 failure stops the study by pre-specification, the sealed trial outcomes were never opened and no association between proximity and trial success was estimated. We report the method's failure, not a result about cardioprotection.

**Registration/integrity.** Ground truth sealed at SHA-256 `16a1bf84…` and never read. Predictions committed at SHA-256 `56018d73…` before unsealing was permitted. All code, configs, hashes and a complete run log, including abandoned runs and protocol deviations, accompany this report.

---

## 1. Introduction

Cardiotoxicity from cancer therapy is mechanistically heterogeneous. Anthracycline cardiomyopathy, anti-HER2 cardiac dysfunction, VEGF-pathway inhibition and proteasome-inhibitor cardiac injury are distinct molecular processes, yet cardioprotection trials have largely tested the same neurohormonal agents across all of them. An obvious hypothesis is that the trials which succeeded were the ones in which the protectant happened to act near the toxicity's own biology.

Network proximity offers a way to ask this quantitatively. We therefore pre-specified a protocol to test whether proximity between a protectant's target set and a cardiotoxicity module distinguishes trial-positive from trial-null cardioprotection pairs.

The protocol was written to fail cleanly. It fixed every analytic choice in advance, sealed the outcome data by hash before the interactome existed, and placed a positive control and a negative control *before* the point at which outcomes could be opened. This report is the result of that design working as intended: the study stopped at a gate, and the sealed outcomes were never used.

### Scope guards

Four constraints were fixed at the outset and held. We did not build a bespoke knowledge graph. We did not attempt to predict which oncology drug is cardiotoxic, a question addressed repeatedly since 2011. We excluded QT prolongation and all electrical endpoints, because an undirected, unsigned protein–protein interaction graph cannot represent state- and use-dependent channel block. And we imported no parameter from any prior work by this group; every graph parameter was specified fresh.

---

## 2. Methods

### 2.1 Integrity design

Three mechanisms enforced pre-specification, in code rather than by intention (`config/integrity.yaml`).

**Sealing.** Trial outcomes were extracted and coded *first*, before the interactome was built, and hashed into `sealed/OUTCOMES_HASH.txt`. This ordering prevents the opposite bias — assembling the outcome set after seeing which pairs scored well. Analysis code refuses to read `sealed/` until a verifying `COMMITMENT.txt` exists.

**Commitment.** After computing proximity for all 64 protectant–module pairs, we wrote every pair's z-score and its binary class under the pre-specified z < −1.0 cutoff to `results/predictions.json`, hashed it (SHA-256 `56018d7324ebf2543f850f11e4669cab4124a2d35f03349a3c55e0f2a34ee63a`) and committed the hash to version control before any gate could permit unsealing.

**Blinded module construction.** The protocol's ordering creates a residual risk it does not itself remove: the analyst who seals the outcomes has already seen them, and then builds the modules. While assembling the ground truth it became apparent that outcome code was perfectly confounded with module identity (§3.1), which is precisely the knowledge that could bias how the gene sets are drawn. Module construction was therefore delegated to a builder given only the §4 construction rules and the index agents, with no access to the sealed outcomes, the run log, or the analysis. It never looked up a cardioprotective drug.

All three threshold arms and both proximity definitions are reported in every table; no arm was dropped for being unfavourable.

### 2.2 Data sources

All sources were downloaded once, hashed and frozen (`data/raw/PROVENANCE.json`):

| Source | Use | Size | SHA-256 (first 16) |
|---|---|---|---|
| STRING v12.0 human (9606) links | interactome | 83,164,437 B | `3e22f32572211aa3` |
| STRING v12.0 protein info | ENSP → symbol | 1,970,090 B | `144de4b0d98c6a7d` |
| STRING v12.0 aliases | symbol resolution | 19,777,800 B | `b65f730b993ed0c1` |
| DGIdb interactions | drug–target edges | 12,178,745 B | `08af778126a4f22a` |
| HGNC complete set | symbol namespace | 17,007,798 B | `6df77ac3cbaeb86a` |

**Deviation.** DrugBank, specified as a target backfill, requires a licensed download and was omitted. Target assembly ran on DGIdb alone; per-drug coverage is reported in full and Gate 1 tested whether it sufficed.

### 2.3 Graph construction

Undirected graphs were built from the combined score at each threshold, with every symbol normalised to an HGNC-approved symbol before touching the graph. Analysis was restricted to the largest connected component (LCC).

| Threshold | Nodes (LCC) | Edges (LCC) | Components | STRING symbols unmapped by HGNC |
|---|---|---|---|---|
| 400 | 19,221 | 919,509 | 2 | 259 |
| **700 (primary)** | **15,726** | **234,156** | 125 | 148 |
| 900 | 11,605 | 99,615 | 245 | 89 |

**Deviation.** The protocol justified 700 as primary because it was the threshold a prior manuscript's code executed. That paper's revision was withdrawn and will not appear, so the justification was restated as free-standing: 700 is STRING's own high-confidence cutoff. The grid was unchanged.

### 2.4 Modules

Four modules were seeded from named published mechanism reviews. A gene entered only if named in ≥2 of that module's seed sources; symbols were HGNC-normalised; no gene could belong to two modules, overlaps being resolved by majority of seed sources with ties dropped from both.

| Module | Mechanism | Seed sources | Declared | ≥2-source | HGNC-mapped | In LCC700 | Mapping loss |
|---|---|---|---|---|---|---|---|
| M1 | anthracycline cardiomyopathy | 7 | 34 | 34 | 34 | **34** | 0.000 |
| M2 | anti-HER2 cardiac dysfunction | 13 | 15 | 15 | 15 | **15** | 0.000 |
| M3 | VEGF-pathway inhibition | 8 | 14 | 14 | 14 | **13** | 0.000 |
| M4 | proteasome-inhibitor dysfunction | 7 | 15 | 15 | 15 | **15** | 0.000 |

All 35 seed-source entries were independently re-verified against Europe PMC by PMID: every one is a real, review-typed article with a matching publication year. No fabricated references. One review (PMID 41189010) seeds both M1 and M2, recorded because M1 versus M2 is the comparison of interest.

Three weaknesses were found by executing the rules and were **not repaired**, because repair after seeing module contents is a degree of freedom the protocol forbids:

1. **M3 reached only 13 genes in the LCC**, below the §4 minimum of 15 (Gate 0).
2. **The overlap rule is biased by unequal source counts.** M2 had 13 reviews and M3 had 8, so shared signalling nodes migrated systematically to M2 (AKT1, MAPK1, EGFR). NOS3 — endothelial nitric oxide synthase, named in M3's own core biology — was an exact 4–4 tie and was dropped from both modules. A majority rule over source counts is not a sound tie-break when modules have different numbers of sources.
3. **No proteasome subunit gene is in M4.** Across all seven M4 reviews, only PSMB10 is ever written as a symbol, once; PSMB5 appears nowhere, the reviews describing proteasome inhibition in prose. Adding it would have been fabrication.

### 2.5 Target sets

Targets were pulled from DGIdb by an explicit per-drug allow-list of spellings rather than fuzzy matching, because DGIdb files drugs under salt forms, metabolites and fixed-dose combinations. Six drugs appear to have no targets under exact-name matching (atorvastatin is filed as `ATORVASTATIN CALCIUM TRIHYDRATE`, candesartan as `CANDESARTAN CILEXETIL`); fuzzy matching would instead have swept in `2-hydroxyatorvastatin` and `amlodipine / atorvastatin / perindopril arginine`. Every accepted spelling and every exclusion is recorded in `src/build_targets.py`, and each drug–target edge carries its DGIdb source database and interaction type.

All **16 of 16** protectants had ≥1 target in the LCC. Median `direction_coverage` — the fraction of a drug's targets whose interaction type states a direction — was **0.42**, ranging from 0.04 (atorvastatin, 52 targets) to 0.83 (nebivolol).

The five negative controls (loratadine, omeprazole, levothyroxine, montelukast, ranitidine) were selected for having no plausible cardioprotective mechanism and no cardio-oncology trial. Ranitidine was declared the fifth control before any proximity was computed, with finasteride as a stated fallback.

### 2.6 Metric

Primary: closest-distance proximity (Guney/Menche), the mean over targets *t* of the shortest-path distance to the nearest module gene. Because the interactome is study-biased, the reported quantity is a z-score against 1000 random (T′, M′) pairs drawn by binned degree matching (≥100 nodes per bin), matching the degree distribution of the target set and of the module separately. Secondary: Menche separation S_AB, reported alongside and never promoted. Seed 20261117; a second seed was frozen and deliberately left unused.

### 2.7 Gates

Evaluated in order, each returning PASS/CONDITIONAL/FAIL with the numbers that produced the call. A FAIL stops the study.

---

## 3. Results

### 3.1 Properties of the evidence base

*Established while building the ground truth, before the interactome existed. These did not inform any analysis decision, and the pair table was never joined to any proximity value.*

Three facts emerged that constrain any study of this design:

1. **M3 and M4 yield zero evaluable pairs.** No completed prospective randomised cardioprotection trial was identified against VEGF-pathway inhibitor cardiac dysfunction, or against proteasome-inhibitor cardiac dysfunction. The only randomised VEGF-side evidence located is a mouse study. Half the modules cannot contribute to an outcome analysis at all.
2. **The pre-specified primary test could not have attained significance.** Thirteen pairs were evaluable; after the pre-specified exclusion of MIXED pairs the primary comparison was 4 versus 3. Computed combinatorially from group sizes alone, the two-sided exact Wilcoxon rank-sum has a floor of p = 0.0571 at those sizes. It cannot return p < 0.05 however perfectly the hypothesis holds.
3. **Outcome code is perfectly confounded with module identity.** Every POSITIVE pair belongs to M1 and every NULL pair to M2. The comparison is therefore entirely between-module, and any proximity difference is indistinguishable from a difference between the modules themselves. This is an identifiability failure, not a power problem; no increase in sample size within this design removes it.

These findings are reported because they are the binding constraint on the question, and a reader attempting a similar study should know them before starting.

### 3.2 Gate results (STRING 700, pre-unsealing)

| Gate | Verdict | Numbers |
|---|---|---|
| 0 module viability | **CONDITIONAL** | M3 = 13 genes (<15); 3 of 4 modules survive |
| 1 target coverage | **CONDITIONAL** | 16/16 protectants mapped; median direction coverage 0.42 (<0.5) |
| 3 positive control | **PASS** | dexrazoxane–M1 z = −2.651; cutoff −1.602; 4.7th percentile of 64 |
| 4 negative control | **FAIL** | 2 violations, both levothyroxine: M2 z = −2.645, M3 z = −3.125 |

Gate 1's CONDITIONAL is stated as a primary limitation, as the protocol requires: for most of these drugs DGIdb does not record whether the interaction is inhibition or activation.

### 3.3 Gate 3 — the positive control passed

Dexrazoxane against the anthracycline module reached the 4.7th percentile of all 64 protectant–module z-scores (Figure 2). The result strengthens monotonically with interactome confidence: 12.5th percentile at STRING 400, 4.7th at 700, and **0.0th at 900**, where it is the single most proximal pair in the panel.

Dexrazoxane is also the most module-*selective* pair in the study (Figure 1): z = −2.65 against M1 but +0.46, +0.29 and +0.20 against M2, M3 and M4. It is close to the anthracycline module and to nothing else.

Exploratory leave-one-target-out (§3.5) shows the signal is carried by TOP2B. The method found the right answer through the right gene.

### 3.4 Gate 4 — the negative control failed

Levothyroxine reached z = −2.645 against M2 and −3.125 against M3, inside the protectant top quartile, despite sharing **no gene** with either module. It is negative against all four modules (M1 −1.49, M4 −1.12). Its DGIdb targets are dominated by broad transcriptional regulators — THRA, THRB, PPARG, NFE2L2, AHR — together with the core cardiac transcription factor NKX2-5.

The degree-matched null corrects for how many edges a gene has. It does not correct for a transcription factor's regulatory *reach*. A drug acting on cardiac transcription is therefore close to any cardiac module, and proximity measures where a drug acts, not whether it is relevant.

### 3.5 All arms (rule 2.4)

| Arm | Cutoff | dexrazoxane–M1 | Percentile | Gate 3 | Gate 4 (pair) | Gate 4 (drug) | Violating controls |
|---|---|---|---|---|---|---|---|
| 400 / z | −1.299 | −1.689 | 12.5% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |
| 400 / S_AB | 0.192 | 0.198 | 28.1% | **FAIL** | FAIL | FAIL | levothyroxine, loratadine, omeprazole |
| **700 / z** | −1.602 | **−2.651** | **4.7%** | **PASS** | **FAIL** | CONDITIONAL | levothyroxine |
| 700 / S_AB | 0.284 | 0.234 | 15.6% | PASS | FAIL | CONDITIONAL | loratadine |
| 900 / z | −1.170 | −3.432 | **0.0%** | PASS | FAIL | FAIL | levothyroxine, loratadine, ranitidine |
| 900 / S_AB | 0.377 | 0.117 | 7.8% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |

Gate 3 passes in 5 of 6 arms, failing only under the secondary metric at the lowest threshold. **Gate 4 passes in none.** The identity of the breaching control varies by arm, so the specificity failure is not a quirk of one drug, one threshold or one metric.

### 3.6 Exploratory analyses

*Labelled exploratory under rule 2.3. These cannot and do not change any recorded verdict.*

**Gate 3 is carried by TOP2B.** Removing TOP2B from dexrazoxane's five-target set moves z from −2.651 to −0.764 (Δ +1.887). No other target shifts it by more than 0.66. TOP2B has degree 15, so this is not a hub artefact. Topoisomerase 2-beta is the established mediator of anthracycline cardiotoxicity and dexrazoxane's own target.

**The Gate 4 breach is distributed.** The largest single-target effect for levothyroxine is Δ +0.461 (NOX3, versus M2) and Δ +0.508 (AHR, versus M3). Every leave-one-out leaves z below −2.1. No exclusion of a single "bad" target would repair specificity.

**Module selectivity.** Ranking pairs by z for one module minus mean z for the other three: dexrazoxane–M1 is most selective at −2.97, ahead of atorvastatin–M1 at −2.27. M3 dominates the remainder of the ranking, consistent with its small size inflating closest-distance proximity.

### 3.7 The study stopped here

Gate 4 failed. Under §7 a FAIL stops the study, so Gate 2 was not run, `sealed/outcomes.json` was not opened, and no association between proximity and trial outcome was estimated. The seal is intact and verifiable: the file appears in version control only in the initial commit and was never modified or read.

---

## 4. Discussion

A pre-specified network-proximity criterion recovered the single clearest case of mechanism-matched cardioprotection in its own domain, and recovered it through the mechanistically correct gene, on a generic human interactome with no cardiac tissue context. That is a real and non-trivial positive finding about the method's **sensitivity**, and it strengthens as interactome confidence increases.

The same criterion placed levothyroxine — a drug with no cardioprotective indication, no cardio-oncology trial and no gene in common with the modules it scored against — deeper inside the top quartile than most genuine cardioprotectants. That is a decisive finding about its **specificity**, and it held in every arm.

The explanation is mechanistic rather than statistical. Closest-distance proximity with a degree-matched null asks whether a drug's targets sit near a module more than chance allows, given how well studied those targets are. It does not ask whether the drug's targets *regulate* the module or merely sit adjacent to it in an undirected graph. Drugs whose targets are transcription factors with broad regulatory reach are close to everything cardiac. Thyroid hormone receptors are a clean example: they are not in any module, yet they are near all of them.

This has a direct consequence for drug repurposing by proximity. A proximity hit is not evidence of mechanism matching unless the method can also exclude drugs that are merely transcriptionally central. Our Gate 4 is a cheap and strong test of that, and we would encourage its routine use: the cost of five negative-control drugs is negligible beside the cost of a false repurposing claim.

Two design lessons also emerged. First, the evidence base cannot support the original question (§3.1): two of four mechanisms have no cardioprotection trials at all, and among those that do, trial outcome is perfectly confounded with mechanism. Anyone proposing to test mechanism matching against trial success in cardio-oncology should establish this before building anything. Second, a majority-of-sources tie-break for module overlap is unsound when modules are seeded from unequal numbers of reviews; it cost us NOS3 from the VEGF module, which is close to the worst possible single loss for that biology.

---

## 5. Limitations

Limitations 1–7 were written into the protocol **before the results existed**, so they could not be softened once the numbers were in. They are reproduced with what the study subsequently showed.

1. **Sample size.** Eight to fifteen evaluable pairs cannot support a prediction claim. Thirteen were evaluable; the primary comparison would have been 4 versus 3, with an attainable-p floor of 0.0571. No prediction claim is made, and no classification metric is reported.
2. **No direction of effect.** STRING edges are undirected and unsigned. The analysis locates where a protectant acts relative to a toxicity module; it cannot establish that the drug opposes the mechanism. Median `direction_coverage` was 0.42, so for most drugs even the drug–target edge direction is unknown. *This is the limitation a reviewer will press hardest, and the Gate 4 failure is its direct consequence.*
3. **Literature-defined modules.** Gene sets come from reviews, not cardiac perturbation data. The two-source rule and pre-commitment constrain this but do not eliminate it. Detection also requires a review to write a symbol: a review that spells out "endothelial nitric oxide synthase" in full contributes nothing.
4. **Interactome study bias.** The degree-matched null addresses edge count but not module composition, which is drawn from the same biased literature — and, as Gate 4 showed, not regulatory reach either.
5. **Endpoint heterogeneity.** Trials mix surrogate LVEF change with clinical events. Moot here, since outcomes were never opened.
6. **Not cardiac-specific.** STRING is a generic human interactome; an interaction that does not occur in the heart is weighted the same as one that does.
7. **Single-analyst adjudication.** Outcome coding was done by one reader against published meta-analyses, with no second independent coder.

Discovered during execution and recorded in `RUNLOG.md`: M3 fell below the module-size minimum; the overlap tie-break is biased by unequal source counts; no proteasome subunit reached M4; §7 does not define whether a Gate 4 "violation" is a drug or a drug–module pair (the stricter pair-counting reading is the headline verdict, and both are reported); and levothyroxine met the §5 negative-control criterion as written but is not pharmacologically inert in the heart. None was repaired after the fact.

---

## 6. Data, code and reproducibility

All configs, source hashes, module definitions with per-gene provenance, drug–target provenance, gate outputs, figures and a complete run log — including abandoned runs and every protocol deviation — are in the `mmc01/` repository.

- Ground truth: `sealed/outcomes.json`, SHA-256 `16a1bf84d9369805e773bf2cc0dc624db0816865fc906c9d451826d2cf53fb50` — sealed, never opened.
- Predictions: `results/predictions.json`, SHA-256 `56018d7324ebf2543f850f11e4669cab4124a2d35f03349a3c55e0f2a34ee63a` — committed before unsealing was permitted.
- Modules: `config/modules.yaml`, SHA-256 `95f84b7b46e8d3ae08afe8d0b03ba1913c7c3906f315b5e2f060d8ccf8ba2c65`.
- Seed: 20261117, 1000 permutations, printed in every output.

## Figures

- **Figure 1.** Proximity landscape: 16 protectants and 5 negative controls × 4 modules, degree-matched z at STRING 700, one colour scale.
- **Figure 2.** Gate 3 positive control: all 64 pairs plotted individually across three thresholds, dexrazoxane–M1 marked against the top-quartile cutoff.
- **Figure 3.** Gate 4 specificity: protectant versus negative-control z by arm, with violations ringed. Replaces the protocol's leave-one-out stability plot, which is not applicable because no primary statistic was computed.

---

## Author note on what this study is

This is a negative methods finding, reported as such. It is not a result about cardioprotection: no cardioprotection outcome was ever joined to a proximity score. The protocol was built so that the study could fail cleanly before that join was permitted, and it did.
