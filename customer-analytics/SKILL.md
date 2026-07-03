---
name: customer-analytics
description: Churn and retention analysis, customer lifetime value, retention-offer targeting by uplift, and customer or store segmentation. Trigger tasks include building or auditing a churn model, estimating CLV or cohort payback, deciding who receives a retention offer, evaluating a campaign with Qini curves, segmenting customers for CRM actions, and clustering stores for assortment localization.
---

# Customer analytics

This skill covers churn and retention modelling, CLV, uplift-based retention
targeting, and segmentation of customers and stores. The reader already knows
the standard methods; what follows is the judgment layer: which model family
the business shape forces, the label traps that quietly invalidate churn
work, the worked numbers behind each recommendation, and the tooling that is
actually alive in 2026. Experiment design belongs to the causal-inference
skill; assortment and store operations belong to retail-analytics, which
consumes the store clusters built here; consulting-cases consumes the cohort
and CLV outputs in diligence work.

Code lives in `assets/` (four runnable modules, numpy/scipy/pandas/sklearn
plus lifelines, each with a synthetic-data demo under `__main__`).
Derivations and extended notes live in `references/`.

## The business shape picks the model family

Ask one question before any churn or CLV work: is the relationship
contractual (the customer must act to leave, so churn is an observed event)
or non-contractual (the customer just stops showing up, so churn is a latent
state you infer)? Every method choice downstream follows from this and from
whether purchasing happens continuously or at discrete occasions.

| Business shape | Example | Churn observability | Method |
|---|---|---|---|
| Contractual, continuous billing | SaaS monthly plans, telecom, utilities | observed event with a date | discrete-time hazard or Cox with time-varying covariates (`assets/survival_churn.py`) |
| Contractual, discrete renewals | annual insurance, season tickets, maintenance contracts | observed at each renewal gate | shifted-beta-geometric on renewal counts (Fader-Hardie 2007; implemented in pymc-marketing) |
| Non-contractual, continuous purchasing | grocery, e-commerce, marketplaces | latent; infer from silence | BG/NBD plus gamma-gamma (`assets/btyd_clv.py`) |
| Non-contractual, discrete occasions | annual appeals, conference attendance | latent, one chance per period | BG/BB (Fader, Hardie and Shang 2010) |
| ELSE (mixed: subscription plus one-off purchases, freemium with paid tiers) | streaming with merch store | mixed | split the revenue streams and model each with its own row above; one blended churn number misstates both sides |

Classifier-only churn modelling ("predict churn in the next 30 days" with
gradient boosting on a snapshot) is defensible only for contractual
businesses with short horizons and stable tenure mix, and even there the
survival framing below produces the same scores with fewer artifacts.

## Churn label construction

Most failed churn engagements die at the label, months before anyone debates
models. The traps, with detection:

| Trap | What goes wrong | Detection and fix |
|---|---|---|
| Fixed activity window in non-contractual ("no purchase in 90 days = churned") | long-cycle customers get labelled churned while alive; the model learns to predict purchase cadence | compare each customer's silence against their own interpurchase gaps (label at their q90 gap); or drop the binary label and use BTYD's P(alive) |
| Seasonal shoppers | holiday-only buyers flip to "churned" every spring and "reactivated" every December | measure the resurrection rate: the share of labelled churners who purchase again within 12 months; above roughly 10 to 15 percent, widen the window or switch to model-based labels |
| Retention-campaign contamination | past campaigns changed outcomes for whoever the old targeting rule picked; labels now encode the old policy, and a model trained on them re-learns it | log treatment exposure per customer; add it as a feature or train on the untreated; keep a 2 to 5 percent permanent no-contact holdout from now on |
| Tenure censoring | recently acquired customers cannot have churned yet; snapshot training sets conflate tenure with survival | survival framing handles censoring by construction; for classifiers, fix an observation window per acquisition cohort |
| Voluntary and involuntary churn merged | payment failures ride in the same label as cancellations | split the labels; dunning fixes involuntary churn and offers address voluntary churn, so a merged model mistargets both |

## Survival churn for contractual businesses

