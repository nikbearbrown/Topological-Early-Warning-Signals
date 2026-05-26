# Topological Early Warning Signals in U.S. Industry Portfolios: Preliminary Evidence from Daily Fama–French 49 Industries

**Nik Bear Brown · Milivoje Davidovic**

*Keywords: Topological data analysis · Persistent homology · Fama–French 49 industries · Recession regimes · Betti numbers · Persistence landscapes · Financial topology*

---

## Abstract

This paper applies persistent homology to daily Fama–French 49 industry portfolio returns over the period July 1926–March 2026 to characterize how the topology of industry co-movement evolves across NBER recession and expansion regimes. Using 60-trading-day rolling Vietoris–Rips filtrations on correlation-distance matrices, I construct five oriented topological signals — H0 and H1 landscape norms, the inverse Betti-one count, and total persistence for H0 and H1 — and combine them into a composite recession-topology indicator. The central finding is that industry co-movement topology simplifies during recessions: loop structure collapses, as measured by a statistically significant decline in β1 (Cohen's *d* = 0.416, *p* < 0.001), and the composite topological signal is meaningfully elevated in recession windows relative to expansions (Cohen's *d* = 0.423, *p* < 0.001). Cross-validated recession classification using TDA alone yields AUC = 0.671, above random but below a simple volatility-plus-returns benchmark (AUC = 0.783). TDA does not add incremental classification power over conventional signals, and predictive regressions for industrial production growth produce at most borderline significance at the one-month horizon. The contribution is a geometric characterization of recession-regime co-movement structure, not a forecasting system.

---

## 1. Introduction

The behavior of asset return correlations across economic regimes has been extensively studied, but the *shape* of dependence structure — the topology of how industries relate to one another as a system — has received comparatively little attention. Standard measures such as average pairwise correlation or rolling covariance summarize the strength of co-movement but discard information about its geometric organization. Two industry systems can have identical average correlations and radically different topological structures: one fragmented into isolated clusters, another organized around a small number of interconnected hubs, a third characterized by pervasive loop-like dependencies.

Topological data analysis (TDA), and persistent homology in particular, offers tools for extracting this shape information from high-dimensional data. Applied to financial returns, TDA constructs a sequence of simplicial complexes from distance matrices and tracks the birth and death of topological features — connected components (H0) and independent loops (H1) — across filtration scales. The resulting persistence barcodes and landscape summaries carry information about co-movement geometry that is invisible to scalar correlation measures.

Prior work has demonstrated TDA's sensitivity to financial crises in equity index data (Gidea and Katz 2018), bubble formation (Akingbade et al. 2024), and general financial time series (Edelsbrunner and Harer 2010). The present paper extends this literature to the cross-sectional industry dimension, using the century-scale Fama–French 49 daily panel as the empirical foundation. Three questions motivate the analysis.

First, does industry co-movement topology exhibit systematic differences between NBER recession and expansion regimes? Second, if such differences exist, do they provide incremental recession-classification power beyond conventional risk signals? Third, does the topological signal carry predictive content for macroeconomic activity?

The answers are: yes to the first, no to the second, and weakly suggestive to the third. Together, these findings support characterizing TDA as a geometric descriptor of recession-regime structure rather than as a superior forecasting device.

The remainder of the paper is organized as follows. Section 2 describes the data and topological measurement methodology. Section 3 presents descriptive evidence. Section 4 reports estimation evidence on timing, classification, and macro prediction. Section 5 characterizes regime heterogeneity by crisis type. Section 6 discusses limitations and next steps. Section 7 concludes.

---

## 2. Data and Methodology

### 2.1 Data

The empirical analysis uses daily value-weighted returns for the Fama–French 49 industry portfolios, obtained from Kenneth French's data library. The sample spans July 1, 1926 through March 31, 2026, yielding a raw panel of 26,212 trading days × 49 industries.

**Coverage and missing data.** Total missing entries number 67,250; seven industries exceed a 5% missing-value rate. No industry exceeds 10% zero-return frequency in the full sample. Coverage by decade rises from approximately 83% in the 1920s and 87–88% in the 1930s–1950s to 94% in the 1960s, reaching 100% from the 1970s onward. This uneven coverage introduces measurement heterogeneity in the early sample that is addressed in robustness checks (Section 6).

**Recession indicator.** NBER recession dates are converted to daily frequency using the standard peak-to-trough convention. The sample covers 14 recession episodes.

### 2.2 Topological Measurement

