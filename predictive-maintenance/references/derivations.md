# Derivations and worked numbers

Every number below either comes from a demo run of the modules in `assets/`
(seeded, reproducible) or from the closed-form computations shown inline.
Source IDs (S1, S2, ...) resolve in `sources.md`.

## Censored Weibull maximum likelihood

For lifetimes with survival function S(t) = exp(-(t/lambda)^rho), hazard
h(t) = (rho/lambda)(t/lambda)^(rho-1), a dataset of failures (delta_i = 1)
and right-censored survivors (delta_i = 0) has log-likelihood

    l(lambda, rho) = sum_i [ delta_i * ln h(t_i) + ln S(t_i) ]

Censored units contribute only ln S(t_i): the evidence that the component
survived to t_i. Given rho, the scale MLE has the closed form

    lambda^rho = sum_i t_i^rho / r        with r = number of failures,

so every censored hour raises the numerator while the denominator counts
failures only. Dropping censored units removes exactly the longest-lived
evidence, because preventive change-outs and still-in-service units are the
survivors. The bias direction is always toward shorter life.

Demo run (`survival_models.py`, seed 7): 150 components, true Weibull
(rho = 2.6, lambda = 14,000 h), preventive change-out at 14,000 h plus a
finite observation window, 52% censored.

| fit | shape | scale (h) | B10 life (h) |
|---|---|---|---|
| censoring handled | 2.46 | 14,802 | 5,937 |
| censored units dropped | 3.01 | 10,111 | 4,785 |
| censored treated as failed | 3.15 | 11,285 | 5,525 |

The dropped-censored fit puts the scale 32% low and the B10 19% low, and it
also inflates the shape, which makes wear-out look sharper than it is. The
common planner KPI "average life of replaced components", computed from
corrective work orders only, is the dropped-censored estimator in disguise.

Quantiles: t_p = lambda * (-ln(1 - p))^(1/rho). B10 is t_0.10.

## Age replacement by renewal-reward

Replace at age T (cost c_p) or on failure (cost c_f), whichever comes
first. Renewal-reward gives the long-run cost rate

    g(T) = [ c_p * S(T) + c_f * F(T) ] / integral_0^T S(t) dt

The numerator is the expected cost per renewal cycle and the denominator is
the expected cycle length. Worked with rho = 2.5, lambda = 14,000 h,
c_p = $95,000 (planned change-out), c_f = $260,000 (failure in service),
computed by numerical quadrature (verified 2026-07-12, scipy 1.18):

| T (h) | cost rate ($/h) | F(T), failures before PM |
|---|---|---|
| 8,000 | 17.54 | 21.9% |
| 9,760 (optimum) | 17.15 | 33.4% |
| 12,000 | 17.53 | 49.3% |
| 16,000 | 18.98 | 75.2% |
| run to failure | 20.93 | 100% |

Mean life is lambda * Gamma(1 + 1/rho) = 12,422 h, so run-to-failure costs
c_f / 12,422 = $20.93/h. Three facts worth quoting to a client:

1. The optimum saves $3.78/h, about $22,700 per component-year at 6,000
   operating hours per year.
2. The optimum is flat: anywhere from 8,000 to 12,000 h stays within
   $0.40/h of the minimum. Precision on T* is worth little; getting the
   shape parameter right is worth a lot, because rho drives whether an
   optimum exists at all.
3. At the optimum, 33% of components still fail in service. A working age
   policy with visible failures is normal; zero failures means the policy
   is far too conservative.

With rho = 1.0 (exponential lives) the same computation gives cost rates
34.38, 25.08, 20.71, 18.98, 18.59 $/h at T = 5,000 / 10,000 / 20,000 /
40,000 / 80,000 h: monotone decreasing toward run-to-failure, so no finite
optimum exists. Age replacement pays only when rho > 1 and c_f > c_p.

## P-F interval and inspection frequency

Let L be the P-F interval (time from detectable potential failure P to
functional failure F) and d the per-inspection detection probability once
the defect is detectable. Inspections every I hours give on average L / I
looks inside the window, so

    P(miss) ~= (1 - d)^(L / I)

