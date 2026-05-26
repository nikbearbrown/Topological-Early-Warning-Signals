# Priority 3 - Results Strengthening and Framing

## 3.1 Macro-predictive section decision

Decision: keep the industrial-production regressions only as a negative-result subsection. Do not present Table 3 as a standalone contribution. The current evidence is too weak for a macro-predictive claim; its value is as a boundary condition on the paper's scope.

Recommended framing: TDA characterizes recession-regime co-movement geometry. It does not, in the current evidence, forecast macroeconomic activity better than conventional return and volatility measures.

## 3.2 Crisis-type heterogeneity

| Episode | Type | During mean Z | Pre mean Z | Elevation | Peak Z | Disruption |
|---|---|---:|---:|---:|---:|---:|
| 1929-1933 | financial | 0.406 | 0.242 | 0.164 | 0.776 | 457.0 |
| 1937-1938 | demand | 0.475 | 0.185 | 0.290 | 0.713 | 154.4 |
| 1945 | supply/monetary | 0.403 | 0.451 | -0.048 | 0.680 | 76.5 |
| 1948-1949 | demand | 0.432 | 0.441 | -0.010 | 0.709 | 112.1 |
| 1953-1954 | demand | 0.217 | 0.288 | -0.071 | 0.562 | 61.7 |
| 1957-1958 | demand | 0.495 | 0.060 | 0.434 | 0.714 | 83.6 |
| 1960-1961 | demand | 0.006 | 0.172 | -0.165 | 0.552 | 51.8 |
| 1969-1970 | supply/monetary | 0.102 | 0.129 | -0.027 | 0.509 | 37.5 |
| 1973-1975 | supply/monetary | 0.352 | 0.246 | 0.106 | 0.637 | 118.4 |
| 1980 | supply/monetary | 0.162 | 0.324 | -0.162 | 0.504 | 25.9 |
| 1981-1982 | supply/monetary | 0.194 | -0.046 | 0.241 | 0.499 | 71.9 |
| 1990-1991 | financial | -0.035 | 0.326 | -0.361 | 0.452 | 13.1 |
| 2001 | demand | -0.620 | -1.785 | 1.165 | 0.240 | 1.1 |
| 2007-2009 | financial | 0.225 | 0.110 | 0.115 | 0.548 | 89.6 |
| 2020 | financial | 0.090 | -0.439 | 0.529 | 0.412 | 6.2 |

### Financial-crisis test

| Test | Financial mean | Other mean | Difference | Cohen's d | p-value |
|---|---:|---:|---:|---:|---:|
| recession-day composite Z | 0.312 | 0.233 | 0.079 | 0.225 | <0.001 |
| recession-day composite Z after residualizing volatility | -0.014 | 0.009 | -0.024 | -0.070 | 0.017 |
| episode-level elevation vs pre-recession | 0.112 | 0.159 | -0.047 | -0.125 | 0.834 |

Interpretation: the narrative financial-crisis classification produces only a small raw recession-day elevation in the composite topological signal. The effect reverses after residualizing 60-day volatility, and the episode-level elevation test is not a stable finding. This is a useful negative result: the current evidence does not support making crisis-type heterogeneity a central contribution.

## 3.3 Distinctness from average correlation

| Metric | Value |
|---|---:|
| corr(composite_z, mean_abs_corr) | 0.520 |
| R2 composite_z ~ mean_abs_corr | 0.270 |
| residual recession Cohen d | 0.288 |
| residual Welch p-value | 0.000 |
| AUC mean_abs_corr | 0.628 |
| AUC composite_z | 0.660 |
| AUC residual_vs_corr | 0.579 |
| AUC logit mean_abs_corr | 0.628 |
| AUC logit mean_abs_corr + TDA residual | 0.674 |

### Block-bootstrap residual test

After regressing composite Z on mean absolute correlation, the residual still has recession Cohen's d = 0.288 with block-bootstrap p-value 0.025.

Interpretation: if the residual effect remains positive and statistically non-random, the topology signal is not merely a renamed average-correlation measure. If the effect is small, the contribution should still be stated carefully: TDA adds a geometric decomposition of co-movement, but the strongest empirical variation is shared with conventional correlation intensity.
