---
name: consulting-cases
#allow:C1 synergy is the M&A term of art in the description below
description: Expert judgment for consulting cases done with real data. Market sizing (bottom-up and top-down builds that must reconcile, TAM/SAM/SOM, Monte Carlo ranges), financial analysis (price-volume-mix bridges, unit economics, cohort revenue from raw transactions, working capital, ROIC), and M&A analytics (DCF with cross-checks, comps discipline, synergy models, quality-of-earnings red flags, commercial and ML/tech due diligence). Trigger on "size this market", "TAM for", "revenue bridge", "why did revenue move", "value this company", "DCF this", "pull comps", "run diligence on", "quality of earnings", "NRR from the transaction tape", "/consulting-cases".
---

# Consulting cases

This skill covers the analytical core of ML and analytics consulting cases: market sizing, financial analysis, and M&A work done from raw data. Everything here targets the failure modes that survive textbook knowledge: builds that never reconcile, bridges whose mix term hides in volume, retention math that flatters the seller, terminal values that smuggle in a re-rating, and ranges quoted to seven digits of false precision. Current reference values (WACC anchors, multiples, retention benchmarks, data-source catalogue) live in `references/` with URLs and access dates; four runnable modules live in `assets/`.

Lane boundaries with sibling skills: customer-analytics owns churn and CLV model builds, and diligence here consumes its outputs; demand-forecasting owns volume projection methods behind any revenue path; price-optimization owns the pricing decision, while the bridge here explains realized price after the fact; causal-inference owns effect claims (elasticities, uplift, attribution) whenever a case asserts that X caused Y; model-operations owns production-readiness judgments inside tech diligence; feature-engineering owns leakage mechanics referenced in model validation.

## Choosing the build

| Situation | Approach |
|---|---|
| Category has public production or consumption statistics (commodities, construction, food, energy) | Top-down from the statistic plus bottom-up from buyer counts; reconcile the two |
| ML or software product with no category statistic | Reachable-spend build: buyers x adoption ceiling x achievable price, anchored to the spend the product displaces; Monte Carlo the range |
| Units are directly observable (licences, permits, filings, registrations) | Census the units; skip ratio math entirely |
| Client opens with "1% of a $X trillion market" | Rebuild SOM from sales capacity (reps x cycles x win rate x ACV); present both numbers and defend the small one |
| ELSE | Two independent builds from different bases, reconciled within tolerance, with a tornado on the gap |

## Market sizing

### Two builds or none

Build the number twice from independent bases and require the builds to land within 25% of each other before anything is presented. This tolerance is this skill's working rule, and the reasoning is mechanical: a sizing stack of four to six multiplicative assumptions, each honest to roughly plus or minus 20%, spreads the answer widely but symmetrically, so a one-sided gap beyond about 25-30% almost always marks an omitted segment or a wrong intensity, and the reconciliation becomes a bug finder that names the broken term. A build that cannot be checked from a second base is an assertion, and it gets labelled as one.

Defensible bases, in order of preference: government statistics (free, citable, revised on a schedule), trade association production series (headline numbers often free through newsletters even when the tables are member-gated), customs data for import-dominated goods, company filings and earnings calls for share cross-checks. The 2026 catalogue with URLs, coverage, and free/paid status sits in `references/market-sizing-sources.md`.

### Worked example, regional ready-mix concrete demand

Setup: a 2.5M-person metro; 9,800 single-family permits and 5,600 multifamily units last year (Census Building Permits Survey gives this by CBSA and county, monthly); 14M sq ft of nonresidential floor area permitted (local permit portals); state DOT lettings of $850M/yr across the districts covering the metro (DOT bid-letting portals are public; TxDOT, Caltrans, and FDOT examples are in the references). The metro is invented; every national anchor below is real and sourced.

Top-down, two anchors:

| Anchor | Computation | Result |
|---|---|---|
| Per-capita production | 377M yd3 US production 2024 (NRMCA) / 337M people = 1.12 yd3 per person; x 2.5M | 2.8M yd3 |
| Permit-intensity adjustment | Metro issues 3.9 SF permits per 1,000 residents against 2.9 nationally (ratio 1.34); apply to the ~55% of demand tied to building construction, hold infrastructure at 1.0: blended 1.19; 2.8M x 1.19 | 3.3M yd3 |