Worked example, scoped to rolling-element bearing defects found by
route-based envelope analysis, where L typically runs 8 to 16 weeks: with
monthly routes (I = 4.3 weeks) and d = 0.7, L = 12 weeks gives 2.8 looks
and P(miss) = 0.3^2.8 = 3.4%. Halving the route frequency (I = 8.7 weeks)
gives 1.4 looks and P(miss) = 19%. The standard heuristic of setting I
between L/3 and L/2 comes straight from this arithmetic: it buys 2 to 3
looks per window. When d is low (oil sampling for a fast-developing
failure), no feasible I rescues the program, and the correct consulting
answer is a different detection technique, with the arithmetic shown.

## Cost-optimal alert threshold

Per asset-period, alerting costs an inspection c_i and converts a true
failure from unplanned (c_u) to planned (c_p). With calibrated failure
probability p:

    cost(alert)    = c_i + p * c_p
    cost(no alert) =        p * c_u
    alert when p > p* = c_i / (c_u - c_p)

Worked numbers (haul-truck final drive; the c_u - c_p premium of $165,000
is consistent with trade-press figures of $5,000 to $20,000 per hour of
haul-truck downtime and roughly $200,000 for an in-service final-drive
failure, S7): c_i = $1,800, c_p = $95,000, c_u = $260,000 gives
p* = 1,800 / 165,000 = 1.09%. The optimal threshold sits two orders of
magnitude below 0.5, so default classifier thresholds destroy
value in maintenance alerting.

The formula holds only for calibrated probabilities. `alert_threshold.py`
(seed 21) demonstrates both halves: on calibrated scores the empirical
cost-minimizing threshold (0.0102) matches p* (0.0109) within grid noise;
on overconfident scores with identical ranking, applying p* costs $149 more
per asset-week than the empirically tuned threshold, which is about $930k
per year on a 120-truck fleet. Recalibrate on a held-out fold or tune the
threshold on validation weeks.

## EWMA and CUSUM constants

EWMA: z_t = lam * x_t + (1 - lam) * z_{t-1}, control limits
mu_0 +- L * sigma * sqrt( lam / (2 - lam) * (1 - (1 - lam)^(2t)) ).
The exact time-varying variance term matters for the first ~10 samples;
the asymptotic limit alone misses early drift on freshly reset baselines.

Published design points (Montgomery, Introduction to Statistical Quality
Control, 7th ed., ch. 9, S13) and the Monte Carlo check from
`control_charts.py` (4,000 runs, seed 11):

| chart | constants | published ARL0 | Monte Carlo ARL0 | ARL at 1 sigma shift |
|---|---|---|---|---|
| Shewhart | 3 sigma | 370 | 375 | 44.1 |
| EWMA | lam = 0.20, L = 2.859 | ~370 | 365 | 8.7 |
| CUSUM | k = 0.5 sigma, h = 5 sigma | ~465 | 466 | 10.3 |

CUSUM design rule: k = delta * sigma / 2 where delta is the shift (in
sigmas) you most want to catch; h = 4 sigma trades roughly 100 units of
ARL0 for one to two samples of detection speed versus h = 5 sigma.
On a slow drift of 0.0375 sigma per sample, the demo run alarms at
+5 samples (EWMA), +32 (CUSUM) and +46 (Shewhart) after onset: the
Shewhart chart waits for the mean to travel most of 3 sigma.

## Concordance under heavy censoring

Harrell's c counts only "comparable" pairs, where the shorter observed time
is an event. Under heavy censoring the comparable pairs over-represent
short lives, and the estimate drifts optimistic as censoring grows; the
IPCW estimator of Uno et al. (2011, S14) reweights by the censoring
distribution and stays consistent. Maintenance datasets sit at 40 to 80%
censoring, squarely where the two diverge, so report
`concordance_index_ipcw` from scikit-survival (S16) and state the follow-up
horizon tau. For the same reason, prefer the IPCW Brier score over
accuracy-style metrics when validating survival predictions.
