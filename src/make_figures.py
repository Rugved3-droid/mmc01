"""MMC-01 section 10 figures.

Fig 1  proximity heatmap: protectants x modules, degree-matched z (STRING 700),
       with the negative-control band shown beneath the same colour scale.
Fig 2  Gate 3: all 64 protectant-module z-scores with dexrazoxane-M1 marked,
       every pair plotted individually, across all three threshold arms.
Fig 3  Gate 4 specificity: protectant vs negative-control z by arm. This
       replaces the leave-one-out stability plot, which is not applicable
       because no primary statistic was computed (see RUNLOG.md).
"""
import json
import pathlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import TwoSlopeNorm

ROOT = pathlib.Path(r"D:\mmc01")
RES = ROOT / "results"
FIG = RES / "figures"
MODULES = ["M1", "M2", "M3", "M4"]
MODLAB = {"M1": "M1\nanthracycline", "M2": "M2\nanti-HER2",
          "M3": "M3\nVEGF pathway", "M4": "M4\nproteasome"}
SEED = 20261117


def load():
    return json.loads((RES / "proximity.json").read_text(encoding="utf-8"))["arms"]


def split(arm):
    prot, neg = {}, {}
    for d, v in arm.items():
        if v.get("dropped"):
            continue
        row = {m: r["z"] for m, r in v["modules"].items()}
        (prot if v["group"] == "protectant" else neg)[d] = row
    return prot, neg


