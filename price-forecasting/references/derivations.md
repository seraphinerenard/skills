# Derivations and worked math

Companion to the price-forecasting SKILL.md. Every result here is implemented
and demo-checked in `assets/`; run the named module to reproduce the numbers.

## Ornstein-Uhlenbeck exact discretization and half-life

The OU process on a log price or spread,

$$dX_t = \kappa(\theta - X_t)\,dt + \sigma\,dW_t,$$

has the exact solution over a step of length $\Delta$:

$$X_{t+\Delta} = \theta + (X_t - \theta)e^{-\kappa\Delta} + \varepsilon_t,
\qquad \varepsilon_t \sim N\!\left(0,\ \frac{\sigma^2}{2\kappa}\bigl(1 - e^{-2\kappa\Delta}\bigr)\right).$$

This is an AR(1), $X_{t+1} = c + bX_t + \varepsilon$, with

$$b = e^{-\kappa\Delta}, \qquad c = \theta(1-b), \qquad
s^2 = \frac{\sigma^2}{2\kappa}(1-b^2).$$

OLS on the AR(1) therefore calibrates the OU exactly, with no Euler
discretization error:

$$\kappa = -\frac{\ln b}{\Delta}, \qquad \theta = \frac{c}{1-b}, \qquad
\sigma^2 = \frac{2\kappa\, s^2}{1-b^2}.$$

The half-life solves $e^{-\kappa H} = \tfrac12$, so $H = \ln 2 / \kappa$.
Worked: a daily series with $b = 0.977$ gives
$\kappa = -\ln(0.977) = 0.02327$ per day and
$H = 0.6931 / 0.02327 = 29.8$ days. The mapping is convex near $b = 1$: at
$b = 0.96$ the half-life is 17.0 days, at $b = 0.99$ it is 69.0 days, so
small estimation error in $b$ produces large error in $H$, always in the
same direction (see the bias below).

### Small-sample bias in the half-life

OLS estimates of AR(1) coefficients are biased downward by approximately
$(1 + 3b)/n$ (Kendall, Biometrika 1954). Since $H$ increases in $b$, the
fitted half-life is biased short. Measured by Monte Carlo in
`assets/ou_calibration.py` (true half-life 30 days, 400 paths per cell):

| n (daily obs) | median fitted H (raw) | median fitted H (Kendall-corrected) |
|---|---|---|
| 125 | 12.0 d | 26.7 d |
| 250 | 16.8 d | 27.4 d |
| 504 | 23.4 d | 32.0 d |
| 2016 | 27.3 d | 29.7 d |

A consultant fitting mean reversion on six months of data and reporting a
12-day half-life has measured the bias, and the client will trade on it. The
module applies the correction $\hat b_{corr} = \hat b + (1+3\hat b)/n$ and
reports a parametric-bootstrap interval whose upper end goes to infinity when
paths refit with $\hat b \ge 1$, which is the honest statement that the
sample carries weak evidence of mean reversion at all.

## VECM identification with a dominant common trend

For a spot-futures pair $y_t = (s_t, f_t)'$ with cointegrating vector
$\beta = (1, -1)'$, the VECM is
$\Delta y_t = \alpha \beta' y_{t-1} + \Gamma \Delta y_{t-1} + \mu + u_t$.
The basis $z_t = f_t - s_t$ then follows
$\Delta z_t = (\alpha_f - \alpha_s)(-z_{t-1}) + \dots$, so the identified
adjustment rate of the spread is $\alpha_f - \alpha_s$ and the basis
half-life is $\ln 2 / (\alpha_f - \alpha_s)$ under this normalization.

When the common trend's innovation variance is large relative to the basis
variance (daily trend moves of 1 to 2 percent against basis noise of a few
tenths, the usual case for storable commodities), the individual $\alpha_s$
and $\alpha_f$ are weakly identified: in the demo
(`assets/vecm_spot_futures.py`, n = 750, trend vol 1.2%/d, basis vol 0.4%/d)
the fitted pair is $(+0.051, +0.081)$ against true values $(-0.027, +0.007)$,
while the difference $0.030$ per day sits close to the true $0.034$ and the
implied 22.8-day half-life brackets the true 20. Forecasts and hedging rules
built on the spread survive this; price-discovery attributions built on
individual alphas from daily data do not.