**Rolling correlation-distance matrices.** For each trading day *t*, I compute the cross-industry correlation matrix over a rolling window of *W* = 60 trading days. The correlation matrix is converted to a distance matrix using the standard transformation *d*(*i*, *j*) = √(2(1 − ρ*ij*)), which preserves metric properties and maps correlation to Euclidean-compatible distances on [0, 2].

The choice of *W* = 60 is motivated by a window-comparison exercise: among windows of 60, 120, and 252 trading days, the 60-day window maximizes mean positive effect size for the recession-regime comparison. Longer windows are examined in robustness analysis.

**Persistent homology.** For each rolling window, I apply Vietoris–Rips persistent homology using the Ripser algorithm (Bauer 2021), computing H0 (connected components) and H1 (independent loops) up to dimension 1. The output is a persistence barcode — a multiset of intervals [*b*, *d*] recording the filtration values at which each topological feature is born and dies.

**Topological summaries.** From each barcode I extract five scalar summaries:
- *H0 landscape L¹ norm*: the L¹ norm of the H0 persistence landscape (Bubenik 2015), measuring the overall persistence of connected components.
- *H1 landscape L¹ norm*: the analogous quantity for H1 (loop structure).
- *β1*: the raw Betti-one count, i.e., the number of independent loops alive at a representative filtration threshold.
- *Total persistence H0* and *Total persistence H1*: the sum of (death − birth) lengths across all H0 and H1 features, respectively.

**Orientation and standardization.** Each signal is oriented so that higher values correspond to more crisis-like topology. The H0 landscape norm is used directly (more components → higher fragmentation). The H1 landscape norm, β1, and both total persistence measures are negated, so that loop collapse — the recession pattern — produces upward movement. All signals are standardized to the expansion-day distribution (mean 0, standard deviation 1 on expansion days). The **composite topological signal Z** is the equal-weighted average of the five oriented, standardized components.

---

## 3. Descriptive Evidence

### 3.1 Time-Series Behavior of Co-movement

Figure 1 plots the mean absolute cross-industry correlation by year. The series exhibits substantial time variation: peaks coincide with the Great Depression, the 1970s oil shocks, the Global Financial Crisis, and the COVID-19 shock, while the postwar expansion period and the 1990s bull market correspond to lower average co-movement. This variation motivates the topological approach: average correlation captures the *intensity* of co-movement, while persistent homology targets its *shape*.

![Mean absolute cross-industry correlation by year for FF49 daily industry portfolios, with major crisis episodes annotated.](images/figure-1.png)
*Figure 1: Mean Absolute Cross-Industry Correlation*

### 3.2 Topological Signals and Recession Regimes

Table 1 reports expansion means, recession means, Cohen's *d*, and two-sample *p*-values for each topological signal. The H0 landscape norm is weakly elevated in recessions (*d* = 0.059, *p* = 0.056), consistent with modest fragmentation but not statistically compelling. The loop-related signals are uniformly significant. The inverse H1 landscape norm (*d* = 0.241), the inverse β1 (*d* = 0.416), the inverse total persistence H0 (*d* = 0.363), and the inverse total persistence H1 (*d* = 0.365) are all significant at *p* < 0.001. The composite signal achieves *d* = 0.423 (*p* < 0.001).

**Table 1: Recession vs. Expansion Differences in Topological Signals**

| Signal | Expansion mean | Recession mean | Cohen's *d* | *p*-value | Read |
|---|---|---|---|---|---|
| H0 landscape L¹ | −0.000 | 0.060 | 0.059 | 0.056 | Weak/marginal |
| −H1 landscape L¹ | 0.000 | 0.229 | 0.241 | <0.001 | Significant |
| −β1 | 0.000 | 0.364 | 0.416 | <0.001 | Strongest component |
| −TP H0 | −0.000 | 0.356 | 0.363 | <0.001 | Significant |
| −TP H1 | 0.000 | 0.316 | 0.365 | <0.001 | Significant |
| Composite Z | −0.000 | 0.265 | 0.423 | <0.001 | Main signal |

*Notes: All signals standardized on expansion days. Larger values indicate more crisis-like topology. The composite is the equal-weighted average of the five oriented, standardized components.*

![Three-panel time series of TDA crisis signals for FF49 daily industry portfolios, with NBER recession bands and spike markers.](images/figure-2.png)
*Figure 2: TDA Crisis Signals Across Recession Regimes*