Top-down range 2.8-3.3M yd3, midpoint 3.05M.

Bottom-up, first pass:

| Leg | Computation | Result |
|---|---|---|
| Single-family | 9,800 starts x 40 yd3 (slab plus footings) | 392k yd3 |
| Multifamily | 5,600 units x 12 yd3 | 67k yd3 |
| Nonresidential | 14M sq ft x 0.04 yd3/sq ft | 560k yd3 |
| Public | $850M lettings x 12% concrete-material share / $180 per yd3 | 567k yd3 |
| Total | | 1.59M yd3 |

1.59M against a 3.05M midpoint is a 48% gap, far outside tolerance, so the build is broken and the gap names the bugs. Three specific misses, each fixed with a stated basis: the per-start intensity covered the foundation only, while the all-in figure for a new US single-family house runs near 20 tons of cement, about 75 yd3 of concrete across foundation, garage, driveway, and flatwork (Gabelli cement-industry research; the defensible range is 25 yd3 for a slab-only townhome to 90 for a basement home with a long driveway); the public leg captured DOT lettings and missed municipal, utility, and school work that never passes through a state letting (add ~35% to the public leg, a stated judgment); and repair-and-remodel plus small private work (driveways, pools, agricultural slabs) got no line at all (add a 10% gross-up).

Bottom-up, second pass:

| Leg | Computation | Result |
|---|---|---|
| Single-family | 9,800 x 70 yd3 (all-in, midpoint of 45-90 given local basement share) | 686k yd3 |
| Multifamily | 5,600 x 14 yd3 | 78k yd3 |
| Nonresidential | 14M sq ft x 0.06 yd3/sq ft (warehouse ~0.03, concrete-frame office ~0.08-0.12; blended to local mix) | 840k yd3 |
| Public | 567k x 1.35 for non-letting public work | 765k yd3 |
| Gross-up | Subtotal 2.37M x 1.10 for repair-and-remodel and small private | 2.61M yd3 |

2.61M against 3.05M is a 14% gap, inside tolerance. Present the range 2.6-3.1M yd3, and dollarize at the NRMCA 2024 weighted-average price of $179.89/yd3: a $470-550M annual market at two significant figures. The per-start intensity is the swing assumption (25 to 90 yd3 moves the residential leg by a factor of 3.6), so it heads the assumptions register and gets the first sensitivity bar.

### Ceilings and sanity anchors

- Per-capita anchors catch broken builds in one division. US ready-mix runs ~1.1 yd3 per person per year (NRMCA 2024 production over Census population); US cement consumption ~790 lb per person (derived from USGS 2023 data); US energy ~279 MMBtu per person (EIA, 2023). A regional result far from its national anchor needs a stated structural reason (climate, construction cycle, industry mix), and "our market is special" without a mechanism fails the check.
- Spend ceilings bound every cost-reduction product. The addressable spend for an ML product that cuts a cost is the cost pool it touches times the achievable reduction, and pricing captures a fraction of created value (30-50% is the usual commercial band; the price-optimization skill owns that split). A tool that saves a 120-person picking operation 8% of labour hours cannot carry a price that implies capturing 200% of the saving, and reachable-spend arithmetic exposes that in one line.
- Penetration ceilings replace hope with an analogue. The share of an ICP that buys any product in a category within the horizon is observable from adjacent categories that already matured, and it lands well under 100% even for winners. Elicit the ceiling as a low/mode/high from the closest analogues and feed it to the Monte Carlo as a PERT marginal.

### TAM, SAM, and SOM defined by who can actually buy

TAM counts buyers who have the problem, hold budget authority over it, and can adopt within the horizon, priced at an achievable contract value. For ML products, add data readiness to the filter: an account whose data cannot support the product inside the sales horizon is outside TAM no matter how large its problem is. SAM applies the go-to-market constraints (geography, segment, channel, compliance). SOM comes from sales capacity, never from an aspiration: reps x attainable cycles per rep-year x win rate x ACV. When a deck claims SOM as a round percentage of TAM, rebuild it from capacity and present the difference.