Frame contractual churn as a hazard over tenure. Censoring, the tenure
confound, and time-varying covariates (price changes, support tickets,
engagement) all enter cleanly, and the same fit answers "who is at risk"
and "what moved the risk".

Two estimators cover practice, both in `assets/survival_churn.py`:

- Discrete-time hazard: expand to person-periods (one row per customer per
  billing month) and fit a logistic regression with tenure-bucket dummies
  plus covariates. This is the default for monthly billing: it is a
  calibrated GLM, covariates update per row by construction, and any
  classifier upgrade (boosting on person-months) drops in later without
  reframing the data.
- Cox with time-varying covariates (`lifelines.CoxTimeVaryingFitter`) on
  (id, start, stop, event) rows, when time is continuous or the client
  expects hazard ratios.

The demo simulates 3,000 subscribers (51,944 person-months, 898 churn
events) where a price increase temporarily lifts the hazard. The
person-period logit recovers the true price-increase coefficient 0.90 as
0.89; on held-out person-months the top predicted-hazard decile shows 1.7x
the base churn rate with calibration holding across deciles. Two cautions
that survive contact with production: monthly hazards near 1 to 2 percent
mean even a well-ranked top decile churns at only 3 to 4 percent, so set
campaign expectations from the calibration table and never from AUC; and any
forecast beyond the next period requires an assumed covariate path (will
engagement hold at its last value?), so the honest short-horizon product is
next-period risk refreshed monthly. Drift monitoring for the deployed score
belongs to model-operations.

## BTYD for non-contractual businesses

For continuous non-contractual purchasing, fit BG/NBD for the
transaction-and-dropout process and gamma-gamma for spend per transaction.
Full likelihood derivations, the Pareto/NBD formulas, and worked numerics
are in `references/btyd-likelihoods.md`; `assets/btyd_clv.py` implements
the MLE from scratch (numpy plus scipy only) and reproduces the published
Fader-Hardie example: with the CDNOW parameters (r 0.243, alpha 4.414,
a 0.793, b 2.426), the customer with x=2, t_x=30.43, T=38.86 weeks gets
E[Y(39 weeks)] = 1.2260 against the paper's 1.226.

What the parameters say, and where readings go wrong:

- r/alpha is the mean repeat rate for a just-acquired customer (CDNOW: 0.055
  per week). a/(a+b) is the mean dropout probability per transaction (CDNOW:
  0.246, so the average customer survives about four purchases).
- Recency dominates frequency. Two demo customers with identical x=4, T=52:
  the one last seen at week 40 gets P(alive) 0.70; last seen at week 12 gets
  0.03. Present P(alive) tables to clients sorted by recency or they will
  read the model as broken.
- Zero-repeat customers get P(alive) = 1 forever, because BG/NBD only allows
  dropout at a purchase. On retail bases where 40 to 60 percent never
  repeat, that block's CLV rests entirely on the prior. MBG/NBD (Batislam
  et al. 2007; in pymc-marketing) adds a dropout draw at time zero and
  repairs this.
- P(alive) is a sawtooth: it jumps at each purchase and decays between
  purchases. Threshold-triggered campaigns re-arm after every purchase,
  which is usually what you want, and needs saying in the design doc.
- A fitted gamma-gamma q near 1 means the spend distribution's mean is
  carried by a few whales; report the top decile's CLV separately before
  multiplying any means.

Tooling, verified 2026-07 (details and URLs in `references/sources.md`):
`lifetimes` was archived June 2024 with its last release in 2020, and its
README hands off to pymc-marketing; the `btyd` fork is archived too. R users
have CLVTools under active maintenance.

| Situation | Tool |
|---|---|
| Production Python, want covariates, MBG/NBD, or posterior bands | pymc-marketing CLV module (0.19.4, 2026-05; Python 3.12+; MAP for speed, full MCMC for bands; heavy PyMC/PyTensor install) |
| Light dependency budget, standard BG/NBD + gamma-gamma | `assets/btyd_clv.py` from-scratch MLE, validated against published values |
| R stack, or need Pareto/NBD with time-varying covariates | CLVTools |
| Literature variants (Pareto/GGG, hierarchical Bayes Pareto/NBD) | BTYDplus in R |
| ELSE | start with `assets/btyd_clv.py`; move to pymc-marketing when covariates or posteriors earn the install |

