# Topological Early Warning Signals in U.S. Industry Portfolios

**Authors:** Nik Bear Brown and Milivoje Davidovic  
**Status:** Draft paper in progress  
**Started:** 2026-05-26  
**Main draft:** `chapters/TDA_Industry_Portfolios_Draft.md`

This repository contains the working paper, data, analysis outputs, D3 figures, static figures, and scripts for a draft empirical paper on topological data analysis (TDA) of daily Fama-French 49 industry portfolio returns.

The coding and robustness bottleneck is mostly cleared. The next major decision is editorial: whether to shape the paper as a full empirical finance paper, a short finance letter, or a TDA/complex-systems paper.

## Decision Needed

Milivoje Davidovic is the economics/domain expert on the paper. The current draft puts his decision gate at the top:

1. **Full paper route:** tighten for *Journal of Empirical Finance*.
2. **Short letter route:** trim hard for *Finance Research Letters*, probably moving macro-predictive and crisis-type material to an appendix.
3. **TDA/complex-systems route:** shape for *Physica A*, emphasizing topology and financial-system geometry.

Once that route is chosen, the draft should be revised toward one audience rather than trying to satisfy all three.

## Current Abstract

This paper applies persistent homology to daily Fama-French 49 industry portfolio returns over the period July 1926-March 2026 to characterize how the topology of industry co-movement evolves across NBER recession and expansion regimes. Using 60-trading-day rolling Vietoris-Rips filtrations on correlation-distance matrices, I construct five oriented topological signals: H0 and H1 landscape norms, the inverse Betti-one count, and total persistence for H0 and H1. These are combined into a composite recession-topology indicator.

The central finding is that industry co-movement topology simplifies during recessions. Loop structure collapses, as measured by a statistically significant decline in beta1 (Cohen's d = 0.382, block-bootstrap p < 0.001), and the composite topological signal is elevated in recession windows relative to expansions (Cohen's d = 0.481, block-bootstrap p < 0.001).

