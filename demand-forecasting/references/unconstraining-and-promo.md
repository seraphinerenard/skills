# Censored demand and promotion effects

Sales data lies twice: it hides demand above the stock level (censoring) and
it moves demand across weeks (promotions). Both distortions sit in the target
variable, so no amount of model capacity fixes them; they get handled in data
preparation and feature design or they poison the forecast. URLs cited here
are consolidated in sources.md; the raw fact sheet with the full citation
trail is research/censored-demand-unconstraining.md.

## Censoring, the size of the hole

Sales = min(demand, availability). Training on raw sales biases the forecast
down, orders follow the forecast down, and service falls further; Cooper,
Homem-de-Mello and Kleywegt (Operations Research 2006) formalized this
spiral-down in revenue management, and Trapero, de Frutos and Pedregal (IJF
2024) restate it for supply-chain demand. Measured magnitude in groceries:
the FreshRetailNet-50K team (Dingdong, 898 stores) found raw sales
underestimate demand by 7.37% weighted percentage error, with hourly stockout
rates climbing from under 2% at 06:00 to 26% by 20:00 (arXiv 2505.16319,
accessed 2026-07-12). M5 has no stockout flags, so its zeros mix true
no-demand with out-of-stock, a documented weakness of every model trained on
it as-is.

## The three treatments, in order of preference

1. Mask. Flag out-of-stock periods and exclude them from the training loss
   (global models: drop the rows or weight them zero; statistical models:
   mark missing). Zalando's production transformer masks every data point
   with zero stock availability and additionally imputes article demand from
   a multinomial size-distribution when only some sizes stocked out (arXiv
   2305.14406). AWS's Amazon Forecast guidance says the same: fill
   out-of-stock targets with NaN, never zero. Masking is safe and cheap; its
   cost is losing the lower-bound information that demand was at least the
   observed sales, and it fails silently when the stockout flags are wrong
   (phantom inventory; the retail-analytics skill owns that detection
   problem).
2. Impute from within-period profiles. When the item was in stock for part of
   the period, scale up by the profile share: sold 70 units through Friday
   noon, and Mon-to-Friday-noon normally carries 62% of a week, estimate
   70 / 0.62 = 113. Blue Yonder documents exactly this arithmetic for its
   "true demand" concept. The refined versions use stockout timing formally:
   Jain, Rudi and Wang (OR 2015) show the stockout time alone recovers most
   of the censored information; Sachs and Minner (IJPE 2014) use hourly
   timing patterns and remove about 76% of the expected-profit loss versus
   knowing only that a stockout happened.
3. Censored likelihoods. Fit the demand distribution acknowledging the cap:
   EM on a censored normal (the airline lineage), negative binomial censored
   MLE for retail counts (Agrawal and Smith 1996 found NB fits SKU demand far
   better than Poisson or normal), or a Tobit Kalman filter / Tobit ETS with
   the censoring level set to on-hand stock per period (Trapero et al. IJF
   2024; Pedregal et al. arXiv 2407.17920).

Worked EM iteration, censored normal. Five weeks of sales [8, 10, 12, 9, 12]
where both 12s were stockouts at a stock level of C = 12. Treating sales as
demand gives mean 10.20, sigma 1.79. The E-step replaces each censored week
with E[X | X >= 12] = mu + sigma * phi(z) / (1 - Phi(z)), z = (12 - mu)/sigma;
the M-step re-estimates (mu, sigma) from the completed data:

| iteration | E[X given X >= 12] | mu | sigma |
|---|---|---|---|
| 1 | 12.94 | 10.58 | 2.09 |
| 2 | 13.24 | 10.70 | 2.27 |
| 3 | 13.41 | 10.76 | 2.37 |
| converged | 13.63 | 10.85 | 2.49 |

Demand mean 10.85 sits 6.4% above the sales mean, and sigma grows 39%; the
naive estimate was too low and too confident, which is the generic signature
of ignoring censoring. With two of five observations censored this small
sample is at the edge of what EM tolerates; Kourentzes, Li and Strauss (JRPM
2019) show EM degrades badly with few sales events and propose
intermittent-demand variants for that regime.

Two corrections before crediting the focal SKU with all recovered demand.
Substitution: within-category stockouts push demand to neighbours, so
single-SKU unconstraining overstates category demand; the Vulcano, van Ryzin
and Ratliff EM over an MNL choice model (OR 2012) estimates first-choice
demand from sales, availability and a market-share estimate. Browse signals:
where the channel records intent during stockouts, prefer the counterfactual
directly; Amazon reconstructs demand as observed demand plus conversion rate
times out-of-stock glance views (Madeka et al., arXiv 2210.03137), which beat
model-based imputation in their 26-week A/B over 10,000 products.

## Promotions, the arithmetic of a lift

A promo week is three effects wearing one number: genuine incremental
consumption, demand pulled forward from future weeks (pantry loading), and
demand pulled sideways from substitutes (cannibalization) or dragged along
with complements (halo). Decompose before believing any uplift figure.

Worked decomposition. SKU baseline 100 units/week. Promo week at 25% off
sells 280. The following week sells 80.

- Single-week read: uplift multiplier 2.8, incremental 180 units.
- Two-week read: the post-promo trough is 20 units below baseline, so
  pantry loading pulled 20 forward; net incremental = 280 + 80 - 200 = 160,
  11% less than the single-week read.
- Category read: a substitute SKU fell from 60 to 45 during the promo week,
  so category-net incremental = 160 - 15 = 145, and the finance case for the
  promo should run on 145, a fifth smaller than the naive 180.

Modelling prescription that captures this in a global GBM or regression:

- Promo indicators split by mechanic and depth (display, feature, price cut
  bands), because a 10% TPR and a BOGO have different multipliers.
- Lagged promo features (promo_lag1, promo_lag2) so the model can learn the
  trough; without them the post-promo weeks read as unexplained bad weeks and
  the baseline estimate drags down.
- Price as log(price / regular_price) so the coefficient reads as elasticity
  against the item's own reference price. Regular price comes from a rolling
  mode or the price-optimization sibling skill; do not let promo price define
  the reference.
- Partial pooling of uplift across the category for sparse promo histories: a
  SKU promoted twice has no stable own-uplift; shrink its multiplier toward
  the category-mechanic mean (hierarchical Bayes or a category-level
  interaction in the GBM). M5's organizer Finding 7 quantifies the covariate
  value at the statistical end: ES with promo/event regressors beat plain
  top-down ES by 6%, ARIMAX beat ARIMA by 13%.
- Forward-buy is stronger for storable items and heavy users; perishables
  show small troughs. If the client sells canned goods, expect the two-week
  read to cut measured uplift by 10-30%; take the exact split from the lag
  coefficients, never from a rule of thumb.

Cannibalization and halo need cross-item features (promo flags of the top
substitutes and complements as regressors on the focal SKU) or a category-
level model whose total is reconciled down. Causal attribution of promo
effects beyond predictive decomposition belongs to the causal-inference
sibling skill; forecast governance of override-heavy promo processes belongs
to model-operations.
