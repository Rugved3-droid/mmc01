# Cover letter

To the Editor-in-Chief
*Cardiovascular Toxicology*

Dear Editor,

We submit for your consideration our Research Article, **"Pre-registered interactome analysis of four cancer-therapy cardiotoxicity mechanisms recovers the dexrazoxane–topoisomerase-2β axis."**

Cancer-therapy cardiotoxicity is mechanistically heterogeneous — anthracycline, anti-HER2, VEGF-pathway and proteasome-inhibitor injury proceed through different molecular processes — yet cardioprotection has largely been attempted with the same neurohormonal agents across all of them. We asked whether protein-interaction network proximity between a drug's targets and the molecular module of a specific cardiotoxicity reflects that mechanism.

The distinguishing feature of this work is that every analytic choice was fixed before any data were examined. The interactome, confidence thresholds, proximity metric, null model, drug list, binary cutoff and four decision gates were all specified in advance. Cardioprotection trial outcomes were coded and sealed by SHA-256 before the interactome was built; the four cardiotoxicity modules were constructed from 35 published mechanism reviews by a builder blinded to all outcome information; and all 64 predictions were hashed and committed to a public version-controlled record before any gate could permit unsealing.

Three findings may interest your readership:

1. The pre-specified positive control passed. Dexrazoxane against the anthracycline module reached the 4.7th percentile of all computed proximity scores, strengthening to the most proximal pair of all on the highest-confidence interactome. Leave-one-target-out attributes this signal to **TOP2B** — the established mediator of anthracycline cardiotoxicity and dexrazoxane's own target. The method recovered the correct pair through the correct gene, on a generic human interactome with no cardiac tissue context.

2. Cardioprotectants as a class sit significantly closer to cardiotoxicity modules than a 100-drug random background (p = 0.0022), under a deliberately conservative test.

3. The method nonetheless lacks drug-level specificity. Levothyroxine, which shares no gene with the modules it scored against, ranked among the most proximal agents examined, because the degree-matched null corrects for connectivity but not for transcription-factor regulatory reach.

We also report two results that constrain future work in this area: two of the four major cardiotoxicity mechanisms have no completed prospective cardioprotection trial, and among those that do, trial outcome is perfectly confounded with mechanism identity. Because the pre-specified negative-control gate failed, the study stopped at that gate as the protocol required, the sealed outcomes were never opened, and no proximity-versus-trial-outcome association is claimed.

All code, configuration, per-gene and per-edge provenance, integrity hashes, and a complete run log — including abandoned runs, every protocol deviation, and a superseded first draft whose framing we withdrew after our own calibration analysis showed it to be incorrect — are publicly available at https://github.com/Rugved3-droid/mmc01.

This manuscript is original, has not been published previously, and is not under consideration elsewhere. All authors have approved the submission. We have no competing interests to declare, and the study received no funding. The study used only publicly available database and published-literature resources; no human participants, human material, human data or animals were involved, so ethics approval was not required. In accordance with publisher policy, our use of a large language model as a computational assistant is declared in Methods Section 2.8; no language model is an author.

Thank you for considering our work.

Yours sincerely,

**Rugved Parmar**
SUNY Downstate Health Sciences University, Brooklyn, New York, USA
rugved.parmar@downstate.edu

on behalf of Md Fahim and Adam Budzikowski
