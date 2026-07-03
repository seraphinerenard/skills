---
name: price-optimization
description: |
  Price-setting engagements end to end. Covers elasticity estimation from
  observational sales data (simultaneity, cost-shifter instruments,
  hierarchical Bayes with a control function), retail base-price and markdown
  optimization, promo calendars with cannibalization, B2B quote pricing with
  win-rate curves and guardrail bands, and the legal limits on pricing
  algorithms. Trigger on: "estimate price elasticity", "what should we
  charge", "markdown plan", "clearance pricing", "promo calendar",
  "optimize our quotes", "discount guardrails", "win-rate pricing",
  "price test design", "/price-optimization".
---

# Price optimization

This skill owns setting our price. Forecasting market prices we accept
(commodities, power, freight) belongs to price-forecasting. Demand-model
mechanics belong to demand-forecasting, promo-lift and cannibalization
measurement to retail-analytics, and experiment design to causal-inference.
The chain in every engagement runs: identify elasticity, optimize under the
business's real constraints, validate with a test, roll out behind
guardrails, and monitor the realized response.

## Elasticity comes before optimization

Everything downstream consumes an elasticity, and observational
price-quantity data is adversarial: price moves because someone responded to
demand. A category manager who raises price when demand runs hot writes his
own decision rule into the data, and a log-log regression then recovers the
manager, with a confident standard error and the wrong sign. The demo in
`assets/hierarchical_elasticity.py` builds a 30-SKU x 6-region x 52-week
panel with true mean elasticity -1.74, a manager who loads 0.20 of the
demand shock into price, and a wholesale-cost shifter as the honest source
of variation. Recovery by method:

| method                     | mean estimate | cell RMSE | sign errors |
|----------------------------|--------------:|----------:|------------:|
| A pooled OLS               |         -1.40 |      0.62 |           0 |
| B cell fixed-effects OLS   |         -0.15 |      1.67 |           0 |
| C pooled 2SLS + FE         |         -1.77 |      0.53 |           0 |
| D per-cell 2SLS            |         -1.85 |      0.81 |           2 |
| E HB + control function    |         -1.78 |      0.20 |           0 |

Method B deserves the stare: fixed effects cure cross-sectional confounding
and leave simultaneity untouched, so the estimate lands at -0.15 and the
client hears "price barely matters". The bias is computable in advance
(derivation with these exact numbers in
`references/elasticity-identification.md`): predicted -0.16, observed -0.15.
Method E pairs the instrument with partial pooling and hits a 0.20 cell RMSE
with 92% coverage from a nominal 90% interval. C gets the average right and
prices every cell with the same number; D is unbiased and unusable.

### Choosing the identification strategy

Ranked by how often the data supports them in practice:

| Data situation | Identify with | It works when |
|---|---|---|
| Wholesale cost, freight, or FX moves that reach shelf price | 2SLS or a control function on the cost shifter | Pass-through is strong (demand a first-stage F above 20) and the cost shock stays out of demand; a supplier's idiosyncratic repricing qualifies, a commodity boom that also heats end demand does not |
| A ladder migration, pack-size change, or zone re-map | Before-after contrast around the change with matched control stores | The change came from policy or cost, with no co-timed promo, assortment, or display change |
| Frequent promos with recorded flags and depths | Promo-window contrasts; depth variation traces the promo-price curve | Display and feature flags exist, so the price effect separates from the visibility effect |
| Many stores with staggered administrative price changes | Store-week panel fixed effects with event-time plots | The timing came from rounding cycles or zone syncs, uncorrelated with local demand |
| Thousands of SKUs with thin history each | Hierarchical Bayes partial pooling layered on one of the schemes above | Pooling cuts variance only; it never repairs endogeneity |
| No exogenous variation anywhere | Run a price test before any optimization (causal-inference owns geo and switchback designs) | The client accepts 4-8 weeks of testing before the optimizer speaks |
| ELSE | Hierarchical Bayes with a cost-shifter control function, then a price test on the top revenue cells before rollout | The default for retail panels that carry cost data |

