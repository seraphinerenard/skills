# BTYD likelihoods, derived and worked

Companion to `assets/btyd_clv.py`. Everything here is checkable: the worked
example reproduces a published Fader-Hardie number to four figures using the
code in that module.

## Data summary

BTYD models consume one row per customer, computed from the transaction log
over a calibration window that starts at each customer's first purchase:

- `x` counts repeat transactions in `(0, T]` (the first purchase is excluded).
- `t_x` is the time of the last repeat transaction, with `t_x = 0` when `x = 0`.
- `T` measures the window length from first purchase to the end of calibration.
- `m_x` averages observed spend per transaction, defined only when `x >= 1`.

Units of `x`, `t_x`, `T` follow whatever time unit you pick (weeks in the
code). A wrong summary is the most common BTYD failure: counting the first
purchase in `x` inflates frequency for everyone and skews `r` upward.

## BG/NBD (Fader, Hardie and Lee 2005)

### Assumptions

1. While active, a customer buys as a Poisson process with rate `lambda`.
2. After every transaction the customer becomes permanently inactive with
   probability `p` (a geometric death coin flipped only at purchases).
3. `lambda ~ Gamma(r, alpha)` (shape `r`, rate `alpha`) across customers.
4. `p ~ Beta(a, b)` across customers, independent of `lambda`.

### Individual-level likelihood

Condition on `(lambda, p)`. A customer observed with history `(x, t_x, T)`
either survived all `x` death coins and bought nothing in `(t_x, T]`, or died
at the `x`-th purchase. The Poisson interarrival density gives:

```
L(lambda, p | x, t_x, T)
  = (1 - p)^x lambda^x exp(-lambda T)                    [still alive at T]
  + delta(x > 0) p (1 - p)^(x - 1) lambda^x exp(-lambda t_x)   [died at t_x]
```

The first term integrates the "no purchase in `(t_x, T]`" survival into
`exp(-lambda T)`; the second stops the clock at `t_x` because a dead customer
generates no exposure afterward. Zero-repeat customers only have the first
term, so the model cannot distinguish a dead zero-repeat customer from a
live slow one (see the P(alive) quirk below).

### Mixed likelihood

Integrate `lambda` against Gamma(r, alpha) and `p` against Beta(a, b). Both
integrals are standard conjugate forms and give:

```
L(r, alpha, a, b | x, t_x, T)
  = A1 * [ B(a, b + x) / B(a, b) * (alpha + T)^-(r + x)
         + delta(x > 0) B(a + 1, b + x - 1) / B(a, b) * (alpha + t_x)^-(r + x) ]

A1 = Gamma(r + x) / Gamma(r) * alpha^r
```

Implementation detail that matters: compute both bracketed terms in log space
and combine with `logaddexp`, since each term underflows for heavy buyers
(`x` above roughly 40 with weekly units). `assets/btyd_clv.py::bgnbd_loglik`
does exactly this.

### P(alive)

The posterior probability that the customer remains active at `T` equals the
first (alive) term's share of the likelihood:

```
P(alive | x, t_x, T) = 1 / (1 + delta(x > 0) * a / (b + x - 1)
                             * ((alpha + T) / (alpha + t_x))^(r + x))
```

### Conditional expected transactions

Expected repeat transactions in `(T, T + t]` (Fader, Hardie and Lee 2005,
eq. 10), with `2F1` the Gaussian hypergeometric function
(`scipy.special.hyp2f1`):

```
E[Y(t) | x, t_x, T] =
  (a + b + x - 1) / (a - 1)
  * [1 - ((alpha + T) / (alpha + T + t))^(r + x)
       * 2F1(r + x, b + x; a + b + x - 1; t / (alpha + T + t))]
  / (1 + delta(x > 0) * a / (b + x - 1)
       * ((alpha + T) / (alpha + t_x))^(r + x))
```

### Worked example, checked against the published value

CDNOW maximum-likelihood estimates from the 2005 paper: `r = 0.243`,
`alpha = 4.414`, `a = 0.793`, `b = 2.426`. Take the paper's example customer:
`x = 2`, `t_x = 30.43` weeks, `T = 38.86` weeks.

Log pieces (from `bgnbd_loglik` internals):

```
ln A1                    = -0.8364
alive term (log)         = -8.9417   -> alive piece  = 5.7e-05
death-at-t_x term (log)  = -9.9190   -> dead piece   = 2.1e-05
log-likelihood contribution: ln(7.8e-05)
```

P(alive) falls out as the alive piece over the sum: `5.7 / 7.8 = 0.727`.
Expected transactions over the next 39 weeks: `E[Y(39)] = 1.2260`, which
matches the 1.226 published in the paper's spreadsheet walk-through. Running
`expected_purchases((0.243, 4.414, 0.793, 2.426), [2], [30.43], [38.86], 39)`
reproduces it.

### Parameter reading

- `r / alpha` gives the mean purchase rate of the mixing distribution
  (CDNOW: 0.243 / 4.414 = 0.055 repeat buys per week for a just-acquired
  customer). Small `r` with small `alpha` means heavy heterogeneity.
- `a / (a + b)` gives the mean death probability per transaction (CDNOW:
  0.793 / 3.219 = 0.246, so the average customer survives about four
  transactions).
