<!-- Compiled 2026-07-12. -->

# Market-Sizing Data Sources for ML/Analytics Consulting — Verified 2026-07-12

All URLs were checked by live search or direct fetch on 2026-07-12. Items that could not be confirmed against a primary source are flagged inline and collected at the end.

---

## 1. Government Statistics

### Statistics Canada (all free, no login; CSV/HTML/API export)

Base pattern: `https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=<PID>`

| Product | Table | URL | Covers | Frequency |
|---|---|---|---|---|
| Building Permits Survey | 34-10-0292-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3410029201 | Permit value by structure type and work type, by province/CMA/CA | Monthly |
| Monthly Retail Trade Survey | 20-10-0056-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=2010005601 | Retail sales by NAICS, province, CMA | Monthly |
| Monthly Survey of Manufacturing | 16-10-0047-01 | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1610004701 | Manufacturers' sales/shipments, inventories, orders by NAICS | Monthly |
| CIMT (merchandise trade) | Web app (replaced cat. 65F0013X) | https://www5.statcan.gc.ca/cimt-cicm/home-accueil | Exports HS8 / imports HS10, by country and province; new web app launched ~Oct 2025 | Monthly (~35-day lag) |
| Canadian Business Counts | 33-10-1095-01 (Dec 2025 vintage) | https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3310109501 | Business location counts by NAICS, employee-size band, geography | Semi-annual (June, Dec) |

Warning on Business Counts: the table PID rolls forward with every semi-annual release (33-10-0764 for Dec 2024, 33-10-1014 for Jun 2025, 33-10-1095 for Dec 2025). Do not hardcode the PID; search "Canadian Business Counts" each vintage.

### US Census Bureau (all free; API at api.census.gov now requires a free key)

| Product | URL | Covers | Frequency |
|---|---|---|---|
| County Business Patterns | https://www.census.gov/programs-surveys/cbp.html | Establishments, employment, payroll by NAICS at county/MSA/ZIP | Annual (latest: 2023 data; 2024 expected summer 2026) |
| Economic Census | https://www.census.gov/programs-surveys/economic-census/year/2022/data.html | Firm counts, revenue, payroll by detailed NAICS down to place level | Every 5 years (2022 cycle release completed by Mar 2026) |
| Building Permits Survey | https://www.census.gov/construction/bps/index.html | See Section 3 for granularity | Monthly + annual |
| Annual Retail Trade Survey | https://www.census.gov/programs-surveys/arts.html | Retail sales, e-commerce, inventories by NAICS. **ARTS has been absorbed into the Annual Integrated Economic Survey (AIES)**; last standalone ARTS release covered 2022. Cite AIES for 2024+ | Annual (under AIES) |
| American Community Survey | https://www.census.gov/programs-surveys/acs.html | Income, occupation, industry, housing down to tract/block group | 1-yr and 5-yr (latest 5-yr: 2020-2024, released Jan 29, 2026) |

### BEA (free; API key free at https://apps.bea.gov/API/signup/)

| Product | URL | Covers | Frequency |
|---|---|---|---|
| GDP by Industry | https://www.bea.gov/data/gdp/gdp-industry | Value added and gross output by NAICS industry | Quarterly (Q1 2026 released Jun 25, 2026) |
| PCE by category | https://www.bea.gov/data/consumer-spending/main | Consumer spending by product type (Table 2.4.5U for detail) | Monthly |
| Input-Output Use tables | https://www.bea.gov/industry/input-output-accounts-data | Who buys what from whom; 71-industry summary annually, 402-industry benchmark ~every 5 years | Annual (late Sept); benchmark 5-yr |

### BLS (free; API free, registration raises limits)

| Product | URL | Covers | Frequency |
|---|---|---|---|
| QCEW | https://www.bls.gov/cew/ | Employment and wages covering >95% of US jobs, by county and detailed NAICS | Quarterly |
| CES | https://www.bls.gov/ces/ | Nonfarm payrolls, hours, earnings by industry, national/state/metro | Monthly |
| Consumer Expenditure Survey | https://www.bls.gov/cex/ | Household spending by category, income, demographics. Note: a collection gap ran Oct 1 to Dec 4, 2025 due to the appropriations lapse | Annual (2024 data released Dec 19, 2025) |
| PPI | https://www.bls.gov/ppi/ | Producer prices by industry and commodity | Monthly |

