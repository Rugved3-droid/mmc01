# Pre-registered interactome analysis of four cancer-therapy cardiotoxicity mechanisms recovers the dexrazoxane–topoisomerase-2β axis

**Article type:** Research Article

Rugved Parmar

*Affiliation to be completed*

Corresponding author: *institutional e-mail required at submission*

ORCID: *to be completed*

---

## Abstract

Cancer-therapy cardiotoxicity is mechanistically heterogeneous, yet cardioprotection has largely been attempted with the same neurohormonal agents across unrelated mechanisms. We asked whether protein-interaction network proximity between a drug's targets and the molecular module of a specific cardiotoxicity reflects that mechanism, under a protocol fixed entirely in advance. Four cardiotoxicity modules — anthracycline, anti-HER2, VEGF-pathway and proteasome-inhibitor — were assembled from 35 published mechanism reviews under a two-source-per-gene rule by a builder blinded to all outcome information. Closest-distance proximity to the targets of 16 cardioprotectants was computed on STRING v12.0 against a 1000-permutation degree-matched null, at three confidence thresholds, with all parameters, the binary cutoff and four decision gates specified before any data were read. The pre-specified positive control passed: dexrazoxane against the anthracycline module reached z = −2.651 (4.7th percentile of 64 pairs), passing in five of six threshold-by-metric arms and strengthening with interactome confidence to the most proximal pair of all at STRING 900. Leave-one-target-out attributed this to TOP2B (Δz = +1.887), the established mediator of anthracycline cardiotoxicity. Cardioprotectants were significantly closer to cardiotoxicity modules than a 100-drug random background (median z −0.722 vs −0.361; p = 0.0022). However, levothyroxine, sharing no gene with either module, entered the top quartile against two of them, and the pre-specified negative-control gate failed. Interactome proximity carries genuine mechanistic signal in cardiotoxicity but lacks drug-level specificity, and quartile-threshold criteria are poorly calibrated as specificity tests.

**Graphical Abstract:** *(to be placed in the Abstract section at submission; source file `results/figures/graphical_abstract.png`)*

**Keywords:** cardio-oncology; anthracycline cardiotoxicity; topoisomerase-2β; network pharmacology; dexrazoxane; pre-registration

**Abbreviations:** APC, article processing charge; CTRCD, cancer-therapy-related cardiac dysfunction; DGIdb, Drug–Gene Interaction Database; HGNC, HUGO Gene Nomenclature Committee; LCC, largest connected component; LVEF, left ventricular ejection fraction; PPI, protein–protein interaction; TOP2B, topoisomerase-2β.

---

## 1. Introduction

Cardiotoxicity from cancer therapy is not one disease. Anthracycline cardiomyopathy, anti-HER2 cardiac dysfunction, VEGF-pathway inhibitor cardiovascular toxicity and proteasome-inhibitor cardiac injury proceed through distinct molecular processes. Anthracycline injury is initiated in large part through topoisomerase-2β in cardiomyocytes [6]; anti-HER2 dysfunction follows interruption of neuregulin–ERBB signalling; VEGF-pathway toxicity is vascular and endothelial; proteasome-inhibitor toxicity is a proteostatic failure.

Cardioprotection trials have not respected these distinctions. The same renin–angiotensin blockers and beta-blockers have been tested across mechanisms, with inconsistent results. The one agent whose protective mechanism is molecularly matched to its target toxicity — dexrazoxane, acting on the topoisomerase-2β/iron axis of anthracycline injury — is also the one with the most consistent evidence of benefit [7].

This raises a question that is testable computationally. If a cardioprotectant's molecular targets sit close to the molecular machinery of a specific cardiotoxicity, does that proximity reflect the mechanism? Network proximity has become a standard instrument for such questions [1, 2], but it is normally applied without pre-specification and without negative controls, so its behaviour in a domain where the right answer is partly known has not been established.

We therefore fixed a protocol in advance — interactome, thresholds, metric, null model, drug list, cutoff and four decision gates — and executed it. Two gates were designed to be falsifying. A positive-control gate required dexrazoxane to be recovered against the anthracycline module; failure would mean the method cannot find the clearest case in its own domain. A negative-control gate required drugs with no cardioprotective rationale to stay out of the top quartile.