- `1 / (1 + odds_dead)` structure means recency dominates: two customers with
  identical `x` and `T` and different `t_x` get wildly different P(alive).
  In the demo, `x = 4, T = 52` with `t_x = 40` gives P(alive) 0.70; the same
  frequency with `t_x = 12` gives 0.03.

## The Pareto/NBD likelihood (Schmittlein, Morrison and Colombo 1987)

Same Poisson purchasing, and death now follows an exponential lifetime with
rate `mu ~ Gamma(s, beta)`, so a customer can die between purchases. In the
Fader-Hardie parameterization `(r, alpha, s, beta)` the likelihood is

```
L(r, alpha, s, beta | x, t_x, T)
  = Gamma(r + x) alpha^r beta^s / Gamma(r)
    * [ (alpha + T)^-(r + x) (beta + T)^-s + (s / (r + s + x)) A0 ]
```

with, for `alpha >= beta`,

```
A0 = 2F1(r + s + x, s + 1; r + s + x + 1; (alpha - beta) / (alpha + t_x))
       / (alpha + t_x)^(r + s + x)
   - 2F1(r + s + x, s + 1; r + s + x + 1; (alpha - beta) / (alpha + T))
       / (alpha + T)^(r + s + x)
```

and for `alpha < beta` the same expression with the second hypergeometric
argument `s + 1` replaced by `r + x`, the `z` numerators replaced by
`beta - alpha`, and the denominators built from `beta + t_x` and `beta + T`.
The derivation appears step by step in Fader and Hardie's technical note on
deriving the Pareto/NBD (see `sources.md`); implement it only when the
death-between-purchases distinction earns its keep, because the two-branch
hypergeometric is the classic source of numerical bugs in this family.

Practical fitting note: the Pareto/NBD likelihood is nearly flat in `(s,
beta)` when the calibration window is short relative to lifetimes, so
optimizers wander. Fit BG/NBD first; switch only if the P(alive) quirks below
bind.

## The P(alive) quirks, stated precisely

These follow from the BG/NBD death-only-at-purchase assumption and surprise
every first-time user:

1. Zero-repeat customers have P(alive) = 1 forever, no matter how long they
   stay silent, because death requires a purchase. On retail data where 40 to
   60 percent of customers never repeat, downstream CLV for that block rests
   entirely on the Gamma prior. MBG/NBD (Batislam, Denizel and Filiztekin
   2007) flips the death coin at time zero as well, which repairs this at the
   cost of one reinterpretation: `a / (a + b)` then includes never-starters.
2. P(alive) jumps upward at each purchase and decays between purchases. A
   plot of one customer's P(alive) over time is a sawtooth. Campaign triggers
   keyed to a P(alive) threshold therefore fire on quiet periods, which is
   usually the desired behaviour, and re-arm after each purchase.
3. For `x = 1`, `b + x - 1 = b`, and the dead-term weight `a / b` is a pure
   prior quantity: single-repeat customers are scored mostly by the
   population, only weakly by their own timing.

## Gamma-gamma spend model (Fader and Hardie 2013)

### Assumptions

Transaction values `z_1..z_x` for a customer are iid `Gamma(p, nu)` with
`nu ~ Gamma(q, gamma)` across customers, and spend is independent of the
transaction-timing process. Check the independence before trusting the model:
correlate `m_x` with `x` across customers; a strong positive correlation
(heavy buyers spending more per trip) violates the factorization that lets
you multiply expected transactions by expected spend.

### Likelihood

Only the average `m_x` and the count `x` enter, because the sum of iid gammas
is gamma:

```
p(m_x | p, q, gamma, x)
  = Gamma(p x + q) / (Gamma(p x) Gamma(q))
    * gamma^q m_x^(p x - 1) x^(p x) / (gamma + m_x x)^(p x + q)
```

### Conditional expected spend is a shrinkage estimator

```
E[M | m_x, x] = w * gamma p / (q - 1) + (1 - w) * m_x,
w = (q - 1) / (p x + q - 1)
```

With the published CDNOW-style estimates `p = 6.25`, `q = 3.74`,
`gamma = 15.44`: the population mean spend is `15.44 * 6.25 / 2.74 = 35.22`
dollars. A customer with one $100 transaction shrinks to an expected $80.26
per future transaction; a customer with eight transactions averaging $100
shrinks only to $96.63. Quoting raw `m_x` as future spend for low-`x`
customers overstates their value by exactly the shrinkage the model applies.

`q <= 1` makes the population mean infinite; a fitted `q` near 1 signals a
heavy right tail where a few whales carry the estimate, so report the CLV of
the top decile separately before anyone multiplies means.

## Discounted CLV assembly

`assets/btyd_clv.py::clv` sums, per month `m` up to the horizon, the
incremental expected transactions `E[Y(m)] - E[Y(m - 1)]` times conditional
expected spend times margin, discounted by `(1 + d)^-m`. Continuous-time
discounted expected residual transactions (DERT) exists in closed form for
the Pareto/NBD (Fader and Hardie's note on customer-base valuation covers
it); the monthly sum above stays within about a percent of it at monthly
discount rates near 1 percent and is auditable by a client analyst, which is
worth more than the closed form.

Parameter uncertainty propagates by bootstrap: resample customers, refit,
recompute. The demo's 90 percent band on mean 24-month CLV came out
[27.46, 31.85] around a 29.88 point estimate on 2,500 simulated customers,
so even a clean, correctly specified fit carries roughly a +/- 7 percent
band on the portfolio mean. Per-customer bands are far wider.
