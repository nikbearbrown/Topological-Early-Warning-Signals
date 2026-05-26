#!/usr/bin/env python3
"""Priority 3 analyses for the FF49 TDA paper.

This script strengthens the results framing:

1. Treat macro prediction as a negative/boundary result rather than a
   standalone contribution.
2. Test crisis-type heterogeneity for narrative financial-crisis episodes.
3. Test whether the composite TDA signal contains information beyond mean
   absolute correlation.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.metrics import roc_auc_score

from run_tda_robustness import (
    ANALYSIS_DIR,
    DATA_DIR,
    NBER_RECESSIONS,
    ROOT,
    add_recession_indicator,
    cohen_d,
    format_p,
    read_ff49_value_weighted,
    signal_cache_path,
)


FINANCIAL_EPISODES = {
    "Great Depression": "financial",
    "1990-1991 recession": "financial",
    "Global Financial Crisis": "financial",
    "COVID recession": "financial",
}


CRISIS_TYPE_OVERRIDES = {
    "1929-1933": "financial",
    "1937-1938": "demand",
    "1945": "supply/monetary",
    "1948-1949": "demand",
    "1953-1954": "demand",
    "1957-1958": "demand",
    "1960-1961": "demand",
    "1969-1970": "supply/monetary",
    "1973-1975": "supply/monetary",
    "1980": "supply/monetary",
    "1981-1982": "supply/monetary",
    "1990-1991": "financial",
    "2001": "demand",
    "2007-2009": "financial",
    "2020": "financial",
}


def setup_matplotlib():
    mpl_dir = ROOT / ".mplconfig"
    cache_dir = ROOT / ".cache"
    mpl_dir.mkdir(exist_ok=True)
    cache_dir.mkdir(exist_ok=True)
    os.environ["MPLCONFIGDIR"] = str(mpl_dir)
    os.environ["XDG_CACHE_HOME"] = str(cache_dir)
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "axes.edgecolor": "#000000",
        "axes.labelcolor": "#000000",
        "xtick.color": "#555555",
        "ytick.color": "#555555",
    })
    return plt


def episode_short_label(label: str) -> str:
    if label == "Great Depression":
        return "1929-1933"
    if label == "Postwar recession":
        return "1945"
    if label == "COVID recession":
        return "2020"
    if "Global Financial Crisis" in label:
        return "2007-2009"
    return label.replace(" recession", "")


def add_market_controls(signals: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    value_cols = [c for c in returns.columns if c not in {"date", "recession"}]
    features = returns[["date"]].copy()
    features["market_return"] = returns[value_cols].mean(axis=1, skipna=True)
    features["volatility_60"] = features["market_return"].rolling(60, min_periods=40).std()
    features["return_60"] = features["market_return"].rolling(60, min_periods=40).sum()
    return signals.merge(features, on="date", how="left")


def add_episode_metadata(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["episode"] = ""
    out["episode_short"] = ""
    out["crisis_type"] = "expansion"
    out["financial_crisis"] = False
    out["days_from_onset"] = np.nan
    for start, end, label in NBER_RECESSIONS:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        mask = (out["date"] >= start_ts) & (out["date"] <= end_ts)
        short = episode_short_label(label)
        crisis_type = FINANCIAL_EPISODES.get(label, CRISIS_TYPE_OVERRIDES.get(short, "demand"))
        out.loc[mask, "episode"] = label
        out.loc[mask, "episode_short"] = short
        out.loc[mask, "crisis_type"] = crisis_type
        out.loc[mask, "financial_crisis"] = crisis_type == "financial"
        out.loc[mask, "days_from_onset"] = (out.loc[mask, "date"] - start_ts).dt.days
    return out


def crisis_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for start, end, label in NBER_RECESSIONS:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        short = episode_short_label(label)
        during = df[(df["date"] >= start_ts) & (df["date"] <= end_ts)]
        pre = df[(df["date"] >= start_ts - pd.Timedelta(days=180)) & (df["date"] < start_ts)]
        post = df[(df["date"] > end_ts) & (df["date"] <= end_ts + pd.Timedelta(days=180))]
        crisis_type = FINANCIAL_EPISODES.get(label, CRISIS_TYPE_OVERRIDES.get(short, "demand"))
        rows.append({
            "episode": label,
            "episode_short": short,
            "crisis_type": crisis_type,
            "financial_crisis": crisis_type == "financial",
            "start": start_ts.strftime("%Y-%m-%d"),
            "end": end_ts.strftime("%Y-%m-%d"),
            "n_during": int(len(during)),
            "pre_mean_z": float(pre["composite_z"].mean()),
            "during_mean_z": float(during["composite_z"].mean()),
            "post_mean_z": float(post["composite_z"].mean()),
            "elevation_vs_pre": float(during["composite_z"].mean() - pre["composite_z"].mean()),
            "peak_z": float(during["composite_z"].max()),
            "mean_volatility_60": float(during["volatility_60"].mean()),
            "disruption_sum": float(during["composite_z"].clip(lower=0).sum()),
        })
    return pd.DataFrame(rows)


def financial_crisis_tests(df: pd.DataFrame, episode_table: pd.DataFrame) -> pd.DataFrame:
    recessions = df[df["recession"]].dropna(subset=["composite_z", "financial_crisis", "volatility_60"]).copy()
    financial = recessions.loc[recessions["financial_crisis"], "composite_z"].to_numpy()
    other = recessions.loc[~recessions["financial_crisis"], "composite_z"].to_numpy()
    _t, p_welch = stats.ttest_ind(financial, other, equal_var=False)

    x = recessions[["volatility_60"]].to_numpy()
    y = recessions["composite_z"].to_numpy()
    residual = y - LinearRegression().fit(x, y).predict(x)
    residual_fin = residual[recessions["financial_crisis"].to_numpy()]
    residual_other = residual[~recessions["financial_crisis"].to_numpy()]
    _t_resid, p_resid = stats.ttest_ind(residual_fin, residual_other, equal_var=False)

    episode_fin = episode_table.loc[episode_table["financial_crisis"], "elevation_vs_pre"].dropna().to_numpy()
    episode_other = episode_table.loc[~episode_table["financial_crisis"], "elevation_vs_pre"].dropna().to_numpy()
    _t_episode, p_episode = stats.ttest_ind(episode_fin, episode_other, equal_var=False)

    rows = [
        {
            "test": "recession-day composite Z",
            "financial_mean": float(np.mean(financial)),
            "other_mean": float(np.mean(other)),
            "difference": float(np.mean(financial) - np.mean(other)),
            "cohen_d": cohen_d(financial, other),
            "p_value": float(p_welch),
        },
        {
            "test": "recession-day composite Z after residualizing volatility",
            "financial_mean": float(np.mean(residual_fin)),
            "other_mean": float(np.mean(residual_other)),
            "difference": float(np.mean(residual_fin) - np.mean(residual_other)),
            "cohen_d": cohen_d(residual_fin, residual_other),
            "p_value": float(p_resid),
        },
        {
            "test": "episode-level elevation vs pre-recession",
            "financial_mean": float(np.mean(episode_fin)),
            "other_mean": float(np.mean(episode_other)),
            "difference": float(np.mean(episode_fin) - np.mean(episode_other)),
            "cohen_d": cohen_d(episode_fin, episode_other),
            "p_value": float(p_episode),
        },
    ]
    return pd.DataFrame(rows)


def financial_event_study(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    selected = ["Great Depression", "1990-1991 recession", "Global Financial Crisis", "COVID recession"]
    for start, end, label in NBER_RECESSIONS:
        if label not in selected:
            continue
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        window = df[(df["date"] >= start_ts - pd.Timedelta(days=180)) & (df["date"] <= end_ts + pd.Timedelta(days=180))].copy()
        window["calendar_days_from_onset"] = (window["date"] - start_ts).dt.days
        window["month_bin"] = np.floor(window["calendar_days_from_onset"] / 30).astype(int)
        grouped = window.groupby("month_bin", as_index=False).agg(
            mean_composite_z=("composite_z", "mean"),
            mean_abs_corr=("mean_abs_corr", "mean"),
            mean_volatility_60=("volatility_60", "mean"),
            n=("composite_z", "size"),
        )
        grouped["episode"] = label
        grouped["episode_short"] = episode_short_label(label)
        grouped["start"] = start_ts.strftime("%Y-%m-%d")
        grouped["end"] = end_ts.strftime("%Y-%m-%d")
        records.append(grouped)
    return pd.concat(records, ignore_index=True)


def distinct_from_correlation(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    clean = df.dropna(subset=["composite_z", "mean_abs_corr", "recession"]).copy()
    x = clean[["mean_abs_corr"]].to_numpy()
    y = clean["composite_z"].to_numpy()
    model = LinearRegression().fit(x, y)
    clean["tda_residual_vs_corr"] = y - model.predict(x)

    rec_resid = clean.loc[clean["recession"], "tda_residual_vs_corr"].to_numpy()
    exp_resid = clean.loc[~clean["recession"], "tda_residual_vs_corr"].to_numpy()
    _t, p_resid = stats.ttest_ind(rec_resid, exp_resid, equal_var=False)

    y_true = clean["recession"].astype(int).to_numpy()
    auc_corr = roc_auc_score(y_true, clean["mean_abs_corr"])
    auc_composite = roc_auc_score(y_true, clean["composite_z"])
    auc_residual = roc_auc_score(y_true, clean["tda_residual_vs_corr"])

    # Logistic incremental test: recession ~ mean_abs_corr vs. mean_abs_corr + TDA residual.
    base = LogisticRegression(max_iter=1000, class_weight="balanced")
    full = LogisticRegression(max_iter=1000, class_weight="balanced")
    base.fit(clean[["mean_abs_corr"]], y_true)
    full.fit(clean[["mean_abs_corr", "tda_residual_vs_corr"]], y_true)
    auc_base_logit = roc_auc_score(y_true, base.predict_proba(clean[["mean_abs_corr"]])[:, 1])
    auc_full_logit = roc_auc_score(y_true, full.predict_proba(clean[["mean_abs_corr", "tda_residual_vs_corr"]])[:, 1])

    stats_table = pd.DataFrame([
        {
            "metric": "corr(composite_z, mean_abs_corr)",
            "value": float(np.corrcoef(clean["composite_z"], clean["mean_abs_corr"])[0, 1]),
        },
        {
            "metric": "R2 composite_z ~ mean_abs_corr",
            "value": float(model.score(x, y)),
        },
        {
            "metric": "residual recession Cohen d",
            "value": cohen_d(rec_resid, exp_resid),
        },
        {
            "metric": "residual Welch p-value",
            "value": float(p_resid),
        },
        {
            "metric": "AUC mean_abs_corr",
            "value": float(auc_corr),
        },
        {
            "metric": "AUC composite_z",
            "value": float(auc_composite),
        },
        {
            "metric": "AUC residual_vs_corr",
            "value": float(auc_residual),
        },
        {
            "metric": "AUC logit mean_abs_corr",
            "value": float(auc_base_logit),
        },
        {
            "metric": "AUC logit mean_abs_corr + TDA residual",
            "value": float(auc_full_logit),
        },
    ])

    residual_bootstrap = block_bootstrap_single_series(
        clean["tda_residual_vs_corr"].to_numpy(dtype=float),
        clean["recession"].to_numpy(dtype=bool),
        "TDA residual vs. mean abs corr",
    )
    return stats_table, residual_bootstrap


def block_bootstrap_single_series(values: np.ndarray, recession: np.ndarray, label: str, block_len: int = 252, reps: int = 1000, seed: int = 20260527) -> pd.DataFrame:
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
    return pd.DataFrame([{
        "signal": label,
        "n": int(n),
        "n_recession": int(recession.sum()),
        "mean_difference": observed,
        "cohen_d": cohen_d(rec, exp),
        "block_length": int(block_len),
        "bootstrap_reps": int(len(boot)),
        "bootstrap_se": se,
        "bootstrap_p_value": p_value,
        "ci_2_5": float(ci_low),
        "ci_97_5": float(ci_high),
    }])


def write_priority_3_markdown(
    episode_table: pd.DataFrame,
    financial_tests: pd.DataFrame,
    distinct_table: pd.DataFrame,
    residual_bootstrap: pd.DataFrame,
    out_path: Path,
) -> None:
    lines = [
        "# Priority 3 - Results Strengthening and Framing",
        "",
        "## 3.1 Macro-predictive section decision",
        "",
        "Decision: keep the industrial-production regressions only as a negative-result subsection. Do not present Table 3 as a standalone contribution. The current evidence is too weak for a macro-predictive claim; its value is as a boundary condition on the paper's scope.",
        "",
        "Recommended framing: TDA characterizes recession-regime co-movement geometry. It does not, in the current evidence, forecast macroeconomic activity better than conventional return and volatility measures.",
        "",
        "## 3.2 Crisis-type heterogeneity",
        "",
        "| Episode | Type | During mean Z | Pre mean Z | Elevation | Peak Z | Disruption |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in episode_table.to_dict("records"):
        lines.append(
            f"| {row['episode_short']} | {row['crisis_type']} | {row['during_mean_z']:.3f} | "
            f"{row['pre_mean_z']:.3f} | {row['elevation_vs_pre']:.3f} | {row['peak_z']:.3f} | {row['disruption_sum']:.1f} |"
        )

    lines.extend([
        "",
        "### Financial-crisis test",
        "",
        "| Test | Financial mean | Other mean | Difference | Cohen's d | p-value |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in financial_tests.to_dict("records"):
        lines.append(
            f"| {row['test']} | {row['financial_mean']:.3f} | {row['other_mean']:.3f} | "
            f"{row['difference']:.3f} | {row['cohen_d']:.3f} | {format_p(row['p_value'])} |"
        )

    lines.extend([
        "",
        "Interpretation: the narrative financial-crisis classification produces only a small raw recession-day elevation in the composite topological signal. The effect reverses after residualizing 60-day volatility, and the episode-level elevation test is not a stable finding. This is a useful negative result: the current evidence does not support making crisis-type heterogeneity a central contribution.",
        "",
        "## 3.3 Distinctness from average correlation",
        "",
        "| Metric | Value |",
        "|---|---:|",
    ])
    for row in distinct_table.to_dict("records"):
        lines.append(f"| {row['metric']} | {row['value']:.3f} |")

    rb = residual_bootstrap.iloc[0]
    lines.extend([
        "",
        "### Block-bootstrap residual test",
        "",
        f"After regressing composite Z on mean absolute correlation, the residual still has recession Cohen's d = {rb['cohen_d']:.3f} with block-bootstrap p-value {format_p(rb['bootstrap_p_value'])}.",
        "",
        "Interpretation: if the residual effect remains positive and statistically non-random, the topology signal is not merely a renamed average-correlation measure. If the effect is small, the contribution should still be stated carefully: TDA adds a geometric decomposition of co-movement, but the strongest empirical variation is shared with conventional correlation intensity.",
        "",
    ])
    out_path.write_text("\n".join(lines))


def plot_financial_event_study(event_table: pd.DataFrame, out_base: Path) -> None:
    plt = setup_matplotlib()
    fig, ax = plt.subplots(figsize=(10.5, 5.2), constrained_layout=True)
    styles = {
        "1929-1933": {"color": "#C8102E", "linestyle": "-", "marker": "o"},
        "1990-1991": {"color": "#555555", "linestyle": "-", "marker": "s"},
        "2007-2009": {"color": "#000000", "linestyle": "-", "marker": "^"},
        "2020": {"color": "#555555", "linestyle": "--", "marker": "D"},
    }
    for episode, group in event_table.groupby("episode_short"):
        style = styles.get(episode, {"color": "#555555", "linestyle": "-", "marker": "o"})
        ax.plot(
            group["month_bin"],
            group["mean_composite_z"],
            marker=style["marker"],
            linewidth=1.7,
            markersize=4,
            label=episode,
            color=style["color"],
            linestyle=style["linestyle"],
        )
    ax.axvline(0, color="#C8102E", linewidth=1.4)
    ax.axhline(0, color="#CCCCCC", linewidth=1.0)
    ax.set_title("Composite TDA signal around narrative financial crises", fontsize=14, fontweight="bold")
    ax.set_xlabel("Months from recession onset")
    ax.set_ylabel("Mean composite Z")
    ax.grid(True, color="#CCCCCC", alpha=0.45, linewidth=0.7)
    ax.legend(frameon=False, ncol=2)
    for ext in ["png", "svg"]:
        fig.savefig(out_base.with_suffix(f".{ext}"), dpi=220, facecolor="white")
    plt.close(fig)


def main() -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    signals = pd.read_csv(signal_cache_path("window_listwise", 60), parse_dates=["date"])
    returns = add_recession_indicator(read_ff49_value_weighted())
    df = add_market_controls(signals, returns)
    df = add_episode_metadata(df)

    episode_table = crisis_type_summary(df)
    episode_table.to_csv(ANALYSIS_DIR / "priority-3-crisis-type-episode-summary.csv", index=False)

    financial_tests = financial_crisis_tests(df, episode_table)
    financial_tests.to_csv(ANALYSIS_DIR / "priority-3-financial-crisis-tests.csv", index=False)

    event_table = financial_event_study(df)
    event_table.to_csv(ANALYSIS_DIR / "priority-3-financial-crisis-event-study.csv", index=False)
    event_json = {
        "notes": "Monthly bins of composite Z around selected narrative financial crises.",
        "episodes": sorted(event_table["episode_short"].unique().tolist()),
        "rows": event_table.to_dict("records"),
    }
    (DATA_DIR / "figure-7-financial-crisis-event-study.json").write_text(json.dumps(event_json, indent=2))
    image_dir = ROOT / "images"
    image_dir.mkdir(exist_ok=True)
    plot_financial_event_study(event_table, image_dir / "figure-7-financial-crisis-event-study")

    distinct_table, residual_bootstrap = distinct_from_correlation(df)
    distinct_table.to_csv(ANALYSIS_DIR / "priority-3-tda-vs-correlation.csv", index=False)
    residual_bootstrap.to_csv(ANALYSIS_DIR / "priority-3-tda-residual-block-bootstrap.csv", index=False)

    write_priority_3_markdown(
        episode_table,
        financial_tests,
        distinct_table,
        residual_bootstrap,
        ANALYSIS_DIR / "priority-3-results-strengthening.md",
    )


if __name__ == "__main__":
    main()
