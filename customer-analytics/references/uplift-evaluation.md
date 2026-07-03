# Uplift estimation and Qini evaluation, worked

Companion to `assets/uplift_qini.py`. All demo numbers below come from that
module's `__main__` run (seed 11, 60,000 simulated customers, 20,000 holdout).

## The estimand and the four response types

A retention offer sent to customer `i` changes their retention probability by
the conditional average treatment effect `tau(x) = E[Y(1) - Y(0) | X = x]`,
with `Y = 1` meaning retained. The population splits into four types:

- sure things retain either way, so `tau = 0` and contacting them burns budget;
- lost causes leave either way, so `tau = 0` and they also burn budget;
- persuadables retain only if contacted, `tau > 0`, the only profitable target;
- sleeping dogs leave because you contacted them, `tau < 0` (an offer or a
  contract-renewal reminder that triggers a cancellation decision).

Sleeping dogs are documented in the field, with Ascarza (2018, Journal of
Marketing Research 55(1)) reporting in two randomized field experiments that
the lowest-lift deciles churned more when treated, while sensitivity-based
targeting cut churn by up to 6.8 percentage points more than risk-based
targeting. Churn-risk models rank customers by `P(Y(0) = 0)`, which correlates
weakly and sometimes negatively with `tau(x)`; that mismatch is the whole case
for uplift modelling in retention.

## Estimators, with selection guidance

### Two-model (T-learner)

Fit `mu_1(x)` on the treated arm and `mu_0(x)` on the control arm; predict
`tau_hat(x) = mu_1(x) - mu_0(x)`. It needs no special library, works with any
well-calibrated classifier, and in the demo it recovered most of the oracle's
Qini. Its known weakness: each model optimizes its own fit, so regularization
noise in `mu_1` and `mu_0` fails to cancel, and with badly imbalanced arms the
smaller arm's model dominates the error.

### Transformed outcome (class transformation)

With randomization probability `e`, the variable

```
Y* = Y (W - e) / (e (1 - e))        [W is the treatment indicator]
```

satisfies `E[Y* | X] = tau(X)`, so a single regression on `Y*` estimates
uplift directly. For `e = 0.5` this reduces to `Y* = 2 Y (2W - 1)`, which
takes values in {-2, 0, +2}: an extremely noisy target whose regression only
stabilizes at large samples. In the demo (20,000 training rows per arm) it
trailed the T-learner (Qini per customer 0.0023 against 0.0032).

### DR-learner and causal forests

<!-- allow:C1 "doubly robust" is the estimator's technical name -->
Doubly robust learners (econml's `DRLearner`) and causal forests
(`CausalForestDML`, causalml's uplift forests) add value when treatment
assignment is non-random (observational campaign logs) or when you need
honest confidence intervals on `tau(x)` for a policy decision. Under clean
randomization with large samples their ranking quality lands close to the
T-learner's, so reach for them when assignment bias or the CI requirement
justifies the extra machinery.

### Selection table

| Situation | Estimator |
|---|---|
| Randomized campaign data, need a ranking this week | T-learner with gradient boosting |
| Randomized, very large N, want one model to maintain | transformed outcome |
| Observational data (no holdout was kept) | DR-learner with cross-fitting; treat results as provisional and cross-reference the causal-inference skill |
| Need CIs on segment-level effects for a rollout decision | causal forest with honest splitting |
| ELSE | T-learner; it degrades the most gracefully |

## Qini, from the definition

Sort the evaluation set by predicted uplift, descending. For the prefix of
size `k` containing `n_T(k)` treated with `Y_T(k)` retained and `n_C(k)`
control with `Y_C(k)` retained (Radcliffe 2007):

```
Q(k) = Y_T(k) - Y_C(k) * n_T(k) / n_C(k)
```

`Q(k)` estimates incremental retained customers among the treated portion of
the prefix. The Qini coefficient is the area between the `Q(k)` curve and the
straight line from the origin to `Q(N)` (random targeting), here reported per
customer. Demo values, T-learner ranking on the 20,000-customer holdout:

| Prefix | Q(k), incremental retained | Share of total effect |
|---|---|---|
| top 10% | 54 | 25% |
| top 20% | 129 | 59% |
| top 30% | 192 | 87% |
| top 50% | 209 | 95% |
| all 100% | 220 | 100% |

The same holdout under the churn-risk ranking gave Q at top 10% of 19 and at
top 30% of 56, a quarter of the uplift ranking's capture. Read the 87%-at-30%
row as the budget case: contacting less than a third of the base with the
uplift ranking preserves nearly all of the campaign's total incremental
retention.

Deployment arithmetic uses the per-contact form. Observed uplift inside the
top 30% was +6.5 points, so contacting 10,000 top-30% customers saves about
650; the blanket campaign's average effect (+2.2 points) saves 222 per 10,000;
the churn-risk top 30% saved 190 per 10,000, below the blanket number, because
the highest-risk block mixes lost causes and sleeping dogs.

### Normalization warning

Libraries disagree on Qini scaling: sklift's `qini_auc_score` normalizes
against a perfect-model curve, causalml's `qini_score` reports the raw area
against random, and papers vary further. Never compare Qini coefficients
across tools or publications; recompute both rankings with one formula on one
dataset. `uplift_qini.py::qini_coefficient` exists for exactly that.

Evaluation always runs on a randomized holdout with both arms present. A
Qini computed on the training rows, or on data where treatment followed a
targeting rule, reports noise dressed as lift.

## Sample-size reality

Uplift heterogeneity is a second-order effect: you estimate differences
between differences of proportions. The contrast between two segments'
treatment effects, `theta = (p_T1 - p_C1) - (p_T2 - p_C2)`, has variance
`sum of p_i (1 - p_i) / n_cell` over four cells. Setting all `p_i` near a
base churn of 0.25, two-sided alpha 0.05 and power 0.80:

```
n_cell = (1.96 + 0.842)^2 * 4 * 0.25 * 0.75 / delta^2
```

Detecting a 2-point gap between two segments' effects (`delta = 0.02`)
needs 14,717 customers per cell, 58,868 in the experiment. Most retention
tests run on a few thousand customers, which supports estimating one average
effect and perhaps two coarse segments; a per-customer `tau_hat` from such a
test carries error bars wider than the effects it claims to rank. Plan the
experiment with the causal-inference skill before promising a personalized
policy.

## Label contamination feeds back

Once a targeting policy runs, next quarter's data has treatment concentrated
on whoever the old model favoured. Training a new churn or uplift model on
that data without the treatment indicator bakes the old policy into the
labels (treated persuadables look like natural stayers). Keep a permanent
random holdout (2 to 5 percent of the base receives no proactive retention
contact) as the clean measurement bed; it also prices every future campaign
for free.
