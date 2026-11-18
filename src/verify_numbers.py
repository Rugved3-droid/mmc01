"""Audit every quantitative claim in the Cardiovascular Toxicology manuscript
against the result files, plus journal formatting constraints. Fails loudly.
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
CFG = ROOT / "config"
PAPER = ROOT / "paper" / "MMC01_CardiovascTox_ResearchArticle.md"

text = PAPER.read_text(encoding="utf-8")
norm = text.replace("\u2212", "-").replace("\u2013", "-")  # minus / en-dash
checks, fails = [], []


def check(name, expected, as_str=None):
    if as_str is not None:
        forms = [as_str]
    elif isinstance(expected, float):
        forms = [str(expected)] + [f"{expected:.{d}f}" for d in (5, 4, 3, 2)]
        forms += [f.lstrip("-") for f in forms if f.startswith("-")]
    else:
        forms = [f"{expected:,}", str(expected)] if isinstance(expected, int) else [str(expected)]
    hit = next((f for f in forms if f in norm), None)
    checks.append((name, hit or forms[0], hit is not None))
    if hit is None:
        fails.append((name, " | ".join(dict.fromkeys(forms))))


def sha_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for c in iter(lambda: fh.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


# hashes + seal integrity
out_hash = sha_file(ROOT / "sealed" / "outcomes.json")
check("sealed outcomes sha256", out_hash)
check("predictions sha256", hashlib.sha256(
    (RES / "predictions.json").read_text(encoding="utf-8").encode()).hexdigest())
check("modules sha256", hashlib.sha256(
    (CFG / "modules.yaml").read_text(encoding="utf-8").encode()).hexdigest())
rec = [l.split(":", 1)[1].strip() for l in
       (ROOT / "sealed" / "OUTCOMES_HASH.txt").read_text(encoding="utf-8").splitlines()
       if l.startswith("outcomes.json sha256:")][0]
checks.append(("seal integrity", rec == out_hash, rec == out_hash))
if rec != out_hash:
    fails.append(("SEAL INTEGRITY", f"{rec} != {out_hash}"))

# graph
gs = {g["threshold"]: g for g in json.loads((RES / "graph_stats.json").read_text())}
for thr in (400, 700, 900):
    check(f"LCC nodes {thr}", gs[thr]["lcc_nodes"])
    check(f"LCC edges {thr}", gs[thr]["lcc_edges_undirected"])

# modules
ms = json.loads((RES / "module_stats.json").read_text())["modules"]
check("total seed sources", sum(s["n_seed_sources"] for s in ms.values()))
for mid, n in (("M1", 34), ("M2", 15), ("M3", 13), ("M4", 15)):
    if ms[mid]["n_in_lcc"]["700"] != n:
        fails.append((f"{mid} size", f"expected {n}, got {ms[mid]['n_in_lcc']['700']}"))

# gates
g = json.loads((RES / "gates.json").read_text())
g3, g4, g1 = (g["gate3_positive_control"], g["gate4_negative_control"],
              g["gate1_target_coverage"])
check("gate3 z", g3["dexrazoxane_M1_z"])
check("gate3 cutoff", g3["top_quartile_cutoff_z"])
check("gate3 percentile", f"{g3['percentile_of_all_z']}")
check("median direction coverage", g1["median_direction_coverage"])
for v in g4["violations"]:
    check(f"gate4 {v['module']}", v["z"])
if g3["verdict"] != "PASS" or g4["verdict"] != "FAIL":
    fails.append(("gate verdicts", f"{g3['verdict']}/{g4['verdict']}"))

# sensitivity arms
sa = json.loads((RES / "sensitivity_arms.json").read_text())
for arm in ("400/z", "700/z", "900/z", "400/s_ab", "700/s_ab", "900/s_ab"):
    check(f"{arm} dexrazoxane", sa[arm]["dexrazoxane_M1"])
    check(f"{arm} cutoff", sa[arm]["top_quartile_cutoff"])
if sum(1 for v in sa.values() if v["gate3"] == "PASS") != 5:
    fails.append(("gate3 arm count", "expected 5"))
if any(v["gate4_by_pair"] == "PASS" for v in sa.values()):
    fails.append(("gate4 arms", "expected no PASS"))

# exploratory: TOP2B + selectivity
ex = json.loads((RES / "exploratory_robustness.json").read_text())
top = ex["leave_one_target_out"]["dexrazoxane__M1"]["leave_one_out"][0]
if top["dropped"] != "TOP2B":
    fails.append(("top driver", top["dropped"]))
check("TOP2B delta", top["delta_vs_full"])
check("z without TOP2B", top["z"])
for k, lbl in (("levothyroxine__M2", "levo M2"), ("levothyroxine__M3", "levo M3")):
    check(f"{lbl} max delta", ex["leave_one_target_out"][k]["leave_one_out"][0]["delta_vs_full"])
sel = ex["selectivity_index_most_selective_first"][0]
check("dexrazoxane selectivity", sel["selectivity"])

# exploratory: calibration + background
cal = json.loads((RES / "exploratory_gate4_calibration.json").read_text())["arms"]
for thr in ("400", "700", "900"):
    check(f"calibration p {thr}", cal[thr]["permutation_two_sided_rank_sum_p"])
    check(f"control median {thr}", cal[thr]["control_median_z"])
bg = json.loads((RES / "exploratory_random_background.json").read_text())
check("background p", bg["permutation_two_sided_p"])
check("background median", bg["background_median_z"])
check("protectant median", bg["protectant_median_z"])
check("background n drugs", bg["n_drugs_sampled"])
check("background n pairs", bg["n_background_pairs"])
check("background frac in quartile", None,
      as_str=f"{bg['background_frac_in_protectant_top_quartile']*100:.1f}%")

# journal formatting constraints
m = re.search(r"## Abstract\s*\n(.+?)\n\*\*Graphical", text, re.S)
if m:
    n_abs = len(m.group(1).split())
    ok = 150 <= n_abs <= 250
    checks.append((f"abstract length {n_abs} words (150-250)", n_abs, ok))
    if not ok:
        fails.append(("abstract length", f"{n_abs} words, must be 150-250"))
kw = re.search(r"\*\*Keywords:\*\*(.+)", text)
if kw:
    n_kw = len([k for k in kw.group(1).split(";") if k.strip()])
    ok = 4 <= n_kw <= 6
    checks.append((f"keywords {n_kw} (4-6)", n_kw, ok))
    if not ok:
        fails.append(("keywords", f"{n_kw}, must be 4-6"))
body = len([w for l in text.splitlines() if not l.startswith("|") for w in l.split()])
checks.append((f"body words {body} (<10000)", body, body < 10000))

print(f"{'check':<44} {'value':<20} ok")
for name, val, ok in checks:
    print(f"{name:<44} {str(val)[:20]:<20} {'OK' if ok else 'MISSING'}")
print()
if fails:
    print(f"*** {len(fails)} PROBLEM(S) ***")
    for n, v in fails:
        print(f"  {n}: {v}")
    sys.exit(1)
print(f"All {len(checks)} checks passed.")
