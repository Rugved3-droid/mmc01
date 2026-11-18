"""EXPLORATORY (rule 2.3) — cannot change the recorded Gate 4 verdict.

Gate 4 asks that NO negative-control drug reach the protectant top quartile.
A quartile holds 25% of values by construction, so if controls were drawn from
the same distribution as protectants you would EXPECT 25% of the 20
control-module pairs - five of them - inside it. This script asks whether the
observed breach count is more or less than chance, and whether the control and
protectant z distributions actually differ.
"""
import json
import pathlib
from itertools import combinations

import numpy as np

RES = pathlib.Path(r"D:\mmc01\results")
MODULES = ["M1", "M2", "M3", "M4"]


def rank_sum_permutation_two_sided(a, b, n_perm=20000, seed=20261117):
    """Two-sided rank-sum p by Monte Carlo permutation.

    Exact enumeration is infeasible here (C(84,20) ~ 1e19), so the reference
    distribution is sampled by shuffling group labels.
    """
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    n1 = a.size
    allv = np.concatenate([a, b])
    ranks = np.empty_like(allv)
    ranks[np.argsort(allv, kind="stable")] = np.arange(1, allv.size + 1)
    obs = ranks[:n1].sum()
    mean = n1 * (allv.size + 1) / 2
    dev = abs(obs - mean)
    hits = 0
    for _ in range(n_perm):
        perm = rng.permutation(ranks)
        if abs(perm[:n1].sum() - mean) >= dev - 1e-9:
            hits += 1
    return obs, (hits + 1) / (n_perm + 1)


def binom_tail_two_sided(k, n, p0=0.25):
    """Two-sided exact binomial p for k breaches out of n at rate p0."""
    from math import comb
    pmf = [comb(n, i) * p0 ** i * (1 - p0) ** (n - i) for i in range(n + 1)]
    return min(1.0, sum(v for v in pmf if v <= pmf[k] + 1e-12))


def main():
    arms = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"]
    out = {"EXPLORATORY": True,
           "note": "rule 2.3: exploratory; cannot change the recorded Gate 4 verdict",
           "arms": {}}

    print(f"{'arm':<12} {'ctrl in Q1':>11} {'expected':>9} {'prot med':>9} "
          f"{'ctrl med':>9} {'rank-sum p':>11}  direction")
    for thr in ("400", "700", "900"):
        arm = arms[thr]
        prot, ctrl = [], []
        for d, v in arm.items():
            if v.get("dropped"):
                continue
            for m in MODULES:
                if m in v["modules"]:
                    (prot if v["group"] == "protectant" else ctrl).append(
                        v["modules"][m]["z"])
        prot = np.array(prot, float)
        ctrl = np.array(ctrl, float)
        cut = float(np.percentile(prot, 25))
        n_in = int((ctrl <= cut).sum())
        expected = 0.25 * ctrl.size
        _, p = rank_sum_permutation_two_sided(ctrl, prot)
        p_binom = binom_tail_two_sided(n_in, ctrl.size)
        direction = ("controls FARTHER (more specific)" if np.median(ctrl) > np.median(prot)
                     else "controls CLOSER (less specific)")
        out["arms"][thr] = {
            "n_protectant_pairs": int(prot.size),
            "n_control_pairs": int(ctrl.size),
            "top_quartile_cutoff": round(cut, 4),
            "controls_in_top_quartile": n_in,
            "expected_under_exchangeability": expected,
            "protectant_median_z": round(float(np.median(prot)), 4),
            "control_median_z": round(float(np.median(ctrl)), 4),
            "permutation_two_sided_rank_sum_p": round(p, 4),
            "binomial_two_sided_p_vs_25pct": round(p_binom, 4),
            "direction": direction,
        }
        print(f"{thr+'/z':<12} {n_in:>11} {expected:>9.1f} {np.median(prot):>9.3f} "
              f"{np.median(ctrl):>9.3f} {p:>11.4f}  {direction}")
        print(f"{'':12} breach count vs 25% chance: binomial two-sided p = {p_binom:.3f}")

    (RES / "exploratory_gate4_calibration.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")
    print("\nwrote results/exploratory_gate4_calibration.json")


if __name__ == "__main__":
    main()
