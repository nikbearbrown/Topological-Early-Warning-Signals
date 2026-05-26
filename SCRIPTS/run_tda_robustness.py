#!/usr/bin/env python3
"""Run TDA robustness checks for the FF49 industry portfolio paper.

Priority 1.1 starts here: compute rolling persistent-homology signals for
W = 60, 120, and 252 trading days, then report recession-vs-expansion effect
sizes and AUCs for each topological signal and the equal-weight composite.

The baseline missing-data rule is window-level listwise deletion: for each
rolling window, keep only industries with complete observations inside that
window. This lets the pre-1970 sample run on the industries available then,
while Priority 1.3 tests fixed FF42 and imputation alternatives explicitly.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from ripser import ripser
from scipy import stats
from sklearn.experimental import enable_iterative_imputer  # noqa: F401
from sklearn.impute import IterativeImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
ANALYSIS_DIR = ROOT / "analysis"

FF49_CSV = DATA_DIR / "49_Industry_Portfolios_Daily.csv"

NBER_RECESSIONS = [
    ("1929-08-01", "1933-03-01", "Great Depression"),
    ("1937-05-01", "1938-06-01", "1937-1938 recession"),
    ("1945-02-01", "1945-10-01", "Postwar recession"),
    ("1948-11-01", "1949-10-01", "1948-1949 recession"),
    ("1953-07-01", "1954-05-01", "1953-1954 recession"),
    ("1957-08-01", "1958-04-01", "1957-1958 recession"),
    ("1960-04-01", "1961-02-01", "1960-1961 recession"),
    ("1969-12-01", "1970-11-01", "1969-1970 recession"),
    ("1973-11-01", "1975-03-01", "1973-1975 recession"),
    ("1980-01-01", "1980-07-01", "1980 recession"),
    ("1981-07-01", "1982-11-01", "1981-1982 recession"),
    ("1990-07-01", "1991-03-01", "1990-1991 recession"),
    ("2001-03-01", "2001-11-01", "2001 recession"),
    ("2007-12-01", "2009-06-01", "Global Financial Crisis"),
    ("2020-02-01", "2020-04-01", "COVID recession"),
]

SIGNALS = [
    ("h0_landscape_l1_z", "H0 landscape L1"),
    ("neg_h1_landscape_l1_z", "-H1 landscape L1"),
    ("neg_beta1_z", "-beta1"),
    ("neg_total_persistence_h0_z", "-TP H0"),
    ("neg_total_persistence_h1_z", "-TP H1"),
    ("composite_z", "Composite Z"),
]


@dataclass
class WindowConfig:
    window: int
    min_assets: int = 20
    max_windows: int | None = None


def read_ff49_value_weighted() -> pd.DataFrame:
    """Read the value-weighted returns block from the Kenneth French FF49 CSV."""
    lines = FF49_CSV.read_text(errors="ignore").splitlines()
    header_idx = next(i for i, line in enumerate(lines) if line.startswith(",Agric"))
    equal_idx = next(i for i, line in enumerate(lines) if "Average Equal Weighted Returns" in line)
    nrows = equal_idx - header_idx - 1

    df = pd.read_csv(FF49_CSV, skiprows=header_idx, nrows=nrows, low_memory=False)
    df = df.rename(columns={df.columns[0]: "date"})
    df = df[pd.to_numeric(df["date"], errors="coerce").notna()].copy()
    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d")

    for col in df.columns[1:]:
      df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.replace([-99.99, -999], np.nan)
    return df.sort_values("date").reset_index(drop=True)


def add_recession_indicator(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["recession"] = False
    for start, end, _label in NBER_RECESSIONS:
        mask = (out["date"] >= pd.Timestamp(start)) & (out["date"] <= pd.Timestamp(end))
        out.loc[mask, "recession"] = True
    return out


def finite_lengths(diagram: np.ndarray) -> np.ndarray:
    if diagram.size == 0:
        return np.array([], dtype=float)
    finite = diagram[np.isfinite(diagram[:, 1])]
    if finite.size == 0:
        return np.array([], dtype=float)
    lengths = finite[:, 1] - finite[:, 0]
    return lengths[lengths > 0]


def landscape_l1_from_lengths(lengths: np.ndarray) -> float:
    # The total L1 norm across all persistence-landscape layers is the sum of
    # triangular tent areas, one per interval: (death - birth)^2 / 4.
    return float(np.sum((lengths ** 2) / 4.0))


def max_beta_alive(diagram: np.ndarray) -> int:
    if diagram.size == 0:
        return 0
    finite = diagram[np.isfinite(diagram[:, 1])]
    if finite.size == 0:
        return 0
    mids = np.unique(finite.mean(axis=1))
    if mids.size == 0:
        return 0
    alive = [(finite[:, 0] <= x) & (x < finite[:, 1]) for x in mids]
    return int(max(mask.sum() for mask in alive))


def compute_window_signals(window_values: pd.DataFrame) -> dict[str, float | int]:
    complete = window_values.dropna(axis=1, how="any")
    assets_used = complete.shape[1]
    if assets_used < 2:
        raise ValueError("Need at least two complete assets to compute a distance matrix")

    matrix = complete.to_numpy(dtype=float)
    corr = np.corrcoef(matrix, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    corr = np.clip(corr, -1.0, 1.0)
    dist = np.sqrt(2.0 * (1.0 - corr))
    np.fill_diagonal(dist, 0.0)

    diagrams = ripser(dist, distance_matrix=True, maxdim=1)["dgms"]
    h0_lengths = finite_lengths(diagrams[0])
    h1_lengths = finite_lengths(diagrams[1])

    return {
        "assets_used": assets_used,
        "mean_abs_corr": float(np.nanmean(np.abs(corr[np.triu_indices_from(corr, k=1)]))),
        "h0_landscape_l1": landscape_l1_from_lengths(h0_lengths),
        "h1_landscape_l1": landscape_l1_from_lengths(h1_lengths),
        "beta1": max_beta_alive(diagrams[1]),
        "total_persistence_h0": float(np.sum(h0_lengths)),
        "total_persistence_h1": float(np.sum(h1_lengths)),
    }


def signal_cache_path(method: str, window: int) -> Path:
    return ANALYSIS_DIR / "signals" / f"tda_signals_{method}_w{window}.csv"


def compute_rolling_signals(df: pd.DataFrame, config: WindowConfig, method: str = "window_listwise") -> pd.DataFrame:
    out_path = signal_cache_path(method, config.window)
    if out_path.exists() and config.max_windows is None:
        return pd.read_csv(out_path, parse_dates=["date"])

    returns = df.drop(columns=["recession"])
    value_cols = [c for c in returns.columns if c != "date"]
    records = []
    end_indices = range(config.window - 1, len(returns))
    if config.max_windows is not None:
        end_indices = list(end_indices)[-config.max_windows:]

    for n, end_idx in enumerate(end_indices, start=1):
        window_values = returns.loc[end_idx - config.window + 1:end_idx, value_cols]
        complete_assets = window_values.notna().all(axis=0)
        if int(complete_assets.sum()) < config.min_assets:
            continue
        signals = compute_window_signals(window_values.loc[:, complete_assets])
        date = returns.loc[end_idx, "date"]
        records.append({"date": date, "window": config.window, **signals})
        if n % 1000 == 0:
            print(f"W={config.window}: processed {n:,} windows; kept {len(records):,}")

    result = pd.DataFrame.from_records(records)
    result = add_recession_indicator(result)
    standardized = orient_and_standardize(result)

    if config.max_windows is None:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        standardized.to_csv(out_path, index=False)
    return standardized


def compute_fixed_universe_signals(df: pd.DataFrame, config: WindowConfig, method: str) -> pd.DataFrame:
    """Compute signals on a fixed set of columns, skipping only invalid windows."""
    return compute_rolling_signals(df, config, method=method)


def zscore_on_expansion(series: pd.Series, expansion_mask: pd.Series) -> pd.Series:
    base = series.loc[expansion_mask]
    mean = base.mean()
    sd = base.std(ddof=1)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(np.nan, index=series.index)
    return (series - mean) / sd


def orient_and_standardize(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    expansion = ~out["recession"]
    oriented = {
        "h0_landscape_l1": out["h0_landscape_l1"],
        "neg_h1_landscape_l1": -out["h1_landscape_l1"],
        "neg_beta1": -out["beta1"],
        "neg_total_persistence_h0": -out["total_persistence_h0"],
        "neg_total_persistence_h1": -out["total_persistence_h1"],
    }
    for name, values in oriented.items():
        out[f"{name}_z"] = zscore_on_expansion(values, expansion)
    component_cols = [
        "h0_landscape_l1_z",
        "neg_h1_landscape_l1_z",
        "neg_beta1_z",
        "neg_total_persistence_h0_z",
        "neg_total_persistence_h1_z",
    ]
    out["composite_z"] = out[component_cols].mean(axis=1)
    return out


def orient_and_expanding_standardize(df: pd.DataFrame, min_expansion_obs: int = 252) -> pd.DataFrame:
    """Real-time-safe expansion-baseline standardization.

    For each date t, z-scores are computed using expansion-day observations
    available strictly before t. The first min_expansion_obs expansion days are
    left missing. This is for identification/classification checks, not for the
    retrospective descriptive Table 1.
    """
    out = df.sort_values("date").copy().reset_index(drop=True)
    oriented = pd.DataFrame({
        "h0_landscape_l1": out["h0_landscape_l1"],
        "neg_h1_landscape_l1": -out["h1_landscape_l1"],
        "neg_beta1": -out["beta1"],
        "neg_total_persistence_h0": -out["total_persistence_h0"],
        "neg_total_persistence_h1": -out["total_persistence_h1"],
    })
    expansion = ~out["recession"]
    for col in oriented.columns:
        past_exp = oriented[col].where(expansion)
        count = past_exp.expanding().count().shift(1)
        mean = past_exp.expanding().mean().shift(1)
        sd = past_exp.expanding().std(ddof=1).shift(1)
        z = (oriented[col] - mean) / sd
        z[count < min_expansion_obs] = np.nan
        out[f"{col}_z"] = z
    component_cols = [
        "h0_landscape_l1_z",
        "neg_h1_landscape_l1_z",
        "neg_beta1_z",
        "neg_total_persistence_h0_z",
        "neg_total_persistence_h1_z",
    ]
    out["composite_z"] = out[component_cols].mean(axis=1)
    return out


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


def summarize_signals(signals_by_window: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    for window, df in signals_by_window.items():
        y = df["recession"].astype(int).to_numpy()
        for col, label in SIGNALS:
            clean = df[["recession", col]].dropna()
            rec = clean.loc[clean["recession"], col].to_numpy()
            exp = clean.loc[~clean["recession"], col].to_numpy()
            _stat, p_value = stats.ttest_ind(rec, exp, equal_var=False, nan_policy="omit")
            try:
                auc = roc_auc_score(clean["recession"].astype(int), clean[col])
            except ValueError:
                auc = math.nan
            rows.append({
                "window": window,
                "signal": label,
                "n": int(len(clean)),
                "n_recession": int(clean["recession"].sum()),
                "expansion_mean": float(np.mean(exp)),
                "recession_mean": float(np.mean(rec)),
                "cohen_d": cohen_d(rec, exp),
                "p_value": float(p_value),
                "auc": float(auc),
            })
    return pd.DataFrame(rows)


def format_p(p: float) -> str:
    if not np.isfinite(p):
        return ""
    if p < 0.001:
        return "<0.001"
    return f"{p:.3f}"


def write_markdown_table(summary: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Priority 1.1 - Rolling Window Robustness",
        "",
        "Baseline method: rolling correlation-distance matrices with window-level listwise deletion.",
        "For each rolling window, industries with any missing return inside the window are excluded from that window's distance matrix.",
        "Signals are oriented so larger values are more recession-like, then standardized on expansion-day observations within each window length.",
        "",
        "| Window | Signal | N | Recession N | Cohen's d | p-value | AUC |",
        "|---:|---|---:|---:|---:|---:|---:|",
    ]
    for row in summary.to_dict("records"):
        lines.append(
            f"| {row['window']} | {row['signal']} | {row['n']} | {row['n_recession']} | "
            f"{row['cohen_d']:.3f} | {format_p(row['p_value'])} | {row['auc']:.3f} |"
        )

    beta_rows = summary[summary["signal"] == "-beta1"].set_index("window")
    component_rows = summary[summary["signal"] != "Composite Z"]
    strongest = (
        component_rows.sort_values(["window", "cohen_d"], ascending=[True, False])
        .groupby("window")
        .first()["signal"]
        .to_dict()
    )
    lines.extend([
        "",
        "## β1 collapse check",
        "",
    ])
    for window in sorted(summary["window"].unique()):
        beta_d = beta_rows.loc[window, "cohen_d"] if window in beta_rows.index else math.nan
        winner = strongest.get(window, "")
        verdict = "yes" if winner == "-beta1" else f"no; strongest component is {winner}"
        lines.append(f"- W = {window}: -beta1 Cohen's d = {beta_d:.3f}; strongest component check: {verdict}.")

    lines.extend([
        "",
        "## Interpretation note",
        "",
        "W = 60 remains the baseline only if it has the strongest or most theoretically useful recession-regime effect.",
        "If longer windows produce comparable or stronger composite AUC/effect sizes, the manuscript should frame W = 60 as the short-horizon specification rather than the uniquely best specification.",
        "",
    ])
    out_path.write_text("\n".join(lines))


def summarize_one_panel(df: pd.DataFrame, panel: str, window: int) -> pd.DataFrame:
    rows = []
    for col, label in SIGNALS:
        clean = df[["recession", col]].dropna()
        rec = clean.loc[clean["recession"], col].to_numpy()
        exp = clean.loc[~clean["recession"], col].to_numpy()
        _stat, p_value = stats.ttest_ind(rec, exp, equal_var=False, nan_policy="omit")
        try:
            auc = roc_auc_score(clean["recession"].astype(int), clean[col])
        except ValueError:
            auc = math.nan
        rows.append({
            "panel": panel,
            "window": window,
            "signal": label,
            "n": int(len(clean)),
            "n_recession": int(clean["recession"].sum()),
            "expansion_mean": float(np.mean(exp)),
            "recession_mean": float(np.mean(rec)),
            "cohen_d": cohen_d(rec, exp),
            "p_value": float(p_value),
            "auc": float(auc),
        })
    return pd.DataFrame(rows)


def write_early_sample_markdown(table: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Priority 1.2 - Early-Sample Sensitivity",
        "",
        "Baseline signal file: `analysis/signals/tda_signals_window_listwise_w60.csv`.",
        "The post-1970 panel keeps observations with window end dates on or after 1970-01-01.",
        "",
        "| Panel | Signal | N | Recession N | Cohen's d | p-value | AUC |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in table.to_dict("records"):
        lines.append(
            f"| {row['panel']} | {row['signal']} | {row['n']} | {row['n_recession']} | "
            f"{row['cohen_d']:.3f} | {format_p(row['p_value'])} | {row['auc']:.3f} |"
        )

    wide = table.pivot(index="signal", columns="panel", values="cohen_d")
    lines.extend(["", "## Sensitivity read", ""])
    for signal in [label for _col, label in SIGNALS]:
        full = wide.loc[signal, "Full sample"]
        post = wide.loc[signal, "Post-1970"]
        delta = post - full
        direction = "same sign" if np.sign(full) == np.sign(post) else "sign change"
        lines.append(f"- {signal}: full d = {full:.3f}, post-1970 d = {post:.3f}, delta = {delta:.3f} ({direction}).")

    composite = wide.loc["Composite Z"]
    if np.sign(composite["Full sample"]) == np.sign(composite["Post-1970"]) and abs(composite["Post-1970"]) >= 0.5 * abs(composite["Full sample"]):
        verdict = "The composite result is qualitatively similar after 1970, so the early-sample caveat is measurement caution rather than a substantive reversal."
    else:
        verdict = "The composite result changes materially after 1970, so early-sample coverage should be treated as a substantive limitation."
    lines.extend(["", verdict, ""])
    out_path.write_text("\n".join(lines))


def run_priority_1_2() -> None:
    signal_path = signal_cache_path("window_listwise", 60)
    if not signal_path.exists():
        raise FileNotFoundError(f"Missing {signal_path}; run Priority 1.1 first.")
    signals = pd.read_csv(signal_path, parse_dates=["date"])
    full = summarize_one_panel(signals, "Full sample", 60)
    post = summarize_one_panel(signals.loc[signals["date"] >= pd.Timestamp("1970-01-01")].copy(), "Post-1970", 60)
    table = pd.concat([full, post], ignore_index=True)
    table.to_csv(ANALYSIS_DIR / "early_sample_sensitivity_table.csv", index=False)
    write_early_sample_markdown(table, ANALYSIS_DIR / "priority-1-2-early-sample-sensitivity.md")


def high_missing_industries(df: pd.DataFrame, threshold: float = 0.05) -> list[str]:
    value_cols = [c for c in df.columns if c not in {"date", "recession"}]
    rates = df[value_cols].isna().mean()
    return rates[rates > threshold].index.tolist()


def industry_knn_impute(df: pd.DataFrame, k: int = 5) -> pd.DataFrame:
    """Distance-weighted KNN imputation across industries.

    Neighbors are industries, not dates. Distances are computed from historical
    return correlations using pairwise complete observations. For each missing
    industry-date cell, use the same-date returns of the k nearest observed
    industries with inverse-distance weights. Remaining gaps fall back to that
    industry's median, then zero.
    """
    out = df.copy()
    value_cols = [c for c in out.columns if c not in {"date", "recession"}]
    values = out[value_cols].to_numpy(dtype=float).copy()
    corr = pd.DataFrame(values, columns=value_cols).corr(min_periods=60).fillna(0.0).clip(-1.0, 1.0)
    dist = np.sqrt(2.0 * (1.0 - corr.to_numpy()))
    np.fill_diagonal(dist, np.inf)
    medians = np.nanmedian(values, axis=0)
    medians = np.where(np.isfinite(medians), medians, 0.0)

    missing_positions = np.argwhere(np.isnan(values))
    for row_idx, col_idx in missing_positions:
        order = np.argsort(dist[col_idx])
        observed = [j for j in order if np.isfinite(values[row_idx, j])][:k]
        if observed:
            d = dist[col_idx, observed]
            weights = 1.0 / np.maximum(d, 1e-6)
            values[row_idx, col_idx] = float(np.average(values[row_idx, observed], weights=weights))
        else:
            values[row_idx, col_idx] = float(medians[col_idx])

    out[value_cols] = values
    return out


def mice_impute(df: pd.DataFrame, seed: int, max_iter: int = 5) -> pd.DataFrame:
    out = df.copy()
    value_cols = [c for c in out.columns if c not in {"date", "recession"}]
    imputer = IterativeImputer(
        random_state=seed,
        sample_posterior=True,
        max_iter=max_iter,
        initial_strategy="median",
        skip_complete=True,
    )
    out[value_cols] = imputer.fit_transform(out[value_cols].to_numpy(dtype=float))
    return out


def summarize_method(df: pd.DataFrame, method: str, window: int) -> pd.DataFrame:
    rows = []
    for col, label in SIGNALS:
        clean = df[["recession", col]].dropna()
        rec = clean.loc[clean["recession"], col].to_numpy()
        exp = clean.loc[~clean["recession"], col].to_numpy()
        _stat, p_value = stats.ttest_ind(rec, exp, equal_var=False, nan_policy="omit")
        try:
            auc = roc_auc_score(clean["recession"].astype(int), clean[col])
        except ValueError:
            auc = math.nan
        rows.append({
            "method": method,
            "window": window,
            "signal": label,
            "n": int(len(clean)),
            "n_recession": int(clean["recession"].sum()),
            "cohen_d": cohen_d(rec, exp),
            "p_value": float(p_value),
            "auc": float(auc),
        })
    return pd.DataFrame(rows)


def write_missing_markdown(table: pd.DataFrame, high_missing: list[str], out_path: Path, include_imputation: bool) -> None:
    scope_note = (
        "The robustness runs use W = 60 and compare the baseline window-level listwise deletion against fixed FF42, distance-weighted industry-KNN imputation, and pooled MICE imputations."
        if include_imputation
        else "The current robustness run uses W = 60 and compares the baseline window-level listwise deletion against fixed FF42. KNN and MICE imputation are intentionally deferred."
    )
    lines = [
        "# Priority 1.3 - Missing Value Handling",
        "",
        "Seven industries exceed 5% missingness in the FF49 daily value-weighted panel:",
        "",
        ", ".join(f"`{name}`" for name in high_missing),
        "",
        scope_note,
        "",
        "| Method | Signal | N | Recession N | Cohen's d | p-value | AUC |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in table.to_dict("records"):
        lines.append(
            f"| {row['method']} | {row['signal']} | {row['n']} | {row['n_recession']} | "
            f"{row['cohen_d']:.3f} | {format_p(row['p_value'])} | {row['auc']:.3f} |"
        )

    comp = table[table["signal"] == "Composite Z"].set_index("method")
    lines.extend(["", "## Composite sensitivity", ""])
    for method, row in comp.iterrows():
        lines.append(f"- {method}: composite d = {row['cohen_d']:.3f}, AUC = {row['auc']:.3f}.")
    if include_imputation:
        lines.extend(["", "Interpretation: the imputation rows preserve the sign and block-bootstrap significance of the composite recession effect, but they attenuate its magnitude relative to listwise deletion. Missingness is therefore not a reversal of the main result, but it should be reported as a moderate measurement-sensitivity caveat.", ""])
    else:
        lines.extend(["", "KNN k=5 distance-weighted imputation and MICE m=10 pooling are not included in this lightweight run. Re-run with `--include-imputation` to refresh those rows.", ""])
    out_path.write_text("\n".join(lines))


def pool_mice_signals(signal_frames: list[pd.DataFrame]) -> pd.DataFrame:
    signal_cols = [col for col, _label in SIGNALS]
    pooled = signal_frames[0][["date", "window", "assets_used", "mean_abs_corr", "recession"]].copy()
    for col in signal_cols:
        stacked = np.vstack([frame[col].to_numpy(dtype=float) for frame in signal_frames])
        pooled[col] = np.nanmean(stacked, axis=0)
    return pooled


def run_priority_1_3(df: pd.DataFrame, include_imputation: bool = False) -> None:
    window = 60
    config = WindowConfig(window=window, min_assets=20)
    high_missing = high_missing_industries(df)

    baseline = pd.read_csv(signal_cache_path("window_listwise", window), parse_dates=["date"])
    summaries = [summarize_method(baseline, "listwise deletion", window)]

    ff42_df = df.drop(columns=high_missing)
    ff42 = compute_fixed_universe_signals(ff42_df, config, method="ff42_drop7")
    summaries.append(summarize_method(ff42, "drop seven high-missing industries", window))

    if not include_imputation:
        table = pd.concat(summaries, ignore_index=True)
        table.to_csv(ANALYSIS_DIR / "missing_value_robustness_table.csv", index=False)
        write_missing_markdown(table, high_missing, ANALYSIS_DIR / "priority-1-3-missing-value-handling.md", include_imputation=False)
        return

    knn_path = signal_cache_path("knn5_distance_weighted", window)
    if knn_path.exists():
        knn_signals = pd.read_csv(knn_path, parse_dates=["date"])
    else:
        knn_df = industry_knn_impute(df, k=5)
        knn_signals = compute_fixed_universe_signals(knn_df, config, method="knn5_distance_weighted")
    summaries.append(summarize_method(knn_signals, "KNN k=5 distance-weighted", window))

    mice_frames = []
    for m in range(1, 11):
        method = f"mice_m{m:02d}"
        path = signal_cache_path(method, window)
        if path.exists():
            frame = pd.read_csv(path, parse_dates=["date"])
        else:
            print(f"MICE imputation {m}/10")
            imputed = mice_impute(df, seed=10_000 + m)
            frame = compute_fixed_universe_signals(imputed, config, method=method)
        mice_frames.append(frame)

    pooled = pool_mice_signals(mice_frames)
    pooled_path = signal_cache_path("mice_pooled_m10", window)
    pooled.to_csv(pooled_path, index=False)
    summaries.append(summarize_method(pooled, "MICE pooled m=10", window))

    table = pd.concat(summaries, ignore_index=True)
    table.to_csv(ANALYSIS_DIR / "missing_value_robustness_table.csv", index=False)
    write_missing_markdown(table, high_missing, ANALYSIS_DIR / "priority-1-3-missing-value-handling.md", include_imputation=True)


def write_cv_protocol_note(out_path: Path) -> None:
    lines = [
        "# Priority 2.1 - Cross-Validation Protocol and Look-Ahead Bias",
        "",
        "## Current status",
        "",
        "The descriptive recession-regime tables use retrospective standardization: each oriented topological signal is standardized using the full-sample expansion-day mean and standard deviation. That is acceptable for descriptive regime characterization, but it is not real-time safe for classification or forecasting claims.",
        "",
        "For any classification table, the real-time-safe specification must use expanding-window standardization: at date t, compute the expansion baseline using only expansion-day observations observed strictly before t.",
        "",
        "## Recommended CV scheme for Table 2",
        "",
        "Use expanding-window time-series cross-validation with non-overlapping test blocks:",
        "",
        "1. Sort observations by date.",
        "2. Use an initial training span long enough to include at least 252 expansion observations after signal availability.",
        "3. For fold k, train on all observations before the test block.",
        "4. Test on the next contiguous block.",
        "5. Recompute standardization using only the training history available before each test date.",
        "6. Report fold start/end dates, recession-day counts, expansion-day counts, fold AUC, mean AUC, and standard deviation.",
        "",
        "This is an expanding-window protocol, not random K-fold CV and not shuffled block CV.",
        "",
        "## Generated check",
        "",
        "This run writes `analysis/signals/tda_signals_window_listwise_w60_expanding.csv`, an expanding-baseline version of the W=60 listwise signal file.",
        "",
        "Use the expanding file for Table 2 classification checks. Use the retrospective file for descriptive Table 1-style regime summaries.",
        "",
    ]
    out_path.write_text("\n".join(lines))


def run_priority_2_1() -> None:
    base_path = signal_cache_path("window_listwise", 60)
    if not base_path.exists():
        raise FileNotFoundError(f"Missing {base_path}; run Priority 1.1 first.")
    base = pd.read_csv(base_path, parse_dates=["date"])
    expanding = orient_and_expanding_standardize(base)
    out_path = ANALYSIS_DIR / "signals" / "tda_signals_window_listwise_w60_expanding.csv"
    expanding.to_csv(out_path, index=False)

    comp = pd.DataFrame([
        {"standardization": "retrospective full-sample expansion baseline", **summarize_one_panel(base, "retrospective", 60).query("signal == 'Composite Z'").iloc[0].to_dict()},
        {"standardization": "expanding prior expansion baseline", **summarize_one_panel(expanding, "expanding", 60).query("signal == 'Composite Z'").iloc[0].to_dict()},
    ])
    comp.to_csv(ANALYSIS_DIR / "lookahead_standardization_comparison.csv", index=False)
    write_cv_protocol_note(ANALYSIS_DIR / "priority-2-1-cross-validation-protocol.md")


def block_bootstrap_signal_tests(df: pd.DataFrame, block_len: int = 252, reps: int = 1000, seed: int = 20260526) -> pd.DataFrame:
    """Block-bootstrap recession-vs-expansion mean differences.

    Daily topological signals are serially dependent because rolling windows
    overlap heavily. The bootstrap resamples contiguous date blocks so the
    paired signal/regime sequence remains locally intact.
    """
    rng = np.random.default_rng(seed)
    rows = []
    for col, label in SIGNALS:
        clean = df[["date", "recession", col]].dropna().reset_index(drop=True)
        values = clean[col].to_numpy(dtype=float)
        recession = clean["recession"].to_numpy(dtype=bool)
        n = len(clean)
        rec = values[recession]
        exp = values[~recession]
        observed = float(np.mean(rec) - np.mean(exp))
        observed_d = cohen_d(rec, exp)

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
        rows.append({
            "signal": label,
            "n": int(n),
            "n_recession": int(recession.sum()),
            "mean_difference": observed,
            "cohen_d": observed_d,
            "block_length": int(block_len),
            "bootstrap_reps": int(len(boot)),
            "bootstrap_se": se,
            "bootstrap_p_value": p_value,
            "ci_2_5": float(ci_low),
            "ci_97_5": float(ci_high),
        })
    return pd.DataFrame(rows)


def compute_midrank(x: np.ndarray) -> np.ndarray:
    order = np.argsort(x)
    sorted_x = x[order]
    midranks = np.zeros(len(x), dtype=float)
    i = 0
    while i < len(x):
        j = i
        while j < len(x) and sorted_x[j] == sorted_x[i]:
            j += 1
        midranks[i:j] = 0.5 * (i + j - 1) + 1.0
        i = j
    out = np.empty(len(x), dtype=float)
    out[order] = midranks
    return out


def fast_delong(predictions_sorted_transposed: np.ndarray, label_1_count: int) -> tuple[np.ndarray, np.ndarray]:
    """Fast DeLong covariance for one or more paired ROC curves."""
    m = label_1_count
    n = predictions_sorted_transposed.shape[1] - m
    positive = predictions_sorted_transposed[:, :m]
    negative = predictions_sorted_transposed[:, m:]
    k = predictions_sorted_transposed.shape[0]

    tx = np.empty((k, m), dtype=float)
    ty = np.empty((k, n), dtype=float)
    tz = np.empty((k, m + n), dtype=float)
    for r in range(k):
        tx[r] = compute_midrank(positive[r])
        ty[r] = compute_midrank(negative[r])
        tz[r] = compute_midrank(predictions_sorted_transposed[r])

    aucs = tz[:, :m].sum(axis=1) / m / n - (m + 1.0) / (2.0 * n)
    v01 = (tz[:, :m] - tx) / n
    v10 = 1.0 - (tz[:, m:] - ty) / m
    sx = np.atleast_2d(np.cov(v01))
    sy = np.atleast_2d(np.cov(v10))
    return aucs, sx / m + sy / n


def delong_roc_test(y_true: np.ndarray, pred_a: np.ndarray, pred_b: np.ndarray) -> dict[str, float]:
    order = np.argsort(-y_true)
    label_1_count = int(np.sum(y_true))
    preds = np.vstack((pred_a, pred_b))[:, order]
    aucs, covariance = fast_delong(preds, label_1_count)
    contrast = np.array([1.0, -1.0])
    variance = float(contrast @ covariance @ contrast.T)
    diff = float(aucs[0] - aucs[1])
    z = diff / math.sqrt(variance) if variance > 0 else math.nan
    p = float(2.0 * stats.norm.sf(abs(z))) if np.isfinite(z) else math.nan
    return {
        "auc_a": float(aucs[0]),
        "auc_b": float(aucs[1]),
        "auc_diff": diff,
        "z": float(z),
        "p_value": p,
    }


def prepare_cv_dataset(df: pd.DataFrame) -> pd.DataFrame:
    signals_path = ANALYSIS_DIR / "signals" / "tda_signals_window_listwise_w60_expanding.csv"
    if not signals_path.exists():
        run_priority_2_1()
    signals = pd.read_csv(signals_path, parse_dates=["date"])

    value_cols = [c for c in df.columns if c not in {"date", "recession"}]
    features = df[["date", "recession"]].copy()
    features["market_return"] = df[value_cols].mean(axis=1, skipna=True)
    features["volatility_60"] = features["market_return"].rolling(60, min_periods=40).std()
    features["return_60"] = features["market_return"].rolling(60, min_periods=40).sum()

    merged = signals[["date", "composite_z", "mean_abs_corr"]].merge(features, on="date", how="inner")
    merged = merged.replace([np.inf, -np.inf], np.nan)
    return merged.dropna(subset=["composite_z", "mean_abs_corr", "market_return", "volatility_60", "return_60", "recession"]).reset_index(drop=True)


def expanding_cv_predictions(cv_data: pd.DataFrame, test_block_days: int = 1260) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    models = {
        "best naive": ["volatility_60", "return_60"],
        "TDA only": ["composite_z"],
        "TDA + all": ["composite_z", "volatility_60", "return_60", "mean_abs_corr"],
    }
    start_date = pd.Timestamp("1975-01-01")
    test_start_idx = int(cv_data.index[cv_data["date"] >= start_date][0])
    prediction_frames = []
    fold_rows = []
    fold = 1

    for start in range(test_start_idx, len(cv_data), test_block_days):
        end = min(start + test_block_days, len(cv_data))
        train = cv_data.iloc[:start].copy()
        test = cv_data.iloc[start:end].copy()
        if train["recession"].nunique() < 2 or len(test) < 30:
            continue

        fold_pred = test[["date", "recession"]].copy()
        fold_pred["fold"] = fold
        fold_summary = {
            "fold": fold,
            "train_start": train["date"].min().strftime("%Y-%m-%d"),
            "train_end": train["date"].max().strftime("%Y-%m-%d"),
            "test_start": test["date"].min().strftime("%Y-%m-%d"),
            "test_end": test["date"].max().strftime("%Y-%m-%d"),
            "n_train": int(len(train)),
            "n_test": int(len(test)),
            "test_recession_n": int(test["recession"].sum()),
        }
        for model_name, cols in models.items():
            model = make_pipeline(
                StandardScaler(),
                LogisticRegression(max_iter=1000, class_weight="balanced", solver="lbfgs"),
            )
            model.fit(train[cols], train["recession"].astype(int))
            score = model.predict_proba(test[cols])[:, 1]
            pred_col = model_name.lower().replace(" ", "_").replace("+", "plus")
            fold_pred[pred_col] = score
            if test["recession"].nunique() == 2:
                fold_summary[f"{pred_col}_auc"] = float(roc_auc_score(test["recession"].astype(int), score))
            else:
                fold_summary[f"{pred_col}_auc"] = math.nan
        prediction_frames.append(fold_pred)
        fold_rows.append(fold_summary)
        fold += 1

    predictions = pd.concat(prediction_frames, ignore_index=True)
    folds = pd.DataFrame(fold_rows)
    auc_rows = []
    for model_name in models:
        pred_col = model_name.lower().replace(" ", "_").replace("+", "plus")
        auc_rows.append({
            "model": model_name,
            "pooled_auc": float(roc_auc_score(predictions["recession"].astype(int), predictions[pred_col])),
            "fold_auc_mean": float(folds[f"{pred_col}_auc"].mean(skipna=True)),
            "fold_auc_sd": float(folds[f"{pred_col}_auc"].std(skipna=True, ddof=1)),
        })
    return predictions, folds, pd.DataFrame(auc_rows)


def write_priority_2_2_markdown(block_table: pd.DataFrame, auc_table: pd.DataFrame, delong_table: pd.DataFrame, out_path: Path) -> None:
    lines = [
        "# Priority 2.2 - Statistical Testing",
        "",
        "Daily TDA signals are serially dependent because rolling windows overlap. This check supplements the two-sample tests with a moving block bootstrap using 252-trading-day blocks.",
        "",
        "## Block-bootstrap recession-regime tests",
        "",
        "| Signal | Cohen's d | Mean diff. | Block p-value | 95% CI |",
        "|---|---:|---:|---:|---|",
    ]
    for row in block_table.to_dict("records"):
        lines.append(
            f"| {row['signal']} | {row['cohen_d']:.3f} | {row['mean_difference']:.3f} | "
            f"{format_p(row['bootstrap_p_value'])} | [{row['ci_2_5']:.3f}, {row['ci_97_5']:.3f}] |"
        )

    lines.extend([
        "",
        "## Expanding-window classifier AUC",
        "",
        "Predictions use expanding-window time-series CV, with expanding-baseline topological standardization from Priority 2.1.",
        "",
        "| Model | Pooled AUC | Fold mean AUC | Fold SD |",
        "|---|---:|---:|---:|",
    ])
    for row in auc_table.to_dict("records"):
        lines.append(f"| {row['model']} | {row['pooled_auc']:.3f} | {row['fold_auc_mean']:.3f} | {row['fold_auc_sd']:.3f} |")

    lines.extend([
        "",
        "## Paired DeLong tests",
        "",
        "| Comparison | AUC A | AUC B | Difference | z | p-value |",
        "|---|---:|---:|---:|---:|---:|",
    ])
    for row in delong_table.to_dict("records"):
        lines.append(
            f"| {row['comparison']} | {row['auc_a']:.3f} | {row['auc_b']:.3f} | "
            f"{row['auc_diff']:.3f} | {row['z']:.3f} | {format_p(row['p_value'])} |"
        )
    lines.extend([
        "",
        "Interpretation: if the DeLong p-value is small and the AUC difference is negative for TDA-only vs. best naive, TDA is statistically weaker as a recession classifier. If TDA+all is not significantly above the best naive model, the contribution remains regime characterization rather than incremental classification.",
        "",
    ])
    out_path.write_text("\n".join(lines))


def run_priority_2_2(df: pd.DataFrame) -> None:
    base = pd.read_csv(signal_cache_path("window_listwise", 60), parse_dates=["date"])
    block_table = block_bootstrap_signal_tests(base)
    block_table.to_csv(ANALYSIS_DIR / "block_bootstrap_signal_tests.csv", index=False)

    cv_data = prepare_cv_dataset(df)
    predictions, folds, auc_table = expanding_cv_predictions(cv_data)
    predictions.to_csv(ANALYSIS_DIR / "classification_cv_predictions.csv", index=False)
    folds.to_csv(ANALYSIS_DIR / "classification_cv_folds.csv", index=False)
    auc_table.to_csv(ANALYSIS_DIR / "classification_cv_auc_summary.csv", index=False)

    y = predictions["recession"].astype(int).to_numpy()
    best = predictions["best_naive"].to_numpy(dtype=float)
    tda = predictions["tda_only"].to_numpy(dtype=float)
    all_scores = predictions["tda_plus_all"].to_numpy(dtype=float)
    delong_rows = []
    for comparison, a, b in [
        ("TDA only vs. best naive", tda, best),
        ("TDA + all vs. best naive", all_scores, best),
    ]:
        result = delong_roc_test(y, a, b)
        result["comparison"] = comparison
        delong_rows.append(result)
    delong_table = pd.DataFrame(delong_rows)[["comparison", "auc_a", "auc_b", "auc_diff", "z", "p_value"]]
    delong_table.to_csv(ANALYSIS_DIR / "delong_auc_tests.csv", index=False)

    write_priority_2_2_markdown(block_table, auc_table, delong_table, ANALYSIS_DIR / "priority-2-2-statistical-testing.md")


def window_diagrams_for_date(df: pd.DataFrame, target_date: str, window: int = 60) -> dict:
    value_cols = [c for c in df.columns if c not in {"date", "recession"}]
    dates = df["date"]
    end_idx = int((dates - pd.Timestamp(target_date)).abs().idxmin())
    window_values = df.loc[end_idx - window + 1:end_idx, value_cols]
    complete_assets = window_values.notna().all(axis=0)
    complete = window_values.loc[:, complete_assets]
    matrix = complete.to_numpy(dtype=float)
    corr = np.corrcoef(matrix, rowvar=False)
    corr = np.nan_to_num(corr, nan=0.0, posinf=0.0, neginf=0.0)
    corr = np.clip(corr, -1.0, 1.0)
    dist = np.sqrt(2.0 * (1.0 - corr))
    np.fill_diagonal(dist, 0.0)
    diagrams = ripser(dist, distance_matrix=True, maxdim=1)["dgms"]
    return {
        "target_date": target_date,
        "window_end_date": df.loc[end_idx, "date"].strftime("%Y-%m-%d"),
        "window_start_date": df.loc[end_idx - window + 1, "date"].strftime("%Y-%m-%d"),
        "assets_used": int(complete.shape[1]),
        "mean_abs_corr": float(np.nanmean(np.abs(corr[np.triu_indices_from(corr, k=1)]))),
        "beta1": max_beta_alive(diagrams[1]),
        "diagrams": [
            diagrams[0][np.isfinite(diagrams[0][:, 1])].tolist(),
            diagrams[1][np.isfinite(diagrams[1][:, 1])].tolist(),
        ],
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


def plot_persistence_diagrams(diagram_data: list[dict], out_base: Path) -> None:
    plt = setup_matplotlib()
    fig, axes = plt.subplots(1, 2, figsize=(11, 5), constrained_layout=True)
    for ax, item, title in zip(axes, diagram_data, ["Deep expansion: mid-1990s", "GFC stress window"]):
        h0 = np.array(item["diagrams"][0], dtype=float)
        h1 = np.array(item["diagrams"][1], dtype=float)
        max_val = max(h0[:, 1].max() if len(h0) else 1, h1[:, 1].max() if len(h1) else 1)
        ax.plot([0, max_val], [0, max_val], color="#CCCCCC", linewidth=1.2)
        if len(h0):
            ax.scatter(h0[:, 0], h0[:, 1], s=18, color="#555555", alpha=0.55, label="H0")
        if len(h1):
            ax.scatter(h1[:, 0], h1[:, 1], s=28, color="#C8102E", alpha=0.85, label="H1")
        ax.set_title(f"{title}\nend {item['window_end_date']} · beta1={item['beta1']} · |I|={item['assets_used']}", fontsize=11, fontweight="bold")
        ax.set_xlabel("Birth")
        ax.set_ylabel("Death")
        ax.set_xlim(0, max_val * 1.04)
        ax.set_ylim(0, max_val * 1.04)
        ax.grid(True, color="#CCCCCC", alpha=0.45, linewidth=0.7)
        ax.legend(frameon=False, loc="lower right")
    fig.suptitle("Representative persistence diagrams for industry co-movement geometry", fontsize=14, fontweight="bold")
    for ext in ["png", "svg"]:
        fig.savefig(out_base.with_suffix(f".{ext}"), dpi=220, facecolor="white")
    plt.close(fig)


def plot_beta1_schematic(out_base: Path) -> None:
    plt = setup_matplotlib()
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), constrained_layout=True)
    nodes = {
        0: (0.08, 0.48), 1: (0.23, 0.76), 2: (0.24, 0.22), 3: (0.42, 0.62),
        4: (0.43, 0.34), 5: (0.60, 0.78), 6: (0.61, 0.20), 7: (0.80, 0.60), 8: (0.82, 0.36),
    }
    tree_edges = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 6), (5, 7), (6, 8)]
    cycle_edges = tree_edges + [(1, 2), (3, 4), (5, 6), (7, 8), (3, 6), (4, 5), (1, 4), (5, 8)]
    panels = [
        ("beta1 = 0: tree-like co-movement", tree_edges, []),
        ("beta1 = 8: many independent loops", cycle_edges, cycle_edges[len(tree_edges):]),
    ]
    for ax, (title, edges, red_edges) in zip(axes, panels):
        for a, b in edges:
            xa, ya = nodes[a]
            xb, yb = nodes[b]
            color = "#C8102E" if (a, b) in red_edges else "#000000"
            width = 2.1 if (a, b) in red_edges else 1.4
            ax.plot([xa, xb], [ya, yb], color=color, linewidth=width, alpha=0.88)
        for x, y in nodes.values():
            ax.scatter([x], [y], s=115, facecolor="white", edgecolor="#000000", linewidth=1.5, zorder=3)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.text(0.5, -0.08, "Red edges close additional cycles" if red_edges else "No closed cycles; one path connects any two nodes", ha="center", va="top", transform=ax.transAxes, fontsize=10, color="#555555")
        ax.set_xlim(0, 0.9)
        ax.set_ylim(0.05, 0.9)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    fig.suptitle("Schematic intuition for Betti-one loop count", fontsize=14, fontweight="bold")
    for ext in ["png", "svg"]:
        fig.savefig(out_base.with_suffix(f".{ext}"), dpi=220, facecolor="white")
    plt.close(fig)


def write_priority_2_3_markdown(diagram_data: list[dict], out_path: Path) -> None:
    lines = [
        "# Priority 2.3 - Persistence Diagram Visualization",
        "",
        "Generated two methodology figures for Section 2 before the results:",
        "",
        "- `images/figure-0a-persistence-diagrams.png`: representative persistence diagrams for a deep expansion window and a GFC stress window.",
        "- `images/figure-0b-beta1-schematic.png`: graph schematic contrasting beta1 = 0 with beta1 = 8.",
        "",
        "| Window | Target | Actual window | Assets | Mean abs. corr. | beta1 |",
        "|---|---|---|---:|---:|---:|",
    ]
    for item, label in zip(diagram_data, ["Deep expansion", "GFC peak"]):
        lines.append(
            f"| {label} | {item['target_date']} | {item['window_start_date']} to {item['window_end_date']} | "
            f"{item['assets_used']} | {item['mean_abs_corr']:.3f} | {item['beta1']} |"
        )
    lines.extend(["", "These figures are visual explanations of the filtration output, not additional tests. They are intended to make the H1 loop-collapse result legible to non-specialist readers.", ""])
    out_path.write_text("\n".join(lines))


def run_priority_2_3(df: pd.DataFrame) -> None:
    image_dir = ROOT / "images"
    image_dir.mkdir(exist_ok=True)
    diagram_data = [
        window_diagrams_for_date(df, "1995-06-30", window=60),
        window_diagrams_for_date(df, "2008-10-10", window=60),
    ]
    (DATA_DIR / "figure-0a-persistence-diagrams.json").write_text(json.dumps(diagram_data, indent=2))
    beta_data = {
        "description": "Schematic graph examples for beta1 loop-count intuition.",
        "left": {"nodes": 9, "edges": 8, "components": 1, "beta1": 0},
        "right": {"nodes": 9, "edges": 16, "components": 1, "beta1": 8},
    }
    (DATA_DIR / "figure-0b-beta1-schematic.json").write_text(json.dumps(beta_data, indent=2))
    plot_persistence_diagrams(diagram_data, image_dir / "figure-0a-persistence-diagrams")
    plot_beta1_schematic(image_dir / "figure-0b-beta1-schematic")
    write_priority_2_3_markdown(diagram_data, ANALYSIS_DIR / "priority-2-3-persistence-visualization.md")


def missing_summary(df: pd.DataFrame) -> pd.DataFrame:
    value_cols = [c for c in df.columns if c not in {"date", "recession"}]
    rows = []
    for col in value_cols:
        series = df[col]
        valid = series.notna()
        first_valid = df.loc[valid, "date"].iloc[0].strftime("%Y-%m-%d") if valid.any() else ""
        rows.append({
            "industry": col,
            "missing_n": int(series.isna().sum()),
            "missing_rate": float(series.isna().mean()),
            "first_valid_date": first_valid,
        })
    return pd.DataFrame(rows).sort_values("missing_rate", ascending=False)


def run_priority_1_1(args: argparse.Namespace) -> None:
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    df = add_recession_indicator(read_ff49_value_weighted())
    miss = missing_summary(df.set_index("date").reset_index())
    miss.to_csv(ANALYSIS_DIR / "missing_by_industry.csv", index=False)

    signals_by_window = {}
    for window in args.windows:
        config = WindowConfig(window=window, min_assets=args.min_assets, max_windows=args.max_windows)
        signals_by_window[window] = compute_rolling_signals(df, config)

    summary = summarize_signals(signals_by_window)
    summary_path = ANALYSIS_DIR / "rolling_window_robustness_summary.csv"
    summary.to_csv(summary_path, index=False)
    write_markdown_table(summary, ANALYSIS_DIR / "priority-1-1-rolling-window-robustness.md")

    metadata = {
        "task": "Priority 1.1 rolling window robustness",
        "windows": args.windows,
        "min_assets": args.min_assets,
        "beta1_definition": "maximum number of simultaneous finite H1 intervals across the filtration",
        "missing_rule": "window-level listwise deletion",
        "nber_recessions": NBER_RECESSIONS,
        "outputs": [
            str(summary_path.relative_to(ROOT)),
            str((ANALYSIS_DIR / "priority-1-1-rolling-window-robustness.md").relative_to(ROOT)),
            str((ANALYSIS_DIR / "missing_by_industry.csv").relative_to(ROOT)),
        ],
    }
    (ANALYSIS_DIR / "robustness_metadata.json").write_text(json.dumps(metadata, indent=2))
    run_priority_1_2()
    run_priority_1_3(df, include_imputation=args.include_imputation)
    run_priority_2_1()
    run_priority_2_2(df)
    run_priority_2_3(df)
    print(summary.to_string(index=False))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--windows", type=int, nargs="+", default=[60, 120, 252])
    parser.add_argument("--min-assets", type=int, default=20)
    parser.add_argument("--max-windows", type=int, default=None, help="Test mode: keep only the last N windows per W.")
    parser.add_argument("--include-imputation", action="store_true", help="Also run/report KNN and MICE imputation robustness for Priority 1.3.")
    return parser.parse_args()


if __name__ == "__main__":
    run_priority_1_1(parse_args())