### Monte Carlo sizing

`assets/mc_sizing.py` samples correlated assumptions through a Gaussian copula (triangular, PERT, and lognormal-from-P10/P90 marginals, with a PSD repair for inconsistent elicited correlations). Three presentation rules: report P10/P50/P90 at two significant figures, never a seven-digit point estimate; never present min-of-everything and max-of-everything as the range, because joint extremes carry vanishing probability; and state where the client's point estimate falls in the distribution (the demo prints exactly that). Correlations matter in both directions: negative price-adoption correlation narrows the band, and correlated optimism widens it, so sampling independently misstates the spread either way.

## Financial analysis

### The price-volume-mix bridge

The two-term split every analyst writes first, `volume_i = (q1-q0)*p0` and `price_i = (p1-p0)*q1`, reconciles per SKU and lies at the portfolio level: a shift toward cheaper SKUs lands in the volume term even in a period when total units grew. The correct decomposition for continuing SKUs (sold in both periods), with `Q` total continuing units and `Pbar0 = continuing revenue / Q0`:

```
volume = (Q1 - Q0) * Pbar0                    change in total units at the old average price
mix    = sum(q1_i * p0_i) - Q1 * Pbar0        basket shift at old prices, everyone botches this term
price  = sum(q1_i * (p1_i - p0_i))            like-for-like price at new volumes
new SKUs add sum(p1*q1); exited SKUs subtract sum(p0*q0); the five terms sum to dRevenue exactly
```

Worked numbers (the demo in `assets/pvm_bridge.py` reproduces them): premium SKU falls 100 to 80 units at $100; economy rises 100 to 130 units, price $60 to $63; a $2,000 legacy SKU exits; a $2,250 launch enters. Continuing units grew 5% (200 to 210), and `Pbar0` is $80. Volume = +800, mix = 8,000 + 7,800 - 16,800 = -1,000, price = +390, new = +2,250, exited = -2,000, total +440, which equals the revenue change exactly. The naive split reports volume as -200 on the same data, and a management team reading it would cut capacity in a quarter when units grew. Three rules: realized price (revenue/units) absorbs discounts and rebates, so bridge discounting separately when it is the question; the volume/mix split has meaning only when units are commensurable across SKUs, so run per-segment bridges when they are heterogeneous; chain year-over-year bridges across multi-year gaps, because offsetting moves cancel inside one long bridge.

### Margins and the decision each supports

| Decision | Margin to use |
|---|---|
| Keep or kill a product line | Contribution after truly avoidable costs; the test is which costs disappear within 12 months of the kill |
| Short-term pricing floor | Variable cost plus the opportunity cost of any constrained capacity consumed |
| Allocating scarce capacity | Contribution per unit of the binding constraint, never per unit of product |
| Benchmarking across companies | Gross margin as reported, with a footnote on COGS composition, since peers bury different things in it |
| ELSE | Draw the unit-economics tree first, then pick the margin line that actually changes with the decision |

The allocation trap has a name: the death spiral. Fully-loaded cost makes a product look unprofitable, the product dies, the fixed costs it carried land on the survivors, another product turns "unprofitable", and the sequence repeats until the factory closes. Any keep/kill analysis on fully-allocated margins gets rebuilt on avoidable cost before it is discussed.

### Cohort revenue and retention from raw transactions

`assets/cohort_engine.py` computes the diligence-grade definitions from an invoice-level tape:

```
Base(t,w) = customers with revenue > 0 in month t-w
GRR = sum(min(rev[t], rev[t-w])) / sum(rev[t-w])   over Base; caps expansion, <= 100%
NRR = sum(rev[t]) / sum(rev[t-w])                  over Base; new logos never count
```

