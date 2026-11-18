"""EXPLORATORY (rule 2.3) — cannot change any recorded gate verdict.

The pre-specified Gate 4 rests on five hand-picked negative controls. This
builds a much larger RANDOM-DRUG BACKGROUND from DGIdb and asks whether the 16
cardioprotectants are closer to the cardiotoxicity modules than drugs in general.

Honest naming: these are NOT verified negative controls. They are drugs sampled
at random, some of which may genuinely act on cardiac biology. That makes this a
conservative test - any contamination works against finding a difference.
"""
import csv
import json
import pathlib
import sys
from collections import defaultdict

import numpy as np
import yaml

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from proximity import (load_graph, distance_matrix, degree_bins, flatten_bins,
                       proximity_z, SEED_PRIMARY)

ROOT = pathlib.Path(r"D:\mmc01")
RAW = ROOT / "data" / "raw"
RES = ROOT / "results"
CFG = ROOT / "config"
THR = 700
N_DRUGS = 100
N_PERM = 1000
MIN_T, MAX_T = 3, 60          # comparable to the protectant target-count range
MODULES = ["M1", "M2", "M3", "M4"]


def load_hgnc():
    mapping, approved = {}, set()
    p = RAW / "hgnc_complete_set.txt"
    with open(p, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r.get("status") == "Approved":
                s = (r.get("symbol") or "").strip()
                if s:
                    approved.add(s)
                    mapping[s] = s
    with open(p, encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            if r.get("status") != "Approved":
                continue
            s = (r.get("symbol") or "").strip()
            for f in ("alias_symbol", "prev_symbol"):
                for alt in (r.get(f) or "").split("|"):
                    alt = alt.strip()
                    if alt and alt not in approved and alt not in mapping:
                        mapping[alt] = s
    return mapping


def main():
    adj, nodes = load_graph(THR)
    index = {n: i for i, n in enumerate(nodes)}
    D = distance_matrix(THR, adj)
    bins, bin_of, _ = degree_bins(adj)
    packed = flatten_bins(bins)
    hgnc = load_hgnc()

    modules_cfg = yaml.safe_load((CFG / "modules.yaml").read_text(encoding="utf-8"))["modules"]
    mod_idx = {m: np.array(sorted(index[g] for g in modules_cfg[m]["genes"] if g in index),
                           dtype=np.int64) for m in MODULES}

    targets = json.loads((RES / "targets.json").read_text(encoding="utf-8"))
    exclude = set()
    for grp in ("protectants", "negative_controls"):
        for d, v in targets[grp].items():
            for sp in v["accepted_spellings"]:
                exclude.add(sp.upper())

    # all DGIdb drugs -> mapped LCC targets
    drug_genes = defaultdict(set)
    with open(RAW / "dgidb_interactions.tsv", encoding="utf-8", newline="") as fh:
        for r in csv.DictReader(fh, delimiter="\t"):
            name = (r.get("drug_name") or "").strip().upper()
            if not name or name in exclude:
                continue
            g = hgnc.get((r.get("gene_name") or "").strip())
            if g and g in index:
                drug_genes[name].add(g)

    pool = sorted(d for d, g in drug_genes.items() if MIN_T <= len(g) <= MAX_T)
    rng = np.random.default_rng(SEED_PRIMARY)
    pick = [pool[i] for i in rng.choice(len(pool), size=min(N_DRUGS, len(pool)),
                                        replace=False)]
    print(f"DGIdb drugs with {MIN_T}-{MAX_T} targets in LCC700: {len(pool)}; "
          f"sampled {len(pick)} (seed {SEED_PRIMARY})")

    rows, bg = [], []
    for d in pick:
        tidx = np.array(sorted(index[g] for g in drug_genes[d]), dtype=np.int64)
        rec = {"drug": d, "n_targets": int(tidx.size)}
        for m in MODULES:
            r = proximity_z(D, tidx, mod_idx[m], packed, bin_of,
                            np.random.default_rng(SEED_PRIMARY), N_PERM)
            rec[m] = round(r["z"], 4)
            bg.append(r["z"])
        rows.append(rec)

    prox = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"][str(THR)]
    prot = [prox[d]["modules"][m]["z"] for d, v in prox.items()
            if not v.get("dropped") and v["group"] == "protectant" for m in MODULES]

    bg = np.array(bg, float)
    prot = np.array(prot, float)

    # permutation rank-sum
    allv = np.concatenate([prot, bg])
    ranks = np.empty_like(allv)
    ranks[np.argsort(allv, kind="stable")] = np.arange(1, allv.size + 1)
    n1 = prot.size
    obs = ranks[:n1].sum()
    mean = n1 * (allv.size + 1) / 2
    dev = abs(obs - mean)
    pr = np.random.default_rng(SEED_PRIMARY)
    hits = sum(1 for _ in range(20000)
               if abs(pr.permutation(ranks)[:n1].sum() - mean) >= dev - 1e-9)
    p = (hits + 1) / 20001

    cut = float(np.percentile(prot, 25))
    out = {
        "EXPLORATORY": True,
        "note": "random-drug background, NOT verified negative controls; "
                "cannot change the recorded Gate 4 verdict",
        "threshold": THR, "seed": SEED_PRIMARY, "n_perm": N_PERM,
        "pool_size": len(pool), "n_drugs_sampled": len(pick),
        "target_count_range": [MIN_T, MAX_T],
        "n_protectant_pairs": int(prot.size), "n_background_pairs": int(bg.size),
        "protectant_median_z": round(float(np.median(prot)), 4),
        "background_median_z": round(float(np.median(bg)), 4),
        "protectant_mean_z": round(float(prot.mean()), 4),
        "background_mean_z": round(float(bg.mean()), 4),
        "permutation_two_sided_p": round(p, 5),
        "protectant_top_quartile_cutoff": round(cut, 4),
        "background_frac_in_protectant_top_quartile": round(float((bg <= cut).mean()), 4),
        "expected_frac_if_exchangeable": 0.25,
        "per_drug": rows,
    }
    (RES / "exploratory_random_background.json").write_text(json.dumps(out, indent=1),
                                                            encoding="utf-8")

    print(f"\nprotectant pairs n={prot.size}  median z={np.median(prot):.3f}  "
          f"mean={prot.mean():.3f}")
    print(f"background pairs n={bg.size}  median z={np.median(bg):.3f}  "
          f"mean={bg.mean():.3f}")
    print(f"permutation two-sided p = {p:.5f}")
    print(f"background fraction inside protectant top quartile = "
          f"{(bg <= cut).mean():.3f} (0.25 expected if exchangeable)")


if __name__ == "__main__":
    main()
