---
name: retail-analytics
description: Floor-level retail and CPG analytics for consulting work. Use for foot traffic forecasting and labour scheduling, phantom inventory and inventory record inaccuracy detection, on-shelf availability and lost-sales estimation, assortment decisions (transferable demand, cannibalization, localization), insurgent and challenger brand analysis (distribution x velocity, ACV-velocity curves, early-signal screens), and site selection (Huff models, trade-area cannibalization, analog method).
---

# Retail analytics

This skill covers the retail floor and the CPG shelf: traffic, inventory records, availability, assortment, challenger brands, and store sites. General demand modelling belongs to the demand-forecasting skill and this skill consumes it; price setting and promo-effect measurement belong to price-optimization; store segmentation mechanics belong to customer-analytics and this skill consumes its clusters. The reader is assumed to know the textbook methods; what follows is the judgment, the data quirks, and the worked numbers that separate a defensible engagement from a plausible one.

## Foot traffic forecasting

### Pick the signal before the model

The traffic signal decides the ceiling on forecast quality, and each source fails differently. Full field notes on the mobility-data supply, vendor status after SafeGraph's exit, and the January 2025 FTC order against Gravy/Venntel sit in references/mobility-data-notes.md; the source list with access dates is references/sources.md.

| Situation | Signal | What to correct for |
|---|---|---|
| Client owns the stores, POS available | POS transactions as the level, panel or counters for hourly shape | Conversion assumption (traffic = transactions / conversion); self-checkout lane splits |
| Client owns the stores, door counters installed | Counter counts anchored by a manual-count calibration | Beam counters miss 10-20% on busy doors (groups break one beam); staff crossings inflate unless excluded |
| Competitor or prospect sites, no inside data | Mobility panel (Placer.ai, Advan, Unacast) | Use relative reads only: year-over-year, rank order, hourly shape. Absolute counts need a ground-truth anchor |
| Small POI, under a few dozen panel devices/week | Do not use the panel alone | Aggregate to chain or market level, or buy counters |
| ELSE | POS where it exists, panel for shape and competitors, counters where absolute in-store counts decide money | Anchor every absolute number to at least one ground truth |

Mobility panels are usable for trends and shapes and weak on levels: they skew Android after Apple's App Tracking Transparency change, home-location attribution mislabels shift workers and students, and visit attribution breaks at malls and shared parking lots. The Coston et al. FAccT 2021 audit found older and minority populations under-covered (sources.md, verify before quoting its numbers). Vendors post-stratify to census demographics by home block group; that fixes panel composition and cannot fix which visits get captured.

### The hourly model

Hour-of-week dummies carry the base shape; everything else enters as log-linear multipliers. The features that pay for themselves in grocery, from engagement experience and the covariate set in assets/foot_traffic.py:

- Weather: centred temperature and its square (traffic dips at both extremes), log precipitation. Use forecast weather at scoring time, never actuals, or the backtest flatters.
- Paydays: the 1st and 15th, biweekly Fridays, and government benefit days (SNAP issuance schedules vary by state and stagger across the month). Worth 10-15% on issuance days in value-oriented grocery.
- School calendar: in-session vs break changes both level and hourly shape (the 15:00-17:00 lift disappears in summer).
- Holiday ramps: an exponential ramp on days-to-holiday fits grocery pre-holiday build better than a single dummy.
- Local events: stadium schedules and festivals for urban stores; a binary flag per venue within walking distance is usually enough.

A Poisson GLM with these features stays inspectable when a store manager challenges the Tuesday 14:00 number, and it loses little accuracy to gradient boosting at this feature count; hand the model choice to the demand-forecasting skill when the client wants a network-wide system. Feature construction conventions live in the feature-engineering skill.

### Evaluate against the schedule, never against MAE alone

The forecast feeds a staffing decision, so the loss function follows from staffing costs. With understaffing cost Cu per unserved customer and overstaffing cost Co per unit of excess capacity, the optimal plan staffs to the newsvendor quantile q* = Cu/(Cu + Co) of the predictive distribution. Worked: a cashier at $18/hour serves about 25 customers/hour, so excess capacity costs $0.72 per customer-unit; pricing an unserved customer at $1.50 of at-risk margin and goodwill gives q* = 1.50/2.22 = 0.68. Staff to the 68th percentile, and get the percentile from a negative binomial around the model mean with dispersion estimated from residuals.

Two consequences the client will not expect. Staffing to the mean forecast underserves every peak by construction (the demo in assets/foot_traffic.py prices that mistake at +5% total cost even with a good mean model). And a worse-MAE model can win on money: report both MAE and realized staffing cost against the incumbent schedule, because the cost comparison is the one that survives the CFO. In the demo, the model beats a seasonal-naive schedule by 47% of staffing cost on two simulated years.

