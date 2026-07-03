# Elasticity identification, derived with the demo's numbers

Companion to `assets/hierarchical_elasticity.py`. Every number below comes
from that file's committed seed (world: 30 SKUs x 6 regions x 52 weeks,
true mean elasticity -1.74). Sources with URLs live in `sources.md`.

## The data-generating process

```
log p_it = lp0_c + pi z_it + phi d_it + e_it        pi = 0.6, phi = 0.20
log q_it = alpha_c + beta_c log p_it + gamma promo_it + d_it + eps_it
```

with z the wholesale-cost shifter (sd 0.15), d the demand shock the manager
sees (sd 0.35), e price-setting noise (sd 0.05), eps demand noise (sd
0.25), gamma = 0.55, and cell-level elasticities beta_c spread around -1.80
(SKU sd 0.45, region sd 0.20, idiosyncratic sd 0.10; the realized mean at
this seed is -1.74). The manager's phi > 0 is the disease: price and
quantity share the shock d.

## Simultaneity bias, computed in advance

Within a cell, the fixed-effects OLS estimand is

```
plim beta_FE = beta + cov(log p, u) / var(log p),   u = d + eps
             = beta + phi var(d) / (pi^2 var(z) + phi^2 var(d) + var(e))
```

Plugging the world's constants:

```
cov  = 0.20 * 0.35^2                      = 0.0245
var  = 0.36*0.0225 + 0.04*0.1225 + 0.0025 = 0.0155
bias = 0.0245 / 0.0155                    = +1.58
```

Predicted fixed-effects estimate: -1.74 + 1.58 = -0.16. The demo observes
-0.15. The bias swamps the signal at modest manager reactivity (phi = 0.20)
because the honest variation (pi z, sd 0.09 in logs) is small against the
reactive variation; that ratio, honest price variance over total price
variance, is the quantity to estimate on real data before promising an
observational elasticity at all. Pooled OLS without fixed effects lands at
-1.40 here through an accident of offsetting cross-sectional confounding;
treat that number as luck, and the -0.15 as the repeatable failure.

## The instrument and its estimand

The cost shifter satisfies relevance (first stage: pass-through 0.60,
strong by construction) and exclusion (z enters demand only through price).
Pooled 2SLS after the within transform recovers -1.77 for a true mean of
-1.74. Two field cautions:

- Exclusion dies quietly. A commodity cost boom during a demand boom (fuel,
  construction inputs) puts the instrument in the demand equation. Prefer
  supplier-idiosyncratic cost changes, list-cost updates on
  administratively scheduled dates, and FX pass-through on imported lines.
- The Hausman instrument, the same SKU's price in other cities, needs
  national demand shocks, national advertising, and coordinated pricing to
  all be absent or controlled. State the assumption in the deliverable
  when used; it is the weakest commonly used instrument.

2SLS answers with a variance-weighted average across cells. When the
deliverable prices individual SKU-region cells, the average is the wrong
shape, which motivates the hierarchical model.

## Control function inside a hierarchical model

First stage, within cells: regress log price on the cost shifter, keep the
residual `vhat = phi d + e`. Second stage, add rho * vhat to the demand
equation. Conditioning on vhat leaves only the z-driven part of price
identifying beta, so the price coefficient is clean while every cell still
contributes to the pooled hierarchy. In the linear homogeneous case this
reproduces 2SLS exactly; its value here is that it drops into a Bayesian
hierarchical model as one extra regressor.

Caveats that matter in production:

- vhat is a proxy for d contaminated by price noise e. With sd(e) = 0.05
  against sd(phi d) = 0.07 the residual confounding is visible only in the
  third decimal; audit the ratio on real data (price-implementation noise
  is often larger).
- The two-step procedure understates posterior uncertainty because vhat
  arrives as data. Bootstrap the first stage, or model both equations
  jointly, when interval width is load-bearing.
