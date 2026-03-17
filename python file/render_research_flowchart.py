from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MPL_CONFIG_DIR = ROOT / ".mplconfig"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPL_CONFIG_DIR)

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


OUTPUT_DIR = ROOT / "paper_assets"
PNG_PATH = OUTPUT_DIR / "research_work_flowchart.png"
SVG_PATH = OUTPUT_DIR / "research_work_flowchart.svg"


def rounded_box(ax, center, width, height, text, face, edge="#0f172a", text_color="white", fontsize=11):
    x, y = center
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.18",
        linewidth=2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=text_color, weight="bold")


def process_box(ax, center, width, height, text, face, edge="#334155", text_color="white", fontsize=10.5):
    x, y = center
    patch = Rectangle(
        (x - width / 2, y - height / 2),
        width,
        height,
        linewidth=2,
        edgecolor=edge,
        facecolor=face,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=text_color, weight="bold")


def decision_box(ax, center, width, height, text, face, edge="#334155", text_color="white", fontsize=10.5):
    x, y = center
    points = [
        (x, y + height / 2),
        (x + width / 2, y),
        (x, y - height / 2),
        (x - width / 2, y),
    ]
    patch = Polygon(points, closed=True, linewidth=2, edgecolor=edge, facecolor=face)
    ax.add_patch(patch)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color=text_color, weight="bold")


def arrow(ax, start, end, color="#475569", lw=2.2, style="-|>"):
    patch = FancyArrowPatch(start, end, arrowstyle=style, mutation_scale=16, linewidth=lw, color=color)
    ax.add_patch(patch)


def elbow(ax, points, color="#475569", lw=2.2):
    for i in range(len(points) - 1):
        ax.plot(
            [points[i][0], points[i + 1][0]],
            [points[i][1], points[i + 1][1]],
            color=color,
            linewidth=lw,
        )
    arrow(ax, points[-2], points[-1], color=color, lw=lw)


def label(ax, pos, text, color="#1e293b", fontsize=9.5):
    ax.text(pos[0], pos[1], text, ha="center", va="center", fontsize=fontsize, color=color, weight="bold")