Fitting note that saves an afternoon: BTYD likelihoods go near-flat when the
calibration window is short relative to lifetimes (the BTYD package docs
recommend multiple optimizer starts). Hold out the last 25 to 40 percent of
the window and check predicted against actual repeat transactions per
customer decile before trusting any parameter reading.

## Retention targeting is an uplift problem

A churn-risk ranking answers "who leaves". The campaign question is "whose
leaving does the offer change", and the two rankings diverge because the
high-risk block mixes lost causes (leave regardless) with sleeping dogs
(leave because you contacted them), while sure things fill the safe-looking
deciles. Ascarza (2018, JMR 55(1)), across two randomized field experiments,
found the lowest-lift deciles churned more when treated and that
lift-based targeting beat risk-based targeting by up to 6.8 points of churn
reduction.

The demo in `assets/uplift_qini.py` makes the budget case concrete. A
simulated base (60,000 customers, randomized offer, control churn 21
percent, average treatment effect +2.2 points on retention) with
persuadables, sleeping dogs and both null types, evaluated on a
20,000-customer holdout targeting the top 30 percent:

| Policy for the top 30% | Incremental saves per 10,000 contacted |
|---|---|
| Churn-risk ranking | 190 |
| Blanket campaign (contact everyone, for reference) | 222 |
| T-learner uplift ranking | 650 |
| True-uplift oracle (upper bound) | 839 |

Risk-based targeting landed below the blanket campaign: the offer's cost went
to exactly the customers it moves least (and some it moves the wrong way).
The uplift ranking also concentrates the effect: its Qini curve captures 87
percent of the campaign's total incremental retention within the top 30
percent of the base (worked Qini table in
`references/uplift-evaluation.md`).

Estimator selection, condensed (full reasoning in the reference):

| Situation | Estimator |
|---|---|
| Randomized campaign data, need a ranking this week | T-learner: two boosted classifiers, difference of predicted retention |
| Randomized, very large N, one maintainable model | transformed outcome Y(W-e)/(e(1-e)) regressed directly |
| Observational logs only | DR-learner with cross-fitting; results provisional until a randomized readout exists (see causal-inference) |
| Segment-level effect CIs for a rollout decision | causal forest with honest splitting (econml `CausalForestDML`) |
| ELSE | T-learner; it degrades most gracefully |

Library status, 2026-07: causalml 0.16.0 is current and its community is
active; econml is maintained under PyWhy; scikit-uplift's last release was
0.5.1 in 2022, so treat it as dormant. Qini normalization differs across all
of them; recompute both rankings with one formula on one holdout
(`uplift_qini.py::qini_coefficient`) and never compare coefficients across
tools or papers.

Sample-size reality caps the ambition. Effect heterogeneity is a difference
of differences of proportions: at base churn 25 percent, detecting a 2-point
gap between two segments' treatment effects at alpha 0.05 and power 0.80
needs 14,717 customers per cell, 58,868 in the experiment (derivation in the
reference). A few-thousand-customer test supports one average effect and at
best two coarse segments; per-customer tau estimates from it carry error
bars wider than the effects they claim to rank. Scope the promised
granularity to the experiment the client can actually run, and design that
experiment with the causal-inference skill.

## CLV economics

CLV enters real decisions as a comparison against CAC, and at that point a
point estimate misleads. Worked numbers with the geometric model (monthly
margin 18 dollars, monthly discount 1 percent):

- Retention 93 percent: CLV = 18 x 0.9208 / 0.0792 = 209 dollars.
- The same book at 91 percent gives 164; at 95 percent gives 285. A band of
  plus or minus 2 points on retention, which is a normal cohort-to-cohort
  wobble, moves CLV by -22 to +36 percent.
- Against a 120-dollar CAC, that band moves LTV:CAC from 1.4 through 1.7 to
  2.4, crossing most acquisition gates in both directions. The retention
  estimate's uncertainty decides the spend before the CLV model does, so
  quote CLV as a band with the retention assumption printed beside it.
