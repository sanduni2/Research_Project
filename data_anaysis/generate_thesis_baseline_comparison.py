"""
Generate thesis-ready baseline comparison tables and graphs.

This script consolidates model artifacts already available in the project and
exports a clean set of baseline visuals for the final thesis.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parent
METRICS_DIR = ROOT / "results" / "metrics"
VIS_OUT_DIR = ROOT / "results" / "visualizations" / "thesis_baseline"
TAB_OUT_DIR = ROOT / "results" / "metrics" / "thesis_baseline"
MODELS_DIR = ROOT / "models"


sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["savefig.dpi"] = 300


def _ensure_dirs() -> None:
    VIS_OUT_DIR.mkdir(parents=True, exist_ok=True)
    TAB_OUT_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_plot(fig: plt.Figure, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(VIS_OUT_DIR / filename, bbox_inches="tight")
    plt.close(fig)


def _plot_class_distribution() -> None:
    summary_path = METRICS_DIR / "dataset_summary.csv"
    if not summary_path.exists():
        return

    df = pd.read_csv(summary_path)
    # Convert percentage strings (e.g., 26.67%) to float.
    df["PercentageValue"] = (
        df["Percentage"].astype(str).str.replace("%", "", regex=False).astype(float)
    )

    df.to_csv(TAB_OUT_DIR / "dataset_class_distribution.csv", index=False)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(df["Feed Level"], df["Image Count"], color=["#4C72B0", "#DD8452", "#55A868", "#C44E52"])
    ax.set_title("Dataset Class Distribution")
    ax.set_xlabel("Feed Level")
    ax.set_ylabel("Image Count")

    for bar, pct in zip(bars, df["PercentageValue"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 3,
            f"{int(bar.get_height())} ({pct:.2f}%)",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    _save_plot(fig, "baseline_01_dataset_class_distribution.png")


def _load_classification_metrics() -> pd.DataFrame:
    custom = _read_json(METRICS_DIR / "custom_cnn_metrics.json")
    resnet = _read_json(METRICS_DIR / "resnet50_metrics.json")

    rows: List[Dict[str, Any]] = [
        {
            "Model": "Custom CNN",
            "Accuracy": custom["validation_metrics"]["accuracy"],
            "Precision": custom["validation_metrics"]["precision"],
            "Recall": custom["validation_metrics"]["recall"],
            "F1Score": custom["validation_metrics"]["f1_score"],
            "Loss": custom["validation_metrics"]["loss"],
            "Epochs": custom["epochs_trained"],
            "TrainingTimeSec": custom["training_time_seconds"],
            "TotalParams": custom["total_parameters"],
            "TrainableParams": custom["trainable_parameters"],
        },
        {
            "Model": "ResNet50",
            "Accuracy": resnet["overall_metrics"]["accuracy"],
            "Precision": resnet["overall_metrics"]["precision"],
            "Recall": resnet["overall_metrics"]["recall"],
            "F1Score": resnet["overall_metrics"]["f1_score"],
            "Loss": resnet["overall_metrics"]["loss"],
            "Epochs": resnet["total_epochs"],
            "TrainingTimeSec": resnet["training_time_seconds"],
            "TotalParams": resnet["model_parameters"]["total_params"],
            "TrainableParams": resnet["model_parameters"]["trainable_params"],
        },
    ]

    df = pd.DataFrame(rows)
    df["TrainingTimeMin"] = df["TrainingTimeSec"] / 60.0
    df["TotalParamsM"] = df["TotalParams"] / 1_000_000.0
    df.to_csv(TAB_OUT_DIR / "classification_overall_baseline.csv", index=False)
    return df


def _plot_classification_overall(df: pd.DataFrame) -> None:
    metric_cols = ["Accuracy", "Precision", "Recall", "F1Score"]
    long_df = df[["Model"] + metric_cols].melt(
        id_vars="Model", var_name="Metric", value_name="Score"
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=long_df, x="Metric", y="Score", hue="Model", ax=ax)
    ax.set_title("Baseline Comparison: Overall Classification Performance")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_xlabel("Metric")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=9, padding=2)

    _save_plot(fig, "baseline_02_classification_overall_metrics.png")


def _plot_efficiency_tradeoff(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 6))

    scatter = ax.scatter(
        df["TrainingTimeMin"],
        df["F1Score"],
        s=df["TotalParamsM"] * 18,
        c=["#4C72B0", "#C44E52"],
        alpha=0.8,
        edgecolors="black",
    )
    _ = scatter

    for _, row in df.iterrows():
        ax.annotate(
            row["Model"],
            (row["TrainingTimeMin"], row["F1Score"]),
            textcoords="offset points",
            xytext=(8, 6),
            fontsize=10,
        )

    ax.set_title("Efficiency Trade-off: F1 vs Training Time")
    ax.set_xlabel("Training Time (minutes)")
    ax.set_ylabel("F1 Score")
    ax.set_ylim(0, 1.05)

    _save_plot(fig, "baseline_03_classification_efficiency_tradeoff.png")


def _load_per_class_metrics() -> pd.DataFrame:
    custom = _read_json(METRICS_DIR / "custom_cnn_metrics.json")["per_class_metrics"]
    resnet = _read_json(METRICS_DIR / "resnet50_metrics.json")["per_class_metrics"]

    class_keys = ["0_percent", "25_percent", "50_percent", "100_percent"]
    rows: List[Dict[str, Any]] = []

    for cls in class_keys:
        rows.append(
            {
                "Model": "Custom CNN",
                "Class": cls,
                "Precision": custom[cls]["precision"],
                "Recall": custom[cls]["recall"],
                "F1Score": custom[cls]["f1-score"],
                "Support": custom[cls]["support"],
            }
        )
        rows.append(
            {
                "Model": "ResNet50",
                "Class": cls,
                "Precision": resnet[cls]["precision"],
                "Recall": resnet[cls]["recall"],
                "F1Score": resnet[cls]["f1_score"],
                "Support": resnet[cls]["support"],
            }
        )

    df = pd.DataFrame(rows)
    df["ClassLabel"] = df["Class"].str.replace("_", " ").str.title()
    df.to_csv(TAB_OUT_DIR / "classification_per_class_baseline.csv", index=False)
    return df


def _plot_per_class(df: pd.DataFrame, metric: str, out_name: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(11, 6))
    sns.barplot(data=df, x="ClassLabel", y=metric, hue="Model", ax=ax)
    ax.set_title(title)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(metric)
    ax.set_xlabel("Feed Level Class")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", fontsize=9, padding=2)

    _save_plot(fig, out_name)


def _load_chickweight_regression() -> pd.DataFrame:
    data = _read_json(METRICS_DIR / "chickweight_model_metrics.json")
    rows: List[Dict[str, Any]] = []

    for model in ["Linear Regression", "Decision Tree", "Random Forest"]:
        rows.append(
            {
                "Model": model,
                "R2": data[model]["R2_Score"],
                "RMSE": data[model]["RMSE"],
                "MAE": data[model]["MAE"],
                "MAPE": data[model]["MAPE"],
                "IsBest": model == data.get("best_model"),
            }
        )

    df = pd.DataFrame(rows)
    df.to_csv(TAB_OUT_DIR / "regression_chickweight_baseline.csv", index=False)
    return df


def _plot_regression_r2(df: pd.DataFrame) -> None:
    colors = ["#C44E52" if is_best else "#4C72B0" for is_best in df["IsBest"]]
    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.bar(df["Model"], df["R2"], color=colors)
    ax.set_title("Baseline Comparison: Weight Regression (R2)")
    ax.set_ylabel("R2 Score")
    ax.set_xlabel("Model")
    ax.set_ylim(0, max(df["R2"]) + 0.1)

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.005,
            f"{bar.get_height():.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    _save_plot(fig, "baseline_06_regression_chickweight_r2.png")


def _plot_regression_errors(df: pd.DataFrame) -> None:
    long_df = df.melt(
        id_vars=["Model", "IsBest"],
        value_vars=["RMSE", "MAE", "MAPE"],
        var_name="Metric",
        value_name="Value",
    )

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=long_df, x="Metric", y="Value", hue="Model", ax=ax)
    ax.set_title("Baseline Comparison: Regression Error Metrics")
    ax.set_xlabel("Error Metric")
    ax.set_ylabel("Value")

    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", fontsize=9, padding=2)

    _save_plot(fig, "baseline_07_regression_chickweight_errors.png")


def _broiler_vs_chickweight_snapshot(chick_df: pd.DataFrame) -> None:
    meta_path = MODELS_DIR / "broiler_weight_metadata.json"
    if not meta_path.exists():
        return

    broiler = _read_json(meta_path)
    chick_best = chick_df.sort_values("R2", ascending=False).iloc[0]

    snapshot = pd.DataFrame(
        [
            {
                "ModelVariant": "Chickweight Best Baseline",
                "Model": chick_best["Model"],
                "R2": chick_best["R2"],
                "RMSE": chick_best["RMSE"],
                "MAE": chick_best["MAE"],
                "MAPE": chick_best["MAPE"],
                "AgeRange": "0-21 days",
            },
            {
                "ModelVariant": "Broiler Extended Model",
                "Model": broiler.get("model_name", "Unknown"),
                "R2": broiler.get("r2_score_test"),
                "RMSE": broiler.get("rmse"),
                "MAE": broiler.get("mae"),
                "MAPE": broiler.get("mape"),
                "AgeRange": broiler.get("age_range", "Unknown"),
            },
        ]
    )

    snapshot.to_csv(TAB_OUT_DIR / "regression_broiler_vs_chickweight_snapshot.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(snapshot["ModelVariant"], snapshot["R2"], color=["#4C72B0", "#55A868"])
    ax.set_title("R2 Snapshot: Chickweight Baseline vs Broiler Extended Model")
    ax.set_ylabel("R2 Score")
    ax.set_ylim(0, 1.05)

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.01,
            f"{bar.get_height():.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    _save_plot(fig, "baseline_08_regression_r2_snapshot_broiler_vs_chickweight.png")


def _feed_regression_consistency_check() -> None:
    metrics_path = METRICS_DIR / "poultry_feed_model_metrics.json"
    metadata_path = MODELS_DIR / "feed_prediction_metadata.json"

    if not metrics_path.exists() or not metadata_path.exists():
        return

    metrics = _read_json(metrics_path)
    metadata = _read_json(metadata_path)

    rows = [
        {
            "Source": "results/metrics/poultry_feed_model_metrics.json",
            "Model": metrics.get("best_model", "Linear Regression"),
            "R2": metrics["Linear Regression"]["R2_Score"],
            "RMSE": metrics["Linear Regression"]["RMSE"],
            "MAE": metrics["Linear Regression"]["MAE"],
            "Notes": "Best from dataset-level baseline file",
        },
        {
            "Source": "models/feed_prediction_metadata.json",
            "Model": metadata.get("model_name", "Linear Regression"),
            "R2": metadata.get("r2_score"),
            "RMSE": metadata.get("rmse"),
            "MAE": metadata.get("mae"),
            "Notes": "Model artifact metadata snapshot",
        },
    ]

    df = pd.DataFrame(rows)
    df.to_csv(TAB_OUT_DIR / "feed_regression_consistency_check.csv", index=False)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(df["Source"], df["R2"], color=["#DD8452", "#8172B2"])
    ax.set_title("Feed Regression Consistency Check (R2)")
    ax.set_ylabel("R2 Score")
    ax.set_xlabel("Metric Source")
    ax.tick_params(axis="x", rotation=18)

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + (0.01 if bar.get_height() >= 0 else 0.03),
            f"{bar.get_height():.4f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    _save_plot(fig, "baseline_09_feed_regression_consistency_check.png")


def _write_summary_report(cls_df: pd.DataFrame, reg_df: pd.DataFrame) -> None:
    best_cls = cls_df.sort_values("F1Score", ascending=False).iloc[0]
    best_reg = reg_df.sort_values("R2", ascending=False).iloc[0]

    report = []
    report.append("# Thesis Baseline Comparison Summary")
    report.append("")
    report.append("## Classification (Feed Image)")
    report.append(
        f"- Best model by F1Score: {best_cls['Model']} (F1={best_cls['F1Score']:.4f}, Accuracy={best_cls['Accuracy']:.4f})"
    )
    report.append(
        "- Inputs: custom_cnn_metrics.json and resnet50_metrics.json"
    )
    report.append("")
    report.append("## Regression (Chickweight Baseline)")
    report.append(
        f"- Best model by R2: {best_reg['Model']} (R2={best_reg['R2']:.4f}, RMSE={best_reg['RMSE']:.2f})"
    )
    report.append("- Input: chickweight_model_metrics.json")
    report.append("")
    report.append("## Notes")
    report.append(
        "- Feed regression consistency check chart is included because two existing files report different R2 values."
    )
    report.append(
        "- If you add MobileNetV2 metrics later, extend this script to include that baseline in the same charts."
    )
    report.append("")
    report.append("## Generated Outputs")
    report.append(f"- Graphs: {VIS_OUT_DIR}")
    report.append(f"- Tables: {TAB_OUT_DIR}")

    (TAB_OUT_DIR / "README_thesis_baseline_summary.md").write_text(
        "\n".join(report), encoding="utf-8"
    )


def main() -> None:
    _ensure_dirs()

    _plot_class_distribution()

    cls_overall = _load_classification_metrics()
    _plot_classification_overall(cls_overall)
    _plot_efficiency_tradeoff(cls_overall)

    cls_per_class = _load_per_class_metrics()
    _plot_per_class(
        cls_per_class,
        metric="Recall",
        out_name="baseline_04_classification_per_class_recall.png",
        title="Baseline Comparison: Per-Class Recall",
    )
    _plot_per_class(
        cls_per_class,
        metric="F1Score",
        out_name="baseline_05_classification_per_class_f1.png",
        title="Baseline Comparison: Per-Class F1 Score",
    )

    reg_chick = _load_chickweight_regression()
    _plot_regression_r2(reg_chick)
    _plot_regression_errors(reg_chick)

    _broiler_vs_chickweight_snapshot(reg_chick)
    _feed_regression_consistency_check()

    _write_summary_report(cls_overall, reg_chick)

    print("Thesis baseline comparison generated successfully.")
    print(f"Graphs: {VIS_OUT_DIR}")
    print(f"Tables: {TAB_OUT_DIR}")


if __name__ == "__main__":
    main()