Electrical endpoints, including QT prolongation, were excluded by design: an undirected, unsigned PPI graph cannot represent state- and use-dependent ion-channel block, and including such endpoints would make the analysis indefensible.

---

## 2. Materials and Methods

### 2.1 Pre-specification and integrity controls

Every analytic parameter was fixed in a written protocol before any data were downloaded. Three controls enforced this in code rather than by intention.

**Sealing.** Cardioprotection trial outcomes were extracted, coded and sealed by SHA-256 *before* the interactome was built, so that the outcome set could not be assembled after seeing which drug–module pairs scored well. Analysis code refuses to read the sealed file until a verifying commitment exists.

**Commitment.** After computing proximity for all 64 protectant–module pairs, every z-score and its binary class under the pre-specified cutoff were written to a predictions file, hashed (SHA-256 `56018d73…`), and committed to version control before any gate could permit unsealing.

**Blinded module construction.** Modules were built by a separate agent given only the construction rules of §2.3 and the index agents, with no access to the sealed outcomes, the run log, or the analysis. It never queried any cardioprotective drug. This was adopted because the protocol's ordering requires outcomes to be sealed first, leaving the analyst who then defines the modules already aware of them.

All three confidence thresholds and both proximity definitions are reported in every table; no arm was dropped.

### 2.2 Data sources

STRING v12.0 (*Homo sapiens*, 9606) protein links, protein information and aliases [3]; DGIdb interactions [4]; and the HGNC complete set [5] were each downloaded once, hashed, and frozen. DrugBank, specified in the protocol as a target backfill, requires a licensed download and was not used; the resulting coverage is reported in full and was tested by a pre-specified gate.

Undirected graphs were built from the combined score at thresholds 400, 700 (primary) and 900, with every symbol normalised to an HGNC-approved symbol before entering the graph. Analysis was restricted to the largest connected component (LCC): 19,221 nodes / 919,509 edges at 400; **15,726 nodes / 234,156 edges at 700**; 11,605 nodes / 99,615 edges at 900.

### 2.3 Cardiotoxicity modules

Four modules were seeded from named published mechanism reviews: M1 anthracycline cardiomyopathy [8–14], M2 anti-HER2 cardiac dysfunction [15–27], M3 VEGF-pathway inhibition [28–35], M4 proteasome-inhibitor cardiac dysfunction [36–42]. A gene entered a module only if named in at least two of that module's seed sources; symbols were HGNC-normalised; no gene could belong to two modules, overlaps being resolved by majority of seed sources with ties dropped from both.

Genes were extracted from review full text rather than from background knowledge, with sections concerning therapy, prevention, diagnosis, biomarkers or imaging removed before scanning, so that no cardioprotective agent could influence module membership. All 35 seed-source entries were independently re-verified by PMID against Europe PMC; every one is a real, review-typed article with a matching year.

Final module sizes in the primary LCC were M1 = 34, M2 = 15, M3 = 13 and M4 = 15 genes, with zero HGNC mapping loss.

### 2.4 Cardioprotectant target sets

Sixteen agents tested as cardioprotection in prospective cardio-oncology trials were specified in advance: dexrazoxane, enalapril, lisinopril, candesartan, valsartan, carvedilol, metoprolol, nebivolol, bisoprolol, spironolactone, eplerenone, atorvastatin, rosuvastatin, sacubitril/valsartan, dapagliflozin and empagliflozin.

Targets were taken from DGIdb using an explicit per-drug allow-list of spellings rather than fuzzy matching, because DGIdb files drugs under salt forms, metabolites and fixed-dose combinations; six agents appear to have no targets under exact-name matching, while fuzzy matching would wrongly incorporate metabolites and combination products. Every accepted spelling and exclusion is recorded in the accompanying code, and each drug–target edge carries its DGIdb source database and interaction type.

`direction_coverage` — the fraction of a drug's targets whose DGIdb interaction type states a direction — was recorded per drug as an explicit measure of how much of the sign problem remains.

