# The mechanics of industry dataset quirks

Depth notes behind SKILL.md section 4. Weather and geospatial detail lives in
`research/weather-geospatial-joins.md` (researcher fact sheet, primary-sourced);
this note covers POS, syndicated scanner, ERP, SCADA, money, and clocks. URLs sit in
`sources.md`.

## Retail POS

Returns and voids. A return posts as a negative-quantity row on the return date,
weeks after the sale it reverses. Netting returns into daily sales creates negative
demand days, and negative days break Tweedie objectives (mass at zero, support on
the non-negative axis) and any log1p transform. Model gross sales as demand and
model returns as a second series with its own lag structure (returns lag purchases
by the return-window distribution). Voids reverse a line inside the same
transaction; they are keying errors, so drop void pairs before any aggregation.

Promo flags. Retailer promo calendars record intent. Execution drifts: stores hang
tags late, run out of display stock, or extend a promo past its end date. A model
keyed to the calendar learns diluted lifts and ghost lifts. Derive realized promo
state from price: estimate base price as the rolling median of shelf price over the
trailing 8 non-promo weeks, then flag promo when shelf price drops below about 95%
of base. Iterate once (flag, re-estimate base excluding flagged weeks, re-flag).
The `discount_depth = shelf_price / base_price` column then carries promo depth as
a continuous feature, and the calendar flag survives only as plan data for
`days_until_promo`.

Item identity. GS1 eliminated GTIN reuse for items active on 2019-01-01 or later;
before that, codes legally recycled after 48 months (30 months for apparel), so a
long POS history can contain one UPC meaning two products. Separately, pack changes
and brand refreshes remap one economic item across several codes. Build a surrogate
item key: start from the item master's effective-dated remap table, chain remaps
transitively, fuzzy-match description+brand+size for undocumented splices, and
validate every splice by velocity continuity (units per store per week within the
same order of magnitude across the joint; a 10x step means a bad match).

## Syndicated scanner data (NielsenIQ, Circana)

Definitions that models get wrong:

- ACV (all-commodity volume) is a store's total sales across every category; it
  weights distribution by store importance.
- %ACV distribution = ACV of stores selling the item / total market ACV * 100. An
  item in 2 stores that do half the market's volume reads 50% ACV and 2 stores.
- TDP (total distribution points) = the sum of %ACV across the items of a brand or
  segment; breadth times depth in one number. Both vendors document TDP as the
  standard distribution denominator.
- Velocity (SPPD) = sales / points of distribution; the standard rate metric.

Modelling consequences. Scanner sales growth decomposes into distribution times
velocity. A demand model on scanner data without a distribution feature forces
velocity to absorb distribution moves, so every new-door expansion reads as organic
demand and the elasticity estimates rot. Carry %ACV (or TDP at brand grain) as a
feature and consider velocity as the target for anything price- or promo-related.

Two reconciliation traps. Household panel numbers and POS-projected numbers measure
different universes with different projection factors, so they disagree by
construction; pick one spine and use the other for shares only. The store universe
rebases periodically (new census of stores, revised ACV weights), which steps every
level series in the data; carry a universe-version column and let the model split
on it, or re-baseline levels at each rebase.

## ERP extracts (SAP, Oracle, NetSuite)

Date semantics. One order carries at least four dates: order entry (customer
intent), requested delivery, actual shipment, invoice (revenue recognition). Demand
models built on shipment or invoice dates learn the warehouse: stockouts read as demand
dips, batching reads as weekly seasonality, quarter-end invoice pushes read as
demand spikes. Forecast on order date; use requested-delivery for the timing the
customer wants; reserve invoice dates for finance reconciliation.

Backorders. A stockout accumulates orders that release the day stock arrives, so
delivery-dated series show a phantom spike carrying weeks of true demand. Flag
release days from the backorder table and either redistribute the units to their
order dates or add the flag as a feature; leaving the spike in teaches the model a
seasonality that does not exist.

Units of measure. The same material moves in eaches, cases, layers, and pallets,
with per-item conversion factors, and catch-weight items (meat, cheese) invoice by
actual weight against nominal case counts. Convert everything to one canonical UoM
through the item-UoM conversion table at extract time; a units column mixing eaches
and cases is unusable and looks plausible in every profile.

Fiscal calendars. 4-4-5 calendars build quarters of 4+4+5 weeks (13 weeks), and the
365.25-day year forces a 53rd week every 5 to 6 years. Consequences: fiscal months
have 28 or 35 days, so month-over-month comparisons on Gregorian months misalign
with the business's own reporting; year-over-year features must lag 52 fiscal weeks
through a fiscal calendar dimension, and the 53-week year breaks both lag-52-weeks
and lag-364-days for that year. Join a fiscal calendar table (fiscal year, quarter,
period, week) and build comparison features on it; add a week-53 indicator for the
years that have one.

## Sensor / SCADA / historian data

Compression semantics. Process historians (AVEVA/OSIsoft PI is the archetype) run
two filters: an exception deadband at the interface (a new value transmits only when
it moves past ExcDev from the last transmitted value) and swinging-door compression
in the archive (a point persists only when a line through the retained points can no
longer reconstruct the signal within CompDev). The archive is therefore a
piecewise-linear reconstruction envelope. Consequences: raw-point counts measure
signal activity plus the deadband setting; variance computed on archived points
understates true variance by up to the deadband; a perfect flatline can mean a
stable process, a stuck sensor, or a wide deadband. Read the per-tag ExcDev/CompDev
settings before interpreting any second-moment feature.

Resampling. Samples arrive irregularly, so fixed-bin features use time-weighted
means (each retained value weighted by the interval it spans), and every
multi-tag ratio aligns tags on a common clock first. Simple `resample().mean()`
over raw points weights bursts of activity and starves quiet periods.

Gap semantics. Missing has two opposite meanings. Report-by-exception: no new point
means the value held; forward-fill is the correct reconstruction. Comms or sensor
outage: no new point means unknown; forward-fill fabricates a flatline through the
outage. Separate the two with heartbeat tags, quality codes, or scan-status tags
before imputing anything, and add an `is_offline` feature so the model can discount
reconstructed stretches. Recalibrations step the level; detect them as change
points and add a since-recalibration distance for drift-sensitive equipment
(predictive-maintenance owns the failure-model side).

## Money over long histories

Deflation. A tree that splits on nominal price at $4.99 learns a boundary that
means a different thing in 2015 and 2025. Deflate prices and revenue to real terms
with CPI for consumer-facing data and the sector PPI for B2B, indexed to the latest
period so current values stay readable. Keep the nominal column too where price
points carry behavioural weight (99-endings, threshold pricing); the pair costs one
column and resolves the ambiguity.

FX. Convert at the transaction-date rate for anything additive (revenue, cost);
converting a year at one average rate hides within-year FX swings inside apparent
demand moves. For pure volume comparisons across countries, a fixed
planning rate removes FX noise deliberately; label the column with which it is.

## Clocks

Store UTC; compute behavioural features (hour-of-day, day-of-week) in site-local
time because demand follows local clocks; run every join between hourly sources in
UTC. DST transition days run 23 and 25 hours: spring-forward loses a local hour and
fall-back duplicates one, so a local-time join doubles the duplicated hour's weather
against one hour of load and a local-time daily sum shifts by an hour of volume on
two days a year. Energy practice keeps the UTC spine and either averages the
duplicated local hour or keys it with a DST flag. Daily aggregates need an explicit
day definition: local-time days for site demand, UTC days for anything joined
across venues or exchanges.