## Phantom inventory and record inaccuracy

### Scale, mechanisms, and why replenishment makes it expensive

DeHoratius and Raman audited ~370,000 records across 37 stores of one retailer and found 65% inaccurate, with 26.4% of the variance between product categories (sources.md). The record-freezing mechanisms: shrink (NRF puts it near 1.6% of sales, flagged in sources.md), receiving errors, unrecorded damage, and checkout mis-scans on price-matched flavours. The 2002 Gruen-Corsten-Bharadwaj worldwide study put the FMCG out-of-stock rate at 8.3% with about 72% of root causes in-store, in ordering and shelf replenishment. Phantom records are the expensive subset because auto-replenishment trusts them: the system sees stock, orders nothing, and the item stays gone until a physical count. Chen (2021) measured lost sales near 3.0% under record-trusting policies against 0.2% with data-driven inspection.

### The zero-sales-run test

Model daily store-item demand as negative binomial (Agrawal and Smith 1996 found NB beats Poisson and normal on real store-item data); the zero probability is p0 = (k/(k+mu))^k. For a trailing run of n zero-sales days, the phantom hypothesis predicts zeros with probability 1, so

    LLR = -sum over the run of ln p0(day)
    P(phantom | run) = pi / (pi + (1-pi) e^-LLR)

Worked at prior pi = 0.05. Fast mover, mu = 2.0, k = 1.5: p0 = 0.28, so 3 zero days give posterior 0.70 and 5 days give 0.97. Slow mover, mu = 0.3, k = 1.2: p0 = 0.77, and the same posterior needs 11-12 zero days. Fit mu and k on history strictly before the run (fitting through the run drags mu to zero and blinds the test), sum day-of-week-specific p0 over the run's actual days, and never substitute Poisson: its p0 at mu = 2 is 0.135, half the NB value, and the detector floods the audit queue with lumpy-demand false positives. Full derivation, estimation discipline, and the promo/seasonality guards: references/phantom-inventory-derivation.md. Runnable implementation with a synthetic-panel demo: assets/phantom_inventory.py (precision 0.81, recall 0.96 at posterior 0.5 on the demo panel).

When perpetual records and receiving feeds are available, add the divergence signals: book-versus-flow drift (on-hand fails the receipts-minus-sales identity between counts), stuck records (on-hand constant above the reorder point while sales sit at zero), negative on-hand events in the same category as a shrink tell, and normal sales at sister stores to eliminate "demand died" as the alternative.

### Audit targeting is an economics problem

Expected recovery per flag = posterior x mu x price x margin x horizon, where the horizon is how long the error would persist untreated (time to the next count). Worked: mu = 2/day, price $4.99, margin 30% loses $2.99/day; a two-week horizon makes a confirmed catch worth about $42 of margin against a $0.90-1.80 directed count. Break-even precision is 3.6%, which any detector clears, so precision is never the constraint; store labour is (10-30 directed counts per day fit around scheduled work). Rank flags by expected recovery and cut at capacity. Ranking by posterior wastes the queue on certain-but-cheap slow movers; the right list puts an uncertain flag on a fast $8 item above a near-certain flag on a slow $2 one.

| Flag state | Action |
|---|---|
| Posterior above audit threshold, capacity available | Directed count task; suppress the record from auto-replenishment until the count clears |
| Very high posterior, no capacity, fast mover | Auto-correct the record to zero so replenishment fires; accept the small over-order risk |
| Very high posterior, no capacity, slow mover | Hold for the next count; the daily loss does not justify the correction risk |
| Flag on a promo or season-end item | Discard unless the same-weeks-last-year comparison confirms; these are the systematic false positives |
| ELSE | Log the flag, keep accumulating run evidence, re-rank tomorrow |

Feed confirmed audit outcomes back to recalibrate pi per category; the DeHoratius-Raman variance decomposition says category-level priors capture most of the structure.

## On-shelf availability and lost sales

Recorded stockouts censor sales from the right; phantom stockouts censor them silently, so the detection section above comes first: every unconstraining method assumes the availability flags are true, and phantoms corrupt the flags. Method choice for estimating demand from censored sales (masking vs imputing vs censored likelihoods, stockout-timing estimators, the Amazon glance-view counterfactual) belongs to the demand-forecasting skill; its research sheet at demand-forecasting/references/research/censored-demand-unconstraining.md carries the full sourced literature, including the FreshRetailNet-50K measurement that raw sales under-read demand by 7.37% on a 50,000-series grocery benchmark.