Five agents with no plausible cardioprotective mechanism and no cardio-oncology trial were specified as negative controls: loratadine, omeprazole, levothyroxine, montelukast and ranitidine.

### 2.5 Proximity metric

The primary metric was closest-distance proximity [1]: for target set *T* and module *M*, the mean over *t* ∈ *T* of the shortest-path distance to the nearest module gene. Because the interactome is study-biased, the analysed quantity is a z-score against 1000 random (*T′*, *M′*) pairs drawn by binned degree matching (≥100 nodes per bin), matching the degree distribution of the target set and of the module separately. Menche separation *S*<sub>AB</sub> [2] was reported as a secondary metric and never promoted. The binary cutoff was fixed at z < −1.0. Random seed 20261117 was frozen and is printed in every output.

### 2.6 Decision gates

Four gates were specified in advance, each returning PASS, CONDITIONAL or FAIL with the numbers producing the call; a FAIL stops the study. **Gate 0** required every module to reach 15 genes. **Gate 1** required ≥12 of 16 protectants to have mapped targets, and returned CONDITIONAL if median `direction_coverage` fell below 0.5. **Gate 3** required dexrazoxane–M1 to fall within the top quartile of all computed z-scores. **Gate 4** required that no negative-control drug reach that quartile.

### 2.7 Exploratory analyses

Analyses not pre-specified are labelled exploratory throughout and cannot alter any recorded gate verdict: leave-one-target-out attribution; a module-selectivity index (z for one module minus the mean z for the other three); a calibration check on the Gate 4 criterion; and a random-drug background of 100 DGIdb drugs with 3–60 LCC targets, sampled excluding all study drugs.

### 2.8 Software and declaration of AI assistance

Analyses used Python 3.12 with NumPy, SciPy and Matplotlib. All code, configuration files, hashes and a complete run log — including abandoned runs and every protocol deviation — accompany this article.

In accordance with publisher policy, the authors declare that a large language model (Claude, Anthropic) was used as a computational assistant in this work: it implemented the analysis pipeline, performed the literature extraction underlying module construction as the blinded builder described in §2.1, and drafted portions of the manuscript text. No large language model is an author. All analytic decisions, the protocol, the gate definitions and the final interpretation are the responsibility of the human author, who verified the numerical results against the output files and independently confirmed every cited reference against Europe PMC.

---

## 3. Results

### 3.1 Gate outcomes

| Gate | Verdict | Numbers |
|---|---|---|
| 0 module viability | CONDITIONAL | M3 = 13 genes (<15); 3 of 4 modules met the minimum |
| 1 target coverage | CONDITIONAL | 16/16 protectants mapped; median `direction_coverage` 0.42 |
| 3 positive control | **PASS** | dexrazoxane–M1 z = −2.651; cutoff −1.602; 4.7th percentile |
| 4 negative control | **FAIL** | 2 violations, both levothyroxine: M2 −2.645, M3 −3.125 |

Gate 1's CONDITIONAL verdict is a substantive limitation: for most of these drugs DGIdb does not record whether the interaction is inhibition or activation, so the analysis locates where a drug acts, not whether it opposes the mechanism.

### 3.2 The positive control was recovered, through TOP2B

Dexrazoxane against the anthracycline module reached the 4.7th percentile of all 64 protectant–module z-scores (Fig. 2). The result strengthened monotonically with interactome confidence — 12.5th percentile at STRING 400, 4.7th at 700, and 0.0th at 900, where it was the single most proximal pair in the study — and passed in five of six threshold-by-metric arms, failing only under the secondary *S*<sub>AB</sub> metric at the lowest threshold (Table 1).

Dexrazoxane was also the most module-*selective* agent in the panel (Fig. 1): z = −2.65 against the anthracycline module but +0.46, +0.29 and +0.20 against the anti-HER2, VEGF and proteasome modules. Its exploratory selectivity index (−2.97) was the most extreme of all 64 pairs.

Exploratory leave-one-target-out attributed the signal to a single gene. Removing TOP2B from dexrazoxane's five-target set moved z from −2.651 to −0.764 (Δ = +1.887); no other target shifted it by more than 0.66. TOP2B has degree 15 in the primary graph, so this is not an artefact of hub connectivity. The method therefore recovered the correct pair through the gene that mediates the toxicity [6].