The dominant pattern is β1 collapse. During recessions, the number of independent loops in the industry co-movement graph falls — industries move together in a simpler, more tree-like structure, with fewer independent cycles of partial co-movement. This geometric simplification is the central empirical finding.

---

## 4. Estimation Evidence

### 4.1 Timing: Does TDA Lead Recessions?

Figure 3 plots the cross-correlation function between the composite topological signal and the NBER recession indicator at leads of up to 250 trading days, alongside an event-study plot aligned to recession onset. The cross-correlation profile shows a small positive-lag association at approximately 31 trading days (correlation ≈ 0.10), but the stronger signal is contemporaneous or post-onset. The event-study confirms: the composite Z begins rising modestly in the weeks before recession onset but the bulk of the elevation occurs during, not before, the recession window.

![Lead-time analysis for the composite TDA signal, including cross-correlation, recession-onset event study, and recession-episode heatmap.](images/figure-3.png)
*Figure 3: Composite TDA Signal Lead-Time Analysis*

This pattern rules out the TDA signal as a long-lead recession predictor. The appropriate characterization is a regime descriptor, not an early warning indicator in the forecasting sense.

### 4.2 Classification: Can TDA Identify Recession Regimes?

Table 2 reports cross-validated AUC for seven classification models using the daily NBER recession indicator as the outcome. The best naive benchmark — volatility plus lagged returns — achieves AUC = 0.783. TDA alone achieves AUC = 0.671, which is meaningfully above random (0.500) but 11.2 percentage points below the naive benchmark. Adding TDA to the full naive suite (volatility + returns + average correlation) produces AUC = 0.736, still 4.7 percentage points below the best naive model and lower than volatility-plus-returns alone.

![ROC curves comparing TDA-only, volatility-only, average-correlation-only, baseline, and TDA-plus-baseline classifiers.](images/figure-4.png)
*Figure 4: ROC Curves for TDA and Baseline Recession Classifiers*

**Table 2: Cross-Validated AUC for Recession Classification**

| Model | CV AUC | Std. dev. | Δ vs. best naive |
|---|---|---|---|
| Naive: volatility only | 0.7725 | 0.1165 | −0.0102 |
| Naive: volatility + returns | 0.7827 | 0.0911 | 0.000 |
| Naive: volatility + returns + correlation | 0.7591 | 0.0803 | −0.0236 |
| TDA only | 0.6707 | 0.1521 | −0.1119 |
| TDA + volatility | 0.7369 | 0.1138 | −0.0458 |
| TDA + volatility + returns | 0.7383 | 0.0827 | −0.0444 |
| TDA + volatility + returns + correlation | 0.7358 | 0.0737 | −0.0468 |

*Notes: Dependent variable is the daily NBER recession indicator. Time-series cross-validated AUC.*

The classification evidence is unambiguous: TDA captures a statistically meaningful recession-regime geometry, but it does not add incremental classification power beyond simple volatility-return information available at the same point in time.

### 4.3 Macro Prediction: Does TDA Forecast Economic Activity?

Table 3 reports OLS predictive regressions of future industrial production growth on the composite topological signal at horizons of 1, 3, 6, and 12 months, alongside comparable regressions for 60-day volatility and lagged monthly returns. Standard errors are Newey–West HAC throughout.

![Scatterplot panels of composite TDA signal against future industrial-production growth at one-, three-, six-, and twelve-month horizons.](images/figure-5.png)
*Figure 5: Composite TDA Signal and Future Industrial-Production Growth*

**Table 3: Predictive Regressions for Industrial Production Growth**

| Predictor | Horizon | β | *t*-stat | *p*-value | *R²* |
|---|---|---|---|---|---|
| Composite Z | 1 month | −0.00156 | −1.851 | 0.064 | 0.004 |
| Composite Z | 3 months | 0.00008 | 0.091 | 0.927 | 0.000 |
| Composite Z | 6 months | −0.00025 | −0.292 | 0.770 | 0.000 |
| Composite Z | 12 months | 0.00061 | 0.819 | 0.413 | 0.001 |
| Monthly return | 1 month | 0.00092 | 2.820 | 0.005 | 0.088 |
| Monthly return | 3 months | 0.00030 | 3.347 | 0.001 | 0.010 |

*Selected rows shown. Full table includes volatility at all horizons.*

The composite topological signal is borderline significant at the one-month horizon (*p* = 0.064) and insignificant at all longer horizons. The lagged monthly return, by contrast, is significant at one and three months and explains substantially more variance. The macro-predictive case for TDA is not established at this stage.

