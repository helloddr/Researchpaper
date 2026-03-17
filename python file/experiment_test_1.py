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
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC


DATASET_PATH = ROOT / "Data sets" / "cardio_train.csv" / "cardio_train.csv"
OUTPUT_DIR = ROOT / "python file" / "outputs_experiment_test_1"
PLOTS_DIR = OUTPUT_DIR / "plots"
TABLES_DIR = OUTPUT_DIR / "tables"
MODELS_DIR = OUTPUT_DIR / "models"


def ensure_dirs() -> None:
    for path in (OUTPUT_DIR, PLOTS_DIR, TABLES_DIR, MODELS_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    return pd.read_csv(DATASET_PATH)


def build_profile(df: pd.DataFrame) -> dict:
    profile = {
        "shape": list(df.shape),
        "columns": df.columns.tolist(),
        "missing_values": df.isna().sum().to_dict(),
        "duplicate_rows": int(df.duplicated().sum()),
        "target_distribution": df["cardio"].value_counts().sort_index().to_dict(),
        "invalid_value_counts": {
            "height_below_120": int((df["height"] < 120).sum()),
            "height_above_220": int((df["height"] > 220).sum()),
            "weight_below_30": int((df["weight"] < 30).sum()),
            "weight_above_200": int((df["weight"] > 200).sum()),
            "ap_hi_below_80": int((df["ap_hi"] < 80).sum()),
            "ap_hi_above_240": int((df["ap_hi"] > 240).sum()),
            "ap_lo_below_40": int((df["ap_lo"] < 40).sum()),
            "ap_lo_above_160": int((df["ap_lo"] > 160).sum()),
            "ap_hi_less_than_ap_lo": int((df["ap_hi"] <= df["ap_lo"]).sum()),
        },
    }
    return profile


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    cleaned = df.copy()
    initial_rows = len(cleaned)
    cleaned = cleaned.drop(columns=["id"])
    cleaned["age_years"] = cleaned["age"] / 365.25
    cleaned = cleaned.drop(columns=["age"])

    valid_mask = (
        cleaned["height"].between(120, 220)
        & cleaned["weight"].between(30, 200)
        & cleaned["ap_hi"].between(80, 240)
        & cleaned["ap_lo"].between(40, 160)
        & (cleaned["ap_hi"] > cleaned["ap_lo"])
    )
    cleaned = cleaned.loc[valid_mask].copy()

    removal_summary = {
        "initial_rows": initial_rows,
        "rows_after_medical_rules": int(len(cleaned)),
        "rows_removed_by_medical_rules": int(initial_rows - len(cleaned)),
    }
    return cleaned, removal_summary


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    featured = df.copy()
    height_m = featured["height"] / 100.0
    featured["bmi"] = featured["weight"] / (height_m**2)
    featured["pulse_pressure"] = featured["ap_hi"] - featured["ap_lo"]
    featured["mean_arterial_pressure"] = (featured["ap_hi"] + 2 * featured["ap_lo"]) / 3.0
    featured["age_group"] = pd.cut(
        featured["age_years"],
        bins=[0, 40, 50, 60, 120],
        labels=[0, 1, 2, 3],
        include_lowest=True,
    ).astype(int)
    featured["bp_ratio"] = featured["ap_hi"] / featured["ap_lo"]
    return featured


def save_profile(profile: dict, cleaning_summary: dict) -> None:
    with (OUTPUT_DIR / "dataset_profile.json").open("w", encoding="utf-8") as fh:
        json.dump({"profile": profile, "cleaning_summary": cleaning_summary}, fh, indent=2)


def make_eda_plots(df: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(data=df, x="age_years", hue="cardio", bins=30, kde=True, ax=ax, stat="density", common_norm=False)
    ax.set_title("Age Distribution by Cardiovascular Outcome")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "age_distribution.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=df, x="cardio", y="pulse_pressure", ax=ax)
    ax.set_title("Pulse Pressure by Cardiovascular Outcome")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "pulse_pressure_boxplot.png", dpi=200)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.countplot(data=df, x="cholesterol", hue="cardio", ax=ax)
    ax.set_title("Cholesterol Levels by Cardiovascular Outcome")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "cholesterol_vs_cardio.png", dpi=200)
    plt.close(fig)

    corr_cols = [
        "age_years",
        "height",
        "weight",
        "ap_hi",
        "ap_lo",
        "bmi",
        "pulse_pressure",
        "mean_arterial_pressure",
        "cholesterol",
        "gluc",
        "smoke",
        "alco",
        "active",
        "cardio",
    ]
    corr = df[corr_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "correlation_heatmap.png", dpi=200)
    plt.close(fig)