### 3.3 Cardioprotectants are closer to cardiotoxicity modules than drugs in general

Because the pre-specified negative-control set contained only five agents, an exploratory random-drug background was constructed: 100 DGIdb drugs with 3–60 LCC targets, sampled at random with all study drugs excluded, giving 400 background drug–module pairs.

Cardioprotectants were significantly closer to the cardiotoxicity modules than this background (median z −0.722 vs −0.361; mean −0.855 vs −0.362; permutation two-sided *p* = 0.0022). Only 16.8% of background pairs fell inside the protectant top quartile, against the 25% expected if the two groups were exchangeable.

This test is conservative: the background drugs were not screened for cardiac activity, so any genuinely cardioactive drug among them works against the observed difference.

### 3.4 The negative-control gate failed, and the criterion was mis-calibrated

Levothyroxine reached z = −2.645 against the anti-HER2 module and −3.125 against the VEGF module, despite sharing **no gene** with either, and was negative against all four modules. Its DGIdb targets are dominated by broad transcriptional regulators — THRA, THRB, PPARG, NFE2L2, AHR — together with the cardiac transcription factor NKX2-5. Exploratory leave-one-target-out showed the effect was distributed rather than attributable to any one gene: the largest single-target contribution was Δ = +0.461 (NOX3) and +0.508 (AHR), and every leave-one-out left z below −2.1.

An exploratory calibration check shows that the gate itself was poorly posed. A quartile contains 25% of values by construction, so if the five controls were exchangeable with the protectants one would expect five of the twenty control pairs inside it. Two were observed. Across arms, the negative controls were in fact *farther* from the modules than the cardioprotectants (permutation two-sided *p* = 0.0027 at STRING 400, *p* = 0.0168 at 700, *p* = 0.152 at 900). Gate 4 as written demanded zero overlap between two distributions that overlap by construction, a criterion almost no method could satisfy.

The recorded verdict is nevertheless retained as FAIL. It was pre-specified, it was executed, and it is reported as it fell; the calibration analysis is exploratory and changes the interpretation, not the result.

### 3.5 Why the trial-outcome analysis was not performed

The protocol's original question was whether proximity predicts cardioprotection trial success. That analysis was not run, for two reasons recorded before unsealing.

First, a FAIL at Gate 4 stops the study by pre-specification. The sealed outcome file was therefore never opened; it appears in version control only in the initial commit.

Second, and independently, assembling the sealed ground truth established that the evidence base cannot support the question. No completed prospective randomised cardioprotection trial was identified against VEGF-pathway or proteasome-inhibitor cardiac toxicity, so two of four modules can contribute no evaluable pairs at all. Among the thirteen evaluable pairs, the pre-specified exclusion of pairs with discordant trial evidence left a 4-versus-3 comparison, for which the two-sided exact Wilcoxon rank-sum has an attainable-*p* floor of 0.0571 and therefore cannot reach significance however strong the effect. Every trial-positive pair belonged to the anthracycline module and every trial-null pair to the anti-HER2 module, so outcome status was perfectly confounded with module identity — an identifiability failure that no increase in sample size within this design would remove.

These are properties of the published trial literature, established before the interactome was built, and are reported so that others do not repeat the design.

---

## 4. Discussion

A protocol fixed entirely in advance recovered the clearest known case of mechanism-matched cardioprotection, on a generic human interactome with no cardiac tissue context, and did so through topoisomerase-2β — the gene that actually mediates anthracycline cardiotoxicity [6]. Dexrazoxane was not merely proximal to the anthracycline module; it was proximal to that module and to no other, and the signal sharpened as low-confidence interactions were removed. That is a meaningful validation of network proximity as an instrument in cardiotoxicity, and it was obtained under conditions that make post-hoc tuning detectable.

The class-level finding extends this. Cardioprotectants sat closer to cardiotoxicity modules than a random drug background at *p* = 0.0022, under a test made conservative by not screening the background for cardiac activity. Interactome position therefore carries real information about which drugs engage cardiotoxicity biology.