## CRPS in the fair ensemble form

For an ensemble $x_1,\dots,x_m$ and outcome $y$,

$$\mathrm{CRPS} = \frac{1}{m}\sum_i |x_i - y| \;-\; \frac{1}{2}\,\widehat{E|X - X'|}.$$

The classic estimator divides the pair sum by $m^2$ and is biased: it rewards
under-dispersed ensembles because it includes the zero self-pairs. The fair
form (Ferro, QJRMS 2014) divides by $m(m-1)$ and is unbiased for the CRPS of
the distribution the members are drawn from. The pair sum computes in
$O(m\log m)$ per observation via the sorted identity
$\sum_{i<j}(x_{(j)} - x_{(i)}) = \sum_i (2i - m - 1)\,x_{(i)}$.

CRPS also equals twice the pinball loss integrated over quantile levels,
$\mathrm{CRPS}(F, y) = 2\int_0^1 \mathrm{PB}_\tau(F^{-1}(\tau), y)\,d\tau$,
so reporting mean pinball at the nine deciles approximates a CRPS ranking
and decomposes it by quantile, which tells the client whether the model
loses in the tails or in the middle.

## Diebold-Mariano with the HLN correction

Given loss differentials $d_t = L(e_{1t}) - L(e_{2t})$, $t = 1,\dots,n$, for
$h$-step forecasts, the DM statistic is
$\bar d / \sqrt{\widehat{\mathrm{LRV}}(d)/n}$ with the long-run variance
estimated by a rectangular kernel through lag $h-1$ (h-step optimal forecast
errors are MA(h-1), so the differentials inherit that autocorrelation).
Harvey, Leybourne and Newbold (IJF 1997) correct the finite-sample size
distortion by scaling with

$$\sqrt{\frac{n + 1 - 2h + h(h-1)/n}{n}}$$

and referring the result to $t_{n-1}$. At $n = 215$, $h = 5$ the factor is
$\sqrt{(215 + 1 - 10 + 20/215)/215} = 0.979$, which moved the demo statistic
from $-2.04$ to $-2.00$ and the two-sided p-value from 0.041 (normal
reference) to 0.047. At small $n$
and long $h$ the correction decides significance on its own; skipping it
overstates the case for the fancier model.

The truncated NW variance can go negative in small samples; the
implementation falls back to $\gamma_0$ when it does, and a Bartlett kernel
is the standard alternative when more lags matter.

## GARCH deciles at a procurement horizon

Aggregating GARCH to a 63-day horizon has no closed form for the level
distribution once innovations are Student-t, so the module simulates: fit
GARCH(1,1)-t on percent log returns, draw 20,000 paths of length 63,
compound $P_H = P_0 \exp(\sum_h r_h / 100)$, and read empirical deciles.
A normal approximation with the analytic variance
$\mathrm{Var}(\sum r) \approx \sum_h E[h_t]$ errs in a quantile-dependent
direction: a matched-variance Student-t (fitted dof 6.8) moves probability
mass from the shoulders into the centre and the extreme tails, so in the
demo the normal P10/P90 band is wider than the simulated one (33.0% versus
30.7% of spot) while beyond roughly P99 the simulation is wider (102.4
versus 99.5 on the up-tail from spot 74.50). The errors change sign across
quantiles, so no single variance inflation repairs the approximation, and
simulation is the method of record for any deliverable quoting both deciles
and tail scenarios.

## Pesaran-Timmermann and the directional trap

The PT test compares the observed hit rate $\hat p$ with the rate
$p^* = p_a p_f + (1-p_a)(1-p_f)$ produced by the marginal sign frequencies
under independence. A forecast that always calls "up" on a series drifting
up 65% of days posts a 65% hit rate and $p^* = 0.65$, so the statistic is
exactly zero. Directional accuracy quoted without the PT benchmark (or a
same-sample naive baseline) inflates every trending-market backtest;
`assets/forecast_eval.py` reproduces this with numbers.