---

## 5. Regime Characterization: Crisis Type Heterogeneity

Table 4 classifies the 16 recession episodes in the sample into three crisis types — financial, supply/monetary, and demand-driven — and reports mean topological elevation (during-recession minus pre-recession composite Z), mean peak Z, mean duration, and a cumulative topological disruption score.

**Table 4: Topological Disruption by Crisis Type**

| Crisis type | Episodes | Mean elevation | Mean peak Z | Mean duration (days) | Mean disruption |
|---|---|---|---|---|---|
| Financial | 4 | 0.412 | 0.826 | 89.0 | 91.3 |
| Supply/monetary | 4 | −0.017 | 0.826 | 51.8 | 45.5 |
| Demand | 8 | 0.263 | 0.705 | 43.4 | 30.9 |

*Notes: One-way ANOVA for elevation: F = 1.278, p = 0.311. Kruskal–Wallis: H = 2.002, p = 0.368.*

Financial crises produce the largest elevation and disruption, which is economically intuitive: balance-sheet crises propagate through inter-industry credit and demand channels in ways that reorganize the entire co-movement geometry. Supply and monetary shocks produce narrower topological footprints. However, formal tests do not reject equality across types (ANOVA p = 0.311; Kruskal–Wallis p = 0.368), and with only 4 financial-crisis episodes the test is severely underpowered. This heterogeneity pattern is promising as a direction for further analysis but cannot be treated as a confirmed finding at this stage.

---

## 6. Discussion, Limitations, and Next Steps

### 6.1 What the Evidence Supports

The evidence supports one substantive claim: industry co-movement topology simplifies during NBER recessions. Specifically, the number of independent loops in the industry correlation graph — as measured by β1 — declines significantly, and the composite topological signal is elevated in recession windows by a medium effect size. This is a geometric characterization that complements, but does not replace, conventional co-movement measures.

The evidence does not support claiming TDA as a superior recession-forecasting device. The classification and macro-predictive analyses make this clear.

### 6.2 Limitations

**Early-sample coverage.** The 1920s and 1930s data cover only 83–88% of the 49 industries, creating measurement heterogeneity in the earliest recession episodes. Results from this period should be interpreted with caution.

**Rolling-window construction.** The 60-day window choice, while empirically motivated, means topological signals are computed from overlapping observations. Serial correlation in the resulting time series is addressed with HAC standard errors, but the window choice affects which regime transitions are captured and which are smoothed away.

**Recession labeling.** NBER recession dates are retrospectively assigned and do not correspond to real-time information. The classification exercise is therefore out-of-sample only in a time-series cross-validation sense, not in a genuine real-time forecasting sense.

**Crisis-type classification.** The assignment of recession episodes to financial, supply/monetary, and demand categories involves judgment calls that are not uniquely determined by the literature. The heterogeneity analysis should be treated as exploratory.

**No out-of-sample test on post-2000 subsample.** All results use the full 1926–2026 sample. An explicit pre-specified hold-out analysis on the post-2000 period would strengthen confidence in the regime-characterization findings.

### 6.3 Conceptual Clarification: What β1 Collapse Means

A Betti-one count of, say, 12 in an expansion window means that the industry co-movement graph contains 12 independent cycles — groups of industries that are pairwise correlated in a loop-like pattern that cannot be reduced to a spanning tree. When β1 falls to 4 in a recession window, those 8 cycles have dissolved: industries that were linked through partial, diversifying correlations are now either more uniformly correlated (merging into large connected components) or have lost the intermediate-strength co-movement links that sustained the loop structure. The result is a geometrically simpler, more "star-like" co-movement system in which conventional diversification logic is compressed.

---

## 7. Conclusion

Using a century of daily Fama–French 49 industry returns, this paper documents that the topology of industry co-movement — as measured by persistent homology of rolling correlation-distance matrices — simplifies during NBER recession regimes. The Betti-one collapse is the cleanest empirical signal. The composite topological indicator is elevated in recessions with a medium effect size and is statistically non-random, but it does not add incremental classification power over simple volatility-return benchmarks, and its macro-predictive evidence is weak. The appropriate contribution is geometric: TDA provides a shape-based characterization of recession-regime co-movement that conventional averages do not capture, and that characterization is consistent across a century of U.S. business cycles.

---

## References

Akingbade, S. W., Gidea, M., Manzi, M., and Nateghi, V. (2024). Why topological data analysis detects financial bubbles. *Communications in Nonlinear Science and Numerical Simulation*, 128, 107665.

