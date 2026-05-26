# Priority 2.2 - Statistical Testing

Daily TDA signals are serially dependent because rolling windows overlap. This check supplements the two-sample tests with a moving block bootstrap using 252-trading-day blocks.

## Block-bootstrap recession-regime tests

| Signal | Cohen's d | Mean diff. | Block p-value | 95% CI |
|---|---:|---:|---:|---|
| H0 landscape L1 | -0.535 | -0.523 | <0.001 | [-0.778, -0.273] |
| -H1 landscape L1 | 0.412 | 0.391 | <0.001 | [0.204, 0.560] |
| -beta1 | 0.382 | 0.364 | <0.001 | [0.172, 0.552] |
| -TP H0 | 0.653 | 0.640 | <0.001 | [0.392, 0.877] |
| -TP H1 | 0.471 | 0.446 | <0.001 | [0.255, 0.641] |
| Composite Z | 0.481 | 0.264 | <0.001 | [0.141, 0.377] |

## Expanding-window classifier AUC

Predictions use expanding-window time-series CV, with expanding-baseline topological standardization from Priority 2.1.

| Model | Pooled AUC | Fold mean AUC | Fold SD |
|---|---:|---:|---:|
| best naive | 0.773 | 0.768 | 0.127 |
| TDA only | 0.559 | 0.628 | 0.152 |
| TDA + all | 0.716 | 0.764 | 0.121 |

## Paired DeLong tests

| Comparison | AUC A | AUC B | Difference | z | p-value |
|---|---:|---:|---:|---:|---:|
| TDA only vs. best naive | 0.559 | 0.773 | -0.214 | -24.249 | <0.001 |
| TDA + all vs. best naive | 0.716 | 0.773 | -0.057 | -17.280 | <0.001 |

Interpretation: if the DeLong p-value is small and the AUC difference is negative for TDA-only vs. best naive, TDA is statistically weaker as a recession classifier. If TDA+all is not significantly above the best naive model, the contribution remains regime characterization rather than incremental classification.
