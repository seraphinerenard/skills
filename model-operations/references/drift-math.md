# Drift math, in the detail the SKILL summarizes

Every number here reproduces with `assets/drift.py` (numpy only); the demo
prints each table on synthetic data with known shifts.

## PSI, defined so the binning is visible

With reference share `r_b` and current share `c_b` in bin `b`,

```
PSI = sum_b (c_b - r_b) * ln(c_b / r_b)
```

Empty bins get an epsilon floor before the log; the epsilon and the bin count
both move the number, so both print beside it. Bins fit on the reference
window with equal frequency and then freeze; refitting bins on each current
window lets a drifting distribution reset its own yardstick.

## The null distribution, and thresholds by sample size

Siddiqi (2006) records the 0.10 (watch) and 0.25 (act) thresholds as
credit-scoring rules of thumb without a distributional argument. Yurdakul
(2018) derived the null: with B bins and independent samples of n and m rows,
PSI under no drift is approximately `(1/n + 1/m) * chi-square(B-1)`. The
consequences, at B = 10 and n = m:

| n per side | E[PSI] under no drift | 95th percentile | 0.25 threshold reads as |
|---|---|---|---|
| 100 | 0.180 | 0.35 | fires regularly on pure noise |
| 1,000 | 0.018 | 0.034 | reasonable |
| 10,000 | 0.0018 | 0.0034 | numb; real drift scores far below it |
| 100,000 | 0.00018 | 0.00034 | any nonzero reading is "real" and mostly trivial |

So the fixed 0.10/0.25 pair is simultaneously too twitchy for small segments
and too numb for large feeds. Set the watch threshold near the null's 95th
percentile at your n and B, and set the act threshold from the backtested
cost of the action the alarm triggers.

## Binning sensitivity, the demo case

The same +0.5 sd shift with 1% outliers scores 0.0003 under equal-width bins
(outliers stretch the range, the body lands in one bin) and 0.116 under
equal-frequency bins. Equal-width binning on long-tailed business data is the
single most common way a real shift reads as calm.

## KS and scaled Wasserstein

Two-sample KS is binning-free and its p-value degrades into a sample-size
detector: the demo's +0.03 sd mean shift (operationally nothing) scores
p = 0.55 at n = 500, p = 0.04 at n = 5,000, and p < 0.0001 at n = 50,000,
while the D statistic holds near 0.015. Read the statistic as the effect
size and the p-value only at small n.

Wasserstein-1 divided by the reference standard deviation reads directly as
"shift in sd units" and holds stable as n grows (the same non-shift scores
W1/sd near 0.03 at every n). A working threshold is 0.1 sd for watch;
Evidently's per-column defaults follow the same split (KS with p < 0.05 up
to 1,000 reference rows, scaled Wasserstein above that; Evidently
documentation, accessed 2026-07-12).

## Categorical and zero-inflated features

Quantile bins collapse on ties, and KS p-values assume continuity, so
discrete features run PSI on category shares directly. Floor rare categories
into an "other" bucket at a fixed share (0.5% works) before computing, and
freeze the category list from the reference window so new categories land in
"other" and raise a schema note through the data contract, which owns
new-category detection.

## Score drift as the first alarm

The cheapest single monitor is PSI or scaled W1 on the model's own output
distribution. It aggregates every input shift the model responds to, it
needs no labels, and in the retraining-policy backtest
(`assets/retraining_policy.py`) it flags pipeline breaks weeks before
label-based metrics can, because labels arrive on a delay and scores arrive
instantly.

## What drift metrics cannot say

They measure marginal distributions. A relationship change with stable
marginals (concept drift) passes every test above and surfaces only in
delayed accuracy or in a proxy with faster labels; the SKILL's proxy table
covers that route. And a unit change upstream is indistinguishable from
drift in these metrics, so the contract log gets read first.
