from __future__ import annotations

import os
from pathlib import Path

import matplotlib

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "paper_assets"
PNG_PATH = OUTPUT_DIR / "research_work_flowchart.png"
SVG_PATH = OUTPUT_DIR / "research_work_flowchart.svg"
MPL_CONFIG_DIR = ROOT / ".mplconfig"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPL_CONFIG_DIR)

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


NODES = [
    ("Start", "#1d4ed8"),
    ("Load Cardio Dataset", "#0f766e"),
    ("Profile Dataset\nshape, missing, duplicates,\nclass balance", "#0f766e"),
    ("Medical Data Cleaning\nremove invalid records", "#ca8a04"),
    ("Baseline Feature Engineering\nBMI, pulse pressure,\nMAP, age group, BP ratio", "#7c3aed"),
    ("EDA and Visualization", "#7c3aed"),
    ("Train Baseline Models\nLR, RF, Linear SVM, GB", "#dc2626"),
    ("Evaluate Performance\nAccuracy, Precision,\nRecall, F1, ROC-AUC", "#dc2626"),
    ("Compare Train/Test Splits\n70/30 to 90/10", "#ea580c"),
    ("Select Best Split\n85/15", "#ea580c"),
    ("Advanced Feature Engineering\nrisk flags and interactions", "#9333ea"),
    ("Tune Gradient Boosting\nGridSearchCV", "#be123c"),
    ("Final Main-Dataset Result\nROC-AUC = 0.8052", "#be123c"),
    ("External Validation\nUCI Heart Disease", "#15803d"),
    ("Report Final Findings\nrobust and generalizable model", "#15803d"),
    ("End", "#1d4ed8"),
]


def add_box(ax: plt.Axes, x: float, y: float, text: str, color: str) -> None:
    width = 5.8
    height = 0.95
    patch = FancyBboxPatch(
        (x - width / 2, y - height / 2),
        width,
        height,
        boxstyle="round,pad=0.03,rounding_size=0.12",
        linewidth=2.0,
        edgecolor=color,
        facecolor=color,
        alpha=0.92,
    )
    ax.add_patch(patch)
    ax.text(
        x,
        y,
        text,
        ha="center",
        va="center",
        fontsize=11,
        color="white",
        weight="bold",
        family="DejaVu Sans",
    )


def add_arrow(ax: plt.Axes, y_top: float, y_bottom: float) -> None:
    arrow = FancyArrowPatch(
        (0, y_top - 0.52),
        (0, y_bottom + 0.52),
        arrowstyle="-|>",
        mutation_scale=18,
        linewidth=2.2,
        color="#334155",
    )
    ax.add_patch(arrow)


def render() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 24), facecolor="#f8fafc")
    ax.set_facecolor("#f8fafc")

    y_positions = list(range(len(NODES) * 2, 0, -2))
    for index, ((label, color), y) in enumerate(zip(NODES, y_positions)):
        add_box(ax, 0, y, label, color)
        if index < len(y_positions) - 1:
            add_arrow(ax, y, y_positions[index + 1])

    ax.text(
        0,
        y_positions[0] + 1.6,
        "AI-Driven Cardiovascular Disease Prediction Research Workflow",
        ha="center",
        va="center",
        fontsize=18,
        weight="bold",
        color="#0f172a",
        family="DejaVu Sans",
    )

    ax.text(
        0,
        0.6,
        "Main dataset -> model comparison -> split study -> feature optimization -> external validation",
        ha="center",
        va="center",
        fontsize=11,
        color="#475569",
        family="DejaVu Sans",
    )

    ax.set_xlim(-4.2, 4.2)
    ax.set_ylim(0, y_positions[0] + 2.4)
    ax.axis("off")

    fig.tight_layout()
    fig.savefig(PNG_PATH, dpi=300, bbox_inches="tight", facecolor=fig.get_facecolor())
    fig.savefig(SVG_PATH, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__ == "__main__":
    render()