What this skill adds is the retail-floor reading of the result. Item-level lost sales overstate category loss because shoppers substitute: the Gruen-Corsten consumer-response splits have roughly 45% substituting within the category, about 31% buying at another store, and single digits abandoning outright (sources.md; verify the exact split before client use). So an OSA business case runs on three numbers with different owners: item lost sales (the brand's problem), category lost sales after substitution (the retailer's problem, roughly half the item figure in centre-store categories), and trip risk from repeated stockouts of destination items (the retailer's bigger problem, visible in panel data as store switching). Present all three or the case will be wrong for whoever is in the room.

For intraday work, expected lost units during a gap = sum of the hourly demand profile over the gap, and the profile matters: FreshRetailNet measured stockout incidence rising from under 2% at 06:00 to 26% by 20:00, so end-of-day gaps censor the demand peak in fresh categories and a flat-profile estimate under-reads the loss.

## Assortment

### Transferable demand and incrementality

A delist decision needs one number per item: incrementality, the share of the item's demand that walks when the item goes. Its complement transfers to surviving items. Estimate transfer from household-panel switching matrices, from cross-price and availability responses, or cheapest of all from delist natural experiments in stores where the item dropped earlier (resets stagger; use the stagger). The stockout-response literature anchors the prior: with ~45% of shoppers substituting on a temporary gap, a permanent delist of a mid-tail item in a deep category typically transfers 60-80% of its volume, and near-duplicates transfer more. Rank the tail by incremental dollars (item dollars x incrementality), never by raw dollars; the raw ranking protects duplicates and kills differentiated slow movers, which is backwards.

### Cannibalization and halo

New-item "success" reads inflated until cannibalization is netted: the launch's incremental dollars = launch dollars minus the dip in substitutes plus any halo on complements. Measure it with the methods in the causal-inference skill (matched control stores, staggered-reset difference-in-differences); the assortment-specific traps are that substitutes share shelf and promo calendars with the launch (confounded timing) and that distribution build overlaps the measurement window, so hold TDP fixed in the comparison or the launch curve is a distribution curve wearing a costume. Promo-effect measurement stays with the price-optimization skill; consume its base/incremental split rather that re-deriving it. allow:A1 "rather" here is the verb "consume X rather that", kept as plain preference wording

### Localization

Localize assortment by store cluster, and take the clusters from the customer-analytics skill as given inputs. The floor-level rules: cluster on demand composition (category mix shares, brand-tier mix), never on store size, because size belongs to space allocation; keep the cluster count small enough that category managers can hold them in mind (5-9 in practice); and validate a localization by the transfer math above, since localization is a batch of adds and delists per cluster. National-brand velocity floors still apply inside clusters; a cluster read on thin store counts is panel noise wearing a segmentation.

## Insurgent brand analysis

### Share is distribution times velocity

dollars = TDP x SPPD, so growth splits exactly in logs: ln(D1/D0) = ln(TDP1/TDP0) + ln(SPPD1/SPPD0). Worked: a brand goes from $1.0M to $2.0M while TDP goes 49 to 91 and SPPD $20.4k to $22.0k; the log split attributes 89% of the growth to distribution and 11% to velocity. That one line is the health check: distribution-led growth is a countdown to the delist wave unless velocity holds as doors are added. Metric definitions, the worked $/point comparison, and provider defaults are in references/velocity-distribution-notes.md; the runnable decomposition, curve fit, and screen are in assets/share_decomposition.py.

The velocity-at-expansion question is answered by the ACV-velocity curve: fit ln(velocity) = a - b ln(ACV) on the brand's own path. b near 0.1 travels; b near 0.3 means doubling ACV yields 1.62x dollars (the demo's naive linear projection overstates by 15% at 49-to-80 ACV); b above 0.5 means the ceiling is close and the growth case must switch to velocity or new items.

### The early-signal screen

High velocity at low ACV is the expansion signal, and the screen must residualize because velocity falls with ACV mechanically (early doors are the best-fit doors). Fit the category's cross-sectional ln(velocity) on ln(ACV), flag positive residuals of +0.25 log points or more at ACV under ~40. The demo shows why raw velocity sorting fails: the flagged brand ranks mid-pack on raw SPPD and first on residual. Then confirm with panel repeat rate (above ~30% separates habit from trial, calibrate per category) and with a base-price velocity read, because promo-bought velocity evaporates. Bain's insurgent series defines the commercial bar: >$25M tracked revenue (>$35M in the 2026 list), 10x category growth over five years, and the population that clears it held under 2% of share while capturing about 36% of tracked-channel growth in 2025 (sources.md).

### Choose the data view by the question

