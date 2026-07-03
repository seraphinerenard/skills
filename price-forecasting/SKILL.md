---
name: price-forecasting
description: |
  Forecast market prices for consulting clients: lumber, aggregates and
  construction materials, wholesale power, natural gas and fuels, metals, ags,
  and FX-driven import costs. Trigger on: "forecast the price of X", "what
  will lumber/power/gas/steel cost next quarter", "build a procurement price
  forecast", "quantify our budget risk on diesel", "PPA capture price
  analysis", "should we trust the futures curve", "when should we hedge".
  Covers method selection with reasons, the futures-curve default and its
  risk-premium bias, OU/VECM/regime/GARCH calibration with worked numbers,
  supply-stack fundamentals for power, vintage-data discipline for ML
  features, decile deliverables, and evaluation (CRPS, pinball,
  Diebold-Mariano). This skill forecasts MARKET prices; setting our own
  selling price belongs to the price-optimization skill.
---

# Price forecasting

Client questions arrive as decisions: "what should the budget assume",
"when do we hedge", "does this PPA clear our return hurdle", "which quarry
wins the bid". Each is a decision under a distribution, so the deliverable
is a distribution with named drivers, and the point forecast is one row of
it. The methods below exist to earn a distribution the client can act on,
and every one of them is judged against two humble baselines: the futures
curve where one trades, and the random walk where none does.

Sibling lanes: demand-forecasting owns volume and load forecasts,
feature-engineering owns generic feature craft, causal-inference owns
pass-through and price-elasticity identification when the client changes
something, price-optimization owns setting our own price. Cross-reference
them; this file stays on market prices.

## Method selection

Pick by market structure and horizon, in this order. The table rows are
decisions; the sections below carry the reasons and the numbers.

| Situation | Method | Why |
|---|---|---|
| Liquid futures curve exists, horizon 3-24 months | Curve as the central forecast, risk-premium adjustment where documented, GARCH bands around it | Decades of evidence that beating the curve at these horizons is rare (Fama-French 1987; Alquist-Kilian 2010; Reichsfeld-Roache 2011) |
| Liquid curve, horizon under ~3 months, the gap to fair carry is wide | OU on the basis or VECM on spot-futures | Short-horizon predictability lives in the mean-reverting basis; the level stays a random walk |
| Hourly or daily power prices | Supply-stack fundamentals plus a probabilistic statistical layer; distributions always | Spikes, negative prices, and renewables make point forecasts useless for trading and PPA work; see the power archetype |
| No traded curve (aggregates, cement, regional materials) | Cost build-up plus pass-through regression plus the producers' announced-increase calendar | Price is set by oligopoly cost-plus behaviour, so model the inputs and the conduct |
| Regime-driven commodity (lumber) | Scenario forecasts keyed to named drivers, wide GARCH-t bands, curve only for the first two or three delivery months | Forecast errors are regime-sized; precision theatre destroys credibility |
| Two prices tied by physics or arbitrage (power-gas, WTI-Brent, cross-region) | VECM or a structural spread model | The spread is stationary while the levels are not; forecast the spread |
| Import cost in the client's currency | Forecast in the trade currency, then apply FX with a pass-through elasticity below 1 | Pass-through is partial and slow; a full-FX translation overstates cost risk |
| ELSE | Random walk centred on the last price with GARCH-t bands, re-estimated weekly | The no-change forecast is the hardest baseline in price forecasting; anything you deliver must beat it out of sample, so start there |

## The futures curve is the default forecast

Where a liquid curve trades, the curve is the market's conditional
expectation plus a risk premium, and the empirical record (URLs in
`references/sources.md`) says which part you can improve on:

- Fama and French (Journal of Business 1987) decompose the basis into an
  expected premium and an expected spot change across 21 commodities and
  find spot-forecast power for 10 of 21 and detectable time-varying premia
  for only 5. The basis starts out as a weak and uneven spot predictor.
- Alquist and Kilian (JAE 2010) show WTI futures forecast spot WORSE than
  the no-change forecast in mean squared error at 1-12 months.