The traps the engine handles are the ones that flatter sellers: a partial final month reads as mass churn (drop it), reactivated customers are new business in the window (a customer at zero in month t-w is outside the base), credit-memo months are clipped at zero so retention denominators stay positive, and currency converts at fixed monthly rates before aggregation so FX never masquerades as expansion. Annual NRR is computed directly on the 12-month window, never as monthly NRR to the 12th power, because reactivation and intra-year expansion break the compounding identity.

Current benchmarks for reading the output (private B2B SaaS): median NRR 101% and falling since the ~105% of 2021 (Benchmarkit 2025, 2024 data); median GRR 88% in 2024, sliding to 84% in the 2026 benchmark cycle; SaaS Capital's 2025 survey puts median NRR at 102% for the $25-50k ACV band with 111% at the top quartile. A seller deck quoting 120%+ NRR in 2026 describes a top-decile business, and the tape either confirms it or it does not. The customer-analytics skill owns modelling churn forward from these observations.

One durability constant worth memorizing: the present value of the existing book, with revenue decaying at GRR `g` and discounted at `r`, is `q/(1-q)` years of current revenue where `q = g/(1+r)`. At GRR 88% and a 10% discount rate the book is worth 4.0x current revenue; at GRR 84% it is worth 3.2x. Four points of GRR move the existing book by most of a year of revenue, so GRR, never NRR, anchors revenue durability in a model.

### Working capital and cash conversion

Cash conversion cycle = DSO + DIO - DPO, and all three compute on average balances (opening plus closing over two, or monthly averages when the tape allows), because quarter-end balances carry the seasonal push. Growth consumes cash at a constant cycle: a company holding net working capital at 15% of revenue that grows $100M to $120M puts $3M of the new revenue into working capital before any of it reaches cash. In a DCF that is the `dNWC = nwc% x dRevenue` line; in a 13-week cash model it is the difference between profitable and insolvent. The quarter-end DSO against average DSO comparison also doubles as a fraud screen, and the quality-of-earnings section below picks it up.

### ROIC trees and ratio traps

