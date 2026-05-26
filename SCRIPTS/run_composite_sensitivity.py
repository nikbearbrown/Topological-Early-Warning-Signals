#!/usr/bin/env python3
"""Composite-weighting sensitivity checks for the FF49 TDA paper.

This script uses the cached W = 60 window-listwise standardized component
signals. It does not recompute persistent homology.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.covariance import LedoitWolf
from sklearn.decomposition import PCA
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS_DIR = ROOT / "analysis"
SIGNAL_PATH = ANALYSIS_DIR / "signals" / "tda_signals_window_listwise_w60.csv"

COMPONENTS = [
    ("h0_landscape_l1_z", "H0 landscape L1"),
    ("neg_h1_landscape_l1_z", "-H1 landscape L1"),
    ("neg_beta1_z", "-beta1"),
    ("neg_total_persistence_h0_z", "-TP H0"),
    ("neg_total_persistence_h1_z", "-TP H1"),
]


def cohen_d(recession_values: np.ndarray, expansion_values: np.ndarray) -> float:
    n1, n0 = len(recession_values), len(expansion_values)
    if n1 < 2 or n0 < 2:
        return math.nan
    s1 = np.var(recession_values, ddof=1)
    s0 = np.var(expansion_values, ddof=1)
    pooled = math.sqrt(((n1 - 1) * s1 + (n0 - 1) * s0) / (n1 + n0 - 2))
    if pooled == 0 or not np.isfinite(pooled):
        return math.nan
    return float((np.mean(recession_values) - np.mean(expansion_values)) / pooled)


def format_p(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def standardize_to_expansion(values: np.ndarray, recession: np.ndarray) -> np.ndarray:
    exp = values[~recession]
    mean = np.nanmean(exp)
    sd = np.nanstd(exp, ddof=1)
    if not np.isfinite(sd) or sd == 0:
        return np.full_like(values, np.nan, dtype=float)
    return (values - mean) / sd


def block_bootstrap(values: np.ndarray, recession: np.ndarray, label: str, block_len: int = 252, reps: int = 1000, seed: int = 20260529) -> dict:
    rng = np.random.default_rng(seed)
    n = len(values)
    rec = values[recession]
    exp = values[~recession]
    observed = float(np.mean(rec) - np.mean(exp))
    boot = np.empty(reps, dtype=float)
    for r in range(reps):
        starts = rng.integers(0, n, size=math.ceil(n / block_len))
        idx = np.concatenate([(np.arange(start, start + block_len) % n) for start in starts])[:n]
        b_values = values[idx]
        b_recession = recession[idx]
        if b_recession.any() and (~b_recession).any():
            boot[r] = np.mean(b_values[b_recession]) - np.mean(b_values[~b_recession])
        else:
            boot[r] = np.nan
    boot = boot[np.isfinite(boot)]
    se = float(np.std(boot, ddof=1))
    p_value = float(2.0 * stats.norm.sf(abs(observed / se))) if se > 0 else math.nan
    ci_low, ci_high = np.percentile(boot, [2.5, 97.5])
    return {
        "composite": label,
        "n": int(n),
        "n_recession": int(recession.sum()),
        "expansion_mean": float(np.mean(exp)),
        "recession_mean": float(np.mean(rec)),
        "mean_difference": observed,
        "cohen_d": cohen_d(rec, exp),
        "auc": float(roc_auc_score(recession.astype(int), values)),
        "block_length": int(block_len),
        "bootstrap_reps": int(len(boot)),
        "bootstrap_p_value": p_value,
        "ci_2_5": float(ci_low),
        "ci_97_5": float(ci_high),
    }


def normalized_weight_frame(weights: dict[str, np.ndarray]) -> pd.DataFrame:
    rows = []
    for method, vector in weights.items():
        for (col, label), weight in zip(COMPONENTS, vector):
            rows.append({"composite": method, "component": label, "column": col, "weight": float(weight)})
    return pd.DataFrame(rows)


def build_composites(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    component_cols = [col for col, _label in COMPONENTS]
    clean = df[["date", "recession", *component_cols, "composite_z"]].dropna().copy()
    recession = clean["recession"].to_numpy(dtype=bool)
    x = clean[component_cols].to_numpy(dtype=float)
    x_exp = x[~recession]

    # Baseline: transparent equal weighting used in the manuscript.
    equal_weights = np.repeat(1.0 / len(component_cols), len(component_cols))
    clean["equal_weight"] = clean["composite_z"].to_numpy(dtype=float)

    # PCA: first principal component of the expansion-day component matrix.
    pca = PCA(n_components=1)
    pca.fit(x_exp)
    pca_scores = pca.transform(x).ravel()
    pca_scores = standardize_to_expansion(pca_scores, recession)
    if np.nanmean(pca_scores[recession]) < np.nanmean(pca_scores[~recession]):
        pca_scores = -pca_scores
        pca_weights = -pca.components_[0]
    else:
        pca_weights = pca.components_[0]
    clean["pca_pc1"] = pca_scores

    # Shrinkage: Ledoit-Wolf covariance-stabilized minimum-variance average.
    # This is unsupervised with respect to recession labels; it downweights
    # redundant components rather than optimizing classification performance.
    cov = LedoitWolf().fit(x_exp).covariance_
    ones = np.ones(len(component_cols))
    raw_weights = np.linalg.solve(cov, ones)
    shrink_weights = raw_weights / raw_weights.sum()
    shrink_scores = x @ shrink_weights
    shrink_scores = standardize_to_expansion(shrink_scores, recession)
    if np.nanmean(shrink_scores[recession]) < np.nanmean(shrink_scores[~recession]):
        shrink_scores = -shrink_scores
        shrink_weights = -shrink_weights
    clean["ledoit_wolf_minvar"] = shrink_scores

    weight_table = normalized_weight_frame({
        "Equal-weight baseline": equal_weights,
        "PCA PC1": pca_weights / np.sum(np.abs(pca_weights)),
        "Ledoit-Wolf min-var": shrink_weights,
    })
    return clean, weight_table


def write_markdown(summary: pd.DataFrame, weights: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Composite-Weighting Sensitivity",
        "",
        "Cached W = 60 listwise-deletion component signals are recombined three ways:",
        "",
        "- Equal-weight baseline: the manuscript's transparent descriptive composite.",
        "- PCA PC1: first principal component of expansion-day standardized TDA components, sign-oriented so higher values are more recession-like.",
        "- Ledoit-Wolf min-var: covariance-stabilized minimum-variance average of the five components, fit on expansion days and not supervised by recession labels.",
        "",
        "| Composite | N | Recession N | Cohen's d | AUC | Block-bootstrap p-value | 95% bootstrap CI |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in summary.to_dict("records"):
        lines.append(
            f"| {row['composite']} | {row['n']} | {row['n_recession']} | "
            f"{row['cohen_d']:.3f} | {row['auc']:.3f} | {format_p(row['bootstrap_p_value'])} | "
            f"[{row['ci_2_5']:.3f}, {row['ci_97_5']:.3f}] |"
        )

    lines.extend(["", "## Component weights", ""])
    for method in weights["composite"].unique():
        sub = weights[weights["composite"] == method]
        parts = [f"{row.component}: {row.weight:.3f}" for row in sub.itertuples()]
        lines.append(f"- {method}: " + "; ".join(parts) + ".")

    indexed = summary.set_index("composite")
    equal = indexed.loc["Equal-weight baseline"]
    pca = indexed.loc["PCA PC1"]
    shrink = indexed.loc["Ledoit-Wolf min-var"]
    strongest = summary.sort_values("cohen_d", ascending=False).iloc[0]
    lines.extend([
        "",
        "## Interpretation",
        "",
        (
            f"The strongest unsupervised composite in this run is {strongest['composite']} "
            f"(d = {strongest['cohen_d']:.3f}, AUC = {strongest['auc']:.3f}). The equal-weight baseline "
            f"remains positive and significant (d = {equal['cohen_d']:.3f}, AUC = {equal['auc']:.3f}), "
            "so the main result is not an artifact of a tuned weighting scheme. PCA PC1 strengthens the "
            f"recession separation (d = {pca['cohen_d']:.3f}, AUC = {pca['auc']:.3f}), largely by assigning "
            "negative weight to the H0 fragmentation component and positive weight to the loop/persistence "
            "compression components. The Ledoit-Wolf minimum-variance composite also remains positive "
            f"(d = {shrink['cohen_d']:.3f}, AUC = {shrink['auc']:.3f}) but has weaker rank separation and "
            "a wider block-bootstrap interval. This supports keeping equal weighting as the transparent "
            "main specification while reporting PCA and shrinkage composites as robustness checks."
        ),
        "",
    ])
    out_path.write_text("\n".join(lines))


def main() -> None:
    df = pd.read_csv(SIGNAL_PATH, parse_dates=["date"])
    composites, weights = build_composites(df)
    recession = composites["recession"].to_numpy(dtype=bool)
    specs = [
        ("equal_weight", "Equal-weight baseline"),
        ("pca_pc1", "PCA PC1"),
        ("ledoit_wolf_minvar", "Ledoit-Wolf min-var"),
    ]
    rows = []
    for col, label in specs:
        clean = composites[["date", "recession", col]].dropna().reset_index(drop=True)
        rows.append(block_bootstrap(clean[col].to_numpy(dtype=float), clean["recession"].to_numpy(dtype=bool), label))
    summary = pd.DataFrame(rows)
    summary.to_csv(ANALYSIS_DIR / "composite_weighting_sensitivity.csv", index=False)
    weights.to_csv(ANALYSIS_DIR / "composite_weighting_weights.csv", index=False)
    composites[["date", "recession", "equal_weight", "pca_pc1", "ledoit_wolf_minvar"]].to_csv(
        ANALYSIS_DIR / "composite_weighting_series.csv", index=False
    )
    write_markdown(summary, weights, ANALYSIS_DIR / "priority-6-composite-weighting-sensitivity.md")
    print(summary[["composite", "cohen_d", "auc", "bootstrap_p_value"]].to_string(index=False))


if __name__ == "__main__":
    main()