- Chinn and Coibion (Journal of Futures Markets 2014) give the group
  verdict on post-1990 data: metals futures fail unbiasedness and lose to
  the random walk (they liken them to Meese-Rogoff exchange-rate forwards);
  energy and agricultural futures sit closer to unbiased and sometimes beat
  the random walk, with natural gas and gasoline beating oil; predictive
  content has declined broadly since the early 2000s.
- Reichsfeld and Roache (IMF WP/11/254) test 10 commodities out of sample
  and conclude the futures forecast is "hard to beat", with performance
  independent of the curve's slope.
- Baumeister and Kilian beat the no-change forecast for oil with real-time
  fundamentals: their equal-weighted combination (oil-market VAR,
  industrial-materials prices, product spreads, the curve) posts MSPE
  ratios of 0.87 to 0.96 out to 18 months (Bank of Canada Review, Spring
  2014). Ellwanger and Snudden (JBF 2023) then discount much of this:
  against the end-of-month no-change benchmark (the true daily random walk)
  most short-horizon model gains vanish, and Benyo (Economic Inquiry 2026)
  finds only futures-based forecasts beat that benchmark, only at long
  horizons. The benchmark choice decides the conclusion, so backtests here
  use end-of-period prices and never monthly averages.

The premium is real money and a poor spot signal, and the distinction pays
for itself. Gorton and Rouwenhorst (FAJ 2006) measure a 5.23% per-annum
collateralized futures premium (t = 2.92, 1959-2004), which fell to an
insignificant 3.67% out of sample 2005-2014 (Bhardwaj-Gorton-Rouwenhorst,
NBER 2015). Per commodity, Erb and Harvey (FAJ 2006) report roll returns
from +5.5% (heating oil) to -5.7% per annum (gold), and the roll explains
91% of the cross-section of futures excess returns. The same basis used as
a time-series signal for one commodity's direction gives R-squared 0.024
(BGR 2015, Figure 5). So the basis tells you which futures position pays a
premium while it barely tells you where spot is going. Practical
adjustment: estimate the premium from that commodity's own
futures-minus-realized history by delivery month, expect a magnitude of 0
to 5% a year with an unstable sign, subtract it from the curve, and state
the adjustment in the deliverable. A model that disagrees with the adjusted
curve at 6-24 months carries the burden of proof: it survives a
Diebold-Mariano test against the curve before the client hears the number,
because the client hears "we forecast 84, the curve says 78" as a trade
recommendation.

## Lumber, where forecast errors are regime-sized

The industry marks to the Fastmarkets Random Lengths framing lumber
composite, a weekly survey price. The futures market is small: CME
delisted the old Random Length contract (110,000 board feet, Prince George
BC delivery) and replaced it with Lumber Futures (LBR, 27,500 board feet,
one truckload, Chicago-area delivery) launched in August 2022, and LBR
liquidity concentrates in the front two or three delivery months. So the
curve anchors the front months and nothing else; beyond a quarter you are
forecasting without a market consensus to lean on.

The price history explains the humility this archetype demands: futures
printed above 1,700 USD per thousand board feet in May 2021, under 500
three months later, above 1,300 again in March 2022, and in a 350-600
range through 2023-2025. Three drivers move it in regime-sized steps:

- Housing starts. Single-family starts lead demand, and short-run supply
  is inelastic (a mill runs or it does not), so demand surprises convert
  into convex price moves.
- Canadian softwood duties. The combined anti-dumping and countervailing
  rate ran near 8.05%, jumped to 14.54% in August 2024, jumped again to
  about 35% in the August 2025 administrative review, and a further 10%
  Section 232 tariff in September 2025 took the total near 45%; Commerce
  then signalled roughly 24.8% for the 2026 review (NAHB, Commerce).
  Roughly a quarter of US consumption crosses that border, so each step is
  a supply-cost shock. Duty outcomes are discrete and datable: model them
  as named scenario branches with probabilities, never smeared into a
  trend.
- Mill curtailments. High-cost BC interior mills curtail or close within
  weeks when the composite trades below their cash cost, which floors the
  price; capacity has migrated to the US South through 2022-2025.
  Curtailment announcements are public and belong in the feature set.