### Other

- **FRED** — https://fred.stlouisfed.org/ — 800,000+ series from 121 sources; free; API free (key required, 120 req/min). Homepage blocks automated retrieval (403 bot-detection), corroborated via the Federal Reserve Board's own reference page.
- **IRS SOI** — https://www.irs.gov/statistics/soi-tax-stats-statistics-of-income — business tax statistics by entity type and industry, plus ZIP-code-level individual income data (through tax year 2022). Free; annual with a multi-year lag; mostly Excel downloads.
- **Eurostat** — https://ec.europa.eu/eurostat/data/database — free. For market sizing the two key products are Structural Business Statistics (business counts, value added, employment at NACE 4-digit, annual) and PRODCOM (product-level production values/volumes). Country detail lags 1-2 years.

---

## 2. Trade / Customs Data

| Source | URL | Granularity | Free/Paid | Frequency |
|---|---|---|---|---|
| UN Comtrade | https://comtradeplus.un.org/ | HS 6-digit, country-pair aggregates; no company names | Free API key: 500 calls/day, 100k records/call. Premium (unlimited calls, 25M-record batches) is quote-based via shop.un.org / subscriptions@un.org; **no 2026 price confirmed** | Rolling; monthly for major economies, annual widest |
| USITC DataWeb | https://dataweb.usitc.gov/ | HTS up to 10-digit imports / 8-digit; no company names; 1989-present | Free. Login.gov account only for saved queries/API | Monthly, ~3 business days after Census trade release |
| USA Trade Online | https://usatradeonline.census.gov/ | HS/Schedule B and HTS, with state-level exports | Free. Redesigned "Reimagined" version launched 2026; no account needed any more | Monthly |
| Canada CIMT | https://www5.statcan.gc.ca/cimt-cicm/home-accueil | HS8 exports / HS10 imports, country and province | Free | Monthly |
| S&P Global Panjiva | https://panjiva.com/ (product page under spglobal.com Market Intelligence) | Bill-of-lading level: shipper + consignee names, HS codes; transactional data covers ~35% of global flows, aggregate "macro" data ~95% | Paid, enterprise quote only; zero public pricing. The Panjiva brand still exists as "Panjiva Supply Chain Intelligence" inside S&P Global Market Intelligence | Continuous ingestion |
| ImportGenius | https://www.importgenius.com/pricing | Bill-of-lading level, US maritime 2006-present plus 25+ countries on higher tiers | Paid. Entry tier ~$125-230/mo (page vs promo figures differ), Pro ~$449/mo, Global Enterprise from ~$1,999/mo | Continuous |
| ImportYeti | https://www.importyeti.com/ | US bill-of-lading (maritime only), company names (some redacted), back to 2015 | Free tier: unlimited browsing/search after signup; no export/API. Paid: Product Sourcing ~$50/mo annual, Sales Prospecting ~$130/mo, Enterprise from ~$1,000/mo, one-time 30-day pass ~$130 | Continuous |

Key structural point: the government sources give product-level aggregates only; company-to-company visibility (shipper-consignee) exists only in the bill-of-lading providers, and only for countries that disclose it (the US does; most of the EU does not).

---

## 3. Construction / Infrastructure