def build_model_pipelines(feature_columns: list[str]) -> tuple[dict[str, Pipeline], list[str], list[str]]:
    scaled_features = [
        "age_years",
        "height",
        "weight",
        "ap_hi",
        "ap_lo",
        "bmi",
        "pulse_pressure",
        "mean_arterial_pressure",
        "bp_ratio",
    ]
    passthrough_features = [col for col in feature_columns if col not in scaled_features]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "scaled",
                Pipeline(
                    steps=[
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                scaled_features,
            ),
            (
                "passthrough",
                Pipeline(steps=[("imputer", SimpleImputer(strategy="most_frequent"))]),
                passthrough_features,
            ),
        ]
    )

    base_preprocessor = ColumnTransformer(
        transformers=[
            ("scaled", SimpleImputer(strategy="median"), scaled_features),
            ("passthrough", SimpleImputer(strategy="most_frequent"), passthrough_features),
        ]
    )

    models = {
        "Logistic Regression": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", LogisticRegression(max_iter=2000, random_state=42, solver="liblinear")),
            ]
        ),
        "Random Forest": Pipeline(
            steps=[
                ("preprocess", base_preprocessor),
                ("model", RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=1)),
            ]
        ),
        "Linear SVM": Pipeline(
            steps=[
                ("preprocess", preprocessor),
                ("model", LinearSVC(random_state=42, dual=False, max_iter=5000)),
            ]
        ),
        "Gradient Boosting": Pipeline(
            steps=[
                ("preprocess", base_preprocessor),
                ("model", GradientBoostingClassifier(random_state=42)),
            ]
        ),
    }
    return models, scaled_features, passthrough_features


def get_prediction_scores(pipeline: Pipeline, X: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    y_pred = pipeline.predict(X)
    if hasattr(pipeline, "predict_proba"):
        y_score = pipeline.predict_proba(X)[:, 1]
    else:
        y_score = pipeline.decision_function(X)
    return y_pred, y_score


def evaluate_models(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, dict], Pipeline, pd.DataFrame, pd.Series]:
    feature_columns = [col for col in df.columns if col != "cardio"]
    X = df[feature_columns]
    y = df["cardio"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    if len(X_train) > 25000:
        X_cv, _, y_cv, _ = train_test_split(
            X_train,
            y_train,
            train_size=25000,
            random_state=42,
            stratify=y_train,
        )
    else:
        X_cv, y_cv = X_train, y_train

    models, _, _ = build_model_pipelines(feature_columns)
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

    summary_rows = []
    detailed_results: dict[str, dict] = {}
    best_model_name = None
    best_model_auc = -1.0
    best_model_pipeline: Pipeline | None = None

    for name, pipeline in models.items():
        cv_result = cross_validate(
            pipeline,
            X_cv,
            y_cv,
            cv=cv,
            scoring=["accuracy", "precision", "recall", "f1", "roc_auc"],
            n_jobs=1,
        )
        pipeline.fit(X_train, y_train)
        y_pred, y_score = get_prediction_scores(pipeline, X_test)

        metrics = {
            "model": name,
            "cv_accuracy_mean": cv_result["test_accuracy"].mean(),
            "cv_precision_mean": cv_result["test_precision"].mean(),
            "cv_recall_mean": cv_result["test_recall"].mean(),
            "cv_f1_mean": cv_result["test_f1"].mean(),
            "cv_roc_auc_mean": cv_result["test_roc_auc"].mean(),
            "test_accuracy": accuracy_score(y_test, y_pred),
            "test_precision": precision_score(y_test, y_pred),
            "test_recall": recall_score(y_test, y_pred),
            "test_f1": f1_score(y_test, y_pred),
            "test_roc_auc": roc_auc_score(y_test, y_score),
        }
        summary_rows.append(metrics)
        fpr, tpr, _ = roc_curve(y_test, y_score)
        detailed_results[name] = {
            "metrics": metrics,
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
            "roc_curve": {"fpr": fpr.tolist(), "tpr": tpr.tolist()},
        }
        if metrics["test_roc_auc"] > best_model_auc:
            best_model_auc = metrics["test_roc_auc"]
            best_model_name = name
            best_model_pipeline = pipeline

    assert best_model_pipeline is not None
    summary_df = pd.DataFrame(summary_rows).sort_values(by="test_roc_auc", ascending=False)
    detailed_results["best_model"] = {"name": best_model_name, "test_roc_auc": best_model_auc}
    return summary_df, detailed_results, best_model_pipeline, X_test, y_test


def save_model_results(summary_df: pd.DataFrame, detailed_results: dict[str, dict]) -> None:
    summary_df.to_csv(TABLES_DIR / "model_comparison.csv", index=False)
    with (MODELS_DIR / "detailed_model_results.json").open("w", encoding="utf-8") as fh:
        json.dump(detailed_results, fh, indent=2)


def plot_roc_curves(detailed_results: dict[str, dict]) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))
    for model_name, payload in detailed_results.items():
        if model_name == "best_model":
            continue
        roc = payload["roc_curve"]
        ax.plot(roc["fpr"], roc["tpr"], label=f"{model_name} (AUC={payload['metrics']['test_roc_auc']:.3f})")
    ax.plot([0, 1], [0, 1], linestyle="--", color="black", linewidth=1)
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.set_title("ROC Curves on Kaggle Cardiovascular Dataset")
    ax.legend()
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "roc_curves.png", dpi=200)
    plt.close(fig)


