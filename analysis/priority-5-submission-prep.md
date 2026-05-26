# Priority 5 - Submission Preparation

## Literature positioning

The paper now has a defensible bridge across three literatures:

| Literature | Anchor papers | How this paper positions itself |
|---|---|---|
| TDA-finance early-warning work | Gidea and Katz (2018); Akingbade et al. (2024) | Extends from index/crash/bubble examples to a century-scale daily cross-section of industry portfolios and all NBER recessions in sample. |
| Correlation-network systemic-risk work | Puliga, Caldarelli, and Battiston (2014) | Keeps the systemic-risk network intuition but uses persistent homology to measure higher-order geometry rather than pairwise network structure alone. |
| Correlation/business-cycle co-movement | Longin and Solnik (2001); Stock and Watson (1990); Hornstein and Praschnik (1997) | Frames TDA as a geometric decomposition of recession co-movement, not as a claim that correlations do not matter. |

## Target journal read

| Target | Fit | Recommendation |
|---|---|---|
| *Journal of Financial Economics* | Low in current form. Needs a much stronger asset-pricing mechanism, return-prediction result, or identification design. | Do not target first unless the paper is substantially rebuilt around asset-pricing contribution. |
| *Review of Asset Pricing Studies* | Low to moderate. Better than JFE only if the topology signal is connected to priced risk, factor structure, or cross-sectional returns. | Not first target for current regime-characterization paper. |
| *Journal of Empirical Finance* | Moderate. Empirical finance, daily panel, regime characterization, robustness tests. | Best finance-journal target if expanded into full empirical paper. |
| *Finance Research Letters* | Moderate to high if shortened. The paper has a focused empirical fact and negative classification result; FRL favors concise novel findings. | Best short-paper route; would require trimming to the core result and probably dropping long macro-predictive material. |
| *Physica A* | High. Prior TDA-finance work appears there; complex-systems framing fits. | Strong target if emphasizing methodology and financial-system geometry. |
| *Journal of Applied and Computational Topology* | Moderate. Good TDA venue, but the math novelty is limited; application novelty must be clear. | Possible if framed as a careful applied TDA finance case study with reproducible data pipeline. |

## Submission decision

Recommended first target depends on paper length:

- Full empirical finance version: *Journal of Empirical Finance*.
- Short, focused result: *Finance Research Letters*.
- TDA/complex-systems version: *Physica A*.

Do not lead with JFE/RAPS unless the advisor wants to rebuild the paper around an asset-pricing mechanism.

## Before submission

Completed:

- Look-ahead bias question resolved through expanding-window standardization.
- Persistence diagram figure produced.
- Clear contribution paragraph drafted.
- Macro-predictive section retained only as a negative/boundary result.
- KNN and MICE missing-data robustness completed; both preserve sign/significance but attenuate the composite effect.
- PCA and Ledoit-Wolf shrinkage composite sensitivity completed; PCA strengthens the recession separation, while shrinkage remains positive but noisier.

Still recommended before external submission:

- Decide whether the manuscript is a full paper or a short letter; this determines whether Table 3 stays.
