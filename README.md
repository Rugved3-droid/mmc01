# MMC-01 — Mechanism-Matched Cardioprotection

Pre-registered network-proximity analysis of four cancer-therapy cardiotoxicity
mechanisms. This repository is the complete record of the study: protocol,
configuration, code, results, figures, every protocol deviation, and the sealed
ground truth that was never opened.

**Paper:** *Pre-registered interactome analysis of four cancer-therapy
cardiotoxicity mechanisms recovers the dexrazoxane–topoisomerase-2β axis.*
Parmar R, Fahim M, Budzikowski A. SUNY Downstate Health Sciences University.

## Headline results

| Finding | Value |
|---|---|
| Positive control (dexrazoxane vs anthracycline module) | z = −2.651, 4.7th percentile of 64 pairs |
| Driver of that signal | **TOP2B** (Δz = +1.887 on removal) |
| Cardioprotectants vs 100-drug random background | median z −0.722 vs −0.361, p = 0.0022 |
| Negative-control gate | FAIL (levothyroxine), subsequently shown to be mis-calibrated |

The method recovers the one cardioprotection pair the field agrees on, through
the gene that actually mediates the toxicity, and separates cardioprotectants
from drugs in general. It does **not** achieve drug-level specificity.

## Integrity design

Three controls were enforced in code rather than by intention.

1. **Sealed ground truth.** Cardioprotection trial outcomes were coded and hashed
   *before* the interactome was built. `sealed/outcomes.json` appears in this
   history exactly once, in the initial commit `334709b`, and was never modified
   or read. Verify with `git log --oneline -- sealed/outcomes.json`.
2. **Hash commitment.** All 64 proximity predictions were written and hashed into
   `results/COMMITMENT.txt` before any gate could permit unsealing.
3. **Blinded module construction.** The four cardiotoxicity modules were built by
   an agent given only the construction rules, with no access to `sealed/`, to
   `RUNLOG.md`, or to the analysis.

The study stopped at Gate 4 by pre-specification, so the sealed outcomes were
never used and no proximity-versus-trial-outcome association is reported.

`RUNLOG.md` records every run, including abandoned ones, every protocol
deviation, and the withdrawal of the first manuscript draft whose headline was
wrong.

## Reproducing

Requires Python 3.12 with `numpy`, `scipy`, `pyyaml`, `matplotlib`, `python-docx`.

```bash
powershell -File src/fetch_sources.ps1   # download + hash STRING, DGIdb, HGNC
python -I src/build_graph.py             # graphs at confidence 400/700/900
python -I src/build_targets.py           # DGIdb target sets with provenance
python -I src/build_modules.py           # validate and freeze modules
python -I src/precompute_distances.py    # BFS distance matrices (~15 min)
python -I src/run_precommit.py 700       # proximity, Gates 0/1/3/4, commitment
python -I src/run_precommit.py 400 900   # sensitivity arms
python -I src/report_arms.py             # all arms, both metrics
python -I src/explore_robustness.py      # exploratory leave-one-target-out
python -I src/explore_gate4_calibration.py
python -I src/explore_random_background.py
python -I src/make_figures.py
python -I src/verify_numbers.py          # audits 49 claims + seal integrity
```

Shortest-path distance matrices (~716 MB) are regenerable and not redistributed.

`src/analyze.py` is the post-unsealing analysis. It refuses to run without a
verifying `COMMITMENT.txt` and was never executed, because Gate 4 failed.

## Data sources

STRING v12.0 (human, 9606), DGIdb, HGNC. Exact files are identified by SHA-256 in
`data/raw/PROVENANCE.json`. DrugBank was specified in the protocol as a target
backfill but requires a licensed download and was not used; the resulting
coverage gap is reported in the paper.

## Declaration

A large language model (Claude, Anthropic) was used as a computational assistant:
it implemented the pipeline, performed the blinded literature extraction for
module construction, and drafted portions of the manuscript. No language model is
an author. All analytic decisions and the final interpretation are the authors'.

## Licence

MIT (see `LICENSE`).
