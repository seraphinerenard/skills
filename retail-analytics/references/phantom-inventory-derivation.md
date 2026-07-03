# Phantom inventory, the detection math in full

The companion module assets/phantom_inventory.py implements everything here. Sources with URLs and access dates live in sources.md.

## The problem and its scale

A phantom-inventory record says on-hand > 0 while the shelf (and often the back room) holds nothing. The record froze because units left without a matching transaction: theft, unrecorded damage, receiving that booked more than arrived, checkout mis-scans (the cashier scans one yogurt three times because the flavours share a price), and units lost in the back room. DeHoratius and Raman audited ~370,000 records at a 37-store retailer and found 65% inaccurate, with 26.4% of the variance between product categories, so the problem concentrates in predictable places: high-theft categories, case-pack-versus-each unit confusion, and dense fixtures. The operational damage runs through replenishment: the system sees stock, orders nothing, and the item stays off-shelf until a physical count. Chen (2021) measured lost sales near 3.0% under record-trusting policies against 0.2% with data-driven inspection.

## The zero-sales-run likelihood ratio

Daily demand for a store-item is negative binomial with mean mu and dispersion k, so Var = mu + mu^2/k. Retail SKU demand is overdispersed relative to Poisson (Agrawal and Smith 1996 showed NB fits store-item demand better than Poisson or normal on a major chain's data), and the zero probability is what the test runs on:

    p0 = P(D = 0) = (k / (k + mu))^k

Hypotheses for a trailing run of n zero-sales days:

    H0 (record correct, item on shelf): each day sells zero with probability p0(t)
    H1 (phantom, shelf empty): sales are zero with probability 1

    LLR = -sum over the run of ln p0(t)
    P(phantom | run) = pi / (pi + (1 - pi) * exp(-LLR))       with prior pi

Worked numbers, fast mover. mu = 2.0/day, k = 1.5: p0 = (1.5/3.5)^1.5 = 0.2805, so each zero day contributes -ln(0.2805) = 1.271 to the LLR.

| run length | P(run under H0) | posterior at pi = 0.05 |
|---|---|---|
| 3 days | 0.2805^3 = 0.0221 | 0.70 |
| 5 days | 0.2805^5 = 0.00174 | 0.97 |
| 7 days | 0.2805^7 = 0.00014 | 0.997 |

Worked numbers, slow mover. mu = 0.3/day, k = 1.2: p0 = (1.2/1.5)^1.2 = 0.765, each zero day contributes only 0.268. Crossing posterior 0.5 needs LLR > ln((1-pi)/pi) = ln(19) = 2.94, so the slow mover needs 11 zero days where the fast mover needs 3. This is the core sizing fact for the audit queue: a store's tail of slow movers can hide phantoms for weeks, and no tuning fixes that; only cycle counts or shelf vision do.

Why NB and never Poisson here: at mu = 2 the Poisson zero probability is e^-2 = 0.135, half the NB value, so a Poisson test reaches posterior 0.5 in 2 days and fires constantly on naturally lumpy items. Overstating the model's surprise at zeros is the classic way these detectors drown the audit team in false positives.

Day-of-week effects enter through mu_t: sum ln p0(t) over the actual days of the run. A run covering Saturday and Sunday carries more evidence for a weekend-heavy item than the same length mid-week.

## Estimation discipline

- Fit mu and k on history strictly before the trailing zero run. Fitting on the full history drags mu toward zero and the test goes blind exactly when it matters.
- Exclude promo periods from the fit or deseasonalize; a post-promo demand cliff mimics a phantom.
- Seasonal items produce false flags at season end (swim goggles in September). Guard with a same-weeks-last-year comparison or a category-level trend factor.
- The dispersion moment estimator alpha = sum((x - mu_t)^2 - mu_t) / sum(mu_t^2), k = 1/alpha, is fine at 60+ days of history; below that, pool k across the category.

## Divergence signals beyond the zero run

The LR test needs no data beyond POS. When perpetual-inventory records and receiving data are available, add:

- Book-versus-flow drift: on-hand(t) should equal on-hand(0) + receipts - POS sales - known waste. A record that drifts from the flow identity without a count event marks unrecorded loss.
- Negative on-hand events elsewhere in the store-category are a shrink tell: the same causes that push records negative push others silently positive.
- Stuck records: on-hand constant for weeks at a value above the reorder point while sales run at zero combines both signals and is the highest-precision single pattern.
- Sales at sister stores: the item selling normally at nearby stores removes "demand died" as the alternative explanation and sharpens the posterior.

## Audit economics, worked

Expected daily margin loss while the phantom persists: mu x price x margin. At mu = 2.0, price $4.99, margin 30%: $2.99 per day. If a flagged-and-confirmed record recovers roughly two weeks of sales that the frozen record would otherwise lose (time to the next natural correction event), the recovery per true positive is about 14 x $2.99 = $42 of margin. A directed count takes 3-6 minutes at a loaded labour rate near $18/hour: $0.90-1.80 per count.

Break-even precision: $1.50 / $42 = 3.6%. Any detector clears that bar by an order of magnitude, so precision is never the binding constraint; store labour is. A store crew can absorb perhaps 10-30 directed counts per day on top of scheduled work. The correct policy ranks flags by expected recovered margin, posterior x mu x price x margin x horizon, and cuts at capacity. Ranking by posterior alone wastes the queue on high-confidence, low-velocity items; the demo in assets/phantom_inventory.py shows uncertain flags on fast expensive items out-ranking near-certain flags on slow cheap ones, and that ordering is the intended behaviour.

## Replenishment integration

The flag must reach the replenishment system, because the failure mode is the system ordering against ghost stock, or worse, never ordering because the ghost stock looks sufficient.

- On flag above the audit threshold: create the directed count task and suppress the record's participation in auto-replenishment until the count clears it.
- On very high posterior with no audit capacity: auto-correct the record to zero and let replenishment fire. This trades a possible over-order (if the item was actually mis-shelved and reappears) against a certain continued out-of-stock. For fast movers the trade favours auto-correction; for slow movers wait for the count.
- Every confirmed audit outcome is labelled training data. Feed confirmations back to recalibrate pi per category; DeHoratius and Raman's variance decomposition says category-level priors capture most of the structure.
