from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parents[1] / ".mplconfig"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
OUTS = [
    ROOT / "figures" / "fig_physical_source_contract.pdf",
    ROOT / "physical_source_submission_source" / "figures" / "fig_physical_source_contract.pdf",
]


def box(ax, x, y, w, h, title, lines, color):
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1.25,
        edgecolor=color,
        facecolor="#fbfcfe",
    )
    ax.add_patch(patch)
    ax.text(x + 0.02, y + h - 0.045, title, fontsize=8.6, weight="bold", color=color, va="top")
    ax.text(x + 0.02, y + h - 0.105, "\n".join(lines), fontsize=8.5, color="#20252b", va="top", linespacing=1.35)


def main():
    fig, ax = plt.subplots(figsize=(10.2, 4.8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    boxes = [
        (0.025, 0.57, 0.21, 0.31, "Complete seed presentation", ["relations + root state", "grading + Hodge unit", "no terminal labels"], "#4056a1"),
        (0.275, 0.57, 0.21, 0.31, "Exact source-compatible fibre", ["Def_src = 0", "common domain", "typed quotient/null policy"], "#6b4c9a"),
        (0.525, 0.57, 0.21, 0.31, "Constrained spectral selector", ["min log Tr exp(-K/A*)", "proper extensions cost more", "equality rigidity required"], "#9b5d26"),
        (0.775, 0.57, 0.20, 0.31, "Realization certificate", ["J*J = I", "JJ* = I", "typed intertwining"], "#26735f"),
        (0.34, 0.12, 0.32, 0.24, "Frozen BaseSeedPacket", ["B_tau_phys, s_U, A_B, J_seed", "N_phys, grading, A*, certificate", "input to TD-I seed--body solve"], "#9b2f3f"),
    ]
    for args in boxes:
        box(ax, *args)

    for x0, x1 in [(0.235, 0.275), (0.485, 0.525), (0.735, 0.775)]:
        ax.annotate("", xy=(x1, 0.725), xytext=(x0, 0.725), arrowprops=dict(arrowstyle="->", lw=1.5, color="#4d555e"))
    ax.annotate("", xy=(0.50, 0.36), xytext=(0.875, 0.57), arrowprops=dict(arrowstyle="->", lw=1.5, color="#4d555e", connectionstyle="arc3,rad=-0.2"))

    ax.text(0.5, 0.96, "TD-0: source realization before body formation and terminal readout", ha="center", va="top", fontsize=13, weight="bold")
    ax.text(0.5, 0.03, "Exact internal closure under stated premises; Nature-level ownership and occupation remain open.", ha="center", fontsize=9, color="#7a1f2b")
    fig.tight_layout()
    for out in OUTS:
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
