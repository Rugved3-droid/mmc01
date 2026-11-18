"""Protocol rule 2.4: report every threshold arm and both proximity definitions.

Recomputes Gate 3 and Gate 4 at STRING 400, 700 and 900, under the primary
metric (closest-distance z) and under the secondary metric (S_AB), so no arm can
be dropped for being unfavourable. The 700 / z-score cell is the headline verdict
recorded in results/gates.json; every other cell is a sensitivity arm.
"""
import json
import pathlib

import numpy as np

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
ARMS = ["400", "700", "900"]


def grade(n):
    return "PASS" if n == 0 else ("CONDITIONAL" if n == 1 else "FAIL")


def main():
    prox = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"]
    table = {}
    for thr in ARMS:
        if thr not in prox:
            continue
        arm = prox[thr]
        for metric in ("z", "s_ab"):
            prot, neg = {}, {}
            for d, v in arm.items():
                if v.get("dropped"):
                    continue
                for mid, r in v["modules"].items():
                    (prot if v["group"] == "protectant" else neg)[(d, mid)] = r[metric]
            vals = np.array(list(prot.values()), dtype=float)
            cut = float(np.percentile(vals, 25))
            dex = prot.get(("dexrazoxane", "M1"))
            pct = float((vals < dex).sum()) / len(vals) * 100.0
            viol = [{"drug": d, "module": m, metric: round(float(z), 4)}
                    for (d, m), z in neg.items() if z <= cut]
            table[f"{thr}/{metric}"] = {
                "threshold": int(thr),
                "metric": "closest_distance_z" if metric == "z" else "S_AB",
                "n_reference_values": int(vals.size),
                "top_quartile_cutoff": round(cut, 4),
                "dexrazoxane_M1": round(float(dex), 4),
                "dexrazoxane_percentile": round(pct, 1),
                "gate3": "PASS" if dex <= cut else "FAIL",
                "gate4_violations_pairs": len(viol),
                "gate4_violations_distinct_drugs": len({v["drug"] for v in viol}),
                "gate4_by_pair": grade(len(viol)),
                "gate4_by_drug": grade(len({v["drug"] for v in viol})),
                "violations": viol,
            }
    (RES / "sensitivity_arms.json").write_text(json.dumps(table, indent=1), encoding="utf-8")

    print(f"{'arm':<12} {'cutoff':>9} {'dexra':>9} {'pctile':>7} {'G3':>6} "
          f"{'G4pair':>12} {'G4drug':>12}  violating drugs")
    for k, v in table.items():
        drugs = ",".join(sorted({x["drug"] for x in v["violations"]})) or "-"
        print(f"{k:<12} {v['top_quartile_cutoff']:>9.3f} {v['dexrazoxane_M1']:>9.3f} "
              f"{v['dexrazoxane_percentile']:>6.1f}% {v['gate3']:>6} "
              f"{v['gate4_by_pair']:>12} {v['gate4_by_drug']:>12}  {drugs}")
    print("\nwrote results/sensitivity_arms.json")


if __name__ == "__main__":
    main()