The limits are equally clear. Levothyroxine — no cardioprotective indication, no cardio-oncology trial, and no gene shared with the modules it scored against — was among the most proximal agents examined. The explanation is mechanistic rather than statistical. Closest-distance proximity with a degree-matched null asks whether targets lie near a module more than chance allows given how well studied they are. It does not ask whether those targets *regulate* the module or merely sit adjacent to it in an undirected graph. Thyroid hormone receptors and the other broad transcriptional regulators in levothyroxine's target set are close to all cardiac biology without being specific to any of it. Group-level discrimination therefore coexists with drug-level false positives, and a proximity hit for an individual agent is not evidence of mechanism matching.

Two methodological conclusions follow for network pharmacology generally. First, negative controls belong in proximity studies as a matter of routine; the cost of a handful of control drugs is negligible beside the cost of a false repurposing claim, and in this study the controls were the only thing that revealed the specificity ceiling. Second, quartile-threshold criteria are badly calibrated as specificity tests. A rule that no control may enter the top quartile is far stricter than it sounds, because the quartile is defined to contain a quarter of the data. A distributional comparison against a sampled background, as in §3.3, is the better instrument, and we would recommend it in place of threshold-crossing rules.

For cardio-oncology specifically, the most consequential finding may be the one in §3.5. Two of the four major cardiotoxicity mechanisms have no completed cardioprotection trial, and among the mechanisms that do, trial outcome is perfectly confounded with mechanism identity. Any study proposing to relate mechanism matching to trial success should establish this before building anything.

### 4.1 Limitations

Limitations 1–7 were written into the protocol before results existed and are reported with what the study subsequently showed.

1. **No direction of effect.** STRING edges are undirected and unsigned, and median `direction_coverage` was 0.42, so for most agents even the drug–target edge direction is unknown. The analysis locates where a drug acts, not whether it opposes the mechanism. This is the limitation most directly responsible for the levothyroxine result.
2. **Literature-defined modules.** Gene sets derive from reviews, not from cardiac perturbation data. The two-source rule and pre-commitment constrain but do not remove this. Detection also requires a review to write a gene symbol: no proteasome subunit entered the proteasome module, because across all seven seed reviews only PSMB10 is written as a symbol, once. Adding PSMB5 would have been fabrication.
3. **A single positive control.** Gate 3 rests on one drug–module pair, because dexrazoxane is the only cardioprotection pair on which the field agrees. No second positive control exists to add.
4. **Interactome study bias.** The degree-matched null addresses edge count but neither module composition, drawn from the same biased literature, nor regulatory reach.
5. **Module construction rules.** M3 reached only 13 genes, below the pre-specified minimum. The overlap tie-break — majority of seed sources — is biased when modules have unequal numbers of sources: the anti-HER2 module had 13 reviews and the VEGF module 8, so shared signalling nodes migrated systematically to the former, and NOS3 was removed from both on an exact tie despite being core VEGF biology. These were recorded and deliberately not repaired, since repair after inspecting module contents is precisely the degree of freedom pre-specification exists to prevent.
6. **Not cardiac-specific.** STRING is a generic human interactome; an interaction that does not occur in myocardium is weighted identically to one that does.
7. **Single-analyst adjudication.** Outcome coding was performed by one reader; no second independent coder was available.

Additionally, the negative-control set itself was flawed. Levothyroxine satisfied the written selection criterion but is not pharmacologically inert in the heart. It was not replaced, as substitution after seeing the result would invalidate the control.

---

## 5. Conclusion

Under full pre-specification, interactome proximity recovered the dexrazoxane–topoisomerase-2β axis from the anthracycline cardiotoxicity module, and separated cardioprotective drugs from a random drug background. It did not achieve drug-level specificity: an agent with no mechanistic relationship to the modules scored among the most proximal. Network proximity is usable as a screening instrument in cardio-oncology provided it is paired with negative controls and distributional rather than threshold-based criteria, and provided its hits are treated as hypotheses about where a drug acts rather than evidence that it helps.

---

