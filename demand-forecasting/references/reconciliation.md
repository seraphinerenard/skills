# Hierarchical reconciliation, worked through

Retail and utility forecasts live on hierarchies (SKU-store-region-total,
<!-- allow:CAN meter here is the metering device in the load hierarchy -->
meter-feeder-substation-system), and independent forecasts at each level are
incoherent: children do not sum to parents, so planning meetings argue about
which number is real. Reconciliation projects the base forecasts onto the
coherent subspace, and the projection choice decides whether accuracy improves
or degrades. The math below is verified numerically; the runnable version is
assets/mint_reconciliation.py.

## The projection

Stack all levels into y (n series, n_b bottom series), with summing matrix S
(n x n_b) mapping bottom series to every node. Any coherent forecast has the
form y_tilde = S G y_hat for some G (n_b x n). Wickramasuriya, Athanasopoulos
and Hyndman (JASA 2019) minimize the trace of the reconciled error covariance
subject to unbiasedness (G S = I) and get

```
G = (S' W^-1 S)^-1 S' W^-1
```

where W is the covariance of the base-forecast errors. Named cases fall out of
the choice of W: identity gives OLS reconciliation; the diagonal of residual
variances gives WLS; the diagonal of S·1 (number of leaves under each node)
gives structural WLS; the shrunk full residual covariance gives MinT-shrink.

## Worked example, two stores under one total

Base forecasts y_hat = [105, 40, 70] for [Total, A, B]. The bottom sum is 110,
so the base set is incoherent by 5 units. S has rows [1 1], [1 0], [0 1].

With W = diag(3, 1, 2) (residual variances from a holdout: the total is
noisier than store A, store B sits between):

```
S' W^-1 S = [[4/3, 1/3], [1/3, 5/6]],  det = 1
(S' W^-1 S)^-1 = [[5/6, -1/3], [-1/3, 4/3]]
S' W^-1 y_hat = [75, 70]
bottom tilde = [39.167, 68.333]
reconciled [Total, A, B] = [107.5, 39.167, 68.333]
```

Read the adjustments: the 5-unit discrepancy is allocated in proportion to
each node's error variance. The total (variance 3) absorbs +2.5, store A
(variance 1, the most trusted forecast) gives up 0.833, store B (variance 2)
gives up 1.667. A gets moved half as much as B because its base forecast is
half as noisy. With W = I (OLS) the same inputs give [106.667, 38.333,
68.333]: OLS spreads the discrepancy without regard to who deserves trust.

## MinT-shrink in practice

The full residual covariance has n(n+1)/2 entries estimated from T residual
rows, and retail hierarchies have n in the tens of thousands with T in the
hundreds, so the sample covariance is singular and MinT with it is
numerically explosive. The fix is Schafer-Strimmer shrinkage toward the
diagonal, W = lambda * diag(W_sample) + (1 - lambda) * W_sample, with lambda
estimated from the data; this is `MinTrace(method="mint_shrink")` in
hierarchicalforecast and the default serious choice. It needs in-sample
residuals: pass base fitted values through `Y_df` (in statsforecast, run
`forecast(..., fitted=True)` and collect `forecast_fitted_values()`), or the
library raises the "you need to pass insample predictions" error, which is the
single most reported hierarchicalforecast failure (Nixtla methods.py, accessed
2026-07-12).

In the assets/mint_reconciliation.py demo (20 noisy stores under 4 regions
with shared regional shocks, MSTL base forecasts, h=13), base RMSSE at the
region level is 1.012 and mint_shrink reaches 0.997 while bottom-up stays at
1.012; at the total, bottom-up degrades the base from 0.740 to 0.819 while
MinT variants hold 0.75-0.79. All reconciled sets are exactly coherent; the
base set misses coherence by up to 11.2 units.

## When bottom-up wins anyway

MinT's edge depends on a stable residual covariance and reasonably unbiased
base forecasts at every level. Bottom-up wins when the bottom level carries
covariates the aggregates cannot see: in M5, competitors forecast only the
30,490 product-store series with price, SNAP and calendar features, and
summed those bottom forecasts to all 12 levels; the winning WRMSSE of 0.520
(a 22.4% gain on the strongest statistical benchmark) came from bottom-up
aggregation of a global LightGBM, and the organizers report the approach as
standard across the top 50 (M5 accuracy paper, IJF 38(4), 2022; preprint at
statmodeling.stat.columbia.edu, accessed 2026-07-12). Two conditions push you
back toward MinT: bias-prone bottom forecasts on sparse series (aggregates
then correct them) and consumers of the forecast who plan at middle levels
where neither pure bottom-up nor top-down is accurate.

Top-down with historical proportions is biased even with perfect top
forecasts (proportions drift), so treat `TopDown` as a reporting convenience,
never as the accuracy play (Hyndman and Athanasopoulos, fpp3, reconciliation
chapter, accessed 2026-07-12).

## Probabilistic reconciliation

Point coherence does not give you coherent predictive distributions. Three
working options in hierarchicalforecast 1.5: `Normality` (Gaussian errors,
covariance from the MinT machinery), `Bootstrap` (Gamakumara sample paths,
reconciled path by path), and `PERMBU` (rank-permutation copula that restores
cross-series dependence before bottom-up aggregation); v1.5.0 added a
conformal variant. Bootstrap is the default recommendation for retail counts
<!-- allow:CAN smart meter is the metering device -->
because Gaussian tails understate zero-heavy bottom series. For smart-meter
hierarchies, Ben Taieb, Taylor and Hyndman (JASA 2021) build coherent
densities from the bottom up with copulas; see the stlf-hierarchical-load
fact sheet in research/ for the citation trail.

## Sequence for a client engagement

1. Fit base models at every level you or the client plan on, with fitted
   values retained.
2. Reconcile with BottomUp, MinTrace(ols), MinTrace(mint_shrink); evaluate
   RMSSE per level on a rolling origin (assets/evaluation.py).
3. Report the per-level table. Expect mint_shrink to win or tie at aggregate
   levels; if bottom-up wins everywhere, the aggregates carry no independent
   signal and you can simplify the stack to bottom-level models plus summing.
4. If the deliverable includes intervals, add Bootstrap reconciliation and
   check empirical coverage per level before quoting any of them.