Deliverable pattern: a scenario table on the three named drivers with
GARCH-t bands per branch, the curve for the front months, and no
directional call against the curve without a Diebold-Mariano result to
back it.

## Aggregates, where price is quarry-gate plus haul

Crushed stone, sand, and gravel sell for about 21 to 24 USD per ton at the
quarry gate (Vulcan's 2024 freight-adjusted average was $21.08; Martin
Marietta's Q1 2025 average selling price was $23.77). The value-to-weight
ratio is so low that trucking dominates delivered cost beyond roughly 30
to 50 miles, so every market is local, sellers in a metro are one to three
quarries, and a national forecast answers the wrong question. Rural
delivered prices spiked 30-40% in 2023-2024 where hauls exceed 50 miles
while gate prices rose single digits (Rock Products).

Producers price on announced list increases and hold them because the
alternative quarry carries a freight penalty: Vulcan raised freight-adjusted
prices 5-7% in 2024 and guided the same for 2025 on flat volumes; Martin
Marietta printed +6.8% in Q1 2025. This conduct makes the forecast a
cost-and-conduct build, and the archetype needs no time-series machinery:

1. Start from the client's actual quoted gate prices; national PPI series
   (BLS publishes industry PPIs for crushed stone and for construction
   sand and gravel) serve as sanity checks and never as the forecast,
   because regional divergence dwarfs the national trend.
2. Layer the producers' announced increase calendar (January and April
   effective dates dominate) with a realization haircut estimated from
   the client's own invoice history.
3. Pass through input costs with lags: diesel through fuel surcharges on
   the haul leg, labour and electricity and explosives at the gate; the
   causal-inference skill owns estimating these pass-through rates
   properly.
4. Scale local demand by state DOT lettings and funded infrastructure
   programs; public work is the volume swing factor.

The deliverable quotes delivered cost per ton for the client's specific
plants with the haul leg priced separately, because the haul is where the
variance lives.

## Power, where the deliverable is a distribution

Hourly granularity (EU day-ahead moved to 15-minute units with SDAC on 30
September 2025), spikes, and negative prices put power in its own class.
The numbers to hold in mind: German day-ahead negative-price hours ran 69
in the crisis year 2022, 301 in 2023, 457 in 2024, and 573 in 2025
(Bundesnetzagentur/SMARD), with a 2024 floor of -135.45 EUR/MWh; CAISO's
SP15 hub printed about 1,180 negative hours in 2024, up from about 530 in
2023 (REsurety); the August 2022 German peak reached 850 EUR/MWh (EWI).
A point forecast of the mean is useless for trading, PPA valuation, and
procurement against that shape; the deliverable is always a predictive
distribution per hour plus scenario conditionals.

Fundamentals set the logic. The marginal unit prices every MWh, so power
is a derivative of fuel and carbon when thermal is marginal (CCGT cost =
gas/0.55 + 0.36 x carbon) and of renewables output when it is not.
`assets/supply_stack.py` implements the mechanism; merit-order and
residual-load features improve day-ahead models by about 5% on average and
about 10% in midday hours against price-only features (arXiv 2501.02963).
Commercial practice is fundamentals-first with statistical correction
layers (Aurora, PLEXOS, EnAppSys, Volue all run dispatch models under
their forecasts).

Renewables cannibalize their own revenue, and the client's PPA or asset
case needs the capture price and never the baseload average. Capture rate
= generation-weighted price over time-weighted price (Hirth, Energy
Economics 2013, who projected solar value factors falling from about 1.3
to about 0.6 at 15% penetration). Realized: German solar capture prices
fell 31% in 2024 to 54.64 EUR/MWh (S&P Global); German monthly solar
capture factors fell from 0.77 in March 2024 to 0.53 in March 2025
(Pexapark); US solar market value bottomed at $27/MWh in CAISO in 2023
(LBNL). Any solar revenue forecast built on baseload price forecasts
overstates revenue by a spread that widens with build-out; forecast the
capture rate as its own declining series keyed to installed capacity.