Bauer, U. (2021). Ripser: Efficient computation of Vietoris–Rips persistence barcodes. *Journal of Applied and Computational Topology*, 5(3), 391–423.

Bubenik, P. (2015). Statistical topological data analysis using persistence landscapes. *Journal of Machine Learning Research*, 16(1), 77–102.

Edelsbrunner, H. and Harer, J. (2010). *Computational Topology: An Introduction*. American Mathematical Society.

Gidea, M. and Katz, Y. (2018). Topological data analysis of financial time series: Landscapes of crashes. *Physica A*, 491, 820–834.

---

---

# Next Steps and Todo

## Priority 1: Data and Measurement Robustness

**1.1 Rolling window robustness**
- [ ] Run all topological signals at W = 120 and W = 252 trading days
- [ ] Produce a comparison table: Cohen's *d* and AUC for each window length for all five signals and the composite
- [ ] Keep W = 60 as the baseline (best mean effect size) but report the others as robustness checks
- [ ] Check: does β1 collapse remain the strongest component across all three windows?

**1.2 Early-sample sensitivity**
- [ ] Re-run all main analyses on the 1970–2026 subsample (full industry coverage)
- [ ] Produce a two-panel Table 1: full sample vs. post-1970 subsample
- [ ] If results are qualitatively similar, report the post-1970 results as a robustness panel; if different, the early-sample caveat becomes a substantive limitation

**1.3 Missing value handling**
- [ ] Document exactly which 7 industries exceed 5% missing
- [ ] Test alternative: drop those 7 industries and re-run on FF42 (or however many remain); check if results are sensitive
- [ ] Add a data appendix table listing industry names, years of entry, and missing-value rates

---

## Priority 2: Core Identification Improvement

**2.1 Cross-validation protocol**
- [ ] Clarify the exact cross-validation scheme used for Table 2 — block CV or expanding window? Report fold structure explicitly
- [ ] Add a note on look-ahead bias: confirm that standardization uses only expansion-day data available up to time *t*, not the full-sample expansion mean
- [ ] If expansion-day standardization uses the full-sample expansion mean, re-do using an expanding-window baseline to eliminate forward-looking contamination

**2.2 Statistical testing**
- [ ] Replace (or supplement) two-sample tests with a block-bootstrap, given the serial dependence in daily TDA signals; report block-bootstrap *p*-values alongside the parametric ones
- [ ] For Table 2 (AUC), add a formal DeLong test comparing TDA-only vs. best naive and TDA+all vs. best naive

**2.3 Persistence diagram visualization**
- [ ] Produce two representative persistence diagrams: one from a deep expansion window (e.g., mid-1990s), one from the peak of the GFC
- [ ] Produce a companion schematic illustrating what β1 = 0 vs. β1 = 8 looks like as a graph — this is essential for non-specialist readers and reviewers
- [ ] Add as a figure early in Section 2 (before the results)

---

## Priority 3: Results Strengthening and Framing

**3.1 Revise or drop the macro-predictive section**
- [ ] Decision required: is Table 3 worth including in the final paper?
  - *Option A*: Drop the industrial production regressions. The evidence is too weak to support a dedicated section. Replace with additional regime-characterization content (crisis-type heterogeneity, episode-level analysis).
  - *Option B*: Reframe explicitly as a negative result — TDA does not predict IP growth — and integrate as a subsection of "what TDA does not do."
- [ ] If retained, add CPI growth, unemployment, or credit spreads as alternative macro targets; one null result is a finding, five null results establish a pattern

**3.2 Crisis-type heterogeneity — path to a real finding**
- [ ] The financial-crisis elevation pattern (mean = 0.412 vs. 0.263 for demand) is economically meaningful but statistically underpowered
- [ ] Add a within-crisis-type analysis: how does the topological signal evolve in the months leading up to, during, and following each financial crisis (GFC, S&L crisis, 1929, 2020 COVID)?
- [ ] Consider a synthetic "financial crisis indicator" based on narrative classification from Reinhart and Rogoff or similar; test whether topological elevation is systematically higher for this subset even after conditioning on volatility

