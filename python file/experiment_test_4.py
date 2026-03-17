from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(r"C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer")
MPL_CONFIG_DIR = ROOT / "python file" / ".mplconfig"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPL_CONFIG_DIR)
os.environ["LOKY_MAX_CPU_COUNT"] = "1"

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline


DATASET_PATH = ROOT / "Data sets" / "UCI Heart Disease" / "processed_cleveland.data"
OUTPUT_DIR = ROOT / "python file" / "outputs_experiment_test_4"
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"

TRAIN_RATIO = 0.85
TEST_RATIO = 0.15
COLUMN_NAMES = [
    "age",
    "sex",
    "cp",
    "trestbps",
    "chol",
    "fbs",
    "restecg",
    "thalach",
    "exang",
    "oldpeak",
    "slope",
    "ca",
    "thal",
    "target",
]


def ensure_dirs() -> None:
    for path in (OUTPUT_DIR, PLOTS_DIR, TABLES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH, header=None, names=COLUMN_NAMES, na_values="?")


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    cleaned = df.copy()
    initial_rows = len(cleaned)
    cleaned["target_binary"] = (cleaned["target"] > 0).astype(int)
    cleaned = cleaned.drop(columns=["target"])

    valid_mask = (
        cleaned["age"].between(20, 100)
        & cleaned["trestbps"].between(80, 250)
        & cleaned["chol"].between(100, 700)
        & cleaned["thalach"].between(60, 250)
        & cleaned["oldpeak"].between(0, 10)
    )
    cleaned = cleaned.loc[valid_mask].copy()

    summary = {
        "initial_rows": initial_rows,
        "rows_after_cleaning": int(len(cleaned)),
        "rows_removed": int(initial_rows - len(cleaned)),
        "missing_values": cleaned.isna().sum().to_dict(),
        "target_distribution": cleaned["target_binary"].value_counts().sort_index().to_dict(),
    }
    return cleaned, summary


def engineer_baseline_features(df: pd.DataFrame) -> pd.DataFrame:
    featured = df.copy()
    featured["age_group"] = pd.cut(
        featured["age"],
        bins=[0, 40, 50, 60, 120],
        labels=[0, 1, 2, 3],
        include_lowest=True,
    ).astype(int)
    featured["st_depression_flag"] = (featured["oldpeak"] >= 2.0).astype(int)
    featured["high_bp_flag"] = (featured["trestbps"] >= 140).astype(int)
    featured["high_chol_flag"] = (featured["chol"] >= 240).astype(int)
    return featured


def engineer_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    featured = engineer_baseline_features(df)
    featured["senior_flag"] = (featured["age"] >= 60).astype(int)
    featured["low_thalach_flag"] = (featured["thalach"] < 120).astype(int)
    featured["exercise_risk_score"] = featured["exang"] + featured["st_depression_flag"]
    featured["vessel_risk_flag"] = featured["ca"].fillna(0).ge(1).astype(int)
    featured["major_vessel_burden"] = featured["ca"].fillna(0)
    featured["thal_risk_flag"] = featured["thal"].fillna(3).isin([6, 7]).astype(int)
    featured["cp_exang_interaction"] = featured["cp"] * featured["exang"]
    featured["age_oldpeak_interaction"] = featured["age"] * featured["oldpeak"]
    featured["bp_chol_interaction"] = featured["trestbps"] * featured["chol"]
    featured["rate_pressure_proxy"] = featured["trestbps"] * featured["thalach"]
    featured["metabolic_pressure_score"] = featured["high_bp_flag"] + featured["high_chol_flag"] + featured["fbs"]
    return featured


def build_pipeline(feature_columns: list[str], params: dict | None = None) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[("numeric", SimpleImputer(strategy="median"), feature_columns)]
    )
    model = GradientBoostingClassifier(random_state=42, **(params or {}))
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def evaluate_fixed_pipeline(df: pd.DataFrame, params: dict | None = None) -> tuple[dict, dict[str, list[float]]]:
    feature_columns = [col for col in df.columns if col != "target_binary"]
    X = df[feature_columns]
    y = df["target_binary"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=TRAIN_RATIO,
        test_size=TEST_RATIO,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(feature_columns, params=params)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    cv_scores = []
    for train_idx, valid_idx in cv.split(X_train, y_train):
        X_cv_train = X_train.iloc[train_idx]
        X_cv_valid = X_train.iloc[valid_idx]
        y_cv_train = y_train.iloc[train_idx]
        y_cv_valid = y_train.iloc[valid_idx]
        pipeline.fit(X_cv_train, y_cv_train)
        y_cv_score = pipeline.predict_proba(X_cv_valid)[:, 1]
        cv_scores.append(roc_auc_score(y_cv_valid, y_cv_score))

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    y_score = pipeline.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_score)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred),
        "recall": recall_score(y_test, y_pred),
        "f1_score": f1_score(y_test, y_pred),
        "roc_auc": roc_auc_score(y_test, y_score),
        "cv_roc_auc_mean": float(sum(cv_scores) / len(cv_scores)),
    }
    return metrics, {"fpr": fpr.tolist(), "tpr": tpr.tolist()}