- Payback: naive CAC/margin says 120/18 = 6.7 months; with survival and
  discounting the cumulative margin crosses 120 in month 11. Cash planning
  off the naive figure funds four fewer months of burn than reality needs.
- Horizon: capping the same book at 36 months yields 199 of the 209, so the
  infinite tail is 5 percent here. At retention above 97 percent monthly the
  tail dominates instead, and the constant-retention assumption breaks
  first, because real cohort retention curves flatten with tenure. Fit
  retention per tenure bucket (or use sBG, whose beta-mixed geometric
  produces the flattening) before quoting long-horizon CLV.

For non-contractual books, take CLV from the BTYD fit and propagate
parameter uncertainty by bootstrap: resample customers, refit, recompute.
The demo's 90 percent band on mean 24-month CLV was [27.46, 31.85] around a
29.88 point estimate, roughly plus or minus 7 percent on a clean, correctly
specified simulation; real data widens this.

Monitor cohort quality over time, since acquisition changes upstream of the
model silently reprice the book: chart each acquisition cohort's cumulative
margin per customer against months since acquisition (the payback triangle),
split by channel. A new channel that delivers the same CAC with a flatter
curve is buying worse customers, and the blended CLV model will take months
to notice on its own.

## Segmentation that maps to actions

The actionability standard: a segmentation earns its keep when every segment
has a distinct action, that action has an owner, and the segment is large
enough to pay for the action. A segmentation failing any leg is decoration,
however clean the silhouette plot looks. Write the action per segment before
fitting anything; if two candidate segments would receive the same
treatment, merge them in the design.

RFM (recency, frequency, monetary quintile scores with rule-based tiers)
remains the baseline to beat, and current CRM practice runs rule-based RFM
first and uses clustering to validate or refine it (sources in
`references/sources.md`). A clustering pitch that cannot beat RFM on the
client's own action set (match rate to distinct treatments, campaign lift)
has no case.

Method choice:

| Situation | Choice |
|---|---|
| Standardized behavioural features, need speed and reproducibility | k-means with many restarts |
| Elliptical or mixed-density structure, want soft assignments | GMM, diagonal covariance first |
| Unsure whether structure exists at all | fit k-means and GMM; if their assignments disagree (ARI below about 0.7), you are slicing a continuum and quantiles along the first factors serve the client better |
| Categorical-heavy features | k-prototypes, or embed first; euclidean distance on one-hot blocks swamps the numeric features |
| ELSE | k-means, with k chosen by bootstrap stability below |

Choose k by stability under resampling: refit on bootstrap resamples, map
labels back, and take mean ARI against the full-data fit
(`assets/store_clustering.py::bootstrap_stability`; the cluster-wise
analogue with Jaccard thresholds is Hennig 2007: below 0.6 dissolved, 0.75
valid, 0.85 highly stable). In the store demo, truth had four archetypes:
stability read 1.000 at k=3, 0.998 at k=4, then fell to 0.907, 0.808, 0.699
for k of 5, 6, 7; silhouette peaked at k=3, GMM BIC picked 4. The rule
"largest k with stability at or above 0.95 and no cluster under 5 percent"
chose 4 and matched truth at ARI 0.99, while relaxing the bar to 0.80 chose
6 and split real archetypes into fragments a next-year refresh would not
reproduce. Carry von Luxburg's (2010) caveat: stability is necessary
evidence, never proof of the true k, so pair the number with the
actionability standard, which caps k anyway.

Basket-embedding segmentation (SVD or word2vec-style product embeddings,
then cluster customers in the embedding space) finds structure that
category-share features miss, and it is production-real: P2V-MAP (Gabel et
al. 2019, JMR) recovers market structure from checkout co-occurrence, and
Instacart reports word2vec features among its top search-ranking features.
The published failure mode is interpretability: a doc2vec customer
segmentation on Instacart data produced 12 silhouette-crisp clusters whose
aggregate department profiles were nearly identical. Before adopting an
embedding segmentation, profile each cluster in business-readable features
and apply the actionability standard; crisp geometry with indistinguishable
profiles fails it.

