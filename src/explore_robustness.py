"""EXPLORATORY (protocol rule 2.3) — not part of the pre-specified analysis.

Nothing here can change a recorded gate verdict. Labelled exploratory wherever
it appears, including in the abstract.

Two questions:
  A. Does Gate 3 hang on one dexrazoxane target?
  B. Does the Gate 4 breach hang on one levothyroxine target, and is it the
     broad transcriptional regulators (THRA/THRB/PPARG/NFE2L2/AHR/NKX2-5)?
Both are answered by leave-one-target-out on the drug's own target set.

Also reports an exploratory module-selectivity index:
     sel(d, m) = z(d, m) - mean over the other modules of z(d, .)
which asks whether a drug is close to ONE module or close to everything.
"""
import json
import pathlib
import sys

import numpy as np
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from proximity import (load_graph, distance_matrix, degree_bins, flatten_bins,
                       proximity_z, SEED_PRIMARY)

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
CFG = ROOT / "config"
THR = 700
N_PERM = 1000
MODULES = ["M1", "M2", "M3", "M4"]


def main():
    adj, nodes = load_graph(THR)
    index = {n: i for i, n in enumerate(nodes)}
    D = distance_matrix(THR, adj)
    bins, bin_of, deg = degree_bins(adj)
    packed = flatten_bins(bins)

    modules_cfg = yaml.safe_load((CFG / "modules.yaml").read_text(encoding="utf-8"))["modules"]
    mod_idx = {m: np.array(sorted(index[g] for g in modules_cfg[m]["genes"] if g in index),
                           dtype=np.int64) for m in MODULES}
    targets = json.loads((RES / "targets.json").read_text(encoding="utf-8"))

    def tset(group, drug):
        v = targets[group][drug]
        return [g for g in v["targets_in_lcc"] if g in index]

    out = {"EXPLORATORY": True, "threshold": THR, "seed": SEED_PRIMARY,
           "note": "rule 2.3: exploratory, cannot change any recorded gate verdict"}

    # ---- A/B: leave-one-target-out ----
    loo = {}
    for group, drug, mods in (("protectants", "dexrazoxane", ["M1"]),
                              ("negative_controls", "levothyroxine", ["M2", "M3"])):
        genes = tset(group, drug)
        for m in mods:
            rng = np.random.default_rng(SEED_PRIMARY)
            full = proximity_z(D, np.array(sorted(index[g] for g in genes), dtype=np.int64),
                               mod_idx[m], packed, bin_of, rng, N_PERM)
            rows = []
            for drop in genes:
                keep = sorted(index[g] for g in genes if g != drop)
                rng2 = np.random.default_rng(SEED_PRIMARY)
                r = proximity_z(D, np.array(keep, dtype=np.int64), mod_idx[m],
                                packed, bin_of, rng2, N_PERM)
                rows.append({"dropped": drop, "z": round(r["z"], 4),
                             "delta_vs_full": round(r["z"] - full["z"], 4),
                             "degree_of_dropped": int(deg[index[drop]])})
            rows.sort(key=lambda r: -r["delta_vs_full"])
            loo[f"{drug}__{m}"] = {"z_full": round(full["z"], 4),
                                   "n_targets": len(genes), "leave_one_out": rows}
    out["leave_one_target_out"] = loo

    # ---- selectivity index ----
    prox = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"][str(THR)]
    sel = []
    for d, v in prox.items():
        if v.get("dropped"):
            continue
        z = {m: v["modules"][m]["z"] for m in MODULES if m in v["modules"]}
        for m in z:
            others = [z[o] for o in z if o != m]
            sel.append({"drug": d, "group": v["group"], "module": m,
                        "z": round(z[m], 4),
                        "selectivity": round(z[m] - float(np.mean(others)), 4)})
    sel.sort(key=lambda r: r["selectivity"])
    out["selectivity_index_most_selective_first"] = sel[:15]

    (RES / "exploratory_robustness.json").write_text(json.dumps(out, indent=1),
                                                     encoding="utf-8")

    for k, v in loo.items():
        print(f"\n=== EXPLORATORY leave-one-target-out: {k} (full z = {v['z_full']}, "
              f"{v['n_targets']} targets) ===")
        print(f"  {'dropped':<12} {'z without it':>13} {'delta':>8} {'degree':>8}")
        for r in v["leave_one_out"]:
            print(f"  {r['dropped']:<12} {r['z']:>13.3f} {r['delta_vs_full']:>8.3f} "
                  f"{r['degree_of_dropped']:>8}")

    print("\n=== EXPLORATORY module-selectivity (most selective pairs) ===")
    print(f"  {'drug':<22} {'grp':<17} {'mod':<4} {'z':>7} {'selectivity':>12}")
    for r in sel[:12]:
        print(f"  {r['drug']:<22} {r['group']:<17} {r['module']:<4} {r['z']:>7.2f} "
              f"{r['selectivity']:>12.2f}")


if __name__ == "__main__":
    main()
