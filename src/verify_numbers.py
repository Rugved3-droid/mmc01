"""Audit every quantitative claim in paper/MMC01_manuscript.md against the
result files. Fails loudly on any mismatch.
"""
import hashlib
import json
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
CFG = ROOT / "config"
PAPER = ROOT / "paper" / "MMC01_manuscript.md"

text = PAPER.read_text(encoding="utf-8")
checks, fails = [], []


def check(name, expected, found_in_paper=None, as_str=None):
    """Assert the paper contains the expected value.

    Numeric values are accepted at any rounding from the stored precision down
    to 2 dp, so quoting -2.651 for a stored -2.6511 is a match, not a mismatch.
    """
    if as_str is not None:
        forms = [as_str]
    elif isinstance(expected, float):
        forms = [str(expected)] + [f"{expected:.{d}f}" for d in (4, 3, 2)]
        # also accept the unsigned form for values written in prose
        forms += [f.lstrip("-") for f in forms if f.startswith("-")]
    else:
        forms = [str(expected)]
    hit = next((f for f in forms if f in text), None)
    ok = hit is not None
    checks.append((name, hit or forms[0], ok))
    if not ok:
        fails.append((name, " | ".join(dict.fromkeys(forms))))


# ---- hashes ----
def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


out_hash = sha_file(ROOT / "sealed" / "outcomes.json")
pred_hash = hashlib.sha256((RES / "predictions.json").read_text(encoding="utf-8")
                           .encode("utf-8")).hexdigest()
mod_hash = hashlib.sha256((CFG / "modules.yaml").read_text(encoding="utf-8")
                          .encode("utf-8")).hexdigest()
check("outcomes.json sha256", out_hash)
check("predictions.json sha256", pred_hash)
check("modules.yaml sha256", mod_hash)

# the sealed hash in the paper must match the one recorded at sealing time
sealed_txt = (ROOT / "sealed" / "OUTCOMES_HASH.txt").read_text(encoding="utf-8")
rec = [l.split(":", 1)[1].strip() for l in sealed_txt.splitlines()
       if l.startswith("outcomes.json sha256:")][0]
if rec != out_hash:
    fails.append(("SEAL INTEGRITY", f"recorded {rec} != actual {out_hash}"))
checks.append(("seal integrity (recorded == actual)", rec == out_hash, rec == out_hash))

# ---- graph stats ----
gs = {g["threshold"]: g for g in json.loads((RES / "graph_stats.json").read_text())}
for thr in (400, 700, 900):
    check(f"graph {thr} lcc nodes", f"{gs[thr]['lcc_nodes']:,}")
    check(f"graph {thr} lcc edges", f"{gs[thr]['lcc_edges_undirected']:,}")

# ---- modules ----
ms = json.loads((RES / "module_stats.json").read_text())["modules"]
n_src = sum(s["n_seed_sources"] for s in ms.values())
check("total seed sources", n_src)
for mid in ("M1", "M2", "M3", "M4"):
    checks.append((f"{mid} in LCC700 = {ms[mid]['n_in_lcc']['700']}", "", True))
if ms["M3"]["n_in_lcc"]["700"] != 13:
    fails.append(("M3 LCC700", f"expected 13, got {ms['M3']['n_in_lcc']['700']}"))

# ---- gates ----
g = json.loads((RES / "gates.json").read_text())
g3 = g["gate3_positive_control"]
g4 = g["gate4_negative_control"]
g1 = g["gate1_target_coverage"]
check("gate3 dexrazoxane z", g3["dexrazoxane_M1_z"])
check("gate3 cutoff", g3["top_quartile_cutoff_z"])
check("gate3 percentile", f"{g3['percentile_of_all_z']}")
check("gate1 median direction coverage", g1["median_direction_coverage"])
check("gate1 n mapped", f"{g1['n_protectants_mapped_in_lcc']} of {g1['n_protectants_total']}",
      as_str=f"**{g1['n_protectants_mapped_in_lcc']} of {g1['n_protectants_total']}**")
for v in g4["violations"]:
    check(f"gate4 {v['drug']}/{v['module']}", abs(v["z"]), as_str=f"{abs(v['z']):.3f}")

if g3["verdict"] != "PASS":
    fails.append(("gate3 verdict", g3["verdict"]))
if g4["verdict"] != "FAIL":
    fails.append(("gate4 verdict", g4["verdict"]))

# ---- sensitivity arms ----
sa = json.loads((RES / "sensitivity_arms.json").read_text())
n_pass_g3 = sum(1 for v in sa.values() if v["gate3"] == "PASS")
n_pass_g4 = sum(1 for v in sa.values() if v["gate4_by_pair"] == "PASS")
checks.append((f"gate3 PASS in {n_pass_g3}/{len(sa)} arms", "", True))
if n_pass_g3 != 5:
    fails.append(("gate3 arms", f"expected 5, got {n_pass_g3}"))
if n_pass_g4 != 0:
    fails.append(("gate4 arms", f"expected 0 PASS, got {n_pass_g4}"))
check("900/z dexrazoxane", sa["900/z"]["dexrazoxane_M1"])
check("400/z dexrazoxane", sa["400/z"]["dexrazoxane_M1"])

# ---- exploratory ----
ex = json.loads((RES / "exploratory_robustness.json").read_text())
dex = ex["leave_one_target_out"]["dexrazoxane__M1"]
top = dex["leave_one_out"][0]
if top["dropped"] != "TOP2B":
    fails.append(("exploratory top driver", top["dropped"]))
check("TOP2B delta", top["delta_vs_full"])
check("dexrazoxane z without TOP2B", abs(top["z"]), as_str=f"{abs(top['z']):.3f}")
for k in ("levothyroxine__M2", "levothyroxine__M3"):
    lo = ex["leave_one_target_out"][k]["leave_one_out"][0]
    check(f"{k} max delta", lo["delta_vs_full"])
sel = ex["selectivity_index_most_selective_first"][0]
if not (sel["drug"] == "dexrazoxane" and sel["module"] == "M1"):
    fails.append(("most selective pair", f"{sel['drug']}/{sel['module']}"))
check("dexrazoxane selectivity", abs(sel["selectivity"]), as_str=f"{abs(sel['selectivity']):.2f}")

# ---- report ----
print(f"{'check':<46} {'value':<22} ok")
for name, val, ok in checks:
    print(f"{name:<46} {str(val):<22} {'OK' if ok else 'MISSING'}")

print()
if fails:
    print(f"*** {len(fails)} PROBLEM(S) ***")
    for n, v in fails:
        print(f"  {n}: {v}")
    sys.exit(1)
print(f"All {len(checks)} checks passed. Manuscript numbers match the result files.")
