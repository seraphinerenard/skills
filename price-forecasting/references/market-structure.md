# Market-structure notes by archetype

Extended background for the SKILL.md archetypes. Full URLs and access dates
live in `sources.md`; the researcher fact sheets in `research/`
carry the primary extracts.

## Lumber

### Futures contracts

| Contract | Size | Delivery | Status |
|---|---|---|---|
| Random Length Lumber (LB) | 110,000 board feet | Prince George, BC | Delisted; final contracts traded 2023 |
| Lumber Futures (LBR) | 27,500 board feet (one truckload) | Chicago area | Launched August 2022, the only listed contract |

LBR volume and open interest sit far below the pre-2022 contract's peak
years, and liquidity concentrates in the front two or three delivery
months, so the curve informs the front quarter and long-dated marks are
appraisals. The physical benchmark is the Fastmarkets Random Lengths
framing lumber composite, a weekly survey of transaction prices across
species and regions; contracts and analytics both key off it.

### Canadian softwood duty timeline (combined AD + CVD, company-average)

| Effective | Combined rate | Event |
|---|---|---|
| pre-Aug 2024 | ~8.05% | Prior administrative review |
| Aug 2024 | 14.54% | AR5 final results (near-doubling) |
| Aug 2025 | ~35% | AR6 final results |
| Sep 2025 | ~45% total | +10% Section 232 tariff on top of AD/CVD |
| Signalled 2026 | ~24.8% | AR7 preliminary, finals due summer 2026 |

Rates are company-specific (the published figures are the all-others or
largest-respondent rates) and each administrative review re-opens them, so
a duty branch in a scenario table carries a date and a rate range. Canadian
volume is roughly a quarter of US softwood consumption; BC interior mills
sit at the high end of the North American cash-cost curve after beetle kill
and fire salvage tightened fibre supply, so BC absorbs the curtailments
when prices fall and capacity keeps migrating to the US South.

### Why lumber errors are regime-sized

Demand shocks (housing starts, repair and remodel) hit a supply curve that
is nearly vertical over weeks (mills run or close; restarts take months and
new capacity takes years). The 2020-2022 record: futures above 1,700
USD/mbf in May 2021, under 500 by August 2021, above 1,300 in March 2022,
under 400 in 2023. A quarterly forecast error of 30% is inside recent
experience, so bands must be wide, drivers must be named, and precision
signalling (a monthly point path to December) reads as incompetence to
anyone who lived through 2021.

## Aggregates and construction materials

Gate prices: Vulcan Materials' freight-adjusted average was $21.08/ton in
2024 (+5-7% year over year, with 2025 guided the same); Martin Marietta's
aggregates average selling price was $23.77/ton in Q1 2025 (+6.8%). Both
producers describe the strategy as price over volume on their earnings
calls, and increases hold because the alternative quarry carries a freight
penalty: hauling dominates delivered cost beyond roughly 30 to 50 miles,
which makes each metro an oligopoly of one to three quarries with local
pricing power. Rural delivered prices rose 30-40% in 2023-2024 where hauls
exceed 50 miles, against single-digit gate increases (Rock Products), so
the national PPI is a sanity check and the local quote history is the
data. Cement shares the structure with a longer haul radius (barge and
rail matter) and periodic import competition at coastal terminals.

Forecast build: client's gate quotes, producer increase calendar with a
realization haircut, input pass-through (diesel on the haul leg through
fuel surcharges; labour, electricity, explosives at the gate), and local
demand from state DOT lettings and funded programs. The BLS publishes
industry PPI series for crushed stone and for construction sand and
gravel; series codes shift with NAICS revisions, so pull them by name from
the BLS PPI industry data finder at engagement time.

## Power

### Negative-price hours per year, German day-ahead (BNetzA/SMARD)

| Year | Hours | Year | Hours |
|---|---|---|---|
| 2015 | 126 | 2021 | 139 |
| 2016 | 97 | 2022 | 69 |
| 2017 | 146 | 2023 | 301 |
| 2018 | 134 | 2024 | 457 |
| 2019 | 211 | 2025 | 573 |
| 2020 | 298 | | |

The crisis years suppressed negatives (high gas floors the merit order)
and the solar build-out drives them: over 92% of 2024's negative hours
fell under the EEG three-hour rule, and the 2025 record low was about
-250 EUR/MWh on 11 May 2025. CAISO SP15 printed about 1,180 negative hours
in 2024 (13% of hours, median negative price near -$17) against about 530
in 2023; CAISO curtailed 3.4 TWh of utility-scale renewables in 2024 (93%
solar). ERCOT curtailed over 8 TWh of wind and solar in 2024 with the West
zone posting the most negative-price intervals (Potomac Economics IMM);
a system-wide ERCOT negative-hour count was not verifiable, treat ERCOT
negatives as zone-specific facts.

### Capture rates and cannibalization