Health-check any live segmentation with a migration matrix: cross-tabulate
segment membership at t against t plus one quarter. Rising outflow from top
segments, a swelling lost segment, or one-way flows (customers enter
"at risk" and never return) are the early warnings, and they appear
quarters before blended revenue moves. Illustrative quarterly read: a
champions row of 71 percent stay, 18 percent to loyal, 9 percent to at-risk
is healthy until the 9 becomes 15 while acquisition holds, which localizes
the problem to the top of the base and hands the uplift section its target
population. CRM platforms operationalize exactly this by storing previous
segment, current segment, and the transition timestamp per customer.

## Store segmentation for assortment localization

Store clustering feeds assortment and planogram localization (the
retail-analytics skill owns those decisions; this section builds the
clusters it consumes). Verified practice, sources in
`references/sources.md`:

- Features combine sales mix by category, store size and format, trade-area
  demographics, and competition. Sales-mix shares are compositional, so
  CLR-transform them before standardizing (`assets/store_clustering.py`
  does), or the shares' sum-to-one constraint manufactures negative
  correlations.
- Keep outcome metrics (total revenue, margin) out of the feature set. They
  cluster stores by how well they perform; the assortment action needs
  stores grouped by what their shoppers demand, and a struggling store with
  urban-premium demand belongs with its demand twins.
- Practitioners run single-digit cluster counts: vendor planning guidance
  describes 5 to 10 cluster-level plans for a roughly 100-store chain.
  Grocery practice increasingly clusters per category, because one
  store-wide grouping hides category-level demand patterns (a small store
  can share a category profile with a large one).
- Two operational pitfalls with named sources: clusters labelled A/B/C read
  as grades to store managers and distort behaviour, so name clusters by
  their demand story ("urban premium", "family bulk"); and over-localization
  has a real supply-chain bill, since every added cluster multiplies
  planograms, resets, and DC picking complexity (weigh it with the
  supply-chain-optimization skill).
- The payoff mechanism is demand transference: localized assortment swaps
  weak items for cluster-appropriate ones and a modelled share of deleted
  items' demand transfers to substitutes. Fisher and Vaidyanathan's field
  work reported a 7.6 percent validation-period lift (12.8 percent in
  calibration); the practitioner range quoted for well-executed programs is
  3 to 10 percent of category revenue. Both figures carry sourcing caveats
  recorded in `references/sources.md`, so quote them as ranges from the
  literature and never as your forecast.

The demo clusters 200 simulated stores (four archetypes; mix plus
demographics plus trade area), picks k=4 by the stability rule, matches the
true archetypes at ARI 0.99, and prints per-cluster over-index profiles
against the chain average (urban premium: population density 214, produce
148, with frozen at 71), which is the exact artifact a category manager can
act on.

## Code assets

| File | Contents | Demo runtime |
|---|---|---|
| `assets/btyd_clv.py` | BG/NBD + gamma-gamma MLE from scratch, P(alive), expected purchases, discounted CLV with bootstrap band; validated against published FH numbers | ~1 s |
| `assets/survival_churn.py` | person-month panel simulator, Cox time-varying and discrete-time logit, held-out calibration table | ~1 s |
| `assets/uplift_qini.py` | campaign simulator with all four response types, T-learner and transformed-outcome, Qini from the definition, uplift power calculator | ~17 s |
| `assets/store_clustering.py` | CLR feature build, bootstrap-stability k selection, GMM BIC and silhouette comparison, over-index profiles | ~4 s |

Each file lists exact pip package names in its top comment and runs
end-to-end via `python3 <file>`.

## References

- `references/btyd-likelihoods.md`: BG/NBD derivation, Pareto/NBD likelihood
  with the two-branch hypergeometric, gamma-gamma shrinkage worked at real
  values, the P(alive) quirks stated precisely.
- `references/uplift-evaluation.md`: estimator selection reasoning, Qini
  worked tables, normalization warning, the sample-size derivation, label
  contamination and the permanent holdout.
- `references/sources.md`: every external claim above with URL and access
  date; raw researcher fact sheets under `references/research/`.
