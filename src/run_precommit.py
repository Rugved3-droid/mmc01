"""MMC-01 pre-commitment run.

Computes proximity for every drug x module x threshold, runs Gates 0, 1, 3 and 4,
writes results/predictions.json and hashes it into results/COMMITMENT.txt.

Nothing here reads sealed/.
"""
import hashlib
import datetime
import json
import pathlib
import sys
import time

import numpy as np
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from proximity import (load_graph, distance_matrix, degree_bins, flatten_bins,
                       proximity_z, separation, SEED_PRIMARY, N_PERM)
import gates as G

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
CFG = ROOT / "config"
PRIMARY = 700
CUTOFF_Z = -1.0


def main():
    # Arms to run: given on the command line, else the primary arm alone.
    # Sensitivity arms are appended later by the same code path; the commitment
    # is written once, from the primary arm, and never overwritten.
    THRESHOLDS = [int(a) for a in sys.argv[1:]] or [PRIMARY]
    print(f"arms this run: {THRESHOLDS}")
    modules_cfg = yaml.safe_load((CFG / "modules.yaml").read_text(encoding="utf-8"))["modules"]
    targets = json.loads((RES / "targets.json").read_text(encoding="utf-8"))
    protectants = targets["protectants"]
    negatives = {d: targets["negative_controls"][d] for d in targets["negative_controls_used"]}

    results = {}
    for thr in THRESHOLDS:
        t0 = time.time()
        adj, nodes = load_graph(thr)
        index = {n: i for i, n in enumerate(nodes)}
        D = distance_matrix(thr, adj)
        bins, bin_of, deg = degree_bins(adj)
        packed = flatten_bins(bins)
        rng = np.random.default_rng(SEED_PRIMARY)

        mod_idx = {}
        for mid, m in modules_cfg.items():
            idx = [index[g] for g in m["genes"] if g in index]
            mod_idx[mid] = np.array(sorted(idx), dtype=np.int64)

        arm = {}
        for group, drugs in (("protectant", protectants), ("negative_control", negatives)):
            for d, v in drugs.items():
                tidx = np.array(sorted(index[g] for g in v["targets_in_lcc"] if g in index),
                                dtype=np.int64)
                if tidx.size == 0:
                    arm[d] = {"group": group, "n_targets": 0, "dropped": True}
                    continue
                per_mod = {}
                for mid, midx in mod_idx.items():
                    if midx.size == 0:
                        continue
                    r = proximity_z(D, tidx, midx, packed, bin_of, rng, N_PERM)
                    r["s_ab"] = round(separation(D, tidx, midx), 4)
                    r["n_module_genes"] = int(midx.size)
                    per_mod[mid] = {k: (round(val, 4) if isinstance(val, float) else val)
                                    for k, val in r.items()}
                arm[d] = {"group": group, "n_targets": int(tidx.size),
                          "dropped": False, "modules": per_mod}
        results[str(thr)] = arm
        print(f"threshold {thr} done in {time.time()-t0:.1f}s")
        sys.stdout.flush()

    # merge with any arms computed in an earlier run
    prox_path = RES / "proximity.json"
    merged = {}
    if prox_path.exists():
        merged = json.loads(prox_path.read_text(encoding="utf-8")).get("arms", {})
    merged.update(results)
    prox_path.write_text(
        json.dumps({"seed": SEED_PRIMARY, "n_perm": N_PERM, "arms": merged}, indent=1),
        encoding="utf-8")
    results = merged

    if str(PRIMARY) not in results:
        print("primary arm not computed yet; gates and commitment deferred")
        return

    # ---- gates ----
    prim = results[str(PRIMARY)]
    z_prot, z_neg = {}, {}
    for d, v in prim.items():
        if v.get("dropped"):
            continue
        for mid, r in v["modules"].items():
            (z_prot if v["group"] == "protectant" else z_neg)[(d, mid)] = r["z"]
    all_z = list(z_prot.values())

    mod_stats = json.loads((RES / "module_stats.json").read_text(encoding="utf-8"))["modules"]
    gate_modules = {mid: {
        "n_declared": s["n_declared"], "n_two_source": s["n_two_source"],
        "n_mapped": s["n_mapped"], "mapping_loss": s["mapping_loss"],
        "genes_in_lcc": s["genes_in_lcc_700"],
    } for mid, s in mod_stats.items()}

    gate_results = {
        "threshold_used_for_gates": PRIMARY,
        "seed": SEED_PRIMARY,
        "gate0_module_viability": G.gate0_module_viability(gate_modules),
        "gate1_target_coverage": G.gate1_target_coverage(protectants),
        "gate3_positive_control": G.gate3_positive_control(z_prot, all_z),
        "gate4_negative_control": G.gate4_negative_controls(
            z_neg, all_z, list(negatives), list(modules_cfg)),
    }
    (RES / "gates.json").write_text(json.dumps(gate_results, indent=1), encoding="utf-8")

    for name in ("gate0_module_viability", "gate1_target_coverage",
                 "gate3_positive_control", "gate4_negative_control"):
        print(f"{name}: {gate_results[name]['verdict']}")
    print(json.dumps(gate_results["gate3_positive_control"], indent=1))

    # ---- predictions + commitment ----
    preds = []
    for (d, mid), z in sorted(z_prot.items()):
        preds.append({"protectant": d, "module": mid, "z": z,
                      "predicted_class": "matched" if z < CUTOFF_Z else "not_matched"})
    payload = {
        "schema": "mmc01-predictions-v1",
        "threshold": PRIMARY, "seed": SEED_PRIMARY, "n_perm": N_PERM,
        "cutoff_z": CUTOFF_Z, "metric": "closest_distance_proximity_zscore",
        "n_pairs": len(preds), "predictions": preds,
    }
    if (RES / "COMMITMENT.txt").exists():
        print("\nCOMMITMENT.txt already exists; predictions are NOT regenerated. "
              "The original commitment stands.")
        return

    text = json.dumps(payload, indent=1, sort_keys=True)
    (RES / "predictions.json").write_text(text, encoding="utf-8")
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (RES / "COMMITMENT.txt").write_text(
        "MMC-01 pre-unsealing commitment (protocol 2.2)\n"
        f"committed_utc: {ts}\n"
        f"results/predictions.json sha256: {h}\n"
        f"n_pairs: {len(preds)}\ncutoff_z: {CUTOFF_Z}\n"
        f"threshold: {PRIMARY}\nseed: {SEED_PRIMARY}\n",
        encoding="utf-8")
    print(f"\nCOMMITMENT predictions.json sha256: {h}")
    print(f"n predicted 'matched': {sum(1 for p in preds if p['predicted_class']=='matched')}"
          f" / {len(preds)}")


if __name__ == "__main__":
    main()