def run_full_grid_search(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    feature_columns = [col for col in df.columns if col != "target_binary"]
    X = df[feature_columns]
    y = df["target_binary"]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        train_size=TRAIN_RATIO,
        test_size=TEST_RATIO,
        random_state=42,
        stratify=y,
    )

    pipeline = build_pipeline(feature_columns)
    param_grid = {
        "model__n_estimators": [50, 100, 150, 200],
        "model__learning_rate": [0.03, 0.05, 0.08, 0.1],
        "model__max_depth": [1, 2, 3],
        "model__subsample": [0.8, 1.0],
        "model__min_samples_leaf": [1, 3, 5, 10],
    }
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="roc_auc",
        cv=cv,
        n_jobs=1,
        verbose=2,
        refit=True,
        return_train_score=False,
    )
    search.fit(X_train, y_train)

    results_df = pd.DataFrame(search.cv_results_).sort_values(by="mean_test_score", ascending=False)
    results_df.to_csv(TABLES_DIR / "uci_gradient_boosting_tuning_results.csv", index=False)

    best_model = search.best_estimator_
    y_pred = best_model.predict(X_test)
    y_score = best_model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_score)

    best_payload = {
        "params": {key.replace("model__", ""): value for key, value in search.best_params_.items()},
        "metrics": {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred),
            "recall": recall_score(y_test, y_pred),
            "f1_score": f1_score(y_test, y_pred),
            "roc_auc": roc_auc_score(y_test, y_score),
            "cv_roc_auc_mean": float(search.best_score_),
        },
        "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
    }
    return best_payload, results_df


def plot_roc_curves(curves: dict[str, dict[str, list[float]]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    for label, curve in curves.items():
        ax.plot(curve["fpr"], curve["tpr"], label=label)
    ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Experiment Test 4 ROC Curve Comparison (UCI)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "uci_optimization_roc_curves.png", dpi=200)
    plt.close(fig)


def save_comparison(cleaning_summary: dict, baseline_metrics: dict, advanced_metrics: dict, tuned_payload: dict) -> pd.DataFrame:
    with (OUTPUT_DIR / "uci_dataset_summary.json").open("w", encoding="utf-8") as fh:
        json.dump(cleaning_summary, fh, indent=2)

    comparison_df = pd.DataFrame(
        [
            {"experiment": "uci_baseline_features_default_gb", **baseline_metrics},
            {"experiment": "uci_advanced_features_default_gb", **advanced_metrics},
            {"experiment": "uci_advanced_features_full_grid_tuned_gb", **tuned_payload["metrics"]},
        ]
    )
    comparison_df.to_csv(TABLES_DIR / "uci_optimization_comparison.csv", index=False)
    return comparison_df


def write_summary(cleaning_summary: dict, comparison_df: pd.DataFrame, tuned_payload: dict) -> None:
    best_row = comparison_df.sort_values(by="roc_auc", ascending=False).iloc[0]
    lines = [
        "Experiment Test 4: UCI Heart Disease Deep Benchmark",
        "",
        f"Input dataset: {DATASET_PATH}",
        f"Rows after cleaning: {cleaning_summary['rows_after_cleaning']}",
        f"Rows removed: {cleaning_summary['rows_removed']}",
        f"Target distribution: {cleaning_summary['target_distribution']}",
        f"Train/Test split: {int(TRAIN_RATIO * 100)}/{int(TEST_RATIO * 100)}",
        "Tuning method: full GridSearchCV on the complete training split",
        "",
        "Best overall experiment:",
        f"- {best_row['experiment']}",
        f"- Accuracy: {best_row['accuracy']:.4f}",
        f"- Precision: {best_row['precision']:.4f}",
        f"- Recall: {best_row['recall']:.4f}",
        f"- F1-score: {best_row['f1_score']:.4f}",
        f"- ROC-AUC: {best_row['roc_auc']:.4f}",
        f"- CV ROC-AUC: {best_row['cv_roc_auc_mean']:.4f}",
        "",
        "Best tuned Gradient Boosting parameters:",
    ]
    lines.extend(f"- {key}: {value}" for key, value in tuned_payload["params"].items())
    (OUTPUT_DIR / "summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()
    print("Loading UCI Cleveland dataset")
    raw_df = load_data()
    cleaned_df, cleaning_summary = clean_data(raw_df)
    baseline_df = engineer_baseline_features(cleaned_df)
    advanced_df = engineer_advanced_features(cleaned_df)

    print("Evaluating baseline feature set with default Gradient Boosting")
    baseline_metrics, baseline_curve = evaluate_fixed_pipeline(baseline_df)

    print("Evaluating advanced feature set with default Gradient Boosting")
    advanced_metrics, advanced_curve = evaluate_fixed_pipeline(advanced_df)

    print("Running full GridSearchCV tuning on the advanced UCI feature set")
    tuned_payload, _ = run_full_grid_search(advanced_df)

    comparison_df = save_comparison(cleaning_summary, baseline_metrics, advanced_metrics, tuned_payload)
    plot_roc_curves(
        {
            "UCI Baseline Features + Default GB": baseline_curve,
            "UCI Advanced Features + Default GB": advanced_curve,
            "UCI Advanced Features + Full Grid Tuned GB": tuned_payload["roc_curve"],
        }
    )
    write_summary(cleaning_summary, comparison_df, tuned_payload)

    with (OUTPUT_DIR / "best_tuned_model.json").open("w", encoding="utf-8") as fh:
        json.dump(tuned_payload, fh, indent=2)

    print(comparison_df.to_string(index=False))
    print(f"Finished. Outputs saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