def fig1(arms):
    prot, neg = split(arms["700"])
    pnames = sorted(prot, key=lambda d: np.mean([prot[d][m] for m in MODULES]))
    nnames = sorted(neg, key=lambda d: np.mean([neg[d][m] for m in MODULES]))
    P = np.array([[prot[d][m] for m in MODULES] for d in pnames])
    N = np.array([[neg[d][m] for m in MODULES] for d in nnames])

    vmax = float(max(abs(P).max(), abs(N).max()))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)
    fig, axes = plt.subplots(
        2, 1, figsize=(7.2, 9.4), height_ratios=[len(pnames), len(nnames) + 1.6],
        constrained_layout=True)

    for ax, M, names, title in (
            (axes[0], P, pnames, "Cardioprotectants"),
            (axes[1], N, nnames, "Negative controls (not part of the primary analysis)")):
        im = ax.imshow(M, cmap="RdBu_r", norm=norm, aspect="auto")
        ax.set_xticks(range(len(MODULES)), [MODLAB[m] for m in MODULES], fontsize=9)
        ax.set_yticks(range(len(names)), names, fontsize=9)
        ax.set_title(title, fontsize=11, pad=6, loc="left", fontweight="bold")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                v = M[i, j]
                ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=7.5,
                        color="white" if abs(v) > vmax * 0.55 else "#222")
        ax.set_xticks(np.arange(-.5, len(MODULES), 1), minor=True)
        ax.set_yticks(np.arange(-.5, len(names), 1), minor=True)
        ax.grid(which="minor", color="white", linewidth=1.2)
        ax.tick_params(which="minor", length=0)

    cb = fig.colorbar(im, ax=axes, shrink=0.45, location="right", pad=0.02)
    cb.set_label("closest-distance proximity z\n(negative = closer than the "
                 "degree-matched null)", fontsize=9)
    fig.suptitle("Figure 1  Proximity landscape, STRING 700, 1000-permutation "
                 f"degree-matched null (seed {SEED})", fontsize=11.5, x=0.02, ha="left")
    fig.savefig(FIG / "fig1_proximity_heatmap.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig2(arms):
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 5.0), sharey=True,
                             constrained_layout=True)
    # shared y-range with room for the annotation under the lowest point
    allv = [r["z"] for thr in ("400", "700", "900")
            for d, v in arms[thr].items() if not v.get("dropped")
            and v["group"] == "protectant" for r in v["modules"].values()]
    lo, hi = min(allv), max(allv)
    for ax, thr in zip(axes, ["400", "700", "900"]):
        prot, _ = split(arms[thr])
        pts, dex = [], None
        for d, row in prot.items():
            for m in MODULES:
                if d == "dexrazoxane" and m == "M1":
                    dex = row[m]
                else:
                    pts.append(row[m])
        pts = np.array(pts)
        cut = float(np.percentile(np.append(pts, dex), 25))
        rng = np.random.default_rng(SEED)
        ax.scatter(rng.normal(0, 0.055, pts.size), pts, s=26, alpha=0.62,
                   color="#5B7DB1", edgecolor="none", label="other pairs (n=63)",
                   zorder=2)
        ax.axhline(cut, color="#C44E52", ls="--", lw=1.5, zorder=3,
                   label=f"top-quartile cutoff ({cut:.2f})")
        ax.scatter([0], [dex], s=190, marker="*", color="#D9A441",
                   edgecolor="#4A3A10", linewidth=0.8, zorder=5,
                   label="dexrazoxane - M1")
        pct = float((pts < dex).sum()) / (pts.size + 1) * 100.0
        ax.annotate(f"z = {dex:.2f}\n{pct:.1f}th pctile",
                    xy=(0, dex), xytext=(0.17, dex - 0.35), fontsize=9,
                    arrowprops=dict(arrowstyle="-", lw=0.8, color="#4A3A10"))
        ax.set_title(f"STRING {thr}   Gate 3 {'PASS' if dex <= cut else 'FAIL'}",
                     fontsize=11, fontweight="bold")
        ax.set_xticks([])
        ax.set_xlim(-0.33, 0.62)
        ax.set_ylim(lo - 0.95, hi + 0.35)
        ax.grid(axis="y", alpha=0.25, zorder=0)
    axes[0].set_ylabel("closest-distance proximity z", fontsize=10)
    axes[0].legend(loc="upper left", fontsize=8.5, framealpha=0.95)
    fig.suptitle("Figure 2  Gate 3 positive control: dexrazoxane against the "
                 "anthracycline module, every pair plotted individually",
                 fontsize=11.5, x=0.01, ha="left")
    fig.savefig(FIG / "fig2_gate3_positive_control.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def fig3(arms):
    fig, ax = plt.subplots(figsize=(9.6, 5.4), constrained_layout=True)
    offsets = {"400": -0.22, "700": 0.0, "900": 0.22}
    colors = {"400": "#8DA9C4", "700": "#2F4B7C", "900": "#13293D"}
    rng = np.random.default_rng(SEED)
    for thr, dx in offsets.items():
        prot, neg = split(arms[thr])
        pv = np.array([prot[d][m] for d in prot for m in MODULES])
        nv = np.array([neg[d][m] for d in neg for m in MODULES])
        cut = float(np.percentile(pv, 25))
        px = np.full(pv.size, 0 + dx) + rng.normal(0, 0.035, pv.size)
        nx = np.full(nv.size, 1 + dx) + rng.normal(0, 0.035, nv.size)
        ax.scatter(px, pv, s=22, alpha=0.5, color=colors[thr], edgecolor="none")
        ax.scatter(nx, nv, s=36, alpha=0.9, color=colors[thr], edgecolor="black",
                   linewidth=0.4)
        ax.plot([0 + dx - 0.1, 0 + dx + 0.1], [cut, cut], color="#C44E52", lw=2)
        ax.plot([1 + dx - 0.1, 1 + dx + 0.1], [cut, cut], color="#C44E52", lw=2,
                ls=":")
        sel = nv <= cut
        if sel.any():
            ax.scatter(nx[sel], nv[sel], s=130, facecolor="none",
                       edgecolor="#C44E52", linewidth=1.7, zorder=6)
    # exploratory random-drug background, computed at STRING 700 only
    bgp = RES / "exploratory_random_background.json"
    if bgp.exists():
        bgj = json.loads(bgp.read_text(encoding="utf-8"))
        bv = np.array([r[m] for r in bgj["per_drug"] for m in MODULES], float)
        # freeze the y-range on the pre-specified data; the background has a
        # long tail that would otherwise compress every other series
        lo_y, hi_y = ax.get_ylim()
        inside = bv[(bv >= lo_y) & (bv <= hi_y)]
        n_out = int(bv.size - inside.size)
        ax.scatter(np.full(inside.size, 2.0) + rng.normal(0, 0.055, inside.size),
                   inside, s=13, alpha=0.4, color="#9AA5B1", edgecolor="none", zorder=1)
        ax.plot([1.88, 2.12], [np.median(bv)] * 2, color="#3F4A54", lw=2.4, zorder=4)
        ax.text(2.0, hi_y, f"median {np.median(bv):.2f}\n"
                f"p = {bgj['permutation_two_sided_p']:.4f} vs protectants"
                + (f"\n({n_out} of {bv.size} outside axis)" if n_out else ""),
                ha="center", va="top", fontsize=8.2,
                bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#CCC", alpha=0.9))
        ax.set_ylim(lo_y, hi_y)

    ax.set_xticks([0, 1, 2], ["cardioprotectants\n(16 drugs x 4 modules)",
                              "negative controls\n(5 drugs x 4 modules)",
                              "random drug background\n(100 drugs x 4 modules,\n"
                              "STRING 700, exploratory)"], fontsize=9.5)
    ax.set_ylabel("closest-distance proximity z", fontsize=10)
    ax.grid(axis="y", alpha=0.25)
    ax.axhline(0, color="#999", lw=0.8)
    handles = [plt.Line2D([], [], marker="o", ls="", color=colors[t],
                          label=f"STRING {t}") for t in offsets]
    handles += [plt.Line2D([], [], color="#C44E52", lw=2, label="top-quartile cutoff"),
                plt.Line2D([], [], marker="o", ls="", markerfacecolor="none",
                           markeredgecolor="#C44E52", markersize=11,
                           label="Gate 4 violation")]
    ax.legend(handles=handles, fontsize=8.5, loc="upper center", ncol=3,
              framealpha=0.95, bbox_to_anchor=(0.5, 1.0))
    ax.margins(y=0.16)
    ax.set_title("Figure 3  Specificity. Negative controls reach the protectant top "
                 "quartile in every arm, yet cardioprotectants as a class\n"
                 "sit closer to the cardiotoxicity modules than a random drug "
                 "background (exploratory)",
                 fontsize=11, loc="left")
    fig.savefig(FIG / "fig3_gate4_specificity.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    FIG.mkdir(parents=True, exist_ok=True)
    arms = load()
    fig1(arms)
    fig2(arms)
    fig3(arms)
    print("wrote:")
    for p in sorted(FIG.glob("*.png")):
        print(" ", p, f"{p.stat().st_size//1024} KB")
