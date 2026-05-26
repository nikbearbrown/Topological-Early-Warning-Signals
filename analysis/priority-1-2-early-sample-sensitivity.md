# Priority 1.2 - Early-Sample Sensitivity

Baseline signal file: `analysis/signals/tda_signals_window_listwise_w60.csv`.
The post-1970 panel keeps observations with window end dates on or after 1970-01-01.

| Panel | Signal | N | Recession N | Cohen's d | p-value | AUC |
|---|---|---:|---:|---:|---:|---:|
| Full sample | H0 landscape L1 | 26153 | 4218 | -0.535 | <0.001 | 0.346 |
| Full sample | -H1 landscape L1 | 26153 | 4218 | 0.412 | <0.001 | 0.649 |
| Full sample | -beta1 | 26153 | 4218 | 0.382 | <0.001 | 0.610 |
| Full sample | -TP H0 | 26153 | 4218 | 0.653 | <0.001 | 0.691 |
| Full sample | -TP H1 | 26153 | 4218 | 0.471 | <0.001 | 0.653 |
| Full sample | Composite Z | 26153 | 4218 | 0.481 | <0.001 | 0.660 |
| Post-1970 | H0 landscape L1 | 14182 | 1768 | -0.694 | <0.001 | 0.296 |
| Post-1970 | -H1 landscape L1 | 14182 | 1768 | 0.405 | <0.001 | 0.626 |
| Post-1970 | -beta1 | 14182 | 1768 | 0.255 | <0.001 | 0.558 |
| Post-1970 | -TP H0 | 14182 | 1768 | 0.684 | <0.001 | 0.703 |
| Post-1970 | -TP H1 | 14182 | 1768 | 0.436 | <0.001 | 0.625 |
| Post-1970 | Composite Z | 14182 | 1768 | 0.404 | <0.001 | 0.614 |

## Sensitivity read

- H0 landscape L1: full d = -0.535, post-1970 d = -0.694, delta = -0.158 (same sign).
- -H1 landscape L1: full d = 0.412, post-1970 d = 0.405, delta = -0.008 (same sign).
- -beta1: full d = 0.382, post-1970 d = 0.255, delta = -0.127 (same sign).
- -TP H0: full d = 0.653, post-1970 d = 0.684, delta = 0.031 (same sign).
- -TP H1: full d = 0.471, post-1970 d = 0.436, delta = -0.035 (same sign).
- Composite Z: full d = 0.481, post-1970 d = 0.404, delta = -0.077 (same sign).

The composite result is qualitatively similar after 1970, so the early-sample caveat is measurement caution rather than a substantive reversal.
