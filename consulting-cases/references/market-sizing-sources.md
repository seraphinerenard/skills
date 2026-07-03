# The 2026 market-sizing data-source catalogue

Curated from the verified research sheet at
`research/market-sizing-data-sources.md`, which carries every URL with a
2026-07-12 access date plus the per-source caveats; this file is the working
summary. Free means no payment and no sales call.

## Government statistics, all free

| Source | What it sizes | Cadence | Trap to know |
|---|---|---|---|
| StatCan tables (Building Permits 34-10-0292, Retail Trade 20-10-0056, Manufacturing 16-10-0047, Business Counts) | Canadian construction, retail, manufacturing, firm counts by NAICS | Monthly; Business Counts semi-annual | Business Counts PIDs roll every release; search the table name, never hardcode the PID |
| US Census (County Business Patterns, Economic Census 2022, Building Permits Survey, ACS) | US establishments, revenue by detailed NAICS, permits to place level, demographics to block group | Annual/5-year/monthly | ARTS was absorbed into the Annual Integrated Economic Survey; cite AIES for 2024+ retail |
| BEA (GDP by industry, PCE detail, input-output use tables) | Industry value added, consumer spend by product, who-buys-from-whom | Quarterly/monthly/annual | The 402-industry benchmark IO table appears ~every 5 years |
| BLS (QCEW, CES, Consumer Expenditure, PPI) | Employment and wages to county x NAICS, household spend, producer prices | Quarterly/monthly/annual | CE had a collection gap Oct-Dec 2025 (appropriations lapse) |
| FRED | 800k+ series, one API | Continuous | Free key, 120 requests/min |
| Eurostat (Structural Business Statistics, PRODCOM) | EU firm counts, value added, product-level production | Annual | Country detail lags 1-2 years |

## Customs and trade

Free tier: UN Comtrade (HS6 country pairs, 500 calls/day on a free key),
USITC DataWeb (HTS-10 US imports, no account needed for queries), USA Trade
Online (state-level exports, redesigned 2026, no account), Canadian CIMT
(HS8/HS10 by province). Company-to-company visibility (shipper and consignee
names) exists only in the bill-of-lading vendors and only for disclosing
countries (the US discloses; most of the EU does not): ImportYeti (free
browsing, no export), ImportGenius (from roughly US$125-230/month, tier
pricing conflicts flagged in the sheet), S&P Panjiva (enterprise quote,
transactional coverage ~35% of global flows).

## Construction and infrastructure

Census Building Permits Survey (state/CBSA/county/place, units and
valuation, monthly), state DOT bid lettings (TxDOT, Caltrans, FDOT portals
verified live; engineer's estimate against actual bids), FHWA Highway
Statistics (annual since 1945), USGS Mineral Industry Surveys for cement and
aggregates (annual MCS 2026 current; monthly series paused mid-migration at
December 2025, so say so when citing), NRMCA ready-mixed production
(member-gated tables; headline figures free via its newsletter). Dodge
project-level data is enterprise-priced.

## Company-derived

SEC EDGAR full-text search (free, 2001-present, 10 req/s), SEDAR+ for
Canadian filings (free, documents from 2015), earnings-call transcripts free
at Motley Fool and Investing.com (Seeking Alpha is paywalled), trade
association headline series (WSTS semiconductors free monthly; AISI weekly
steel tonnage headline free; most association detail is member-gated with
the headline liberated through press releases).

## Alternative-data status, mid-2026

| Provider | Status | Access |
|---|---|---|
| Placer.ai | Independent | Research-grade access is paid; third-party estimates ~$5k-50k/yr, no published price |
| Advan / SafeGraph | Advan bought only SafeGraph's foot-traffic Patterns product (2022); SafeGraph still sells Places/POI | Both enterprise |
| Bloomberg Second Measure | Operating, Terminal or feed | Paid, card-panel spend data |
| Consumer Edge / Earnest | Merged April 2025 | Paid, card panels |
| Sensor Tower | Absorbed data.ai (2024) | Platform paid; annual State of Mobile report free |
| Lightcast | Job postings; powers Conference Board HWOL | Smallest tier ~$5k-12k/yr |
| Indeed Hiring Lab | Daily postings index and wage tracker | Fully free, CC BY 4.0 |

## Per-capita anchors, all free

USGS cement (series to 1900; per-capita figures are derived, so cite them as
"derived from USGS data"), USDA ERS Food Availability (200+ commodities,
supply-based, a demand proxy), EIA energy per capita (~279 MMBtu/person,
2023, national; state rankings via SEDS).

## Worked-example facts kept for reuse

US ready-mixed concrete: ~377M cubic yards produced in 2024 (NRMCA, ~5.7%
below 2023; 2025 estimate ~373M cy; 2005 peak ~459M cy; 2024 weighted
average price $179.89/cy). Concrete per single-family start: no single
authoritative figure exists; the defensible modelling range is 25-40 cy for
slab-on-grade rising to 50-75+ cy with basements and flatwork, so state the
midpoint as an assumption and sensitivity-test 25-75 cy, since foundation
type dominates the variance.