ROIC = NOPAT / invested capital, decomposed as NOPAT margin x capital turns, and the tree earns its keep when the two branches disagree with the narrative (a "high-margin" business earning 6% ROIC has a capital problem the income statement never shows). Two scope choices change conclusions and must be stated: goodwill in (management's record as an acquirer) against goodwill out (operating performance of the base business), and both numbers belong in an M&A memo; leases sit on the balance sheet post ASC 842/IFRS 16, so invested capital includes them and the comparison with pre-2019 history needs restating.

Three ratio traps, each with the fix: never average ratios, aggregate components (divisions at 30% ROIC on $10M and 5% on $90M average to 17.5% by ratio and earn 7.5% in fact); never mix fiscal calendars in a comp set, calendarize to a common year first; never compound currency into growth, quote constant-currency growth by restating current results at prior-year rates and bridge the translation effect separately.

## M&A analytics

### DCF mechanics that survive review

Mid-year convention is the practitioner default (about 75% of 2024 SEC fairness opinions that state a convention use it), and it lifts value 3-5% against year-end discounting because operating cash arrives through the year: year t discounts at `(1+WACC)^-(t-0.5)`, a Gordon terminal value keeps the mid-year timing (discount at N-0.5), and an exit-multiple terminal value is a sale event, so it discounts at the full N.

Terminal value discipline, the part reviews actually contest:

- Build terminal FCF from reinvestment economics, `FCFF_T = NOPAT_T x (1 - g/ROIC_T)`, never by growing final-year FCF at g, because the grow-last shortcut carries the explicit period's capex-over-depreciation gap into perpetuity and double-counts growth spending against terminal growth.
- Default ROIC_T to WACC (economic profit fades to zero), and raise it above WACC only with a stated moat argument. A working consequence worth using in the room: at ROIC_T = WACC the terminal value goes nearly flat in g, because growth at the cost of capital adds no value, and that single fact defuses most terminal-growth fights.
- Cross-check both directions, every time. The worked example in `assets/dcf_tornado.py` ($480M revenue, growth fading 8% to 3%, EBIT margin walking to 16%, WACC 9.2%, g 2.4%) prices at $6.95/share on the Gordon terminal and $10.32 on a 9.0x exit: the Gordon TV implies 6.3x terminal EBITDA, and the 9.0x exit implies g = 3.5% against the assumed 2.4%. A 49% equity-value gap between the two methods is a finding, and when the implied exit multiple exceeds today's trading multiple, the growth assumption smuggles in a re-rating.
- Terminal value at 60-75% of EV is normal for a 5-year horizon; beyond ~80%, extend the explicit period until the business reaches steady state, because the model is otherwise a perpetuity with a decorative forecast attached.
- Terminal g caps at long-run nominal GDP growth, roughly 3.8-4.0% for the US on CBO's February 2026 outlook, and practitioners sit at 2-3%.

WACC has two live schools in 2026, and the choice moves cost of equity by almost 2 points, so state the school and hold it: Damodaran's implied ERP ran 4.2% (January 2026) to 4.5% (July 2026, US) over a 10-year at ~4.5%, while Kroll recommends a 5.0% ERP (cut from 5.5% effective September 2, 2025) over the higher of a 3.5% normalized risk-free rate or the spot 20-year, which at ~5.07% currently governs, so a beta-1 cost of equity reads ~8.7% in one school and ~10.1% in the other. Sector WACC anchors as of January 2026 (Damodaran, USD): software 9.3-10.7%, semiconductors 10.6%, machinery 7.7%, staples 5.8-7.0%, healthcare 7.5-8.2%, retail 7.3%, utilities 4.4-4.9%; Kroll-school numbers run 1-2 points higher, and `references/valuation-anchors.md` carries the full table with dates. Remaining pitfalls with one-line fixes: weight the capital structure at market values of the target's sustainable structure, never the acquirer's; unlever peer betas and relever at that structure; discount each cash-flow stream at the rate matching its own risk, which is what forbids valuing revenue upside at the base-business WACC.

### Comps discipline

Selection is the analysis: pick 5-8 names on business model, growth-margin profile, and capital intensity, and document every exclusion, because a 20-name set spanning three business models is a scatter plot wearing a table's clothes. Adjustments before any multiple gets computed: calendarize mixed fiscal years; treat stock-based compensation one way across the whole set (in or out of EBITDA, never mixed); put lease liabilities in EV wherever the earnings metric excludes rent; normalize one-time items with the same rule for every name. Multiples mislead on schedule in three situations: cyclicals at peak or trough (use mid-cycle earnings or EV per unit of capacity), no true peers (a triangulated DCF beats a fake comp set), and regime changes, for which the SaaS record is the standing exhibit: the SaaS Capital Index peaked at 16.9x ARR in August 2021 and printed roughly 3.2-4.8x in June 2026, so a 2021 comp is history, never evidence. Transaction comps embed control and deal logic: the 2024 US median control premium was ~28% (FactSet/BVR; tech deals ran ~17%), so when deal comps are thin, trading comps plus an explicit premium beat two stale transactions.

Current transaction anchors (details and URLs in the references): Bain's 2026 M&A report has strategic deals at a median 11.6x EV/EBITDA for 2025, PE buyers near 12.6x against corporate buyers near 9.8x; PitchBook has US buyouts around 12x with the middle market near 9.6x.

<!-- allow:C1 synergy/synergies is the M&A term of art throughout this section -->
### Synergy modelling

Cost synergies are built bottom-up by line or they are theatre: headcount overlap by function at loaded cost, procurement as spend by category times a category-specific saving, facilities and systems by named site and contract. Model the ramp explicitly (a 30/70/100% capture path over three years is a common base case) and net the cost to achieve against it, which runs 50-100% of the year-one announced amount and lands in the first 18-24 months (published integration-cost benchmarks).
<!-- allow:C1 synergy is the M&A term of art -->
The realization evidence says to haircut before believing: acquirers capture roughly 70-85% of announced cost synergies within about 18 months, while revenue synergies realize 25-35% over 18-36 months (aggregated McKinsey/Bain/BCG figures; Bain's survey of 352 executives ranks overestimating them as the second most common cause of deal disappointment). Two consequences for the model: revenue synergies enter as scenarios with named mechanisms and their own realization discount, never as a base-case line, which matches how the market prices announcements (credit for cost, little for revenue); and each stream discounts at the rate matching its own risk, so cost take-outs sit near the target's WACC while cross-sell cash flows carry an equity-like rate.
<!-- allow:C1 synergies is the M&A term of art -->
The one-line sanity check on any synergy claim: announced cost synergies as a share of the smaller party's cost base, against the 2-5% that typical same-industry deals actually deliver at the median; a 15% claim requires an integration thesis the data room can support.

### Quality-of-earnings red flags in the data

Channel stuffing has a signature the invoice table cannot hide, and each screen below is one GROUP BY: the share of quarterly revenue invoiced in the final two weeks, trended over eight quarters (a rising last-two-weeks share with flat intra-quarter demand is the classic pull-forward pattern); DSO rising while revenue is flat (receivables aging faster than sales grow means paper sales); credit memos and returns spiking in the first three weeks of the following quarter, matched back to quarter-end invoices; distributor or channel inventory days building while sell-through is flat, wherever sell-through data exists. The enforcement anchor: Under Armour pulled forward $408M of orders across six quarters in 2015-2016 and settled SEC disclosure charges for $9M (SEC press release 2021-78), and the conduct would have been visible in exactly these screens.

Addback abuse reads from the adjustments schedule: any "one-time" item that recurs in three consecutive years is operating cost; the addback share of adjusted EBITDA, trended, is the single most informative QoE chart; and proof-of-cash is the floor check, because adjusted EBITDA that walks steadily away from operating cash flow is being adjusted into existence. Round out the pass with cutoff screens (revenue recognized in month 13, weekend-dated invoices, credit memos dated days after period close) and, for subscription businesses, the deferred-revenue burn: revenue growing while deferred revenue is flat means the backlog is being consumed, and bookings will say so a quarter later.

### Commercial due diligence from the data room

Run `assets/cohort_engine.py` on the raw transaction tape before accepting a single management chart, and reconcile the tape's revenue to the audited P&L first (a tape that misses the ledger by more than 1-2% is describing a different company). The outputs that matter: GRR/NRR against the benchmarks above; the cohort revenue triangle, where healthy expansion shows cohort revenue crossing back above 1.0 with age and early plateaus mark a product that stops delivering; customer concentration as top-1/top-10 shares and HHI (1/HHI is the effective customer count), where common US middle-market practice flags a top customer above ~10% of revenue and prices real discounts or structures earn-outs beyond ~20%, and asset-based lenders cap per-obligor receivable concentration in the same band; and the durability multiple from the GRR constant above, which converts retention straight into the value of the book being bought.

Then reconcile systems against each other: CRM ARR against the invoice tape (gaps are usually definitional until they are not), contracted seats against usage telemetry (a high shelfware ratio is churn that has not happened yet), and logo counts between the deck and the tape. Every seller metric gets recomputed from raw data under this skill's definitions; "management-defined NRR" is a phrase that pays for the whole diligence when it appears.

### ML and tech diligence

Validating a target's model-performance claims is a replication exercise with a fixed protocol: demand timestamped prediction logs and score the predictions against realized outcomes (logs that do not exist are themselves the finding); when only data reaches the room, replicate the claimed metric with a strictly time-based split at the claimed operating point; audit for leakage (features computed after the outcome, entity overlap across train/test, target proxies in the feature set; the feature-engineering skill owns the mechanics); compare the evaluation population with current production traffic, because a model measured on 2023 customers and sold on 2026 traffic has an unmeasured drift gap; and weigh retrospective accuracy claims against any live A/B evidence, which is the only grade that counts. The regulatory floor exists now: the SEC's first AI-washing actions (Delphia and Global Predictions, March 2024, $400k combined, press release 2024-36) established that unsupported AI capability claims are enforceable misstatements, and diligence memos should say whether the target's public claims would survive that test.

Data advantage gets assessed on four axes, honestly: rights (is the data licensed for the current use, and do the licences survive a change of control; post-2023 training-data scrutiny makes this a closing condition, never a footnote), uniqueness (could a competitor assemble an equivalent corpus, at what cost and delay), decay (how fast the data stales and what refresh depends on), and marginal value (learning curves flatten, so "more data" claims need the incremental-lift curve, never the total volume). Standard tech-diligence mechanics ride along: open-source scans of the codebase (Black Duck-style audits are routine in tech M&A), and an end-to-end retrain from raw data as the reproducibility test, because a model nobody can retrain is a depreciating asset with no maintenance plan. The model-operations skill owns the production-readiness verdict that feeds this section.

## Deliverable norms

### The assumptions register

Every model that leaves the building carries a register with one row per assumption: value, unit, low/high range, basis (measured, sourced, analogue, or judgment, named as such), the source with its date, and the sensitivity rank from the tornado. The register is the negotiation surface, since arguments happen at assumptions, never at outputs. First rows from the sizing example:

| Assumption | Value | Range | Basis | Source |
|---|---|---|---|---|
| Concrete per SF start | 70 yd3 | 45-90 | Sourced anchor plus local basement share | Gabelli cement research; NAHB slab-share series |
| US per-capita ready-mix | 1.12 yd3/yr | 1.0-1.2 | Measured | NRMCA 2024 production / Census population |
| Non-letting public share | +35% | +20-50% | Judgment, named | None; flagged for diligence |

### Sensitivities, scenarios, and simulation

| Question on the table | Tool |
|---|---|
| Which assumption deserves the diligence budget | Tornado, one-at-a-time low/high, sorted by swing (`assets/dcf_tornado.py` prints one) |
| What a coherent bad world does to the answer | Three or four scenarios with internally consistent joint moves (recession moves volume, price, and working capital together) |
| What range to print in the deliverable | Monte Carlo with correlated inputs, P10/P90 at two significant figures |
| "What if X and Y happen together" | A scenario, because X and Y co-move and one-at-a-time math denies it |
| ELSE | Tornado first; it costs nothing, ranks everything, and tells you whether the Monte Carlo is worth building |

Scenarios and sensitivities answer different questions and the deliverable says which is which: a tornado ranks single assumptions for attention, a scenario prices a state of the world, and presenting a 27-cell sensitivity grid as "scenarios" hands the client false comfort in combinations that were never checked for internal consistency. Ranges print at two significant figures with the percentile stated, and the point estimate's percentile gets stated next to it.

## Code assets

| Module | What it does | Run |
|---|---|---|
| `assets/cohort_engine.py` | GRR/NRR/logo retention with decomposition identities, cohort triangles, HHI concentration, from a raw transaction table | `python3 assets/cohort_engine.py` |
| `assets/pvm_bridge.py` | Exact price-volume-mix bridge with new/exited SKU terms, naive-split contrast, per-SKU price attribution | `python3 assets/pvm_bridge.py` |
| `assets/dcf_tornado.py` | Mid-year FCFF DCF, reinvestment-consistent terminal value, dual-TV cross-checks, ASCII tornado | `python3 assets/dcf_tornado.py` |
| `assets/mc_sizing.py` | Correlated Monte Carlo sizing (Gaussian copula, PSD repair), two-sig-fig summaries, contribution to variance | `python3 assets/mc_sizing.py` |

Dependencies: `pandas`, `numpy`, `scipy` (each file lists its own in the header). All four run on synthetic data with no network access.

## References

- `references/market-sizing-sources.md`: the 2026 data-source catalogue (government statistics, customs, construction, alternative data) with free/paid status.
- `references/valuation-anchors.md`: ERP schools, sector WACCs, trading and transaction multiples, control premium, DLOM, LBO debt levels, all dated.
- `references/ma-diligence.md`: retention benchmarks, QoE red-flag catalogue with enforcement anchors, concentration norms, synergy realization evidence, ML diligence protocol. <!-- allow:C1 synergy is the M&A term of art -->
- `references/sources.md`: every URL cited anywhere in this skill, with access dates.
- `references/research/`: raw researcher fact sheets these files were curated from (kept for provenance; exempt from house style).