**3.3 What makes TDA distinct from average correlation?**
- [ ] The current paper shows that TDA correlates with recession regimes, but does not clearly establish *what topology captures that correlation doesn't*
- [ ] Add a partial correlation analysis: regress the composite Z on mean absolute correlation; examine whether the residual still predicts recession regime membership
- [ ] If yes: TDA adds shape information beyond average co-movement strength — this is the contribution claim
- [ ] If no: the paper's contribution narrows to "a geometric description that is roughly equivalent to correlation-based measures" — still publishable, but the framing changes

---

## Priority 4: Writing and Structure

**4.1 Introduction**
- [ ] The current draft opens with motivation but lacks a clear statement of the gap in the existing TDA-finance literature
- [ ] Add 2–3 sentences on what prior TDA-finance papers have done and what they have not: most use equity indices, not cross-sectional industry returns; most use monthly data, not daily; none uses a century-long panel
- [ ] End the introduction with an explicit contribution paragraph: three numbered sentences stating what this paper establishes

**4.2 Methodology section**
- [ ] Add intuition for the Vietoris–Rips filtration — one paragraph for readers unfamiliar with TDA, linking the mathematical construction to the economic intuition
- [ ] Add a formal definition of persistence landscapes (Bubenik 2015) — currently referenced but not explained
- [ ] Clarify the equal-weighting of composite Z: why equal weights? Consider sensitivity check with PCA-based or shrinkage-based weights

**4.3 Results narration**
- [ ] The H0 signal is the weakest component (*d* = 0.059, *p* = 0.056). Either explain why fragmentation (H0) is not a recession pattern given the data, or discuss it as evidence that recession topology is primarily a loop-dissolution phenomenon rather than a connectivity-collapse phenomenon
- [ ] The recession mean for Supply/monetary crises (elevation = −0.017) means topology does *not* simplify in those episodes. This is an interesting null result — discuss it

**4.4 Figures**
- [ ] Add a persistence diagram figure (see Priority 2.3)
- [ ] Add a β1 schematic (see Priority 2.3)
- [ ] Label Figure 3 recession shading consistently — some bands appear to extend to 2025; confirm all 14 NBER episodes are represented
- [ ] Produce a figure that shows the composite Z at the episode level (one time series per recession, aligned to onset) — this is more interpretable than the heatmap for most readers

---

## Priority 5: Submission Preparation

**5.1 Literature to engage before submission**
- [ ] Gidea and Katz (2018) — main TDA-finance paper; compare methodology directly
- [ ] Akingbade et al. (2024) — bubble detection with TDA; discuss why recession detection is a different problem
- [ ] Puliga et al. and related systemic risk papers on correlation-based network topology — the "shape of co-movement" literature is broader than TDA
- [ ] Longin and Solnik (2001) on correlation breakdown in bear markets — this is the non-TDA version of the same phenomenon; frame TDA as capturing this with richer geometric detail
- [ ] Müller and Watson (or similar) on business-cycle co-movement — establishes what is known about industry co-movement across regimes from a factor perspective

**5.2 Target journals (preliminary)**
- [ ] Tier 1 target: *Journal of Financial Economics* (if the contribution claim can be sharpened — requires Priority 3.3 to resolve)
- [ ] Tier 2 targets: *Journal of Empirical Finance*, *Review of Asset Pricing Studies*, *Finance Research Letters* (for a shorter, focused version)
- [ ] Alternative route: *Journal of Applied and Computational Topology* or *Physica A* for the TDA audience, where the methodology contribution is weighted more heavily

**5.3 Before any submission**
- [ ] Resolve the look-ahead bias question (Priority 2.1)
- [ ] Produce the persistence diagram figure (Priority 2.3)
- [ ] Draft a clear contribution paragraph (Priority 4.1)
- [ ] Decide on macro-predictive section (Priority 3.1)

---

## Outstanding Questions for Discussion with Advisor

1. **Contribution framing**: Is the paper's primary contribution (a) a new empirical fact about recession-regime geometry, (b) a methodological demonstration that TDA can be applied at the industry level, or (c) a negative result establishing the limits of TDA as a forecasting tool? The answer changes what journal to target and how the introduction is written.

2. **The equal-weighting of composite Z**: Is there a principled reason to equal-weight the five signals, or should this be motivated or compared against data-driven alternatives? A referee will ask.

3. **Supply/monetary crises with elevation = −0.017**: Is this credible as a finding — that topology does not simplify during supply shocks — or does it reflect a classification artifact? Worth discussing before the paper is circulated.

4. **Window length 60 vs. 120 vs. 252**: What is the theoretical prediction for which window should be most sensitive? Having a prior before looking at the results would strengthen the claim that W = 60 is the right choice.