Definitions (Hirth 2013): capture price = generation-weighted average
wholesale price; capture rate (value factor) = capture price over the
time-weighted base price. Hirth projected solar value factors falling from
about 1.3 at low penetration to about 0.6 at 15% market share, and wind to
0.5-0.75 at 30%. Realized 2024-2026: German solar capture price 54.64
EUR/MWh in 2024 (-31% year over year, S&P Global); German monthly capture
factor 0.77 (March 2024) to 0.53 (March 2025), with April monthly troughs
near 0.40 (2025) and 0.26 (2026) (Pexapark; monthly troughs sit well below
annual rates, quote them as such); Spanish solar capture price 45.56
EUR/MWh in 2024 (-40%); CAISO solar market value $27/MWh in 2023 (LBNL),
the lowest US market. Wind cannibalizes more slowly because its output is
less time-concentrated. Cross-border cannibalization is measurable in
coupled EU markets (Enervis). Consulting consequence: model the capture
rate as a declining function of installed capacity in the client's market
and price PPAs off capture forecasts.

### EPF benchmark results worth memorizing (German day-ahead, CRPS in EUR/MWh)

| Model family | 2020 | 2022 | 2023 | Source |
|---|---|---|---|---|
| LEAR + QRA | 1.35 | 10.65 | 4.42 | Lipiecki et al. 2024 |
| LEAR + IDR | 1.42 | 10.93 | 4.34 | Lipiecki et al. 2024 |
| LEAR-Ave (QRA+CP+IDR averaged) | 1.31 | 10.20 | 4.22 | Lipiecki et al. 2024 |
| DDNN-JSU (distributional net) | 1.34 | 13.38 | 5.27 | Lipiecki et al. 2024 re-run |

The distributional net won its own pre-crisis benchmark (Marcjasz et al.
2023, >7% CRPS over LEAR-QRA) and lost through the crisis to post-processed
linear models; 2024-2025 refinements (isotonic QRA, arXiv 2507.15079) tie
tuned Lasso-QRA at lower cost. Coverage collapses at breaks: the EDF
French study (arXiv 2405.15359) found every base model's intervals invalid
after September 2021, with online conformal wrappers restoring coverage.
CRPS scales with the price regime (calm German year 1.3-1.6, normal 4-5,
crisis 7-11), so never quote a CRPS target without a year and market
attached.

### Market mechanics

EU: single day-ahead coupling (SDAC) clears with the EUPHEMIA algorithm
across bidding zones; market time units moved from hourly to 15 minutes on
30 September 2025, which quadruples the target dimension for day-ahead
models. US nodal markets: LMP is the shadow price of the nodal balance
constraint in security-constrained economic dispatch, decomposing into
energy, congestion, and losses; day-ahead comes from SCUC. Vendors deploy
fundamentals (Aurora, Energy Exemplar PLEXOS, EnAppSys multi-market
equilibrium, Volue weather-driven) with statistical and ML correction
layers on top (Montel's hybrid framing), which matches the merit-order
finding that curve/residual-load features beat price-only inputs by about
5% on average and about 10% midday.

## Natural gas

Waha (Permian) basis chronology: 164 negative-price days in 2024 with an
August 2024 low of -$7/MMBtu, driven by production against takeaway
capacity; Matterhorn Express (2.5 Bcf/d) in service October 2024 relieved
the constraint; renewed production growth pushed Waha to a fresh record of
-$9.53/MMBtu in April 2026. The lesson generalizes: pipeline in-service
dates against basin production growth ARE the basis forecast at the one-to
three-year horizon, and any OU fit on basis history that spans a capacity
change mixes two regimes and calibrates neither. Algonquin city-gates (New
England) carries the winter mirror image, a scarcity premium into the
heating season set by pipeline capacity. Henry Hub itself trades on the
storage cycle: the EIA weekly report against the five-year average is the
state variable, and inventories link to basis and premium through the
theory of storage (Gorton-Hayashi-Rouwenhorst 2013: convenience yield is a
decreasing, non-linear function of inventories).

## The futures-curve evidence in one table

| Question | Finding | Source |
|---|---|---|
| Does the curve forecast spot? | Basis has forecast power for 10 of 21 commodities | Fama-French 1987 |
| Oil futures vs random walk | Futures lose in MSE at 1-12 months | Alquist-Kilian 2010 |
| Group verdict | Metals fail; gas/gasoline/ags closer to unbiased | Chinn-Coibion 2014 |
| Can models beat no-change for oil? | Combination gains 4-13% MSPE to 18 months | Baumeister-Kilian (BoC Review 2014) |
| Do those gains survive a fair benchmark? | Mostly no; end-of-month no-change kills most of them | Ellwanger-Snudden 2023; Benyo 2026 |
| Size of the long-only premium | 5.23%/yr 1959-2004; 3.67%/yr (insignificant) 2005-2014 | Gorton-Rouwenhorst 2006; BGR 2015 |
| Per-commodity roll returns | +5.5%/yr (heating oil) to -5.7%/yr (gold) | Erb-Harvey 2006 |
| What the basis predicts | 91% of the cross-section of futures returns; R-squared 0.024 as a time-series spot signal | Erb-Harvey 2006; BGR 2015 |

The one-line synthesis: the basis prices which futures position pays, and
it barely says where spot is going, so use the curve as the central spot
forecast, subtract an own-history premium estimate, and spend modelling
effort on the basis and the fundamentals.