def save_feature_importance(best_model: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
    importances = permutation_importance(
        best_model,
        X_test,
        y_test,
        n_repeats=5,
        random_state=42,
        scoring="roc_auc",
        n_jobs=1,
    )
    importance_df = pd.DataFrame(
        {
            "feature": X_test.columns,
            "importance_mean": importances.importances_mean,
            "importance_std": importances.importances_std,
        }
    ).sort_values(by="importance_mean", ascending=False)
    importance_df.to_csv(TABLES_DIR / "feature_importance.csv", index=False)

    top_features = importance_df.head(12).iloc[::-1]
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_features["feature"], top_features["importance_mean"], xerr=top_features["importance_std"])
    ax.set_title("Permutation Feature Importance")
    ax.set_xlabel("Mean ROC-AUC Importance")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "feature_importance.png", dpi=200)
    plt.close(fig)
    return importance_df


def save_cleaned_dataset(df: pd.DataFrame) -> None:
    df.to_csv(OUTPUT_DIR / "cardio_train_cleaned.csv", index=False)


def write_run_summary(profile: dict, cleaning_summary: dict, model_summary: pd.DataFrame, importance_df: pd.DataFrame) -> None:
    best_row = model_summary.iloc[0]
    top_features = importance_df.head(5)["feature"].tolist()
    lines = [
        "AI-Driven Early Prediction of Cardiovascular Disease",
        "",
        f"Input dataset: {DATASET_PATH}",
        f"Original shape: {tuple(profile['shape'])}",
        f"Rows after cleaning: {cleaning_summary['rows_after_medical_rules']}",
        f"Rows removed by medical rules: {cleaning_summary['rows_removed_by_medical_rules']}",
        "",
        "Top model on test ROC-AUC:",
        f"- {best_row['model']}",
        f"- Test Accuracy: {best_row['test_accuracy']:.4f}",
        f"- Test Precision: {best_row['test_precision']:.4f}",
        f"- Test Recall: {best_row['test_recall']:.4f}",
        f"- Test F1: {best_row['test_f1']:.4f}",
        f"- Test ROC-AUC: {best_row['test_roc_auc']:.4f}",
        "",
        "Top permutation-importance features:",
    ]
    lines.extend(f"- {feature}" for feature in top_features)
    (OUTPUT_DIR / "run_summary.txt").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_dirs()

    print("Step 1: Loading dataset")
    df = load_data()
    profile = build_profile(df)
    print(f"Loaded dataset with shape {df.shape}")
    print(f"Invalid blood pressure pairs: {profile['invalid_value_counts']['ap_hi_less_than_ap_lo']}")

    print("Step 2: Cleaning data")
    cleaned_df, cleaning_summary = clean_data(df)
    print(cleaning_summary)

    print("Step 3: Feature engineering")
    featured_df = engineer_features(cleaned_df)
    save_cleaned_dataset(featured_df)
    print(f"Feature-engineered dataset shape: {featured_df.shape}")

    print("Step 4: Saving dataset profile and EDA plots")
    save_profile(profile, cleaning_summary)
    make_eda_plots(featured_df)

    print("Step 5: Training and evaluating models")
    model_summary, detailed_results, best_model, X_test, y_test = evaluate_models(featured_df)
    save_model_results(model_summary, detailed_results)
    plot_roc_curves(detailed_results)
    print(model_summary[["model", "test_accuracy", "test_f1", "test_roc_auc"]].to_string(index=False))

    print("Step 6: Feature importance")
    importance_df = save_feature_importance(best_model, X_test, y_test)
    write_run_summary(profile, cleaning_summary, model_summary, importance_df)
    print(importance_df.head(10).to_string(index=False))

    print(f"Finished. Outputs saved in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