The Hausman-style instrument (the same SKU's price in other cities) fails
exactly where it is most tempting: national demand shocks, national
advertising, and coordinated pricing all sit in both cities' prices, so the
exclusion restriction dies. Use it only with region-specific demand controls
and say so in the report.

### The hierarchical model, specified

The working specification from the demo, which recovered truth on synthetic
data (priors and reasoning expanded in
`references/elasticity-identification.md`):

```
log q_it = a_c(i) + beta_c(i) * logp~_it + gamma * promo_it + rho * vhat_it + eps_it
beta_c   = mu_beta + sd_sku * z_sku(c) + sd_reg * z_reg(c) + sd_cell * z_cell(c)
mu_beta  ~ Normal(-1.5, 1)        sd_sku, sd_reg, sd_cell ~ HalfNormal
vhat     = residual of within-cell log price on the cost shifter
logp~    = within-cell centred log price
```

Three implementation facts carry most of the value:

- Centre log price within cell. Raw log price has level about 4.1 against
  within-cell spread about 0.12, which welds each cell's intercept to its
  slope along a ridge and stalls the sampler on `mu_beta`. In the demo,
  centring moved the posterior mean from -1.48 to -1.78, coverage from 0.52
  to 0.92, and runtime from 4 minutes to 21 seconds. An uncentred
  hierarchical elasticity model that "converged" deserves an r-hat audit
  before anything else.
- The control function residual `vhat` is what buys identification; the
  hierarchy only buys precision. Skipping `vhat` gives beautifully shrunk
  versions of method B's wrong answer.
- Keep the prior on `mu_beta` centred in category-typical territory (most
  grocery and general-merchandise categories live between -0.5 and -3) and
  let the data move it. Hard sign truncation on cell elasticities hides
  data problems; a cell that wants a positive elasticity is a data quality
  alarm, and shrinkage should absorb it while it gets investigated.

Tooling, as of mid-2026: PyMC 6.1 (May 2026 6.0 broke the API: PyTensor 3,
numba default backend, nutpie as default NUTS when installed, ArviZ 1.0
DataTree) and NumPyro 0.21 both handle this model class; nutpie reports
about 2x Stan on posteriordb, and the JAX path is the scaling lever past
roughly 50,000 observations. pymc-marketing contains MMM, CLV, and choice
models and has no pricing module, so hierarchical elasticity stays
hand-built. A published reference implementation at useful scale is Orduz's
87-SKU, 33-category hierarchical elasticity model (NumPyro SVI). Sources
with URLs sit in `references/sources.md`.

### Promo lift and base elasticity are different numbers

A promo week bundles a price cut with display, feature, and often quality
signalling, and the volume spike includes pull-forward that a naive
regression books as price response. Fit them separately: promo flags (and
depth within promo) identify the promo curve; base elasticity comes from
non-promo price variation only. The demo's model recovers the promo lift
+0.54 against a truth of +0.55 while estimating base elasticity from the
cost-driven variation. Post-promo dip measurement and the full lift
decomposition belong to retail-analytics; consume their output, and when
they report lift that decays across repeated promos, feed the decayed
number into the calendar optimizer below.

### Cross-price effects need sparsity to survive

A dense J x J elasticity matrix from one year of weekly data is noise off
the diagonal, and any optimizer downstream will arbitrage the noise. Ridge
or lasso on the off-diagonals of a log-log system is the floor. Better:
restrict cross-terms to pairs inside a category or need-state, pool them
hierarchically (pair effects shrink toward a category-level substitution
rate), and constrain signs (substitutes get non-negative cross-price
terms). BLP-style structural demand earns its cost when the client needs
counterfactuals far from history; on consulting timelines the regularized
log-log system with a hierarchy answers the calendar and base-price
questions first.

### Reference prices make response asymmetric

Buyers respond to price against an internal reference formed by past
prices, and losses outweigh gains: the Kalyanaram and Winer 1995 empirical
generalizations paper consolidated the evidence, with Putler's egg-demand
study measuring loss response roughly double the gain response and Hardie,
Johnson and Fader showing the same pattern with brand choice. Two
operational consequences. First, a price increase gets punished more than
the symmetric decrease helps, so increases need a higher evidence bar than
decreases of the same size, and staged small increases beat one large one.
Second, deep frequent promos reset the reference price downward and tax
every future full-price week; that cost belongs in the promo calendar's
objective. Magnitudes vary by category and era; treat the asymmetry
direction as settled and the ratio as something to estimate on the client's
data (model form in `references/elasticity-identification.md`).

## Optimization by archetype

| Business shape | Formulation | Worked asset |
|---|---|---|
| Stable catalogue, base prices | Per-item search over the price ladder under margin, index, and line constraints | formulation below |
| Seasonal stock, hard end date, no reorder | Finite-horizon DP over (week, inventory, ladder step) | `assets/markdown_dp.py` |
| Weekly promo slots across an assortment | MILP with a cannibalization penalty matrix | `assets/promo_milp.py` |
| Quoted B2B deals against a reference price | Win-rate logistic, expected-margin FOC, guardrail bands | `assets/b2b_quote_optimizer.py` |
| Plant or quarry near capacity | Elasticity rule with the capacity shadow price added to cost | `references/optimization-formulations.md` |
| ELSE | Write profit and constraints explicitly, match the constraint structure to the nearest archetype above, and split mixed businesses by channel | - |

### Retail base price

The optimizer proposes; the constraint set disposes. Encode all of these or
the recommendations die in review: the chain's price ladder and ending-digit
rules (Anderson and Simester's catalogue field experiments found 9-endings
raising demand even against lower neighbouring prices, so endings are a
constraint, and fighting them costs real volume); margin floors by category
role; competitor index bands on known-value items (KVIs price to index,
blind items recover the margin); line-pricing gaps inside good-better-best
families; and a maximum step per change cycle, because a 15% jump invites
reference-price punishment that a 2x4% staircase avoids. What large vendors
deploy matches this shape: Revionics describes Bayesian hierarchical demand
models with an optimizer on top (TensorFlow and SciPy in their 2024
technical interview), and none of Revionics, Blue Yonder, or o9 claims
reinforcement learning in production pricing in their own materials. Treat
all vendor lift claims as marketing: the one named-client number with a
metric attached is Farmacorp's 10% year-over-year revenue growth, and the
5-10% gross-profit lift ranges circulating in whitepapers trace back to the
vendors themselves.

### Markdown

The DP in `assets/markdown_dp.py` prices the option value of inventory:
hold price when stock is thin, drop early when stock is heavy and season
traffic can still absorb units. On the demo season (16 weeks, 400 units,
$60 full price, ladder 60/45/36/24, elasticity -2.8, $8 salvage) the DP
books $18,367 expected revenue against $16,011 for a fixed
week-8/12/14 calendar (+14.7%) and $13,580 for no markdowns (+35.2%).
Deliver the policy as a threshold frontier (week 2: marked down if more
than 302 units remain; week 8: 92), because merchants can run a frontier
without a solver in the room. Use markdown-range elasticity estimated from
past clearance windows; base-price elasticity is smaller and under-marks
every season. The published field results set honest expectations:
Zara's optimized clearance pricing raised clearance revenue about 6% in a
country-level experiment, and Rue La La's first-exposure price
optimization raised revenue about 9.7% (90% CI 2.3% to 17.8%). Single-digit
lift on the affected revenue is the honest promise; re-estimate the demand
rate from early sell-through and re-solve nightly, which both deployments
above did.

### Promo calendar

`assets/promo_milp.py` selects item-weeks under slot, frequency, gap, and
budget constraints with same-week substitute penalties. The demo's greedy
baseline (rank by own margin, ignore cannibalization) actually books more
own margin and then hands 12% of it back in four substitute clashes; the
MILP nets $78,146 against greedy's $68,861, +13.5%. Cannibalization
concentrates exactly where naive ranking concentrates, in the same
categories and hot weeks. The penalty-only pair encoding keeps pair
variables continuous (details in `references/optimization-formulations.md`),
so the model scales linearly in items times weeks.

### B2B and industrial quotes

Start every B2B pricing engagement with the pocket-price waterfall (Marn
and Rosiello, HBR 1992): walk invoice price down through on-invoice
discounts, rebates, co-op money, freight absorption, payment terms, and
returns to the pocket price, then plot the pocket-price band by customer
for one product. The band is routinely wide enough that the first
deliverable writes itself; Marn and Rosiello's cases turned small realized
price gains into large profit gains (3% price, +35% operating profit at an
industrial equipment maker; 2.5% price, +30% at a consumer durables firm),
because price falls straight to operating profit at typical margins.

Then fit the win-rate curve and optimize expected margin. The FOC gives
markup = r / (100 b (1 - w*)) for a logistic win curve with premium
sensitivity b per percentage point against reference price r; the demo deal
(r $100, cost $78, b 0.12) prices at $102.71 with a 66% win rate, and the
95%-of-optimum band spans $98.12 to $107.31, 8.9% of target. Hand sales
that band as floor, target, and stretch with escalation above the band and
a hard stop below floor; the flat top of the profit curve is what makes
bands cheap and adoption real. Two traps carry most of the failure mass:

- Win-loss endogeneity. Reps cut price on deals they can see are
  competitive, so the naive premium coefficient flips positive (+0.045 in
  the demo against a truth of -0.120) and the data appears to say price
  never mattered. A competitiveness proxy (bidder count) restores most of
  the coefficient (-0.107); the honest fix is a randomized band-width test
  on a slice of quotes.
- Segmentation without pooling. Deal size, region, and customer tier move
  both a and b, and cutting the data into 40 segments of 30 quotes each
  reproduces method D from the elasticity table. Pool the segment
  coefficients hierarchically, same machinery as SKU elasticities.

In aggregates and building materials specifically, haul distance makes
every market local and capacity turns discounts into displacement: a
discounted tonne from a full quarry displaces a full-price tonne, so the
effective cost under the FOC is cost plus the capacity shadow price
(worked in `references/optimization-formulations.md`; volume planning in
supply-chain-optimization).

## Validation and rollout safety

- Do not price outside the observed range. A constant-elasticity fit is a
  local approximation, and an optimizer with loose floors will happily
  recommend prices 30% beyond any price the data contains. Clamp the
  candidate set to the observed support (plus at most one ladder step) and
  widen only through tests.
- Test before rollout. Validate the model's top-revenue cells with a geo or
  switchback price test (designs in causal-inference); the model predicts
  the test outcome before it runs, and the prediction goes in writing. A
  model that cannot call its own test does not price a category.
- Monitor realized elasticity. After rollout, regress realized volume
  changes on realized price changes cell by cell and compare against the
  model (mechanics in model-operations). Elasticities drift with
  competitor moves, inflation psychology, and assortment shifts; grocery
  demand around the 2022-2024 inflation wave repriced whole categories'
  elasticities, so a quarterly refresh is the floor.
- Design guardrails the pricing team accepts: maximum step per cycle,
  category margin floors, KVI no-increase lists, competitor index bands,
  and change-frequency caps. Every recommendation carries its reason
  (elasticity, cost change, index breach) in plain words, because a price
  the merchant cannot explain to a store manager gets overridden, and
  overrides are the adoption metric: log them with reason codes, review
  weekly, and treat a rising override rate as a model bug report.

## Legal lines and organizational reality

- Never pool competitor pricing data into the engine. The RealPage
  settlement (DOJ, November 2025) is the operating blueprint: runtime
  recommendations from the client's own data plus public data only, any
  pooled training data at least 12 months old and no finer than statewide,
  and no vendor-hosted forums where competitors discuss pricing. The
  hub-and-spoke theory reaches a common vendor that ingests competitors'
  nonpublic data even when the competitors never speak, and the evidence
  that coordination concerns are real is published: German gas stations
  gained about 9% margin from algorithmic pricing overall and about 28%
  where both duopolists adopted (JPE 2024), and Q-learning pricers learn
  supracompetitive pricing without communication (Calvano et al., AER
  2020).
- Competitor-index constraints built on public shelf prices are fine;
  benchmarking services that pool members' nonpublic transaction prices
  are the Agri Stats / RealPage fact pattern wearing a B2B suit. Decline.
- Bound every automated repricer with absolute floors and ceilings. The
  canonical failure is the 2011 Amazon book spiral: two ratio-rule
  repricers with no sanity bound multiplied a biology text to $23.7M.
  Amazon's own Project Nessie allegations (raise, wait for followers, keep
  the elevated price) show follower-aware logic drawing regulatory fire.