- A heterogeneous rho (managers in some regions react harder) is a real
  pattern; hierarchical rho_c is a cheap extension.

## Priors, with reasons

From the demo's model, which achieved 92% coverage at nominal 90%:

- `mu_beta ~ Normal(-1.5, 1)`. Centre in category-typical territory; most
  packaged-goods and general-merchandise categories sit between -0.5 and
  -3. The prior matters little at 180 cells and a real instrument; it
  matters a lot in the first month of an engagement when only 12 weeks of
  data have arrived.
- `sd_sku ~ HalfNormal(0.5)`, `sd_reg ~ HalfNormal(0.3)`,
  `sd_cell ~ HalfNormal(0.2)`. Scale priors encode where heterogeneity
  lives: across SKUs more than regions, with a small idiosyncratic floor
  so no cell is forced onto the additive structure.
- No hard sign truncation on beta_c. Truncation hides broken cells;
  shrinkage flags them instead (a cell pulled hard toward zero from
  positive territory has a data problem worth reading). Truncate only in a
  final production refit after the audit, if the optimizer requires signed
  inputs.
- Non-centred parameterization throughout, and the slope regressor centred
  within cell. Centring is the difference between the demo's failed run
  (posterior mean -1.48, coverage 0.52, max r-hat above 1.1, 4 minutes)
  and its passing run (-1.78, coverage 0.92, max r-hat 1.009, 21
  seconds) on identical data. The intercept-slope ridge from an uncentred
  regressor with level 4.1 and spread 0.12 is a geometry problem no
  sampler tunes its way out of.

## Separating promo lift from base elasticity

Model promo as its own regressor (flag, plus depth within promo when
depths vary) and estimate base elasticity from non-promo variation. The
demo recovers gamma = +0.54 against a truth of +0.55 simultaneously with
the elasticities. On real data add the two corrections the synthetic world
omits: pull-forward (a post-promo dip that a same-week regression books
into baseline) and display confounding (promo weeks buy visibility with
the price cut; without display flags the promo coefficient absorbs both).
Retail-analytics owns the full decomposition; this model consumes its
flags.

## Cross-price systems under sparsity

The workable form for a category of J items:

```
log q_i = a_i + beta_i log p_i + sum_{j in N(i)} theta_ij log p_j + controls
```

with N(i) restricted to same-category or same-need-state neighbours,
theta_ij shrunk hierarchically toward a category substitution rate, and
sign constraints where the merchandising relationship is known (substitutes
non-negative, complements non-positive). A dense unpenalized theta matrix
on 52 weeks of data returns noise off the diagonal, and a promo optimizer
consuming it will schedule around phantom substitution. Identification
needs the neighbours' prices to move for their own exogenous reasons, so
the instrument requirement applies to every column, and in practice promo
schedules provide most of the honest cross-variation. BLP-style structural
systems answer far-from-history counterfactuals at the cost of weeks of
modelling; fit them when the client question is a new entrant or a large
permanent repositioning, and use the regularized log-log system for
calendars and base prices.

## Reference-price asymmetry

The standard sticker-shock form adds gain and loss terms against a
reference r_t (exponentially smoothed past price is the common choice):

```
log q_t = a + beta log p_t + delta_g max(0, log r_t - log p_t)
                          + delta_l max(0, log p_t - log r_t) + ...
```

with the evidence saying delta_l > delta_g: Kalyanaram and Winer's 1995
consolidation calls the reference-price effect an empirical
generalization, Putler's egg study measured loss response about twice the
gain response, and Hardie, Johnson and Fader found the same asymmetry in
brand choice. The ratio is category-specific and decades of inflation
sit between those estimates and a 2026 client, so estimate delta_l/delta_g
on the client's data and carry only the direction as prior knowledge. The
operating consequences: increases need more evidence than equal-sized
decreases, staged increases beat one jump, and each deep promo lowers r
for every following week, a cost the promo calendar's objective should
carry explicitly.
