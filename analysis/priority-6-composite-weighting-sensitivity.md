# Composite-Weighting Sensitivity

Cached W = 60 listwise-deletion component signals are recombined three ways:

- Equal-weight baseline: the manuscript's transparent descriptive composite.
- PCA PC1: first principal component of expansion-day standardized TDA components, sign-oriented so higher values are more recession-like.
- Ledoit-Wolf min-var: covariance-stabilized minimum-variance average of the five components, fit on expansion days and not supervised by recession labels.

| Composite | N | Recession N | Cohen's d | AUC | Block-bootstrap p-value | 95% bootstrap CI |
|---|---:|---:|---:|---:|---:|---:|
| Equal-weight baseline | 26153 | 4218 | 0.481 | 0.660 | <0.001 | [0.155, 0.377] |
| PCA PC1 | 26153 | 4218 | 0.567 | 0.685 | <0.001 | [0.333, 0.743] |
| Ledoit-Wolf min-var | 26153 | 4218 | 0.480 | 0.640 | 0.022 | [0.085, 0.880] |

## Component weights

- Equal-weight baseline: H0 landscape L1: 0.200; -H1 landscape L1: 0.200; -beta1: 0.200; -TP H0: 0.200; -TP H1: 0.200.
- PCA PC1: H0 landscape L1: -0.191; -H1 landscape L1: 0.205; -beta1: 0.192; -TP H0: 0.196; -TP H1: 0.216.
- Ledoit-Wolf min-var: H0 landscape L1: 0.500; -H1 landscape L1: 0.013; -beta1: -0.013; -TP H0: 0.499; -TP H1: 0.002.

## Interpretation

The strongest unsupervised composite in this run is PCA PC1 (d = 0.567, AUC = 0.685). The equal-weight baseline remains positive and significant (d = 0.481, AUC = 0.660), so the main result is not an artifact of a tuned weighting scheme. PCA PC1 strengthens the recession separation (d = 0.567, AUC = 0.685), largely by assigning negative weight to the H0 fragmentation component and positive weight to the loop/persistence compression components. The Ledoit-Wolf minimum-variance composite also remains positive (d = 0.480, AUC = 0.640) but has weaker rank separation and a wider block-bootstrap interval. This supports keeping equal weighting as the transparent main specification while reporting PCA and shrinkage composites as robustness checks.
