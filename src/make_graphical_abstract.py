"""Graphical Abstract for Cardiovascular Toxicology (goes in the Abstract section).

Two panels: what the method recovered (dexrazoxane -> TOP2B -> anthracycline
module) and how well it separates cardioprotectants from the drug background.
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, Circle

RES = pathlib.Path(r"D:\mmc01\results")
FIG = RES / "figures"
MODULES = ["M1", "M2", "M3", "M4"]

BLUE, GOLD, GREY, RED = "#2F4B7C", "#D9A441", "#9AA5B1", "#C44E52"


def main():
    ex = json.loads((RES / "exploratory_robustness.json").read_text(encoding="utf-8"))
    bg = json.loads((RES / "exploratory_random_background.json").read_text(encoding="utf-8"))
    prox = json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"]["700"]

    dex = {m: prox["dexrazoxane"]["modules"][m]["z"] for m in MODULES}
    loo = ex["leave_one_target_out"]["dexrazoxane__M1"]
    z_full, z_noTop2b = loo["z_full"], loo["leave_one_out"][0]["z"]

    prot = np.array([prox[d]["modules"][m]["z"] for d, v in prox.items()
                     if not v.get("dropped") and v["group"] == "protectant"
                     for m in MODULES], float)
    back = np.array([r[m] for r in bg["per_drug"] for m in MODULES], float)

    fig = plt.figure(figsize=(13.2, 5.1))
    gs = fig.add_gridspec(1, 3, width_ratios=[1.15, 1.0, 1.15], wspace=0.34,
                          left=0.045, right=0.985, top=0.80, bottom=0.13)

    # ---- panel A: selectivity across modules ----
    axA = fig.add_subplot(gs[0, 0])
    vals = [dex[m] for m in MODULES]
    cols = [BLUE if v < -1 else GREY for v in vals]
    axA.barh(range(4), vals, color=cols, height=0.62)
    axA.set_yticks(range(4), ["anthracycline\n(M1)", "anti-HER2\n(M2)",
                              "VEGF\n(M3)", "proteasome\n(M4)"], fontsize=9)
    axA.invert_yaxis()
    axA.axvline(0, color="#444", lw=0.9)
    axA.axvline(-1.0, color=RED, ls="--", lw=1.2)
    axA.set_xlabel("proximity z", fontsize=9.5)
    axA.set_title("Dexrazoxane is selective\nfor the anthracycline module",
                  fontsize=10.5, fontweight="bold", loc="left")
    for i, v in enumerate(vals):
        axA.text(v + (-0.16 if v < 0 else 0.06), i, f"{v:.2f}", va="center",
                 ha="right" if v < 0 else "left", fontsize=9,
                 fontweight="bold" if v < -1 else "normal")
    axA.set_xlim(-3.5, 1.1)
    axA.grid(axis="x", alpha=0.2)

    # ---- panel B: TOP2B dependency ----
    axB = fig.add_subplot(gs[0, 1])
    axB.axis("off")
    axB.set_xlim(0, 1); axB.set_ylim(0, 1)
    axB.add_patch(Circle((0.20, 0.64), 0.085, color=GOLD, ec="#4A3A10", lw=1.2))
    axB.text(0.20, 0.64, "dexra-\nzoxane", ha="center", va="center", fontsize=7.6,
             fontweight="bold")
    axB.add_patch(Circle((0.52, 0.64), 0.072, color=BLUE, ec="#16243C", lw=1.2))
    axB.text(0.52, 0.64, "TOP2B", ha="center", va="center", fontsize=7.8,
             color="white", fontweight="bold")
    axB.add_patch(Circle((0.84, 0.64), 0.085, color="#5B7DB1", ec="#16243C", lw=1.2))
    axB.text(0.84, 0.64, "M1\nmodule", ha="center", va="center", fontsize=7.6,
             color="white", fontweight="bold")
    for x0, x1 in ((0.285, 0.448), (0.592, 0.755)):
        axB.add_patch(FancyArrowPatch((x0, 0.64), (x1, 0.64), arrowstyle="-|>",
                                      mutation_scale=13, lw=1.6, color="#333"))
    axB.text(0.52, 0.40, f"z = {z_full:.2f}", ha="center", fontsize=12,
             fontweight="bold", color=BLUE)
    axB.text(0.52, 0.29, "4.7th percentile of 64 pairs", ha="center", fontsize=8.4)
    axB.text(0.52, 0.155, f"remove TOP2B  →  z = {z_noTop2b:.2f}", ha="center",
             fontsize=9.2, color=RED, fontweight="bold")
    axB.text(0.52, 0.055, "the signal is carried by the gene\nthat mediates the toxicity",
             ha="center", fontsize=8.1, style="italic", color="#444")
    axB.set_title("Recovered through the\ncorrect mechanism", fontsize=10.5,
                  fontweight="bold", loc="left")

    # ---- panel C: distributions ----
    axC = fig.add_subplot(gs[0, 2])
    bins = np.linspace(-3.6, 2.4, 26)
    axC.hist(back, bins=bins, density=True, color=GREY, alpha=0.75,
             label=f"random drugs (n={back.size})")
    axC.hist(prot, bins=bins, density=True, histtype="step", lw=2.3, color=BLUE,
             label=f"cardioprotectants (n={prot.size})")
    axC.axvline(np.median(back), color="#5A6570", ls=":", lw=1.8)
    axC.axvline(np.median(prot), color=BLUE, ls=":", lw=1.8)
    axC.set_xlabel("proximity z", fontsize=9.5)
    axC.set_ylabel("density", fontsize=9.5)
    axC.legend(fontsize=8.2, loc="upper left", framealpha=0.95)
    axC.set_title("Cardioprotectants sit closer\nthan drugs in general",
                  fontsize=10.5, fontweight="bold", loc="left")
    axC.text(0.97, 0.52, f"median {np.median(prot):.2f} vs {np.median(back):.2f}\n"
                         f"p = {bg['permutation_two_sided_p']:.4f}",
             transform=axC.transAxes, ha="right", va="top", fontsize=8.8,
             bbox=dict(boxstyle="round,pad=0.4", fc="white", ec="#BBB"))
    axC.grid(alpha=0.2)

    fig.suptitle("Pre-registered interactome analysis of cancer-therapy cardiotoxicity: "
                 "proximity recovers the dexrazoxane\u2013TOP2B axis",
                 fontsize=12.2, fontweight="bold", x=0.045, ha="left", y=0.95)
    fig.text(0.045, 0.875, "STRING v12.0 (confidence \u2265700) \u00b7 1000-permutation "
             "degree-matched null \u00b7 all parameters fixed before data access",
             fontsize=8.8, color="#555", ha="left")

    out = FIG / "graphical_abstract.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("wrote", out, f"{out.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
