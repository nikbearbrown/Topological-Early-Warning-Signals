# D3 Figures

Interactive browser-runnable D3 v7 figures for this book.

Each file is a standalone HTML file — open directly in a browser, no build step.

## Current figures

| Figure | File | Data source | Status |
| --- | --- | --- | --- |
| Figure 1: Mean absolute cross-industry correlation | `figure-1-mean-absolute-correlation.html` | `../data/figure-1-yearly-correlation.json` | Recreated from the downloaded Kenneth R. French FF49 daily portfolio CSV |
| Figure 2: TDA crisis signals across recession regimes | `figure-2-tda-crisis-signals.html` | `../data/figure-2-tda-crisis-signals.json` | Generated companion data matching manuscript signal descriptions |
| Figure 3: Composite TDA signal lead cross-correlation | `figure-3-lead-cross-correlation.html` | `../data/figure-3-lead-cross-correlation.json` | Generated companion data matching manuscript lead-time description |
| Figure 4: Composite TDA signal around recession onset | `figure-4-recession-event-study.html` | `../data/figure-4-recession-event-study.json` | Generated companion data matching manuscript event-study description |
| Figure 5: Composite TDA signal by recession episode | `figure-5-recession-episode-heatmap.html` | `../data/figure-5-recession-episode-heatmap.json` | Generated companion data split from the original lead-time composite panel |
| Figure 6: ROC curves for TDA and baseline classifiers | `figure-6-roc-curves.html` | `../data/figure-6-roc-curves.json` | Generated smooth ROC curves from manuscript AUC targets |

Figures 2-6 are D3 companions built under the NEU three-file system (`CLAUDE.md`, `DESIGN.md`, `VIZ.md`). Their JSON files are explicit, inspectable companion data. Replace those JSON files with the real TDA, event-study, heatmap, or ROC outputs when the original analysis artifacts are available.

## Relationship to images/

The `images/` directory currently holds static PNG versions used by the compiled EPUB.
The D3 HTML files are browser-viewable companions and can become the living source once
the matching analysis outputs are available.

## Regenerating

D3 HTML files and generated companion JSON are recreated with:

```bash
node SCRIPTS/generate-neu-d3-figures.mjs
```

SVG → PNG conversion:
```bash
node SCRIPTS/svg-to-png.mjs
```
