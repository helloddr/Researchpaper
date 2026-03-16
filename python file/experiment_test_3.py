from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(r"C:\Users\Dharanidhar Nikki\Desktop\Pesearch papaer")
MPL_CONFIG_DIR = ROOT / "python file" / ".mplconfig"
MPL_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
os.environ["MPLCONFIGDIR"] = str(MPL_CONFIG_DIR)
os.environ["LOKY_MAX_CPU_COUNT"] = "1"

import matplotlib.pyplot as plt
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, StratifiedKFold, train_test_split
from sklearn.pipeline import Pipeline

from cvd_pipeline import clean_data, engineer_features, load_data


OUTPUT_DIR = ROOT / "python file" / "outputs_experiment_test_3"
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"

TRAIN_RATIO = 0.85
TEST_RATIO = 0.15


def ensure_dirs() -> None:
    for path in (OUTPUT_DIR, PLOTS_DIR, TABLES_DIR):
        path.mkdir(parents=True, exist_ok=True)


def add_advanced_features(df: pd.DataFrame) -> pd.DataFrame:
    featured = df.copy()
    featured["bmi_overweight_flag"] = (featured["bmi"] >= 25).astype(int)
    featured["bmi_obese_flag"] = (featured["bmi"] >= 30).astype(int)
    featured["high_bp_flag"] = ((featured["ap_hi"] >= 140) | (featured["ap_lo"] >= 90)).astype(int)
    featured["stage2_bp_flag"] = ((featured["ap_hi"] >= 160) | (featured["ap_lo"] >= 100)).astype(int)
    featured["pulse_pressure_high_flag"] = (featured["pulse_pressure"] >= 60).astype(int)
    featured["cholesterol_risk_flag"] = (featured["cholesterol"] > 1).astype(int)
    featured["glucose_risk_flag"] = (featured["gluc"] > 1).astype(int)
    featured["lifestyle_risk_score"] = featured["smoke"] + featured["alco"] + (1 - featured["active"])
    featured["metabolic_risk_score"] = (
        featured["cholesterol_risk_flag"]
        + featured["glucose_risk_flag"]
        + featured["bmi_overweight_flag"]
        + featured["high_bp_flag"]
    )
    featured["age_pressure_interaction"] = featured["age_years"] * featured["ap_hi"]
    featured["age_bmi_interaction"] = featured["age_years"] * featured["bmi"]
    featured["chol_gluc_interaction"] = featured["cholesterol"] * featured["gluc"]
    featured["pressure_load"] = featured["ap_hi"] + featured["ap_lo"]
    return featured


def prepare_datasets() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw_df = load_data()
    cleaned_df, _ = clean_data(raw_df)
    baseline_df = engineer_features(cleaned_df)
    advanced_df = add_advanced_features(baseline_df)
    return baseline_df, advanced_df


def build_pipeline(feature_columns: list[str], params: dict | None = None) -> Pipeline:
    preprocessor = ColumnTransformer(
        transformers=[
            ("numeric", SimpleImputer(strategy="median"), feature_columns),
        ]
    )
    model = GradientBoostingClassifier(random_state=42, **(params or {}))
    return Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )


def evaluate_fixed_pipeline(df: pd.DataFrame, params: dict | None = None) -> tuple[dict, dict[str, list[float]]]:
    feature_columns = [col for col in df.columns if col != "cardio"]
    X = df[feature_columns]
    y = df["cardio"]

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
    search_scores = []
    for train_idx, valid_idx in cv.split(X_train, y_train):
        X_cv_train = X_train.iloc[train_idx]
        X_cv_valid = X_train.iloc[valid_idx]
        y_cv_train = y_train.iloc[train_idx]
        y_cv_valid = y_train.iloc[valid_idx]
        pipeline.fit(X_cv_train, y_cv_train)
        y_cv_score = pipeline.predict_proba(X_cv_valid)[:, 1]
        search_scores.append(roc_auc_score(y_cv_valid, y_cv_score))

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
        "cv_roc_auc_mean": float(sum(search_scores) / len(search_scores)),
    }
    return metrics, {"fpr": fpr.tolist(), "tpr": tpr.tolist()}


def run_full_grid_search(df: pd.DataFrame) -> tuple[dict, pd.DataFrame]:
    feature_columns = [col for col in df.columns if col != "cardio"]
    X = df[feature_columns]
    y = df["cardio"]

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
        "model__n_estimators": [100, 150, 200],
        "model__learning_rate": [0.03, 0.05, 0.08],
        "model__max_depth": [2, 3, 4],
        "model__subsample": [0.8, 1.0],
        "model__min_samples_leaf": [20, 40],
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
    results_df.to_csv(TABLES_DIR / "gradient_boosting_tuning_results.csv", index=False)

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


def save_comparison(baseline_metrics: dict, advanced_metrics: dict, tuned_payload: dict) -> pd.DataFrame:
    comparison_df = pd.DataFrame(
        [
            {"experiment": "baseline_features_default_gb", **baseline_metrics},
            {"experiment": "advanced_features_default_gb", **advanced_metrics},
            {"experiment": "advanced_features_full_grid_tuned_gb", **tuned_payload["metrics"]},
        ]
    )
    comparison_df.to_csv(TABLES_DIR / "optimization_comparison.csv", index=False)
    return comparison_df


def plot_roc_curves(curves: dict[str, dict[str, list[float]]]) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    for label, curve in curves.items():
        ax.plot(curve["fpr"], curve["tpr"], label=label)
    ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("Experiment Test 3 ROC Curve Comparison")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "optimization_roc_curves.png", dpi=200)
    plt.close(fig)


def write_summary(comparison_df: pd.DataFrame, tuned_payload: dict) -> None:
    best_row = comparison_df.sort_values(by="roc_auc", ascending=False).iloc[0]
    lines = [
        "Experiment Test 3: Full-Data Deep Optimization",
        "",
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
    print("Preparing baseline and advanced feature sets")
    baseline_df, advanced_df = prepare_datasets()

    print("Evaluating baseline Gradient Boosting with default parameters on full data split")
    baseline_metrics, baseline_curve = evaluate_fixed_pipeline(baseline_df)

    print("Evaluating advanced feature set with default Gradient Boosting on full data split")
    advanced_metrics, advanced_curve = evaluate_fixed_pipeline(advanced_df)

    print("Running full GridSearchCV tuning on the advanced feature set")
    tuned_payload, _ = run_full_grid_search(advanced_df)

    comparison_df = save_comparison(baseline_metrics, advanced_metrics, tuned_payload)
    plot_roc_curves(
        {
            "Baseline Features + Default GB": baseline_curve,
            "Advanced Features + Default GB": advanced_curve,
            "Advanced Features + Full Grid Tuned GB": tuned_payload["roc_curve"],
        }
    )
    write_summary(comparison_df, tuned_payload)

    with (OUTPUT_DIR / "best_tuned_model.json").open("w", encoding="utf-8") as fh:
        json.dump(tuned_payload, fh, indent=2)

    print(comparison_df.to_string(index=False))
    print(f"Finished. Outputs saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