- **Census Building Permits Survey** — https://www.census.gov/construction/bps/index.html — free. Granularity: state, CBSA, county, and permit-issuing place; broken out by structure size (1, 2, 3-4, 5+ units) with both unit counts and valuation. Monthly (17th workday) plus annual (2025 annual released May 14, 2026).
- **Dodge Construction Network** — https://www.construction.com/ — paid, enterprise quote. Project-level intelligence: 700k+ projects tracked/year, planning-stage leads, county-level starts forecasts. A third-party site cites ~$300/user/month as a starting point; **unverified by Dodge**.
- **State DOT bid lettings** — public and free, confirmed live at three examples:
  - TxDOT bid tabulations dashboard: https://www.txdot.gov/business/road-bridge-maintenance/contract-letting/bid-tabulations-dashboard.html (24 months of lettings, engineer's estimate vs bids)
  - Caltrans bid results: https://dot.ca.gov/programs/procurement-and-contracts/bid-results (posted within 24h of openings)
  - FDOT bid letting portal: https://bidletting.fdot.gov/
- **FHWA Highway Statistics** — https://www.fhwa.dot.gov/policyinformation/statistics.cfm — free, annual since 1945; latest edition is Highway Statistics 2024. State-level fuel, VMT, registrations, highway finance.
- **USGS Mineral Industry Surveys (cement, crushed stone, sand and gravel)** — free, confirmed. Cement page: https://www.usgs.gov/centers/national-minerals-information-center/cement-statistics-and-information. Two products: monthly Mineral Industry Surveys (MIS) and annual Mineral Commodity Summaries (MCS 2026 is published: https://pubs.usgs.gov/periodicals/mcs2026/mcs2026-cement.pdf). **Caveat confirmed on the USGS page itself: monthly MIS posting is temporarily paused during a migration to ScienceBase; latest posted monthly data is December 2025.** The annual MCS 2026 is current and unaffected.
- **NRMCA production statistics** — https://www.nrmca.org/association-resources/production-statistics/ is **member-only** (password-protected page, verified by direct fetch). Headline monthly figures are released free through NRMCA's newsletter on naylornetwork.com (e.g. https://www.naylornetwork.com/nrc-nwl/articles/index-v5.asp?aid=893381&issueID=100442 gives April 2025 = 32.7M cy, Jan-May 2025 = 139M cy).

---

## 4. Company-Derived Sources