| Question | View |
|---|---|
| Is velocity real at current doors | Syndicated POS (Circana/NIQ; SPINS for natural channel), base vs incremental split |
| Is anyone buying twice | Household panel (Homescan, Numerator): penetration, repeat, buy rate; directional below ~1% penetration |
| Is the growth just channel fill | Factory shipments plotted against POS takeaway; divergence = pipeline, common at launch and resets |
| Does the brand travel outside its founding channel | Retailer direct portals plus syndicated by-channel splits; watch the Costco/Trader Joe's/Aldi blind spots |
| How big can it get | ACV-velocity curve projection plus whitespace grid (retailer x region cells weighted by category development) |
| ELSE | Start with syndicated POS for the shared fact base, add panel for buyer dynamics, and reconcile shipments last |

The standing measurement traps (unmeasured retailers manufacturing fake acceleration as brands enter measured channels, new-item ACV lag depressing first-quarter velocity, panel noise on small brands, Bass fits unidentified on short series) are catalogued in references/velocity-distribution-notes.md.

## Site selection

### The Huff model, worked

P(zone i shops store j) = A_j^alpha d_ij^-beta, normalized over stores. Worked zone: three stores of 40k, 25k, and 60k sq ft at 2.0, 1.0, and 4.5 km with alpha = 1, beta = 2 give utilities 10000, 25000, and 2963, so capture probabilities 26.3%, 65.9%, and 7.8%; expected store revenue sums zone spend times capture over zones. Judgment that the formula hides: beta is category-specific (convenience decays fast, destination slowly) and load-bearing, so calibrate it, and with revenue-only data fix alpha = 1 because a handful of store revenues identifies the pair only jointly. Zone-to-store flows from loyalty cards identify both parameters: the Huff model is a conditional logit with log size and log distance as covariates, so fit the logit when flows exist. Implementation with grid calibration: assets/huff_model.py.

### Cannibalization decides, never gross

Huff reallocates a fixed demand pool, so a candidate's gross projection is always partly taken from the client's own stores and the decision number is net-new revenue = gross minus own-banner losses. The demo makes the ranking flip concrete: candidate A near the own cluster grosses $15.4M with 78.5% cannibalization (net-new $3.3M); candidate B in competitor territory grosses $11.6M with 20.8% cannibalization (net-new $9.2M). Gross picks A, the money picks B. Any market-growth claim (the new store expanding total demand) needs evidence from outside the model, because the model cannot produce it. Simulating a full network of openings and closures belongs to the simulation-digital-twins skill; this skill supplies its capture model.

### When analogs beat the model

The analog method (Applebaum): project a candidate from the performance of the client's most similar existing stores, adjusted for the differences. It wins surprisingly often.

| Situation | Method |
|---|---|
| Chain with 50+ comparable stores, prototype rollout | Analogs: the estate is a better model of the concept than any gravity formula |
| Loyalty-card flows available | Conditional logit (Huff generalization); the only setting where alpha and beta are both credibly identified |
| Dense competitive market, cannibalization is the question | Calibrated Huff: reallocation is exactly what it models |
| New market, no own stores, no flows | Huff with a borrowed category beta and wide sensitivity bands; present ranges, never points |
| Under ~10 existing stores | Analogs plus judgment; too little data to calibrate anything |
| ELSE | Analog set for the level, Huff for the competitive and cannibalization deltas on top |

Trade-area demographics for either method come from the mobility-panel notes above, with the panel's home-attribution caveats applied.

## Code assets

All four modules run on numpy and pandas alone (exact pip names in each file's top comment) and each carries a __main__ demo on synthetic data.

| Module | What it does | Demo result |
|---|---|---|
| assets/phantom_inventory.py | NB likelihood-ratio detector on zero-sales runs, audit ranking by expected recovery | precision 0.81 / recall 0.96 at posterior 0.5; precision@15 = 0.80 on the capacity-ranked audit list |
| assets/share_decomposition.py | TDP/SPPD metrics, exact log growth split, ACV-velocity curve fit, residualized expansion screen | recovers b = 0.28 (true 0.25); flags the planted insurgent that raw velocity sorting buries |
| assets/foot_traffic.py | Hourly Poisson GLM (IRLS), NB predictive quantiles, newsvendor staffing evaluation | beats seasonal-naive staffing cost by 47%; prices mean-staffing at +5% |
| assets/huff_model.py | Huff capture, beta calibration on revenues, candidate evaluation with own-banner cannibalization split | recovers beta 2.40 (true 2.50); shows the gross-vs-net-new ranking flip |

## Sibling skills

demand-forecasting owns forecasting method choice and censored-demand recovery; price-optimization owns price and promo effect measurement; customer-analytics owns store and customer segmentation mechanics; causal-inference owns the identification designs used for cannibalization and halo; feature-engineering owns covariate construction conventions; simulation-digital-twins owns network-level what-if simulation; supply-chain-optimization owns the replenishment policies this skill's detectors feed; model-operations owns deployment and monitoring of anything built here; consulting-cases owns engagement framing; price-forecasting and predictive-maintenance sit outside this skill's surface and are listed for lane completeness.
