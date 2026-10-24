"""
Generate statistical significance outputs for thesis model selection.

Includes:
- Classification comparison on a shared held-out split with McNemar tests.
- Regression comparison with repeated K-fold and paired permutation tests.
- Thesis-ready plots and tables.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import (
    accuracy_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_fscore_support,
    r2_score,
)
from sklearn.model_selection import RepeatedKFold, train_test_split
from sklearn.tree import DecisionTreeRegressor
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
METRIC_OUT = ROOT / "results" / "metrics" / "thesis_baseline"
VIZ_OUT = ROOT / "results" / "visualizations" / "thesis_baseline"

CLASS_FOLDERS = ["0_percent", "25_percent", "50_percent", "100_percent"]
IMG_SIZE = (224, 224)


sns.set_theme(style="whitegrid", context="talk")
plt.rcParams["figure.dpi"] = 130
plt.rcParams["savefig.dpi"] = 300


def ensure_output_dirs() -> None:
    METRIC_OUT.mkdir(parents=True, exist_ok=True)
    VIZ_OUT.mkdir(parents=True, exist_ok=True)


def wilson_ci(k: int, n: int, z: float = 1.96) -> Tuple[float, float]:
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    denom = 1 + (z ** 2) / n
    center = (p + (z ** 2) / (2 * n)) / denom
    half = (
        z
        * math.sqrt((p * (1 - p) / n) + ((z ** 2) / (4 * (n ** 2))))
        / denom
    )
    return center - half, center + half


def mcnemar_test(y_true: np.ndarray, pred_a: np.ndarray, pred_b: np.ndarray) -> Dict[str, float]:
    a_correct = pred_a == y_true
    b_correct = pred_b == y_true

    b = int(np.sum(a_correct & ~b_correct))
    c = int(np.sum(~a_correct & b_correct))

    if b + c == 0:
        return {
            "b_a_correct_b_wrong": float(b),
            "c_a_wrong_b_correct": float(c),
            "chi2": 0.0,
            "p_value": 1.0,
        }

    chi2 = ((abs(b - c) - 1) ** 2) / (b + c)
    # For chi-square with 1 degree of freedom, survival fn:
    p_value = math.erfc(math.sqrt(chi2 / 2.0))

    return {
        "b_a_correct_b_wrong": float(b),
        "c_a_wrong_b_correct": float(c),
        "chi2": float(chi2),
        "p_value": float(p_value),
    }


def paired_permutation_test(
    x: np.ndarray,
    y: np.ndarray,
    n_iter: int = 10000,
    seed: int = 42,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    d = x - y
    observed = float(np.mean(d))

    if np.allclose(d, 0):
        return {"mean_diff": observed, "p_value": 1.0}

    counts = 0
    for _ in range(n_iter):
        signs = rng.choice([-1.0, 1.0], size=d.shape[0])
        perm_stat = np.mean(d * signs)
        if abs(perm_stat) >= abs(observed):
            counts += 1

    p_value = (counts + 1) / (n_iter + 1)
    return {"mean_diff": observed, "p_value": float(p_value)}


def load_classification_dataset() -> Tuple[np.ndarray, np.ndarray, List[str]]:
    image_paths: List[Path] = []
    labels: List[int] = []

    for label_idx, folder in enumerate(CLASS_FOLDERS):
        folder_path = DATA_DIR / folder
        if not folder_path.exists():
            continue
        for p in sorted(folder_path.iterdir()):
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".bmp", ".webp"}:
                image_paths.append(p)
                labels.append(label_idx)

    if not image_paths:
        raise RuntimeError("No classification images found in data folders.")

    return np.array(image_paths), np.array(labels), CLASS_FOLDERS


def load_and_preprocess_images(paths: np.ndarray) -> np.ndarray:
    x_list: List[np.ndarray] = []
    for p in paths:
        img = keras_image.load_img(str(p), target_size=IMG_SIZE)
        arr = keras_image.img_to_array(img)
        x_list.append(arr)
    x = np.array(x_list, dtype=np.float32) / 255.0
    return x


def discover_classification_models() -> Dict[str, Path]:
    candidates = {
        "Custom CNN": MODELS_DIR / "custom_cnn" / "best_model.h5",
        "ResNet50": MODELS_DIR / "resnet50" / "best_model.h5",
        "ResNet50 Improved": MODELS_DIR / "resnet50" / "best_model_improved.h5",
    }
    return {name: path for name, path in candidates.items() if path.exists()}


def run_classification_significance() -> Tuple[pd.DataFrame, pd.DataFrame]:
    paths, labels, class_names = load_classification_dataset()

    p_train, p_test, y_train, y_test = train_test_split(
        paths,
        labels,
        test_size=0.2,
        random_state=42,
        stratify=labels,
    )
    _ = (p_train, y_train)

    x_test = load_and_preprocess_images(p_test)

    model_paths = discover_classification_models()
    if len(model_paths) < 2:
        raise RuntimeError("Need at least 2 classification models for significance testing.")

    y_preds: Dict[str, np.ndarray] = {}
    metrics_rows: List[Dict[str, float]] = []

    for model_name, model_path in model_paths.items():
        model = load_model(str(model_path), compile=False)
        probs = model.predict(x_test, verbose=0)
        pred = np.argmax(probs, axis=1)
        y_preds[model_name] = pred

        acc = accuracy_score(y_test, pred)
        precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
            y_test,
            pred,
            average="macro",
            zero_division=0,
        )

        per_prec, per_rec, per_f1, per_sup = precision_recall_fscore_support(
            y_test,
            pred,
            average=None,
            labels=list(range(len(class_names))),
            zero_division=0,
        )

        k = int(np.sum(pred == y_test))
        ci_low, ci_high = wilson_ci(k, len(y_test))

        row = {
            "Model": model_name,
            "Accuracy": float(acc),
            "AccuracyCI95Low": float(ci_low),
            "AccuracyCI95High": float(ci_high),
            "MacroPrecision": float(precision_macro),
            "MacroRecall": float(recall_macro),
            "MacroF1": float(f1_macro),
            "NTest": int(len(y_test)),
        }

        for i, cls in enumerate(class_names):
            row[f"Recall_{cls}"] = float(per_rec[i])
            row[f"F1_{cls}"] = float(per_f1[i])
            row[f"Support_{cls}"] = int(per_sup[i])

        metrics_rows.append(row)

    metrics_df = pd.DataFrame(metrics_rows).sort_values("MacroF1", ascending=False)
    metrics_df.to_csv(METRIC_OUT / "significance_classification_metrics.csv", index=False)

    pair_rows: List[Dict[str, float]] = []
    for a, b in itertools.combinations(metrics_df["Model"].tolist(), 2):
        result = mcnemar_test(y_test, y_preds[a], y_preds[b])
        pair_rows.append(
            {
                "ModelA": a,
                "ModelB": b,
                **result,
            }
        )

    pair_df = pd.DataFrame(pair_rows)
    pair_df.to_csv(METRIC_OUT / "significance_classification_mcnemar.csv", index=False)

    return metrics_df, pair_df


def run_regression_significance() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DATA_DIR / "chickweight.csv")

    df = df.copy()
    df["Time_squared"] = df["Time"] ** 2
    df["Time_Diet_interaction"] = df["Time"] * df["Diet"]
    dummies = pd.get_dummies(df["Diet"], prefix="Diet", drop_first=False)
    df = pd.concat([df, dummies], axis=1)

    feature_cols = [
        "Time",
        "Diet",
        "Time_squared",
        "Time_Diet_interaction",
        "Diet_1",
        "Diet_2",
        "Diet_3",
        "Diet_4",
    ]

    x = df[feature_cols].values
    y = df["weight"].values

    rkf = RepeatedKFold(n_splits=5, n_repeats=5, random_state=42)

    models = {
        "Linear Regression": LinearRegression(),
        "Decision Tree": DecisionTreeRegressor(random_state=42, max_depth=10),
        "Random Forest": RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            random_state=42,
            n_jobs=-1,
        ),
    }

    fold_rows: List[Dict[str, float]] = []

    for fold_idx, (tr, te) in enumerate(rkf.split(x), start=1):
        x_train, x_test = x[tr], x[te]
        y_train, y_test = y[tr], y[te]

        for model_name, model in models.items():
            if model_name == "Linear Regression":
                scaler = StandardScaler()
                x_train_fit = scaler.fit_transform(x_train)
                x_test_fit = scaler.transform(x_test)
            else:
                x_train_fit = x_train
                x_test_fit = x_test

            model.fit(x_train_fit, y_train)
            pred = model.predict(x_test_fit)

            fold_rows.append(
                {
                    "Fold": fold_idx,
                    "Model": model_name,
                    "R2": float(r2_score(y_test, pred)),
                    "RMSE": float(math.sqrt(mean_squared_error(y_test, pred))),
                    "MAE": float(mean_absolute_error(y_test, pred)),
                }
            )

    fold_df = pd.DataFrame(fold_rows)
    fold_df.to_csv(METRIC_OUT / "significance_regression_fold_scores.csv", index=False)

    summary_df = (
        fold_df.groupby("Model")[["R2", "RMSE", "MAE"]]
        .agg(["mean", "std"])
        .reset_index()
    )
    summary_df.columns = [
        "Model",
        "R2_mean",
        "R2_std",
        "RMSE_mean",
        "RMSE_std",
        "MAE_mean",
        "MAE_std",
    ]
    summary_df = summary_df.sort_values("R2_mean", ascending=False)
    summary_df.to_csv(METRIC_OUT / "significance_regression_summary.csv", index=False)

    pair_rows: List[Dict[str, float]] = []
    model_names = summary_df["Model"].tolist()

    for a, b in itertools.combinations(model_names, 2):
        a_scores = fold_df.loc[fold_df["Model"] == a, "R2"].values
        b_scores = fold_df.loc[fold_df["Model"] == b, "R2"].values
        test = paired_permutation_test(a_scores, b_scores)

        pair_rows.append(
            {
                "ModelA": a,
                "ModelB": b,
                "Metric": "R2",
                "MeanDiff_A_minus_B": test["mean_diff"],
                "PValue": test["p_value"],
            }
        )

    pair_df = pd.DataFrame(pair_rows)
    pair_df.to_csv(METRIC_OUT / "significance_regression_pairwise_permutation.csv", index=False)

    return fold_df, summary_df, pair_df


def plot_classification_significance(metrics_df: pd.DataFrame, pair_df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))

    x = np.arange(len(metrics_df))
    y = metrics_df["Accuracy"].values
    yerr_low = y - metrics_df["AccuracyCI95Low"].values
    yerr_high = metrics_df["AccuracyCI95High"].values - y

    bars = ax.bar(x, y, color="#4C72B0", alpha=0.85)
    ax.errorbar(
        x,
        y,
        yerr=[yerr_low, yerr_high],
        fmt="none",
        ecolor="black",
        capsize=5,
        linewidth=1.5,
    )

    ax.set_xticks(x)
    ax.set_xticklabels(metrics_df["Model"], rotation=15)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Accuracy")
    ax.set_title("Classification Accuracy with 95% Wilson CI")

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.012,
            f"{bar.get_height():.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    fig.tight_layout()
    fig.savefig(VIZ_OUT / "significance_01_classification_accuracy_ci.png", bbox_inches="tight")
    plt.close(fig)

    long_df = metrics_df[["Model", "MacroPrecision", "MacroRecall", "MacroF1"]].melt(
        id_vars="Model", var_name="Metric", value_name="Score"
    )

    fig2, ax2 = plt.subplots(figsize=(10, 6))
    sns.barplot(data=long_df, x="Metric", y="Score", hue="Model", ax=ax2)
    ax2.set_ylim(0, 1.05)
    ax2.set_title("Classification Macro Metrics Comparison")

    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.3f", fontsize=9, padding=2)

    fig2.tight_layout()
    fig2.savefig(VIZ_OUT / "significance_02_classification_macro_metrics.png", bbox_inches="tight")
    plt.close(fig2)

    if not pair_df.empty:
        models = sorted(set(pair_df["ModelA"]).union(set(pair_df["ModelB"])))
        mat = pd.DataFrame(np.nan, index=models, columns=models)
        np.fill_diagonal(mat.values, 0.0)

        for _, row in pair_df.iterrows():
            mat.loc[row["ModelA"], row["ModelB"]] = row["p_value"]
            mat.loc[row["ModelB"], row["ModelA"]] = row["p_value"]

        fig3, ax3 = plt.subplots(figsize=(8, 6))
        sns.heatmap(mat, annot=True, fmt=".4f", cmap="YlGnBu_r", ax=ax3)
        ax3.set_title("McNemar Pairwise P-values (Classification)")
        fig3.tight_layout()
        fig3.savefig(VIZ_OUT / "significance_03_classification_mcnemar_pvalues.png", bbox_inches="tight")
        plt.close(fig3)


def plot_regression_significance(
    fold_df: pd.DataFrame,
    summary_df: pd.DataFrame,
    pair_df: pd.DataFrame,
) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=fold_df, x="Model", y="R2", ax=ax)
    sns.stripplot(data=fold_df, x="Model", y="R2", color="black", alpha=0.25, size=3, ax=ax)
    ax.set_title("Repeated K-Fold R2 Distribution by Regression Model")
    ax.set_ylabel("R2 Score")
    ax.set_xlabel("Model")
    fig.tight_layout()
    fig.savefig(VIZ_OUT / "significance_04_regression_r2_distribution.png", bbox_inches="tight")
    plt.close(fig)

    long_df = summary_df.melt(
        id_vars="Model",
        value_vars=["RMSE_mean", "MAE_mean"],
        var_name="Metric",
        value_name="Value",
    )
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    sns.barplot(data=long_df, x="Metric", y="Value", hue="Model", ax=ax2)
    ax2.set_title("Regression Mean Error Metrics (Repeated K-Fold)")

    for container in ax2.containers:
        ax2.bar_label(container, fmt="%.2f", fontsize=9, padding=2)

    fig2.tight_layout()
    fig2.savefig(VIZ_OUT / "significance_05_regression_error_means.png", bbox_inches="tight")
    plt.close(fig2)

    if not pair_df.empty:
        models = sorted(set(pair_df["ModelA"]).union(set(pair_df["ModelB"])))
        mat = pd.DataFrame(np.nan, index=models, columns=models)
        np.fill_diagonal(mat.values, 0.0)

        for _, row in pair_df.iterrows():
            mat.loc[row["ModelA"], row["ModelB"]] = row["PValue"]
            mat.loc[row["ModelB"], row["ModelA"]] = row["PValue"]

        fig3, ax3 = plt.subplots(figsize=(8, 6))
        sns.heatmap(mat, annot=True, fmt=".4f", cmap="YlOrBr_r", ax=ax3)
        ax3.set_title("Pairwise Permutation P-values (Regression R2)")
        fig3.tight_layout()
        fig3.savefig(VIZ_OUT / "significance_06_regression_pairwise_pvalues.png", bbox_inches="tight")
        plt.close(fig3)


def plot_full_graph_sheet_with_metric_direction() -> None:
    """Create one thesis-ready image containing all major graphs and metric direction notes."""
    chart_specs = [
        (
            "significance_01_classification_accuracy_ci.png",
            "Classification Accuracy + 95% CI (Higher is better)",
        ),
        (
            "significance_02_classification_macro_metrics.png",
            "Macro Precision / Recall / F1 (Higher is better)",
        ),
        (
            "significance_03_classification_mcnemar_pvalues.png",
            "McNemar Pairwise P-values (Lower is better; p < 0.05)",
        ),
        (
            "significance_04_regression_r2_distribution.png",
            "Regression R2 Distribution (Higher is better)",
        ),
        (
            "significance_05_regression_error_means.png",
            "Regression Errors RMSE/MAE (Lower is better)",
        ),
        (
            "significance_06_regression_pairwise_pvalues.png",
            "Regression Pairwise P-values (Lower is better; p < 0.05)",
        ),
    ]

    fig, axes = plt.subplots(3, 2, figsize=(22, 16))
    axes = axes.flatten()

    for ax, (filename, title) in zip(axes, chart_specs):
        img_path = VIZ_OUT / filename
        if img_path.exists():
            img = mpimg.imread(img_path)
            ax.imshow(img)
            ax.set_title(title, fontsize=12, pad=8)
            ax.axis("off")
        else:
            ax.axis("off")
            ax.text(
                0.5,
                0.5,
                f"Missing chart:\n{filename}",
                ha="center",
                va="center",
                fontsize=11,
            )

    fig.suptitle(
        "Full Baseline Significance Graph Sheet with Metric Direction Guide",
        fontsize=18,
        fontweight="bold",
        y=0.995,
    )

    fig.text(
        0.5,
        0.01,
        "Direction rule: Higher is better for Accuracy/Precision/Recall/F1/R2. "
        "Lower is better for RMSE/MAE and for p-values (stronger evidence when p < 0.05).",
        ha="center",
        va="bottom",
        fontsize=12,
    )

    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    fig.savefig(
        VIZ_OUT / "significance_00_full_graphs_with_metric_direction.png",
        bbox_inches="tight",
    )
    plt.close(fig)


def write_summary(
    cls_metrics: pd.DataFrame,
    cls_pairs: pd.DataFrame,
    reg_summary: pd.DataFrame,
    reg_pairs: pd.DataFrame,
) -> None:
    cls_best = cls_metrics.sort_values("MacroF1", ascending=False).iloc[0]
    reg_best = reg_summary.sort_values("R2_mean", ascending=False).iloc[0]

    lines: List[str] = []
    lines.append("# Statistical Significance Summary")
    lines.append("")
    lines.append("## Classification")
    lines.append(
        f"- Best by MacroF1: {cls_best['Model']} (Accuracy={cls_best['Accuracy']:.4f}, MacroF1={cls_best['MacroF1']:.4f})"
    )
    lines.append("- Pairwise significance: see significance_classification_mcnemar.csv")
    if not cls_pairs.empty:
        sig_rows = cls_pairs[cls_pairs["p_value"] < 0.05]
        lines.append(f"- Significant pairwise differences (p < 0.05): {len(sig_rows)}")

    lines.append("")
    lines.append("## Regression")
    lines.append(
        f"- Best by mean R2 (Repeated K-Fold): {reg_best['Model']} (R2_mean={reg_best['R2_mean']:.4f})"
    )
    lines.append("- Pairwise significance: see significance_regression_pairwise_permutation.csv")
    if not reg_pairs.empty:
        sig_rows_r = reg_pairs[reg_pairs["PValue"] < 0.05]
        lines.append(f"- Significant pairwise differences (p < 0.05): {len(sig_rows_r)}")

    lines.append("")
    lines.append("## Outputs")
    lines.append(f"- Metrics: {METRIC_OUT}")
    lines.append(f"- Visuals: {VIZ_OUT}")

    (METRIC_OUT / "README_significance_summary.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_output_dirs()

    cls_metrics, cls_pairs = run_classification_significance()
    fold_df, reg_summary, reg_pairs = run_regression_significance()

    plot_classification_significance(cls_metrics, cls_pairs)
    plot_regression_significance(fold_df, reg_summary, reg_pairs)
    plot_full_graph_sheet_with_metric_direction()

    write_summary(cls_metrics, cls_pairs, reg_summary, reg_pairs)

    print("Significance testing outputs generated successfully.")
    print(f"Metrics: {METRIC_OUT}")
    print(f"Visuals: {VIZ_OUT}")


if __name__ == "__main__":
    main()