- **SEC EDGAR full-text search** — https://www.sec.gov/edgar/search/ (API: efts.sec.gov) — free, no key; full-text index starts 2001-05-04; continuous updates; rate limit 10 req/s. (SEC pages return 403 to automated retrieval; facts corroborated across three secondary sources quoting the SEC FAQ.)
- **SEDAR+** — https://www.sedarplus.ca — free public search of Canadian issuer filings; full documents from 2015-01-01, prospectuses back to 1997; migration from SEDAR completed 2023-07-25. (Direct fetch hit bot-detection; confirmed via CSA/OSC indexed content.)
- **Earnings-call transcripts, genuinely free in 2026:** Motley Fool (https://www.fool.com/earnings-call-transcripts/, archive to 2007, verified with July 2026 examples), Investing.com transcripts (no paywall), company IR pages/webcasts, the Quartr mobile app (free; the Quartr API is paid), Roic.ai API free tier (https://www.roic.ai/api/docs/earnings-calls, 2026 transcripts confirmed), and MarketBeat. **Paywalled:** Seeking Alpha (Premium, $299/yr list, June-July 2026 promo at $225/yr) and Financial Modeling Prep (transcripts gated to the Ultimate paid tier).
- **Trade association statistics, verified examples:**
  - WSTS (semiconductors): https://www.wsts.org/ — monthly global semiconductor revenue by region, free, current through May 2026. Note SEMI discontinued the monthly book-to-bill in Dec 2016; SEMI now publishes billings only, registration-gated.
  - AISI (steel): https://www.steel.org/industry-data/ — weekly raw steel tonnage and capacity utilization, free headline (week ending 2026-07-04: 1,856,000 net tons, 80.4%); monthly AIS 7 detail is subscription.
  - RVIA (RVs): https://www.rvia.org/reports-trends — monthly wholesale shipment headline free via press pages; full PDF is member-only.
  - Aluminum Association: https://www.aluminum.org/aluminum-statistics-portal — explicitly hybrid; monthly primary production and annual facts free, full archive member-only.
  - American Cement Association (formerly PCA): https://www.cement.org/intelligence-resources/market-intelligence/ — apparent cement use by market/state; mostly member/subscription with free sample tables and forecast summaries.

---

## 5. Alternative Data Proxies — 2026 Status

| Provider | 2026 status | Free/Paid | Contract notes |
|---|---|---|---|
| Placer.ai (https://www.placer.ai/) | Independent, VC-backed (Series D $75M, Jul 2024) | Freemium signup exists but Placer's own FAQ calls it a limited display; research-grade access is paid | Third-party estimates ~$5k-$30k+/yr, up to $50k+; **no vendor-published price** |
| Advan Research / SafeGraph | **Advan acquired only SafeGraph's Patterns (foot-traffic) business, Nov 3, 2022** (now "Advan Patterns Plus", per Advan's own press release). SafeGraph itself remains independent and sells Places/POI data (https://www.safegraph.com/). Advan's Nov 2024 acquisition was RetailStat's REI product; sources that say "Advan bought SafeGraph in 2024" conflate the deals | Both paid/enterprise | — |
| Orbital Insight | **Acquired by Privateer (Steve Wozniak's company), announced May 6, 2024** with a $56.5M Series A; not shut down. Its TerraScope platform continues under Privateer; orbitalinsight.com still resolves | Paid | Whether the customer-facing brand survives as "Orbital Insight" vs full Privateer branding is unconfirmed from 2026 primary sources |
| Bloomberg Second Measure (https://secondmeasure.com/) | Still operating as Second Measure LLC, a Bloomberg subsidiary (acquired Dec 2020); delivered via Terminal (ALTD/ECAN) or enterprise feed | Paid only | 20M+ US consumer panel, history to 2016/17; no public minimum |
| Earnest Analytics | **Acquired by Consumer Edge, completed Apr 28, 2025** (PR Newswire); brand remains live as "part of Consumer Edge" | Paid/enterprise | Card panels: Orion ~50M cards, Vela ~100M accounts; no public minimum |
| Consumer Edge (https://www.consumeredge.com/) | Independent, now parent of Earnest | Paid/enterprise | No public minimum |
| Sensor Tower / data.ai | **Sensor Tower acquired data.ai in March 2024**; data.ai brand retired ("Sensor Tower, formerly data.ai") | Platform paid, custom-quoted. Free: annual State of Mobile 2026 report (email-gated), https://sensortower.com/report/state-of-mobile-2026 | — |
| Lightcast (https://lightcast.io/) | Independent (Emsi + Burning Glass merger, rebranded 2022); powers the Conference Board HWOL index, publishing monthly through 2026 | Paid | Smallest published tier: Developer API $5k-$12k/yr by region size ($4k-$10k on 2-yr terms); platform pricing not public |
| Indeed Hiring Lab | Indeed's research arm (Recruit Holdings) | **Fully free**, CC BY 4.0 | Daily job-postings index and wage tracker: https://www.hiringlab.org/, https://data.indeed.com/, GitHub: https://github.com/hiring-lab/job_postings_tracker |

---

## 6. Per-Capita Consumption Anchors (all free government sources)

- **USGS cement**: https://www.usgs.gov/centers/national-minerals-information-center/cement-statistics-and-information plus Historical Statistics Data Series 140 (series back to 1900). USGS publishes consumption in tons; the commonly cited ~790 lb per capita (2023) is a third-party derivation (consumption divided by Census population), so cite it as "derived from USGS data."
- **USDA ERS Food Availability (Per Capita) Data System**: https://www.ers.usda.gov/data-products/food-availability-per-capita-data-system — 200+ commodities, plus Loss-Adjusted Food Availability. These are supply-based availability estimates, which serve as a demand proxy; the Nutrient Availability sub-series is stale (last updated 2010).
- **EIA energy per capita**: https://www.eia.gov/tools/faqs/faq.php?id=85&t=1 (national: ~279 MMBtu/person, 2023, EIA's own figure) and state rankings via SEDS at https://www.eia.gov/state/rankings/?sid=US.

---

## Worked-Example Facts: Ready-Mixed Concrete

### (a) US annual ready-mixed concrete production

**377 million cubic yards in 2024** (NRMCA estimate, about 5.7% below 2023), published free via NRMCA's newsletter "Ready Mixed Concrete Production Statistics Updated Through December 2024" (https://www.naylornetwork.com/nrc-nwl/articles/index-v5.asp?aid=870342&issueID=100418). The **2025 estimate is ~373 million cubic yards** (NRMCA figure as relayed by Concrete Financial Insights, https://concretefinancialinsights.com/us-concrete-industry-data, which also notes the 2005 peak of ~459M cy). Two independent NRMCA documents corroborate the 2024 level: the 2024 Quality Survey (59.6M cy = ~16% of US production implies ~373M) and the 2025 Quality Benchmark Report (52M cy = ~14% of 2024 production implies ~371M). NRMCA also reports a 2024 weighted-average price of $179.89/cy, which supports revenue sizing. A USGS cement back-calculation (100M metric tons 2025 shipments, ~70-75% to ready-mix, ~517 lb cement/cy) yields 270-290M cy, the same order of magnitude; treat it as a plausibility check only, since the mix-design and end-use-share assumptions are rough.

### (b) Concrete per single-family housing start

**No single authoritative NAHB/PCA headline figure exists; the defensible planning range is roughly 25-40 cubic yards for a slab-on-grade foundation (slab plus footings), rising toward 50-75+ cy for homes with basements, garages, and driveways.** Basis: a typical 1,500-2,000 sq ft slab at 4-6 in thickness computes to ~23-37 cy using standard industry conversion (1.23 cy per 100 sq ft at 4 in, 1.85 at 6 in; Concrete Network calculator, https://www.concretenetwork.com/concrete/howmuch/calculator.htm, and concretecalculate.com); footings add ~8-12 cy. As an upper anchor, the widely quoted industry figure that an average new US single-family house uses about 20 tons of cement (cited in Gabelli's global cement industry research, https://gabelli.com/research/global-cement-industry/) implies ~75 cy of concrete-equivalent at ~517 lb cement/cy, covering all concrete on the lot. NAHB's Cost of Constructing a Home 2024 study (https://www.nahb.org/news-and-economics/housing-economics-plus/special-studies/special-studies-pages/cost-of-constructing-a-home-in-2024) gives foundation as ~10% of construction cost but no physical quantity. For a market-sizing model, state the assumption explicitly (e.g. 40 cy per start as a midpoint) and sensitivity-testing 25-75 cy, since foundation type (slab vs basement) dominates the variance; NAHB's own data shows the slab share of new homes has been rising (https://www.nahb.org/blog/2024/07/share-homes-built-on-slabs-surges).

---

## Unverified Items (flagged)

1. UN Comtrade premium pricing: no 2026 dollar figure found; the shop.un.org listing 404'd.
2. Panjiva pricing: quote-only, zero public figures; any dollar estimate would be speculation.
3. ImportGenius entry tier: sources conflict ($125 vs $229/mo), likely annual-vs-monthly billing; confirm before quoting.
4. Dodge pricing (~$300/user/mo) and Placer.ai minimums ($5k-$50k/yr): third-party estimates only.
5. Bloomberg Second Measure, Consumer Edge, and Earnest contract minimums: not disclosed anywhere.
6. Orbital Insight's surviving brand name under Privateer: acquisition confirmed, current customer-facing branding not pinned to a 2026 primary source.
7. USGS monthly MIS pause: confirmed on the cement page; the identical notice on the aggregates pages is inferred from the shared platform migration, not checked page-by-page.
8. Per-home concrete volume: synthesized from calculator/industry sources; no single named association statistic exists, so it must be presented as a stated modelling assumption.
9. Several official sites (SEC, SEDAR+, BLS QCEW, FRED, comtradeplus.un.org) block automated retrieval with 403s; facts for those were cross-confirmed through at least two independent secondary sources each.
10. NADA Data pricing, A4A access terms, SEMI billings-report gating, and ACC dataset tiers could not be pinned down beyond search-snippet text.