## Statements and Declarations

**Funding.** No funding was received for conducting this study.

**Competing interests.** The author has no competing interests to declare that are relevant to the content of this article.

**Ethics approval.** Not applicable. This study used only publicly available database and published-literature resources and involved no human participants, human material, human data or animals.

**Consent to participate / Consent to publish.** Not applicable.

**Data availability.** All data supporting this study are publicly available. STRING v12.0, DGIdb and HGNC were obtained from their public distributions; the exact files used are identified by SHA-256 in the accompanying provenance record. All derived data — module definitions with per-gene source provenance, drug–target assignments with per-edge provenance, proximity results for every arm, gate outputs, and the sealed outcome file with its hash — are provided with the code. Key integrity hashes: sealed outcomes `16a1bf84d9369805e773bf2cc0dc624db0816865fc906c9d451826d2cf53fb50`; committed predictions `56018d7324ebf2543f850f11e4669cab4124a2d35f03349a3c55e0f2a34ee63a`; frozen modules `95f84b7b46e8d3ae08afe8d0b03ba1913c7c3906f315b5e2f060d8ccf8ba2c65`.

**Code availability.** All analysis code, configuration files and the complete run log, including abandoned runs and protocol deviations, are provided.

**Author contributions.** R.P. conceived the study, wrote the protocol, defined the gates, supervised and verified all analyses, and approved the final manuscript. Use of an AI computational assistant is declared in §2.8.

---

## Figures

**Fig. 1** Proximity landscape. Sixteen cardioprotectants and five negative-control drugs against four cardiotoxicity modules, degree-matched proximity z at STRING 700 on a shared colour scale. Negative values indicate closer-than-null proximity. Dexrazoxane shows the most module-selective profile in the panel.

**Fig. 2** Gate 3 positive control. All 64 protectant–module z-scores plotted individually at each STRING threshold, with dexrazoxane–M1 marked against the pre-specified top-quartile cutoff. The positive control strengthens as interactome confidence increases.

**Fig. 3** Specificity. Cardioprotectant versus negative-control proximity z by threshold arm, with gate violations ringed, alongside the 100-drug random background distribution.

## Tables

**Table 1** Gate 3 and Gate 4 outcomes at every STRING threshold under both the primary closest-distance z and the secondary *S*<sub>AB</sub> metric. All arms are reported; none was dropped. Gate 4 is shown under both readings of the protocol's ambiguous "violation" unit (drug–module pair, and distinct drug).

| Arm | Top-quartile cutoff | dexrazoxane–M1 | Percentile | Gate 3 | Gate 4 (by pair) | Gate 4 (by drug) | Violating controls |
|---|---|---|---|---|---|---|---|
| 400 / z | −1.299 | −1.689 | 12.5% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |
| 400 / *S*AB | 0.192 | 0.198 | 28.1% | FAIL | FAIL | FAIL | levothyroxine, loratadine, omeprazole |
| **700 / z (primary)** | **−1.602** | **−2.651** | **4.7%** | **PASS** | **FAIL** | CONDITIONAL | levothyroxine |
| 700 / *S*AB | 0.284 | 0.234 | 15.6% | PASS | FAIL | CONDITIONAL | loratadine |
| 900 / z | −1.170 | −3.432 | 0.0% | PASS | FAIL | FAIL | levothyroxine, loratadine, ranitidine |
| 900 / *S*AB | 0.377 | 0.117 | 7.8% | PASS | CONDITIONAL | CONDITIONAL | levothyroxine |

**Table 2** Exploratory calibration of the Gate 4 criterion. A top quartile contains 25% of values by construction, so five of the twenty negative-control pairs would be expected inside it if controls and cardioprotectants were exchangeable.

| Arm | Controls in top quartile | Expected by chance | Protectant median z | Control median z | Permutation *p* |
|---|---|---|---|---|---|
| 400 / z | 1 | 5.0 | −0.359 | +0.545 | 0.0027 |
| 700 / z | 2 | 5.0 | −0.722 | −0.052 | 0.0168 |
| 900 / z | 6 | 5.0 | −0.560 | −0.058 | 0.1518 |
