#!/usr/bin/env python3
"""Priority 4 writing/figure support.

Generates an episode-aligned composite-Z figure from the real W=60 signal file
and writes a small figure audit note for the manuscript checklist.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

from run_tda_robustness import ANALYSIS_DIR, DATA_DIR, NBER_RECESSIONS, ROOT, signal_cache_path


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
    if label == "Global Financial Crisis":
        return "2007-2009"
    if label == "COVID recession":
        return "2020"
    return label.replace(" recession", "")


def build_episode_panel(signals: pd.DataFrame) -> pd.DataFrame:
    records = []
    for start, end, label in NBER_RECESSIONS:
        start_ts = pd.Timestamp(start)
        end_ts = pd.Timestamp(end)
        window = signals[(signals["date"] >= start_ts - pd.Timedelta(days=126)) & (signals["date"] <= end_ts + pd.Timedelta(days=126))].copy()
        if window.empty:
            continue
        window["trading_day_from_onset"] = np.arange(len(window)) - int((window["date"] < start_ts).sum())
        window["calendar_day_from_onset"] = (window["date"] - start_ts).dt.days
        window["phase"] = np.where(window["date"] < start_ts, "pre", np.where(window["date"] <= end_ts, "during", "post"))
        window["episode"] = label
        window["episode_short"] = episode_short_label(label)
        records.append(window[["episode", "episode_short", "date", "calendar_day_from_onset", "trading_day_from_onset", "phase", "composite_z"]])
    return pd.concat(records, ignore_index=True)


def plot_episode_panel(panel: pd.DataFrame, out_base: Path) -> None:
    plt = setup_matplotlib()
    episodes = panel["episode_short"].drop_duplicates().tolist()
    ncols = 3
    nrows = int(np.ceil(len(episodes) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(12, 14), sharex=True, sharey=True, constrained_layout=True)
    axes_flat = axes.flatten()
    for ax, episode in zip(axes_flat, episodes):
        group = panel[panel["episode_short"] == episode]
        ax.axvspan(0, group.loc[group["phase"] == "during", "trading_day_from_onset"].max(), color="#C8102E", alpha=0.08, linewidth=0)
        ax.axvline(0, color="#C8102E", linewidth=1.0)
        ax.axhline(0, color="#CCCCCC", linewidth=0.8)
        ax.plot(group["trading_day_from_onset"], group["composite_z"], color="#000000", linewidth=1.1)
        ax.set_title(episode, fontsize=10, fontweight="bold")
        ax.set_xlim(-126, 252)
        ax.grid(True, color="#CCCCCC", alpha=0.35, linewidth=0.55)
    for ax in axes_flat[len(episodes):]:
        ax.axis("off")
    fig.supxlabel("Trading days from recession onset")
    fig.supylabel("Composite Z")
    fig.suptitle("Composite TDA signal by recession episode, aligned to onset", fontsize=15, fontweight="bold")
    for ext in ["png", "svg"]:
        fig.savefig(out_base.with_suffix(f".{ext}"), dpi=220, facecolor="white")
    plt.close(fig)


def main() -> None:
    signals = pd.read_csv(signal_cache_path("window_listwise", 60), parse_dates=["date"])
    panel = build_episode_panel(signals)
    panel.to_csv(ANALYSIS_DIR / "priority-4-episode-aligned-composite-z.csv", index=False)
    (DATA_DIR / "figure-8-episode-aligned-composite-z.json").write_text(json.dumps({
        "notes": "Composite Z by NBER recession episode, aligned to recession onset; derived from W=60 listwise TDA signal file.",
        "episodes": panel["episode_short"].drop_duplicates().tolist(),
        "rows": panel.assign(date=panel["date"].dt.strftime("%Y-%m-%d")).to_dict("records"),
    }, indent=2))
    image_dir = ROOT / "images"
    image_dir.mkdir(exist_ok=True)
    plot_episode_panel(panel, image_dir / "figure-8-episode-aligned-composite-z")

    figure2_payload = json.loads((DATA_DIR / "figure-2-tda-crisis-signals.json").read_text())
    heatmap_payload = json.loads((DATA_DIR / "figure-5-recession-episode-heatmap.json").read_text())
    lines = [
        "# Priority 4 Figure Audit",
        "",
        f"- Figure 2 companion JSON recession bands: {len(figure2_payload.get('recessions', []))}; expected NBER episodes in sample: {len(NBER_RECESSIONS)}.",
        f"- Existing heatmap companion JSON episodes: {len(heatmap_payload.get('episodes', []))}; it omits the Great Depression because it was generated as visual companion data, not the authoritative analysis panel.",
        "- New episode-aligned panel generated from the real W=60 signal file: `images/figure-8-episode-aligned-composite-z.png`.",
        "",
    ]
    (ANALYSIS_DIR / "priority-4-figure-audit.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
