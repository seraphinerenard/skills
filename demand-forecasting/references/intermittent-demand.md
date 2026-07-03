# Intermittent demand methods, with the math

Spare parts, slow-moving SKUs, and B2B tail items produce histories where most
periods are zero and the informative events are (interval, size) pairs. Point
methods tuned for smooth series smear these events into a useless average, and
error metrics built on per-period point accuracy actively reward refusing to
forecast. This file carries the derivations and worked numbers behind the
recommendations in SKILL.md.

## Classify before choosing a method

Syntetos, Boylan and Croston (2005) partition series by two statistics: the
average inter-demand interval ADI (mean periods between non-zero demands) and
the squared coefficient of variation of demand sizes CV2. The cutoffs
ADI = 1.32 and CV2 = 0.49 come from comparing the theoretical MSE of Croston
and SBA estimators across the parameter space.

| region | ADI | CV2 | character | first method |
|---|---|---|---|---|
| smooth | < 1.32 | < 0.49 | regular timing and size | ETS or a global model; Croston-family adds nothing |
| erratic | < 1.32 | >= 0.49 | regular timing, wild sizes | ETS on the series; consider variance-stabilizing links |
| intermittent | >= 1.32 | < 0.49 | gaps, stable sizes | SBA; TSB when obsolescence matters |
| lumpy | >= 1.32 | >= 0.49 | gaps and wild sizes | SBA or TSB for the rate, plus an explicit lead-time demand distribution for stocking |

## Croston's decomposition and its bias

Croston (1972) smooths sizes and intervals separately. On each period with
demand y > 0, with interval q periods since the previous demand and smoothing
parameter alpha,

```
z_hat <- z_hat + alpha * (y - z_hat)      # demand size
q_hat <- q_hat + alpha * (q - q_hat)      # inter-demand interval
forecast rate = z_hat / q_hat             # unchanged on zero periods
```

Worked pass, alpha = 0.2, demand history [0, 0, 5, 0, 0, 0, 8, 0, 3]:

| event | interval q | z_hat | q_hat | Croston rate | SBA rate |
|---|---|---|---|---|---|
| y=5 at t=3 (initialization) | 3 | 5.000 | 3.000 | 1.667 | 1.500 |
| y=8 at t=7 | 4 | 5.600 | 3.200 | 1.750 | 1.575 |
| y=3 at t=9 | 2 | 5.080 | 2.960 | 1.716 | 1.545 |

The estimator is biased upward: the rate is the ratio of two smoothed
quantities, and by Jensen's inequality E[z_hat / q_hat] > E[z_hat] / E[q_hat]
because 1/x is convex. Expanding E[1/q_hat] to second order gives
(1/mu_q)(1 + Var(q_hat)/mu_q^2 + ...), and for SES-smoothed geometric
intervals Syntetos and Boylan (2005) reduce the leading term to a clean
multiplicative factor. Their correction, the SBA estimator, deflates Croston
by (1 - alpha/2):

```
SBA rate = (1 - alpha/2) * z_hat / q_hat
```

Simulation check (Bernoulli incidence p = 0.25, sizes 1 + Poisson(5) so the
true rate is 1.500, alpha = 0.2, 4,000 replications of 400 periods, seed 42;
the script is a 20-line variant of assets/stats_baselines.py):

| estimator | long-run mean | bias |
|---|---|---|
| Croston | 1.631 | +8.8% |
| SBA | 1.468 | -2.1% |
| TSB | 1.506 | +0.4% |

The +8.8% matters because it compounds into stock: an 8.8% inflated rate at a
95% service target over-buys every part in the tail, and tails run to tens of
thousands of SKUs in spare-parts businesses.

## TSB handles obsolescence, Croston cannot

Croston updates only on demand events, so after the last-ever demand for a
dying part the forecast stays frozen at its final rate forever. Teunter,
Syntetos and Babai (2011) replace the interval with a demand probability that
updates every period:

```
p_hat <- p_hat + alpha_p * (1{y>0} - p_hat)     # every period
z_hat <- z_hat + alpha_z * (y - z_hat)          # demand periods only
forecast rate = p_hat * z_hat
```

A run of zeros decays p_hat geometrically, so the forecast follows a part into
retirement. Use TSB whenever the portfolio contains phase-outs, which in spare
parts is always. The cost is one more smoothing parameter; alpha_p in
0.05-0.30 and alpha_z near 0.2 are the usual search ranges.

<!-- allow:E2 ADIDA and IMAPA are method acronyms -->
## Temporal aggregation, ADIDA and IMAPA

ADIDA (Nikolopoulos et al., 2011) aggregates the series into buckets whose
length equals the ADI, which converts an intermittent series into a mostly
non-zero one, forecasts the bucket totals with SES, then spreads the total
back over the bucket. IMAPA runs several aggregation levels and averages the
resulting rates. Both are in statsforecast as `ADIDA` and `IMAPA`. They win
when intermittency comes from reporting granularity (daily data for a part
ordered monthly) and add little when demand events are genuinely rare at every
useful aggregation level.

## Evaluation that will not lie to you

Per-period point metrics degenerate on intermittent series:

- The zero forecast minimizes MAE whenever the per-period demand probability
  is below one half, because the median of the demand distribution is zero.
  In the assets/stats_baselines.py demo the zero forecast posts MAE 1.56
  against 2.52-2.63 for the Croston family while achieving 63.6% service
  against their 95%+. Any MAE-ranked tournament crowns the forecast that never
  stocks anything.
- MAPE divides by zero on most periods; sMAPE saturates at 200% on every
  missed demand event and its ranking is dominated by the zero periods.
- MASE stays defined (the scaling denominator uses in-sample naive errors)
  and works for comparing rate forecasts, with the caveat that it still scores
  per-period points, so it cannot see distributional quality.

The decision-grade evaluation converts each method's rate into a stock policy
and simulates it. The recipe used in assets/stats_baselines.py:

1. Convert the rate forecast into a lead-time (or review-period) demand mean,
   mu_LT = rate x periods.
2. Pick a distribution for lead-time demand. Poisson is only defensible when
   sizes are near 1. Compound (burst) demand is overdispersed; a negative
   binomial parameterized by (mu_LT, var_LT) with var_LT estimated from
   training data closes the gap. In the demo, Poisson sizing achieved 81-85%
   against a 95% target while negative binomial sizing achieved 92-96%.
3. Set the order-up-to level at the target quantile and replay the test
   period, recording achieved service and average stock.

Rank methods on achieved service at equal stock, or stock at equal service.
Cross-reference the supply-chain-optimization skill for the newsvendor logic
that turns the cost asymmetry into the target quantile.

## Sources

Croston (1972), "Forecasting and stock control for intermittent demands",
Operational Research Quarterly 23(3). Syntetos and Boylan (2005), "The
accuracy of intermittent demand estimates", International Journal of
Forecasting 21(2). Syntetos, Boylan and Croston (2005), "On the
categorization of demand patterns", JORS 56(5). Teunter, Syntetos and Babai
(2011), "Intermittent demand: linking forecasting to inventory obsolescence",
EJOR 214(3). Nikolopoulos et al. (2011), "An aggregate-disaggregate
intermittent demand approach (ADIDA) to forecasting", JORS 62(3). See
sources.md for the online copies checked on 2026-07-12.