For the statistical layer, the benchmark lineage settles method choice.
Lago et al. (Applied Energy 2021) set the open benchmark: LEAR
(LASSO-estimated autoregression) and a small DNN, with the epftoolbox
datasets. Distributional networks (DDNN-JSU, Marcjasz et al., Energy
Economics 2023) beat LEAR-QRA by over 7% in CRPS on pre-crisis German
data. Then the crisis reversed the ranking: LEAR point forecasts
post-processed by quantile regression averaging, conformal prediction, and
isotonic distributional regression, then averaged, beat the DDNN through
2021-2023 (Lipiecki, Uniejewski, Weron, Energy Economics 2024), with best
German CRPS around 1.3 EUR/MWh in calm 2020, 10.2 in crisis 2022, and 4.2
in 2023. A French study (EDF, arXiv 2405.15359) shows every base model's
coverage failed after September 2021 and online conformal wrappers
restored it. The production conclusion, scoped to European day-ahead
markets 2019-2025: regularized linear models with distributional
post-processing are the deployable frontier, deep nets add single-digit
CRPS in stable regimes and give it back through breaks, and an online
conformal wrapper is cheap insurance on whatever you deploy.

Power forwards carry hedging-pressure premia. Bessembinder-Lemmon (Journal
of Finance 2002) derive the equilibrium: the forward premium falls with
expected spot variance and rises with spot skewness, so premia concentrate
in spike-prone delivery periods. Calibrate the premium per delivery month
from forwards-minus-realized history before reading any forward as a
forecast, and expect the PPA counterparty to have done the same.

## Natural gas and fuels

Storage is the state variable. The EIA weekly storage report against the
five-year average positions the market between scarcity and glut, the
deviation drives both the price level and the curve shape, and inventories
link mechanically to the basis and the risk premium
(Gorton-Hayashi-Rouwenhorst, Review of Finance 2013). Gas futures also
earn more trust as forecasts than oil futures do (Chinn-Coibion). The
forecast recipe: Henry Hub curve as the anchor, a storage-deviation
adjustment estimated on history, GARCH-t bands, and event risk scheduled
around the Thursday storage release.

Basis is where gas consulting money is made or lost. Each hub's basis is
an OU process with a seasonal mean and a capacity regime on top: Waha
(Permian) traded negative on 164 days in 2024 with an August low of
-$7/MMBtu because production outran pipeline takeaway, the 2.5 Bcf/d
Matterhorn Express line relieved it from October 2024, and new negative
records returned by April 2026 (-$9.53/MMBtu) as production caught up
again (EIA, NGI, RBN). The capacity calendar (pipeline in-service dates
against production growth) IS the basis forecast at the one-to-three-year
horizon; the OU machinery only fills in the path between regimes. New
England's Algonquin city-gates carries the mirror-image structure: a
winter basis premium priced by pipeline scarcity into the heating season.
For refined fuels exposure (diesel for an aggregates or freight client),
crack spreads mean-revert and product spreads carry forecast information
for crude itself at one-to-two-year horizons (Baumeister-Kilian-Zhou).

## Metals, ags, and FX pass-through, briefly

Metals: futures fail unbiasedness and lose to the random walk in squared
error (Chinn-Coibion), so the default is the random walk with GARCH-t
bands, and modelling effort goes to the basis (LME cash-to-3M) and
inventory signals, which carry premium information (GHR 2013). Ags:
futures sit closer to unbiased and WASDE releases move prices the same
day, so the curve anchors, vintage discipline around report dates is
mandatory, and old-crop and new-crop months are treated as distinct
commodities. FX pass-through for import costs: pass-through into import
prices is partial and slow, averaging about 0.46 within a quarter and 0.64
in the long run across OECD countries (Campa-Goldberg, REStat 2005), and
lower short-run for dollar-invoiced trade (Gopinath et al., dominant
currency pricing). Forecast the commodity in its trade currency, apply an
elasticity of 0.4 to 0.6 on the FX leg for the first year unless the
client's contracts fix the currency, and name the invoicing currency in
the deliverable.

## Methods with judgment

