# Priority 1.3 - Missing Value Handling

Seven industries exceed 5% missingness in the FF49 daily value-weighted panel:

`Soda`, `Hlth`, `Rubbr`, `FabPr`, `Guns`, `Gold`, `Softw`

The robustness runs use W = 60 and compare the baseline window-level listwise deletion against fixed FF42, distance-weighted industry-KNN imputation, and pooled MICE imputations.

| Method | Signal | N | Recession N | Cohen's d | p-value | AUC |
|---|---|---:|---:|---:|---:|---:|
| listwise deletion | H0 landscape L1 | 26153 | 4218 | -0.535 | <0.001 | 0.346 |
| listwise deletion | -H1 landscape L1 | 26153 | 4218 | 0.412 | <0.001 | 0.649 |
| listwise deletion | -beta1 | 26153 | 4218 | 0.382 | <0.001 | 0.610 |
| listwise deletion | -TP H0 | 26153 | 4218 | 0.653 | <0.001 | 0.691 |
| listwise deletion | -TP H1 | 26153 | 4218 | 0.471 | <0.001 | 0.653 |
| listwise deletion | Composite Z | 26153 | 4218 | 0.481 | <0.001 | 0.660 |
| drop seven high-missing industries | H0 landscape L1 | 26153 | 4218 | -0.410 | <0.001 | 0.383 |
| drop seven high-missing industries | -H1 landscape L1 | 26153 | 4218 | 0.381 | <0.001 | 0.637 |
| drop seven high-missing industries | -beta1 | 26153 | 4218 | 0.334 | <0.001 | 0.595 |
| drop seven high-missing industries | -TP H0 | 26153 | 4218 | 0.459 | <0.001 | 0.633 |
| drop seven high-missing industries | -TP H1 | 26153 | 4218 | 0.432 | <0.001 | 0.640 |
| drop seven high-missing industries | Composite Z | 26153 | 4218 | 0.425 | <0.001 | 0.640 |
| KNN k=5 distance-weighted | H0 landscape L1 | 26153 | 4218 | -0.552 | <0.001 | 0.340 |
| KNN k=5 distance-weighted | -H1 landscape L1 | 26153 | 4218 | 0.346 | <0.001 | 0.600 |
| KNN k=5 distance-weighted | -beta1 | 26153 | 4218 | 0.294 | <0.001 | 0.571 |
| KNN k=5 distance-weighted | -TP H0 | 26153 | 4218 | 0.577 | <0.001 | 0.670 |
| KNN k=5 distance-weighted | -TP H1 | 26153 | 4218 | 0.393 | <0.001 | 0.602 |
| KNN k=5 distance-weighted | Composite Z | 26153 | 4218 | 0.374 | <0.001 | 0.599 |
| MICE pooled m=10 | H0 landscape L1 | 26153 | 4218 | -0.409 | <0.001 | 0.384 |
| MICE pooled m=10 | -H1 landscape L1 | 26153 | 4218 | 0.318 | <0.001 | 0.603 |
| MICE pooled m=10 | -beta1 | 26153 | 4218 | 0.365 | <0.001 | 0.605 |
| MICE pooled m=10 | -TP H0 | 26153 | 4218 | 0.441 | <0.001 | 0.627 |
| MICE pooled m=10 | -TP H1 | 26153 | 4218 | 0.387 | <0.001 | 0.619 |
| MICE pooled m=10 | Composite Z | 26153 | 4218 | 0.388 | <0.001 | 0.623 |

## Composite sensitivity

- listwise deletion: composite d = 0.481, AUC = 0.660.
- drop seven high-missing industries: composite d = 0.425, AUC = 0.640.
- KNN k=5 distance-weighted: composite d = 0.374, AUC = 0.599.
- MICE pooled m=10: composite d = 0.388, AUC = 0.623.

Interpretation: the imputation rows preserve the sign and block-bootstrap significance of the composite recession effect, but they attenuate its magnitude relative to listwise deletion. Missingness is therefore not a reversal of the main result, but it should be reported as a moderate measurement-sensitivity caveat.
