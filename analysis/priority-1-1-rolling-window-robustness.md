# Priority 1.1 - Rolling Window Robustness

Baseline method: rolling correlation-distance matrices with window-level listwise deletion.
For each rolling window, industries with any missing return inside the window are excluded from that window's distance matrix.
Signals are oriented so larger values are more recession-like, then standardized on expansion-day observations within each window length.

| Window | Signal | N | Recession N | Cohen's d | p-value | AUC |
|---:|---|---:|---:|---:|---:|---:|
| 60 | H0 landscape L1 | 26153 | 4218 | -0.535 | <0.001 | 0.346 |
| 60 | -H1 landscape L1 | 26153 | 4218 | 0.412 | <0.001 | 0.649 |
| 60 | -beta1 | 26153 | 4218 | 0.382 | <0.001 | 0.610 |
| 60 | -TP H0 | 26153 | 4218 | 0.653 | <0.001 | 0.691 |
| 60 | -TP H1 | 26153 | 4218 | 0.471 | <0.001 | 0.653 |
| 60 | Composite Z | 26153 | 4218 | 0.481 | <0.001 | 0.660 |
| 120 | H0 landscape L1 | 26093 | 4218 | -0.554 | <0.001 | 0.339 |
| 120 | -H1 landscape L1 | 26093 | 4218 | 0.336 | <0.001 | 0.619 |
| 120 | -beta1 | 26093 | 4218 | 0.311 | <0.001 | 0.578 |
| 120 | -TP H0 | 26093 | 4218 | 0.673 | <0.001 | 0.701 |
| 120 | -TP H1 | 26093 | 4218 | 0.409 | <0.001 | 0.625 |
| 120 | Composite Z | 26093 | 4218 | 0.410 | <0.001 | 0.631 |
| 252 | H0 landscape L1 | 25961 | 4218 | -0.403 | <0.001 | 0.375 |
| 252 | -H1 landscape L1 | 25961 | 4218 | 0.194 | <0.001 | 0.602 |
| 252 | -beta1 | 25961 | 4218 | 0.324 | <0.001 | 0.586 |
| 252 | -TP H0 | 25961 | 4218 | 0.514 | <0.001 | 0.667 |
| 252 | -TP H1 | 25961 | 4218 | 0.283 | <0.001 | 0.605 |
| 252 | Composite Z | 25961 | 4218 | 0.318 | <0.001 | 0.613 |

## β1 collapse check

- W = 60: -beta1 Cohen's d = 0.382; strongest component check: no; strongest component is -TP H0.
- W = 120: -beta1 Cohen's d = 0.311; strongest component check: no; strongest component is -TP H0.
- W = 252: -beta1 Cohen's d = 0.324; strongest component check: no; strongest component is -TP H0.

## Interpretation note

W = 60 remains the baseline only if it has the strongest or most theoretically useful recession-regime effect.
If longer windows produce comparable or stronger composite AUC/effect sizes, the manuscript should frame W = 60 as the short-horizon specification rather than the uniquely best specification.
