"""MMC-01 section 9 analysis. Refuses to run without a verified COMMITMENT.txt.

Study status: by decision recorded in RUNLOG.md, MMC-01 was redesignated a
DESCRIPTIVE + Gate 3 methods study before unsealing, because outcome code is
perfectly confounded with module identity (all POSITIVE pairs M1, all NULL
pairs M2) and the pre-specified primary test has an attainable-p floor above
0.05. Accordingly this script reports the proximity landscape and the pair
table, and deliberately does NOT compute the primary inferential test or any
classification performance metric. The withheld tests are named in the output
so a reader can see exactly what was not run, and why.
"""
import hashlib
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
SEALED = ROOT / "sealed"


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verified_unseal():
    """Protocol 2.2 step 4-5: refuse to read sealed/ without a verifying commitment."""
    commit = RES / "COMMITMENT.txt"
    if not commit.exists():
        raise SystemExit("REFUSED: results/COMMITMENT.txt does not exist. "
                         "sealed/ may not be read before the commitment.")
    txt = commit.read_text(encoding="utf-8")
    recorded = None
    for line in txt.splitlines():
        if line.startswith("results/predictions.json sha256:"):
            recorded = line.split(":", 1)[1].strip()
    if recorded is None:
        raise SystemExit("REFUSED: COMMITMENT.txt has no predictions hash.")
    actual = sha256_text((RES / "predictions.json").read_text(encoding="utf-8"))
    if actual != recorded:
        raise SystemExit(f"VOID: predictions.json hash mismatch.\n"
                         f"  committed: {recorded}\n  actual:    {actual}")

    outcomes_hash_txt = (SEALED / "OUTCOMES_HASH.txt").read_text(encoding="utf-8")
    recorded_out = None
    for line in outcomes_hash_txt.splitlines():
        if line.startswith("outcomes.json sha256:"):
            recorded_out = line.split(":", 1)[1].strip()
    actual_out = sha256_file(SEALED / "outcomes.json")
    if recorded_out != actual_out:
        raise SystemExit(f"VOID: outcomes.json hash mismatch.\n"
                         f"  sealed: {recorded_out}\n  actual: {actual_out}")

    return {
        "predictions_sha256_committed": recorded,
        "predictions_sha256_verified": actual,
        "outcomes_sha256_sealed": recorded_out,
        "outcomes_sha256_verified": actual_out,
        "verification": "PASS",
    }


def main():
    verif = verified_unseal()
    print("Commitment verification:", verif["verification"])
    print("  predictions.json sha256:", verif["predictions_sha256_verified"])
    print("  outcomes.json    sha256:", verif["outcomes_sha256_verified"])

    outcomes = json.loads((SEALED / "outcomes.json").read_text(encoding="utf-8"))
    preds = json.loads((RES / "predictions.json").read_text(encoding="utf-8"))
    prox = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))

    zmap = {}
    for arm_thr, arm in prox["arms"].items():
        for d, v in arm.items():
            if v.get("dropped"):
                continue
            for mid, r in v["modules"].items():
                zmap[(arm_thr, d, mid)] = r

    # Gate 2
    pairs = outcomes["pairs"]
    import gates as G
    gate2 = G.gate2_evaluable_pairs(len(pairs))
    print(f"\ngate2_evaluable_pairs: {gate2['verdict']} (n={gate2['n_evaluable_pairs']})")

    key = {"dexrazoxane": "dexrazoxane", "sacubitril/valsartan": "sacubitril/valsartan"}
    rows = []
    for p in pairs:
        d = key.get(p["protectant"], p["protectant"])
        rec = {"pair_id": p["pair_id"], "protectant": d, "module": p["module"],
               "outcome": p["outcome_code"], "endpoint_type": p["endpoint_type"],
               "n_trials": p["n_trials"], "pooled_n": p["pooled_n"]}
        for thr in ("700", "400", "900"):
            r = zmap.get((thr, d, p["module"]))
            rec[f"z_{thr}"] = r["z"] if r else None
            rec[f"sab_{thr}"] = r["s_ab"] if r else None
        rows.append(rec)

    def summarise(code, thr="700"):
        vals = [r[f"z_{thr}"] for r in rows if r["outcome"] == code and r[f"z_{thr}"] is not None]
        if not vals:
            return None
        a = np.array(vals, dtype=float)
        return {"n": len(vals), "median": round(float(np.median(a)), 3),
                "min": round(float(a.min()), 3), "max": round(float(a.max()), 3),
                "values": [round(v, 3) for v in vals]}

    descriptive = {thr: {code: summarise(code, thr) for code in ("POSITIVE", "NULL", "MIXED")}
                   for thr in ("700", "400", "900")}

    modules_of = {}
    for r in rows:
        modules_of.setdefault(r["outcome"], set()).add(r["module"])

    report = {
        "study_status": "DESCRIPTIVE + Gate 3 methods study",
        "commitment_verification": verif,
        "gate2_evaluable_pairs": gate2,
        "pair_table": rows,
        "descriptive_z_by_outcome": descriptive,
        "confounding_check": {
            "modules_per_outcome_code": {k: sorted(v) for k, v in modules_of.items()},
            "outcome_collinear_with_module": (
                len(modules_of.get("POSITIVE", set()) & modules_of.get("NULL", set())) == 0),
            "interpretation": (
                "POSITIVE and NULL pairs occupy disjoint modules, so any difference "
                "in proximity z between them is indistinguishable from a difference "
                "between the modules themselves. This is an identifiability failure, "
                "not a power problem."),
        },
        "withheld_by_decision": {
            "two_sided_exact_wilcoxon_POSITIVE_vs_NULL": (
                "not computed: attainable-p floor 0.0571 at 4 vs 3, and the "
                "comparison is fully confounded with module identity"),
            "fishers_exact_on_2x2": "not computed: same confounding",
            "classification_performance": "not computed: no prediction claim is made",
            "leave_one_pair_out": "not applicable without a primary statistic",
            "rationale": "recorded in RUNLOG.md before unsealing",
        },
    }
    (RES / "analysis.json").write_text(json.dumps(report, indent=1), encoding="utf-8")

    print("\nDescriptive proximity z by outcome code (STRING 700):")
    for code in ("POSITIVE", "NULL", "MIXED"):
        s = descriptive["700"][code]
        if s:
            print(f"  {code:<9} n={s['n']:<3} median z={s['median']:>7} "
                  f"range [{s['min']}, {s['max']}]")
    print("\nPair table (STRING 700):")
    print(f"  {'pair':<30} {'outcome':<9} {'z700':>8} {'S_AB':>8}")
    for r in sorted(rows, key=lambda x: (x["outcome"], x["z_700"] if x["z_700"] is not None else 9)):
        z = f"{r['z_700']:.3f}" if r["z_700"] is not None else "NA"
        s = f"{r['sab_700']:.3f}" if r["sab_700"] is not None else "NA"
        print(f"  {r['pair_id']:<30} {r['outcome']:<9} {z:>8} {s:>8}")
    print("\nwrote results/analysis.json")


if __name__ == "__main__":
    sys.exit(main())