### Calibrate the OU for mean reversion, then distrust the half-life

`assets/ou_calibration.py`. The OU process sampled at interval dt is exactly
an AR(1) with slope b = exp(-kappa dt), so OLS calibrates it without
discretization error, and the half-life is ln 2 / kappa. Worked: daily
basis data with fitted b = 0.977 gives kappa = -ln(0.977) = 0.0233 per day
and a 29.8-day half-life. The mapping is convex near b = 1 (b = 0.96 maps
to 17 days, b = 0.99 to 69 days), and OLS biases b low by about (1+3b)/n
(Kendall 1954), so fitted half-lives come out short. Measured in the module
(true half-life 30 days, 400 Monte Carlo paths per cell): median fitted
half-life is 12.0 days at n = 125, 16.8 at n = 250, 23.4 at n = 504, 27.3
at n = 2016; the Kendall correction recovers 26.7 to 32.0 across the same
cells. A six-month sample cannot support a two-week half-life claim, and
the module's bootstrap interval reports infinity when refits lose mean
reversion, which is the honest answer on weak samples.

### Cointegration and VECM forecast the spread; distrust the alphas

`assets/vecm_spot_futures.py`. Use for spot-futures pairs, cross-region
bases, and physics-linked pairs (power-gas spark spread, crack spreads,
WTI-Brent). Lag selection runs on levels and the VECM takes k_ar_diff one
less than the VAR order; the constant belongs inside the cointegrating
relation (deterministic="ci") for a basis that reverts to a non-zero carry
level. The identified quantity is the spread-adjustment rate (alpha_f -
alpha_s under beta = [1, -1]); the individual alphas are weakly identified
whenever the common trend's variance dominates the basis variance, which is
the normal case in storable commodities. In the module's demo (n = 750) the
fitted alphas are (+0.051, +0.081) against true (-0.027, +0.007), while the
spread rate 0.030/day sits near the true 0.034 and implies a 22.8-day
half-life against a true 20. Deliver spread forecasts and hedging rules;
decline price-discovery attributions from daily data. Johansen critical
values in statsmodels cover at most 12 series, and statsmodels 0.14.6 with
numpy 2.x emits a benign ComplexWarning from coint_johansen.

### Regime switching describes history and extrapolates poorly

`assets/markov_regimes.py`. Markov switching earns its place as a
description (how long do stress regimes last, what volatility do they
carry) and as a spike-state input to power models. As a forecaster it is
fragile out of sample: the likelihood surface has local optima (fit with
search_reps around 30), regime labels permute between fits (sort by fitted
variance before comparing anything), and the regime means are weakly
identified even when variances and durations recover well. The module's
demo (n = 1000, true stress mean +0.5%/day) recovers the two volatilities
within 3% relative error and classifies 97% of days correctly, and still
fits the stress mean at -0.04%/day with the wrong sign; the half-versus-full
refit audit moves the calm regime's expected duration by 15 days. The
audit is the deliverable discipline: if durations or variances move
materially between refits, present regimes as descriptive history and keep
them out of the point forecast. Marcjasz-Weron style EPF work uses regime
information through probabilistic layers for the same reason.

### Volatility earns the deciles with GARCH-t simulated to the horizon

`assets/garch_deciles.py`. Procurement decisions consume price levels at a
date, so simulate: fit GARCH(1,1)-t on percent log returns (the arch
package wants returns scaled to percent; raw decimals trigger
DataScaleWarning and a fragile fit), draw 20,000 paths to the horizon with
forecast(method="simulation", reindex=False), compound from spot, and read
deciles. Demo numbers (5 years of synthetic daily data, persistence 0.981,
t dof 6.8, spot 74.50, 63-day horizon): P10 = 63.01, P50 = 73.49, P90 =
85.91, an 80% band of 30.7% of spot. The matched-variance normal
approximation errs in a quantile-dependent direction (wider than the
simulation at the deciles, narrower beyond about P99), so no single
inflation factor repairs it; simulation is the method of record when the
deliverable quotes both deciles and tail scenarios. Details and the
crossover numbers sit in `references/derivations.md`.

