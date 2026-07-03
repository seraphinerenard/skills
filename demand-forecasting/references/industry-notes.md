# Extended industry notes

Depth that would bloat SKILL.md: operational formulas for utility load,
the order-book blend for project-driven manufacturers, and the channel
dynamics of lumber. URLs are consolidated in sources.md; the utility material
traces to research/stlf-hierarchical-load.md.

## Utility load, the operational detail

### The GAM that runs France

EDF's operational short-term model is a semi-parametric GAM (Obst, de
Vilmarest and Goude, IEEE TPS 2021, equation 1). Its terms are the checklist
for any serious load model:

- Day-type categorical effects interacted with a daylight-saving indicator,
  with public holidays and bridge days as their own day types.
- Lagged load at one day (interacted with day type) and one week.
- A long-term trend smooth and a cyclic time-of-year smooth.
- A tensor smooth of time-of-day with temperature: the temperature response
  differs at 07:00 and 15:00.
- Exponentially smoothed temperatures with coefficients 0.95 and 0.99, plus
  smoothed daily min and max. Buildings integrate weather; yesterday's heat
  is still in the walls, and the smoothed series carry that thermal inertia.

Fit with mgcv (bam for scale). The same specification fitted locally to each
of 2,260 French substations is the reference for feeder-level work (Goude,
Nedellec and Kong, IEEE TSG 2014). During the 2020 lockdown EDF kept the GAM
and made it adaptive with a Kalman layer on the coefficients, which is the
pattern for structural breaks generally: keep the structure, let the levels
move (Obst et al. 2021).

### Weather variable constructions worth stealing

- PJM winter wind adjustment: WWP = T - 0.5 x (wind - 10) when wind exceeds
  10 mph, else T. PJM summer humidity index: THI = T - 0.55 x (1 - RH) x
  (T - 58) for T >= 58 F, else T. Both feed four-section temperature splines,
  with CDD, HDD and their one-day lags entering year-round (PJM Load
  Forecasting Whitepaper, 2016).
- Great Britain effective temperature: TE_h = 0.5 x (TE_{h-24} + TO_h), a
  recursive smoother giving a one-day memory, plus population-weighted 10 m
  wind for wind chill (NESO model as described in arXiv 2604.20445).
- Holiday engineering: PJM uses fractional "fuzzy" holiday variables whose
  value depends on which weekday the holiday lands on, and a graduated
  Christmas-lights ramp from the Friday after Thanksgiving to December 23.
  Moving-date holidays wreck naive calendar dummies in any industry; the
  fuzzy-fraction trick transfers directly to retail (Easter, Ramadan).

### GEFCom lineage, the probabilistic recipe

GEFCom2014's load and price tracks were both won by the quantile-GAM plus
temperature-scenario method (Gaillard, Goude and Nedellec, IJF 2016): fit
quantile additive models, generate temperature scenarios from historical
weather years, push each scenario through the load model, and read predictive
quantiles off the scenario ensemble. That two-stage shape (conditional model
x weather ensemble) remains the default for probabilistic load in 2026, with
ECMWF ensemble members replacing historical shuffles where the budget allows.

### The inference-time weather trap

Load models train on weather actuals and predict on weather forecasts, so
production error contains weather-forecast error the backtest never saw.
Backtest on archived NWP forecasts (not actuals) whenever the archive exists;
otherwise report the backtest as an upper bound on achievable accuracy and
say so in the deliverable. Scale of the gap: CAISO's day-ahead system
forecast logged 4.55% MAPE with a 3,211 MW peak miss during the July 2024
heat wave (yesenergy.com writeup, accessed 2026-07-12).

### Net load, solar and EVs

<!-- allow:CAN behind-the-meter names the metering device -->
Behind-the-meter PV subtracts an unmetered, weather-driven generator from
every feeder's load, so net load looks like decay where adoption grows. Two
architectures: reconstruct gross load (net + estimated BTM PV from irradiance
and capacity registries) and forecast the parts separately, or forecast net
directly with irradiance covariates. A 2026 feeder-level comparison
(ITEGAM-JETIA) found direct net-load forecasting statistically more accurate
across the hierarchy but with an over-forecasting bias; the decomposed route
stays preferable when the PV registry is good and when the client needs the
gross series for planning. EV and large-load growth enters as explicit
scenario adders, and ERCOT's 2025 waterfall is the worked example: base
econometric load + EV forecast + crypto growth - rooftop PV + contracted
large loads, with new data-centre requests haircut to 49.8% and in-service
dates pushed 180 days because 2022-2024 actuals averaged about 220 days of
delay. The reason for the discipline: ERCOT's 2030 data-centre load estimate
jumped from 29,614 MW in the 2024 vintage to 77,965 MW in 2025, and unhedged
acceptance of interconnection requests would have produced a 218 GW system
forecast by 2031 (ERCOT LTLF materials, April 2025).

### Doctrine

Load-serving forecasts in MISO must be P50 by rule; the GB capacity standard
uses a 1-in-20 Average Cold Spell peak. Ask which probability level the
client's process expects before arguing about models; a "conservative" P70
forecast fed into a process that assumes P50 quietly over-procures every
year.

## Building materials and aggregates

Cement, aggregates and asphalt volumes are project-driven: a few DOT
contracts and large commercial pours dominate a plant's year, so SKU-week
history alone carries little signal and a pure statistical forecast misses
every step change. The working structure is a blend of the order book and a
statistical baseline.

- Order book as the near-horizon forecast. Booked and quoted work converts to
  volume with estimable realization rates and timing slip. Build the booking
  curve from history: at lead time h, what share of finally delivered volume
  was already visible in bookings? If 4 weeks out that share is 80%, the
  4-week forecast is bookings / 0.80 blended with the baseline at weight 0.8.
  The blend weight at each lead IS the booking-curve share; this is the same
  pickup logic airlines use on reservation curves, and it degrades gracefully
  as the book thins with horizon.
- Statistical baseline for the far horizon: seasonal profile on workable
  days, at the plant-month level. Concrete pours and asphalt paving need
  temperatures above roughly 5 C and dry conditions, so normalize volume per
  workable day (from climatology) and forecast workable days per month;
  weather shifts demand across weeks more than it destroys it, so expect
  catch-up volume after a wet month.
- Leading indicators for the annual plan, at regional aggregate level only:
  housing permits and starts (US Census), state DOT lettings schedules, and
  the Architecture Billings Index, which leads non-residential construction
  spending by about 9 to 12 months (AIA's published lead-time
  characterization). These move the yearly level; they add nothing at
  SKU-week.
- Customer concentration: forecast the top accounts individually with sales
  input logged as overrides (the model-operations skill owns the scoring of
  those overrides), and run statistics on the long tail.

## Lumber

Dimensional lumber demand derives from residential construction plus repair
and remodel. A single-family start consumes roughly 15,000 board feet of
framing lumber (NAHB estimates; varies with home size), so single-family
starts times board-feet-per-start, lagged over the construction schedule,
anchors the consumption forecast; permits lead starts by one to two months
and give the earliest usable signal.

The trap specific to lumber is channel inventory feedback. Dealers and
distributors pre-buy when prices rise and destock when prices fall, so mill
shipments overstate end-use demand in rallies and understate it in slides;
the 2021 futures spike is the canonical episode. Model end-use demand (starts
x usage plus R&R proxies) separately from the channel effect, and treat price
expectations as a demand covariate with the price path itself owned by the
price-forecasting sibling skill. When shipments and end-use diverge, the gap
is inventory motion and it mean-reverts; forecasting shipments as if the gap
were demand growth is how lumber forecasts miss by a quarter.
