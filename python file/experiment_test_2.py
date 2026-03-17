from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(r"C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer")
MPL_CONFIG_DIR = ROOT / "python file" / ".mplconfig"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPL_CONFIG_DIR)

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score
from sklearn.model_selection import train_test_split

from experiment_test_1 import build_model_pipelines, clean_data, engineer_features, load_data


OUTPUT_DIR = ROOT / "python file" / "outputs_experiment_test_2"
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"

SPLITS = [
    (0.70, 0.30),
    (0.75, 0.25),
    (0.80, 0.20),
    (0.85, 0.15),
    (0.90, 0.10),
]


def ensure_dirs() -> None:
    for path in (OUTPUT_DIR, PLOTS_DIR, TABLES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def prepare_dataset() -> pd.DataFrame:
    raw_df = load_data()
    cleaned_df, _ = clean_data(raw_df)
    return engineer_features(cleaned_df)


def evaluate_split(df: pd.DataFrame, train_ratio: float, test_ratio: float) -> list[dict]:
    feature_columns = [col for col in df.columns if col != "cardio"]
    X = df[feature_columns]
    y = df["cardio"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=train_ratio,
        test_size=test_ratio,
        random_state=42,
        stratify=y,
    )

    models, _, _ = build_model_pipelines(feature_columns)
    rows = []
    for model_name, pipeline in models.items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        if hasattr(pipeline, "predict_proba"):
            y_score = pipeline.predict_proba(X_test)[:, 1]
        else:
            y_score = pipeline.decision_function(X_test)

        rows.append(
            {
                "train_ratio": train_ratio,
                "test_ratio": test_ratio,
                "model": model_name,
                "accuracy": accuracy_score(y_test, y_pred),
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_score),
            }
        )
    return rows


def plot_best_auc(best_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    labels = [f"{int(t * 100)}/{int(s * 100)}" for t, s in zip(best_df["train_ratio"], best_df["test_ratio"])]
    ax.plot(labels, best_df["roc_auc"], marker="o")
    ax.set_xlabel("Train/Test Split")
    ax.set_ylabel("Best ROC-AUC")
    ax.set_title("Best ROC-AUC Across Train/Test Splits")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "best_roc_auc_by_split.png", dpi=200)
    plt.close(fig)


def write_summary(best_df: pd.DataFrame) -> None:
    lines = ["Experiment Test 2: Train/Test Split Comparison", ""]
    for _, row in best_df.iterrows():
        lines.extend(
            [
                f"Split {int(row['train_ratio'] * 100)}/{int(row['test_ratio'] * 100)}",
                f"- Best model: {row['model']}",
                f"- Accuracy: {row['accuracy']:.4f}",
                f"- Precision: {row['precision']:.4f}",
                f"- Recall: {row['recall']:.4f}",
                f"- F1-score: {row['f1_score']:.4f}",
                f"- ROC-AUC: {row['roc_auc']:.4f}",
                "",
            ]
        )
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    print("Preparing cleaned feature-engineered dataset")
    df = prepare_dataset()

    all_rows: list[dict] = []
    for train_ratio, test_ratio in SPLITS:
        print(f"Running split {int(train_ratio * 100)}/{int(test_ratio * 100)}")
        all_rows.extend(evaluate_split(df, train_ratio, test_ratio))

    results_df = pd.DataFrame(all_rows).sort_values(by=["train_ratio", "roc_auc"], ascending=[True, False])
    results_df.to_csv(TABLES_DIR / "split_comparison_all_models.csv", index=False)

    best_df = results_df.groupby(["train_ratio", "test_ratio"], as_index=False).first()
    best_df.to_csv(TABLES_DIR / "split_comparison_best_models.csv", index=False)
    plot_best_auc(best_df)
    write_summary(best_df)

    with (OUTPUT_DIR / "summary.json").open("w", encoding="utf-8") as fh:
        json.dump(best_df.to_dict(orient="records"), fh, indent=2)

    print(best_df[["train_ratio", "test_ratio", "model", "accuracy", "f1_score", "roc_auc"]].to_string(index=False))
    print(f"Finished. Outputs saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