### Jumps and spikes belong to power

Daily GARCH bands cover storable commodities. Hourly power needs an
explicit spike mechanism because scarcity hours sit 5-30x the median and
arrive in clusters: either a jump component on top of the diffusion, a
spike-state regime layer, or (the current practical winner) distributional
and quantile models that let the upper quantiles carry the spikes without
naming a mechanism. The power archetype carries the specifics; the general
rule is that any model whose residual QQ plot fails above the 99th
percentile understates exactly the hours the client cares about.

### Structural models earn their data cost on conditional questions

`assets/supply_stack.py`. A reduced-form model answers "what will the price
be"; a structural model answers "what will the price be if gas doubles, if
8 GW of solar arrives, if the duty rises". When the client's question has
an "if" in it, fundamentals earn their data cost, because the conditional
is computed mechanically: in the module's synthetic two-week stack, raising
gas from 25 to 50 EUR/MWh moves mean power from 69 to 90 EUR/MWh (CCGT sets
the margin in most hours, pass-through near hours-marginal divided by 0.55),
and raising solar from 2 to 8 GW cuts the solar capture rate from 0.99 to
0.69 while creating 19 negative-price hours a fortnight. No reduced-form
model produces those conditionals credibly, and both numbers are the kind a
PPA or procurement client is actually buying. The cost side is real: a
stack model needs plant lists, efficiencies, fuel and carbon forwards, and
outage data, so reserve it for engagements where the conditional question
recurs.

### ML on fundamentals lives or dies on vintage discipline

Gradient boosting and regularized regressions on fundamental features beat
naive statistical models in backtests with depressing regularity and then
give it back in production, and the usual cause is the information set:
features enter the backtest at their revised values and their event
timestamps, while production sees them only at publication. The discipline: every
feature carries an availability timestamp (EIA weekly gas storage covers
the week ended Friday and publishes the following Thursday; WASDE is
monthly with same-day price impact; PPI for a month publishes mid the next
month; housing starts publish near the 17th and revise for two months), and
the backtest joins on availability, and revised series are replaced with
first-release vintages where the agency publishes them (ALFRED for FRED
series). A model whose backtest edge survives the vintage join is rare and
valuable; one that does not is the most common consulting failure in this
domain. Feature craft beyond timing belongs to the feature-engineering
skill.

### Ensembles anchor on the curve

The combination that survives client scrutiny: the curve (or random walk)
as the anchor, one statistical model (VECM or OU on the basis), one
fundamental or ML model, weights estimated on pinball loss over an
expanding-origin backtest and shrunk toward the anchor. Equal-weight
combinations are hard to beat (the forecast-combination literature since
Bates-Granger 1969 keeps refinding this); the practical gain from the
ensemble is less the point accuracy and more that the members' disagreement
is itself deliverable as scenario spread.

## Deliverables for procurement and hedging clients

Three artifacts cover nearly every engagement:

1. A decile table at the decision horizons (the GARCH module prints one),
   quoted as prices and as percent versus today, with the fitted volatility
   state named ("current conditional vol 26% annualized, 60th percentile of
   the last five years").
2. A scenario table tied to named inputs, computed structurally where
   possible: each row is a named, dated, plausible event (gas at 50, duty
   at 35%, housing starts at 1.6M) with the implied price and the mechanism
   in one sentence. Scenarios with named drivers survive client meetings;
   unnamed percentiles do not.
3. Trigger-based hedging rules, pre-agreed: "hedge 50% of H2 volume when
   the P25 of the H2 average rises above budget; hedge the rest at 10%
   below budget or 30 days before the season, whichever comes first." The
   rule converts the distribution into actions and removes the client's
   temptation to treat the P50 as a promise.

State the forecast's information date on every artifact. A forecast is a
statement about a distribution conditional on a date's information, and
half the disputes a consultant faces dissolve when the artifact says so.

## Evaluation

Score distributions with pinball loss at the deciles and CRPS; score point
forecasts with MAE against the curve and the random walk; test differences
with Diebold-Mariano; treat directional accuracy as marketing until it
passes Pesaran-Timmermann. All four are implemented with worked numbers in
`assets/forecast_eval.py`.

- Pinball, worked: a P90 forecast of 620 against an outcome of 585 scores
  (1 - 0.9) x 35 = 3.5; the same miss under the quantile would score
  0.9 x 35 = 31.5. The asymmetry is the point: it prices under- and
  over-coverage the way the client's decision does.
- CRPS uses the fair (unbiased) ensemble form; the classic m-squared form
  rewards under-dispersed ensembles. Demo: a calibrated ensemble scores
  1.17, a 3x over-dispersed one 3.49, a +6 biased one 3.73 (units of the
  target). CRPS integrates pinball over quantile levels, so reporting
  pinball at the nine deciles decomposes the same ranking by quantile.
- Diebold-Mariano, worked: 5-step forecasts, n = 215, MSE 4.34 versus 5.08;
  DM = -2.04 raw, -2.00 after the Harvey-Leybourne-Newbold small-sample
  factor 0.979, p = 0.047 against t(214). The HLN correction and the
  Newey-West variance with h-1 lags decide borderline cases exactly where
  consulting claims live. statsmodels has no built-in DM test; the module
  implements it.
- The directional trap, worked: on a series drifting up 65% of days, the
  forecast "always up" posts a 65% hit rate, and the Pesaran-Timmermann
  statistic is exactly 0 because the chance benchmark is also 65%. Quote
  hit rates only with the PT p-value attached.

Backtest discipline: expanding-origin refits at the client's real decision
frequency; features joined on availability timestamps with first-release
vintages (the ML section above); settlement prices from the actual venue,
never interpolated; the curve and the random walk as mandatory baselines in
every table. The backtest-gauntlet skill's timing table applies unchanged
when a forecast feeds a trading decision.

## Regional basis modelling

Hub prices carry the trend; the client's price is hub plus a basis set by
freight, capacity, and local supply. Model the basis separately: it is
stationary (OU with seasonal mean) while the hub is not, its half-life and
seasonal shape are estimable on short samples, and freight costs bound it
on both sides (a basis above delivered-freight-from-the-next-region invites
arbitrage flows that close it). Gas basis needs pipeline capacity as a
state variable (constrained paths let basis blow out past freight parity:
Waha traded negative for months in 2024 while Henry Hub sat above 2
USD/MMBtu, and Algonquin winter basis spikes when New England pipes fill).
Lumber and aggregates carry the same structure with trucks: the aggregates
archetype treats haul cost as the dominant term, and lumber regional prices
(coastal BC versus SPF versus southern yellow pine) diverge for quarters
when duties or curtailments hit one supply region. The general recipe:
forecast the hub with the methods above, forecast the basis as OU with
seasonal mean and capacity dummies, add, and quote the basis assumptions
separately so the client sees which half of the number moved.

## Assets and references

| File | Contents |
|---|---|
| `assets/ou_calibration.py` | OU calibration, half-life, Kendall correction, bootstrap CI, Monte Carlo bias demo |
| `assets/vecm_spot_futures.py` | Johansen test, VECM fit, spread-rate identification, 20-day forecast demo |
| `assets/markov_regimes.py` | 2-regime switching fit, label alignment, refit-stability audit |
| `assets/garch_deciles.py` | GARCH(1,1)-t decile table at a procurement horizon via simulation |
| `assets/forecast_eval.py` | Pinball, fair CRPS, Diebold-Mariano with HLN, Pesaran-Timmermann |
| `assets/supply_stack.py` | Merit-order stack, capture-rate cannibalization, gas pass-through |
| `references/derivations.md` | The math behind every worked number above |
| `references/market-structure.md` | Extended lumber, aggregates, power, and gas market-structure notes |
| `references/sources.md` | Sources with URLs and access dates |
| `references/research/*.md` | Researcher fact sheets with primary extracts and verification flags |

All modules run on Python 3.12+ with numpy 2.5, pandas 3.0, statsmodels
0.14.6, arch 8.0 (pip names in each file's top comment); each has a
`__main__` demo on synthetic data whose printed numbers match the worked
examples in this file.