Cross-validated recession classification using TDA alone yields AUC = 0.559, below a simple volatility-plus-returns benchmark (AUC = 0.773). TDA does not add incremental classification power over conventional signals. However, the topological signal is not merely average correlation in disguise: after residualizing composite Z on mean absolute correlation, the residual still predicts recession-regime membership (Cohen's d = 0.288, block-bootstrap p = 0.025). The contribution is a geometric characterization of recession-regime co-movement structure, not a forecasting system.

## Current Introduction

The paper starts from a gap in the finance/TDA literature. Asset-return correlations across regimes are well studied, but the shape of cross-industry dependence has received less attention. Average pairwise correlation and rolling covariance summarize co-movement intensity but discard geometric organization. Two systems can have similar average correlations while having different topology: isolated clusters, hub-like structures, or loop-like dependencies.

Persistent homology provides a way to measure this shape. Prior TDA-finance work has studied equity indices, short crisis windows, financial bubbles, and lower-frequency financial series. This draft extends that work to the cross-sectional industry dimension using a century-scale daily panel.

The paper asks three questions:

1. Does industry co-movement topology differ systematically between NBER recession and expansion regimes?
2. If so, does it improve recession classification beyond conventional risk signals?
3. Does topology capture information beyond average cross-industry correlation?

The current answer is: yes to the first, no to the second, and yes with qualification to the third.

## Current Methods

The empirical sample is daily value-weighted Fama-French 49 industry portfolio returns from July 1, 1926 through March 31, 2026.

For each trading day, the baseline pipeline:

1. Computes a rolling cross-industry correlation matrix using a 60-trading-day window.
2. Converts correlation to distance using `d(i,j) = sqrt(2 * (1 - rho_ij))`.
3. Applies Vietoris-Rips persistent homology with Ripser up to dimension 1.
4. Extracts five scalar topological summaries:
   - H0 persistence landscape L1 norm
   - H1 persistence landscape L1 norm
   - beta1 loop count
   - total persistence H0
   - total persistence H1
5. Orients the signals so larger values are more recession-like.
6. Standardizes signals on expansion-day observations.
7. Forms an equal-weight composite topological signal.

The draft also includes:

- Representative persistence diagrams.
- A beta1 graph schematic for non-specialist readers.
- Expanding-window classification protocol to avoid look-ahead bias.
- Block-bootstrap tests for serially dependent daily TDA signals.
- DeLong AUC tests for classifier comparisons.
- PCA and Ledoit-Wolf shrinkage composite-weighting sensitivity.

## Current Results

### Main recession-regime result

The baseline W = 60 results show recession topology is primarily compression/loop dissolution, not fragmentation:

| Signal | Cohen's d | AUC | Read |
|---|---:|---:|---|
| H0 landscape L1 | -0.535 | 0.346 | Opposite sign |
| -H1 landscape L1 | 0.412 | 0.649 | Positive |
| -beta1 | 0.382 | 0.610 | Loop collapse |
| -TP H0 | 0.653 | 0.691 | Strongest component |
| -TP H1 | 0.471 | 0.653 | Positive |
| Composite Z | 0.481 | 0.660 | Main signal |

### Robustness

- **Window length:** W = 60 is the baseline. W = 120 and W = 252 preserve the qualitative loop/persistence-compression pattern but attenuate the composite effect.
- **Post-1970 full-coverage sample:** Composite remains positive (d = 0.404, AUC = 0.614).
- **Missing data:** Dropping the seven high-missing industries, KNN imputation, and MICE imputation preserve sign/significance but attenuate magnitude.
- **Look-ahead standardization:** Expanding prior expansion baseline does not weaken the result (composite d = 0.531, AUC = 0.676).
- **Composite weighting:** PCA PC1 strengthens separation (d = 0.567, AUC = 0.685); Ledoit-Wolf minimum-variance composite remains positive but noisier (d = 0.480, AUC = 0.640).

### Classification

The best naive classifier, volatility plus lagged returns, outperforms TDA:

| Model | Pooled AUC | Fold mean AUC | Fold SD |
|---|---:|---:|---:|
| Naive: volatility + returns | 0.773 | 0.768 | 0.127 |
| TDA only | 0.559 | 0.628 | 0.152 |
| TDA + volatility + returns + correlation | 0.716 | 0.764 | 0.121 |

DeLong tests reject equality versus the best naive model for both TDA-only and TDA-plus-all. The paper should not claim superior recession classification.

### Distinctness from average correlation

Composite Z is correlated with mean absolute correlation (corr = 0.520), and mean absolute correlation explains 27.0% of composite-Z variation. But the residual topological signal remains associated with recession membership:

- Residual recession Cohen's d = 0.288
- Block-bootstrap p = 0.025
- AUC mean absolute correlation = 0.628
- AUC composite Z = 0.660
- AUC mean correlation + TDA residual = 0.674

This is the strongest incremental contribution claim currently in the paper.

### Macro prediction and crisis-type heterogeneity

The industrial-production regressions do not establish macro-predictive content. The composite signal is borderline at the one-month horizon and insignificant at longer horizons. This is framed as a negative/boundary result.

Crisis-type heterogeneity is exploratory. Financial-crisis days have slightly higher raw composite Z, but the effect reverses after residualizing volatility and is not significant at the episode level.

## Current Conclusion

The current conclusion is deliberately restrained. TDA provides a shape-based characterization of recession-regime co-movement that conventional averages do not fully capture. It should not be sold as a forecasting system. The defensible contribution is geometric: industry co-movement topology simplifies during recessions, and part of that topology is distinct from mean absolute correlation.

## Repository Map

```text
chapters/
  TDA_Industry_Portfolios_Draft.md
    Main working paper. Includes Milivoje decision gate, abstract, introduction,
    methods, results, robustness section, limitations, conclusion, references,
    and completed-analysis inventory.

data/
  49_Industry_Portfolios_Daily.csv
    Local copy of the Fama-French 49 daily industry return data.
  49_Industry_Portfolios_daily_CSV.zip
    Original downloaded archive.
  figure-*.json
    Data payloads for D3 and static figure generation.

analysis/
  *.md
    Human-readable reports for robustness priorities and submission prep.
  *.csv
    Machine-readable analysis outputs: rolling-window robustness, missingness,
    classification folds, DeLong tests, composite weighting, crisis-type tests,
    and episode-aligned data.
  signals/
    Cached rolling TDA signal series. These avoid recomputing persistent
    homology every time a downstream robustness table is refreshed.

d3/
  figure-*.html
    Browser-runnable interactive D3 figures.
  README.md
    Figure-specific notes.

images/
  figure-*.png
  figure-*.svg
    Static figures used by the paper draft. SVGs are converted to PNG for
    document/export workflows.

SCRIPTS/
  run_tda_robustness.py
    Main TDA robustness pipeline. Computes rolling persistent-homology signals,
    rolling-window comparisons, post-1970 sensitivity, missing-value robustness,
    look-ahead standardization checks, block bootstrap tests, classification CV,
    and DeLong AUC comparisons.
  run_priority_3.py
    Results-strengthening script. Runs crisis-type heterogeneity checks and
    tests whether TDA contains information beyond mean absolute correlation.
  run_priority_4.py
    Figure/writing support script. Produces episode-aligned composite-Z outputs.
  run_composite_sensitivity.py
    Composite-weighting sensitivity. Recombines cached W = 60 component signals
    as equal-weight, PCA PC1, and Ledoit-Wolf minimum-variance composites.
  generate-neu-d3-figures.mjs
    Generates/updates NEU-styled D3 figure files and companion figure data.
  svg-to-png.mjs
    Converts SVG figures in `images/` to PNG.

package.json
  npm task runner for the scripts above.
```

## Key Analysis Outputs

| File | Purpose |
|---|---|
| `analysis/rolling_window_robustness_summary.csv` | W = 60/120/252 signal-level Cohen's d and AUC |
| `analysis/early_sample_sensitivity_table.csv` | Full sample vs post-1970 robustness |
| `analysis/missing_by_industry.csv` | Industry missingness, rates, and first valid dates |
| `analysis/missing_value_robustness_table.csv` | Listwise/drop-seven/KNN/MICE robustness |
| `analysis/lookahead_standardization_comparison.csv` | Retrospective vs expanding standardization |
| `analysis/block_bootstrap_signal_tests.csv` | 252-trading-day block bootstrap tests |
| `analysis/classification_cv_auc_summary.csv` | Expanding-window classification AUC summary |
| `analysis/classification_cv_folds.csv` | Fold structure for classification CV |
| `analysis/delong_auc_tests.csv` | DeLong AUC tests versus best naive benchmark |
| `analysis/priority-3-tda-vs-correlation.csv` | TDA vs mean absolute correlation analysis |
| `analysis/priority-3-tda-residual-block-bootstrap.csv` | Block bootstrap for residual topology |
| `analysis/priority-3-financial-crisis-tests.csv` | Crisis-type heterogeneity tests |
| `analysis/composite_weighting_sensitivity.csv` | Equal/PCA/Ledoit-Wolf composite results |
| `analysis/composite_weighting_weights.csv` | Component weights for alternative composites |

## Commands

Create the Python environment and install the needed packages before running the analysis scripts. The current local environment is `.venv/`.

```bash
npm install
```

Run the main robustness pipeline:

```bash
npm run robustness
```

Run missing-data imputation robustness too:

```bash
npm run robustness -- --include-imputation
```

Run Priority 3 results-strengthening analysis:

```bash
npm run priority-3
```

Run Priority 4 figure/writing support:

```bash
npm run priority-4
```

Run composite-weighting sensitivity:

```bash
npm run composite-sensitivity
```

Regenerate D3 figure files:

```bash
npm run generate-d3
```

Convert SVG figures to PNG:

```bash
npm run svg-to-png
```

Build document output:

```bash
./build.sh
```

Build artifacts go to `output/`, which is gitignored.

## Notes for the Next Revision

The next revision should not add more analyses by default. It should first choose the target route:

- For *Journal of Empirical Finance*: tighten identification language, keep the robustness section, and make the average-correlation residual result central.
- For *Finance Research Letters*: compress to the main empirical fact plus one robustness table.
- For *Physica A*: foreground the TDA geometry, persistence diagrams, beta1 schematic, and complex-systems interpretation.

The current paper is strongest when it says: topology characterizes recession-regime co-movement geometry. It is weakest when it sounds like a forecasting paper.