- Personalized pricing on individual behavioural data sits under an open
  FTC 6(b) study (surveillance pricing, staff findings January 2025).
  Segment pricing on cost-to-serve and willingness-to-pay at the segment
  level; individual-level price targeting needs counsel in the room.
- Robinson-Patman is enforced again: the FTC's Southern Glazer's suit
  (filed December 2024) survived dismissal in April 2025 and resolved in
  2026. For B2B discount architecture this means volume discounts need
  published, practically available tiers, and functionally identical
  customers should not discover multi-point pocket-price gaps without a
  cost justification behind them.
- MAP agreements cap advertised resale prices; encode them as hard
  constraints on the advertised channel and let pocket levers (bundles,
  freight, terms) carry differentiation.
- Framing decides survival. Wendy's announced "dynamic pricing" in
  February 2024 and ate a national backlash within two weeks despite never
  planning surge pricing; discount-in-the-trough framing of the identical
  mechanism draws none of it. Deliver price changes as markdowns,
  round-downs, and targeted discounts wherever the economics allow.

## Assets

All demos run on synthetic data with known ground truth and print
recovery-versus-truth numbers. Pip names sit in each file's top comment.

- `assets/hierarchical_elasticity.py` (numpy, jax[cpu], numpyro): the
  five-method recovery shootout and the HB control-function reference
  implementation; about 25 seconds on CPU.
- `assets/markdown_dp.py` (numpy, scipy): markdown DP with Monte Carlo
  validation and fixed-calendar benchmarks; seconds.
- `assets/b2b_quote_optimizer.py` (numpy, scipy): win-rate MLE with
  recovery check, the endogeneity trap demo, FOC pricing, and guardrail
  bands; seconds.
- `assets/promo_milp.py` (numpy, scipy >= 1.9 for HiGHS): promo calendar
  MILP against a cannibalization-blind greedy; seconds.

## References

- `references/elasticity-identification.md`: bias algebra with the demo's
  numbers, control-function derivation and caveats, full prior reasoning,
  reference-price model forms.
- `references/optimization-formulations.md`: the B2B FOC derivation, the
  markdown Bellman recursion, the MILP encoding, capacity shadow pricing.
- `references/sources.md`: every external claim above with URL and access
  date, plus which claims rest on training knowledge.
- `references/research/`: researcher fact sheets (tooling,
  vendors, regulation) with per-claim URLs.
