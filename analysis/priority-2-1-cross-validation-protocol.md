# Priority 2.1 - Cross-Validation Protocol and Look-Ahead Bias

## Current status

The descriptive recession-regime tables use retrospective standardization: each oriented topological signal is standardized using the full-sample expansion-day mean and standard deviation. That is acceptable for descriptive regime characterization, but it is not real-time safe for classification or forecasting claims.

For any classification table, the real-time-safe specification must use expanding-window standardization: at date t, compute the expansion baseline using only expansion-day observations observed strictly before t.

## Recommended CV scheme for Table 2

Use expanding-window time-series cross-validation with non-overlapping test blocks:

1. Sort observations by date.
2. Use an initial training span long enough to include at least 252 expansion observations after signal availability.
3. For fold k, train on all observations before the test block.
4. Test on the next contiguous block.
5. Recompute standardization using only the training history available before each test date.
6. Report fold start/end dates, recession-day counts, expansion-day counts, fold AUC, mean AUC, and standard deviation.

This is an expanding-window protocol, not random K-fold CV and not shuffled block CV.

## Generated check

This run writes `analysis/signals/tda_signals_window_listwise_w60_expanding.csv`, an expanding-baseline version of the W=60 listwise signal file.

Use the expanding file for Table 2 classification checks. Use the retrospective file for descriptive Table 1-style regime summaries.