def render():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(20, 11), facecolor="#f8fafc")
    ax.set_facecolor("#f8fafc")

    # Title
    ax.text(
        10,
        10.35,
        "Research Workflow Flowchart for Cardiovascular Disease Prediction",
        ha="center",
        va="center",
        fontsize=22,
        weight="bold",
        color="#0f172a",
    )
    ax.text(
        10,
        9.92,
        "Branching design: main dataset modeling, external UCI validation, then final comparison",
        ha="center",
        va="center",
        fontsize=11.5,
        color="#475569",
    )

    # Core nodes
    rounded_box(ax, (10, 9.0), 3.6, 0.9, "Start", "#2563eb")
    process_box(ax, (10, 7.8), 5.2, 1.0, "Define objective:\nEarly prediction of cardiovascular disease", "#0f766e")
    decision_box(ax, (10, 6.3), 4.2, 1.5, "Which dataset\npipeline is executed?", "#b45309")

    # Left branch: main dataset
    process_box(ax, (4.2, 5.0), 4.6, 1.0, "Load primary dataset:\ncardio_train.csv", "#7c3aed")
    process_box(ax, (4.2, 3.8), 4.8, 1.0, "Profile and clean data\nusing medical validity rules", "#7c3aed")
    process_box(ax, (4.2, 2.55), 5.2, 1.0, "Engineer baseline features:\nBMI, pulse pressure, MAP,\nage group, BP ratio", "#9333ea")
    process_box(ax, (4.2, 1.2), 4.7, 1.0, "Train baseline models:\nLR, RF, Linear SVM, GB", "#dc2626")
    decision_box(ax, (4.2, -0.25), 4.1, 1.5, "Best baseline\nmodel?", "#dc2626")
    process_box(ax, (4.2, -1.8), 5.0, 1.0, "Select Gradient Boosting\nbased on ROC-AUC", "#be123c")
    process_box(ax, (4.2, -3.05), 5.3, 1.0, "Compare train/test splits:\n70/30, 75/25, 80/20,\n85/15, 90/10", "#ea580c")
    decision_box(ax, (4.2, -4.6), 4.1, 1.5, "Best split\nidentified?", "#ea580c")
    process_box(ax, (4.2, -6.15), 5.0, 1.0, "Choose 85/15 split", "#0891b2")
    process_box(ax, (4.2, -7.45), 5.4, 1.0, "Create advanced risk and\ninteraction features", "#9333ea")
    process_box(ax, (4.2, -8.8), 5.0, 1.0, "Tune Gradient Boosting\nwith GridSearchCV", "#be123c")
    process_box(ax, (4.2, -10.15), 5.2, 1.0, "Main dataset result:\nROC-AUC = 0.8052", "#15803d")

    # Right branch: external validation
    process_box(ax, (15.8, 5.0), 4.9, 1.0, "Load external dataset:\nUCI Heart Disease", "#7c3aed")
    process_box(ax, (15.8, 3.8), 4.8, 1.0, "Clean data and convert\nmulti-class target to binary", "#7c3aed")
    process_box(ax, (15.8, 2.55), 5.1, 1.0, "Engineer baseline and\nadvanced UCI features", "#9333ea")
    process_box(ax, (15.8, 1.2), 4.9, 1.0, "Train Gradient Boosting\nfor external validation", "#dc2626")
    process_box(ax, (15.8, -0.25), 5.1, 1.0, "Evaluate default and tuned\nUCI models", "#be123c")
    process_box(ax, (15.8, -1.8), 5.0, 1.0, "Best UCI result:\nROC-AUC = 0.9238", "#15803d")

    # Merge and finish
    decision_box(ax, (10, -3.9), 4.7, 1.6, "Do both results support\nmodel robustness?", "#0f766e")
    process_box(ax, (10, -6.3), 5.4, 1.0, "Compare both datasets and\nsummarize findings", "#0369a1")
    process_box(ax, (10, -7.75), 5.5, 1.0, "Conclude: model is accurate,\noptimized, and generalizable", "#15803d")
    rounded_box(ax, (10, -9.15), 3.8, 0.9, "End", "#2563eb")

    # Straight arrows
    arrow(ax, (10, 8.55), (10, 8.3))
    arrow(ax, (10, 7.3), (10, 7.05))
    arrow(ax, (4.2, 4.5), (4.2, 4.3))
    arrow(ax, (4.2, 3.3), (4.2, 3.05))
    arrow(ax, (4.2, 2.05), (4.2, 1.75))
    arrow(ax, (4.2, 0.7), (4.2, 0.45))
    arrow(ax, (4.2, -1.0), (4.2, -1.3))
    arrow(ax, (4.2, -2.3), (4.2, -2.55))
    arrow(ax, (4.2, -3.55), (4.2, -3.85))
    arrow(ax, (4.2, -5.35), (4.2, -5.65))
    arrow(ax, (4.2, -6.65), (4.2, -6.95))
    arrow(ax, (4.2, -7.95), (4.2, -8.3))
    arrow(ax, (4.2, -9.3), (4.2, -9.65))

    arrow(ax, (15.8, 4.5), (15.8, 4.3))
    arrow(ax, (15.8, 3.3), (15.8, 3.05))
    arrow(ax, (15.8, 2.05), (15.8, 1.75))
    arrow(ax, (15.8, 0.7), (15.8, 0.25))
    arrow(ax, (15.8, -0.75), (15.8, -1.3))

    arrow(ax, (10, -4.7), (10, -5.75))
    arrow(ax, (10, -6.8), (10, -7.25))
    arrow(ax, (10, -8.25), (10, -8.7))

    # Branch arrows from dataset decision
    elbow(ax, [(8.0, 6.3), (4.2, 6.3), (4.2, 5.55)])
    elbow(ax, [(12.0, 6.3), (15.8, 6.3), (15.8, 5.55)])
    label(ax, (6.2, 6.65), "Primary modeling path", "#7c3aed")
    label(ax, (13.8, 6.65), "External validation path", "#7c3aed")

    # Labels on left decisions
    elbow(ax, [(6.25, -0.25), (8.0, -0.25), (8.0, -3.15), (12.3, -3.15), (12.3, -3.9)])
    label(ax, (7.05, -0.62), "GB", "#991b1b")
    elbow(ax, [(6.25, -4.6), (8.1, -4.6), (8.1, -4.05)])
    label(ax, (7.1, -4.95), "Yes", "#9a3412")

    # Merge from main and external results
    elbow(ax, [(6.8, -10.15), (6.8, -3.9), (7.65, -3.9)])
    elbow(ax, [(13.3, -1.8), (12.35, -1.8), (12.35, -3.9)])
    label(ax, (6.9, -6.9), "Optimized main result", "#15803d")
    label(ax, (13.45, -2.45), "UCI validation result", "#15803d")

    # Decision outcome labels
    label(ax, (10.95, -4.45), "Yes", "#0f766e")

    # Decorative legend
    rounded_box(ax, (2.55, 9.0), 2.4, 0.65, "Start/End", "#2563eb", fontsize=9.5)
    process_box(ax, (2.55, 8.15), 2.4, 0.65, "Process", "#475569", fontsize=9.5)
    decision_box(ax, (2.55, 7.28), 2.1, 0.78, "Decision", "#b45309", fontsize=9.5)

    ax.set_xlim(0.5, 19.5)
    ax.set_ylim(-10.2, 10.9)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(SVG_PATH, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    render()
