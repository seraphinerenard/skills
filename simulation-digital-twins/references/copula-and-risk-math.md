# Copula and risk-model mathematics

Companion to assets/monte_carlo_copula.py. Numbers labelled "computed" come
from scipy evaluations reproduced by the snippets shown.

## Gaussian copula construction

Sklar's theorem factors any joint distribution into marginals plus a copula.
The Gaussian copula sampling recipe: draw Z ~ N(0, R) with latent
correlation matrix R (via Cholesky), map U = Phi(Z) componentwise, then
X_j = F_j^{-1}(U_j) for arbitrary marginals F_j. Rank-based dependence
survives the monotone maps exactly, so elicit and state dependence targets
as Spearman or Kendall.

## Rank-correlation mappings

For a bivariate normal with Pearson correlation r:

    Spearman rho_s = (6/pi) arcsin(r/2)        Kendall tau = (2/pi) arcsin(r)

Invert the first to hit a Spearman target: r = 2 sin(pi rho_s / 6)
(Kruskal 1958, JASA 53). The raw-feed error (using rho_s directly as r),
computed:

| Spearman target | Latent r required | Error if fed raw |
|---|---|---|
| 0.30 | 0.3129 | +0.013 |
| 0.50 | 0.5176 | +0.018 |
| 0.60 | 0.6180 | +0.018 |
| 0.80 | 0.8135 | +0.014 |

The demo verifies the mapping end to end: targets 0.30/0.50/0.40 come back
as sample Spearman 0.302/0.499/0.401 at n = 20,000.

Elicited pairwise matrices are frequently not positive definite as a set
(three experts, three pairwise numbers, no joint consistency check). Repair
before Cholesky: eigenvalue clipping (in the asset) or Higham (2002)
alternating projections when the matrix is large and the clip distorts
entries you care about. Report the repaired entries back to whoever
elicited them; a 0.50 that becomes 0.41 after repair is a finding.

## Tail dependence, the Gaussian copula's structural limit

Upper tail dependence lambda_U = lim_{q->1} P(U_2 > q | U_1 > q). For the
Gaussian copula lambda_U = 0 for every r < 1: joint extremes decouple in
the limit, and a risk model built on it structurally understates the
probability that several inputs go wrong together. The t copula keeps tail
dependence alive:

    lambda = 2 * T_{nu+1}( -sqrt( (nu+1)(1-r) / (1+r) ) )

with T the univariate t CDF. Computed values:

| r | nu | lambda |
|---|---|---|
| 0.5 | 4 | 0.253 |
| 0.5 | 10 | 0.082 |
| 0.618 | 4 | 0.327 |
| any r < 1 | Gaussian limit | 0 |

Decision rule: when the client question involves joint stress ("price falls
while grade disappoints while capex overruns"), sample from a t copula with
nu fit to data where data exists, or nu in 4 to 8 as a stress convention
stated in the report. Swapping the copula changes P10 and P(NPV < 0) while
leaving every marginal untouched, which makes it the cleanest sensitivity
of the whole risk model.

## Iman-Conover as the alternative correlation injector

Iman and Conover (1982): reorder existing marginal samples so their ranks
match those of a reference multivariate normal sample with the target
correlation. This is what @RISK and most spreadsheet risk tools run under
the hood. Use it when the marginal samples already exist (bootstrap draws,
scenario outputs from other teams) and re-sampling through a ppf is
unavailable. The Gaussian-copula ppf route in the asset is equivalent in
distribution and simpler to reason about when you own the marginals.

## Quantile standard errors

The p-quantile estimator from n IID draws is asymptotically normal:

    se(q_p) = sqrt( p (1-p) / n ) / f(q_p)

with f the output density at the quantile, estimated in the asset by a
Gaussian KDE. Demo at n = 20,000: P10 SE 8 MUSD, P50 SE 8, P90 SE 14 on a
distribution whose interdecile range spans 2,157 MUSD. The formula exposes
the practitioner rule: tail quantiles need more draws because f is small
out there, so size n for the worst quantile you must quote, and print the
SE next to every quoted percentile. Round the deliverable numbers to the
SE: P90 = 1,553 with SE 14 supports "about 1,550", and three trailing
digits would overstate what the run knows.

For P(loss) style probabilities, the binomial SE sqrt(p(1-p)/n) applies
directly: the demo's P(NPV < 0) = 0.334 at n = 20,000 carries SE 0.003.

## What sensitivity analysis costs

| Method | Runs required | Valid with correlated inputs | Use when |
|---|---|---|---|
| One-at-a-time tornado | 2d + 1 | Misleading: moving one input while freezing correlated partners breaks the joint | Never with a correlated set; acceptable for independent screening |
| PRCC (in the asset) | 0 extra (reuses the MC sample) | Yes, under monotone response | Default tornado for cash-flow models |
| Sobol via Saltelli | N(d+2), so d = 8 at N = 1024 costs 10,240 | No; the variance decomposition loses uniqueness | Independent inputs and either a cheap vectorized model or a surrogate |
| Shapley effects | Higher still (permutation sampling) | Yes | Correlated inputs where a true variance attribution is contractually needed |
| ELSE | Reuse the sample with PRCC | Yes | The marginal cost is zero and the monotonicity assumption holds for most DCF-shaped models |

The demo's PRCC tornado on the open-pit NPV: price +0.94, grade +0.88,
recovery +0.71, opex -0.59, capex -0.43, which ranks the diligence agenda
(price assumptions and the grade model) without a single extra model run.
