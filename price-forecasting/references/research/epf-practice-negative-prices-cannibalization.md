<!-- Compiled 2026-07-12. -->

---

# Electricity Price Forecasting: Industry Practice, Negative Prices/Spikes, and Cannibalization

Compiled 2026-07-12. Every figure carries its source URL and a note. Items that could not be verified are flagged explicitly.

---

## TOPIC A — What practitioners actually deploy

### The two paradigms, and how they are combined

Practitioner EPF splits into **fundamental (structural) models** and **statistical/ML models**, and the current state of the art is a hybrid of the two.

- **Fundamental / merit-order / supply-stack models** simulate the market clearing physically. They rank generators by marginal cost (the "merit order" / supply stack), meet demand from cheapest to most expensive, and the **most expensive plant dispatched sets the price for everyone (the marginal unit)**. The key input is **residual load** = demand minus wind/solar generation; the marginal technology on the residual-load stack sets the price. Source: arXiv review "A data-driven merit order" and the merit-order-curve forecasting literature. https://arxiv.org/abs/2501.02963 and https://arxiv.org/abs/2512.17758 — both describe residual load feeding a supply stack, and note curve-based methods beat price-based ones by ~5% on average and up to ~10% in midday hours when renewables depress prices.
- **How gas sets the marginal price (Europe):** In 2022 gas-fired plants had higher marginal cost than coal, so they were frequently the price-setting unit. EWI (University of Cologne) states plainly: "the most expensive power plant required to meet demand in each hour determines the price for all market participants," and "gas-fired power plants were often price-setting in the 2022 day-ahead market." The clean-spark-spread logic: power price ≈ (gas price / plant efficiency) + (CO2 price × emission factor) + variable O&M. https://www.ewi.uni-koeln.de/en/news/mo-tool-2022-update/
- **Statistical/ML models** learn patterns from history (regressions, gradient boosting, deep learning). A 2026 deep-learning EPF review covers day-ahead, intraday, and balancing markets. https://arxiv.org/html/2602.10071
- **Hybrid is now standard.** Montel's practitioner note: fundamentals "establish market logic while ML corrects residual errors and captures non-linear effects such as renewables forecast bias"; typical inputs are weather, generation outages, carbon and fuel prices, interconnector flows, and demand; validation via time-series CV, MAE/RMSE/MAPE, SHAP explainability. https://montel.energy/resources/blog/forecasting-power-prices-combining-fundamentals-and-machine-learning

### How ISOs form prices (US nodal markets)

- **LMP (Locational Marginal Price)** is the dual variable (shadow price) on each node's power-balance constraint in a **Security-Constrained Economic Dispatch (SCED)** optimization. LMP = energy component + congestion component + losses. Day-ahead prices come from **Security-Constrained Unit Commitment (SCUC)** plus dispatch, a least-cost optimization over supply offers, demand bids, and network constraints (DC-OPF). Sources: ISO-NE FAQ https://www.iso-ne.com/participate/support/faq/lmp ; PCI explainer https://www.pcienergysolutions.com/2022/03/02/how-locational-marginal-pricing-markets-work/ ; MISO SCUC/SCED reference https://home.engineering.iastate.edu/~jdm/ee553/MISO1-2009.pdf

### How EU day-ahead prices form (market coupling)

- The **Single Day-Ahead Coupling (SDAC)** clears all coupled European bidding zones with one algorithm, **EUPHEMIA** (Pan-European Hybrid Electricity Market Integration Algorithm), run by the NEMOs (EPEX SPOT, Nord Pool, OMIE, GME, etc.) under the PCR project. It maximizes social welfare and implicitly allocates cross-border capacity. Note: SDAC moved to **15-minute market time units on 30 September 2025** (delivery day 1 Oct 2025). Sources: ENTSO-E SDAC https://www.entsoe.eu/network_codes/cacm/implementation/sdac/ ; EUPHEMIA public description https://www.nemo-committee.eu/assets/files/euphemia-public-description.pdf

### Commercial EPF vendors and what each does

| Vendor | Approach to price forecasting | Source |
|---|---|---|
| **Aurora Energy Research** | Fundamental production-cost/dispatch models (ORIGIN for scenarios); transmission-constrained chronological dispatch on hourly demand + individual resource characteristics; models extreme price events (>$1,000 or <−$100/MWh) via statistical overlays on the fundamental run | https://auroraer.com/products/power-renewables ; https://auroraer.com/software/origin |
| **Montel / EnAppSys** | EnAppSys uses a multi-spatial equilibrium model predicting spot prices + power flows up to 45 days out across ~32 European countries; Montel's "Multi-Model Day-Ahead" blends Montel AI, Energy Quantified, and SysPower across 18 markets | https://montel.energy/products/analytics/multi-model-forecast ; https://montel.energy/platforms/enappsys |
| **Volue (ex-Wattsight/Markedskraft), "Insight by Volue"** | Weather-driven fundamentals + AI; hourly and 15-min resolution for day-ahead and intraday; multi-weather ensemble (ECMWF, Jua AI-weather, GFS, ICON, ERA5); pan-European + Japan | https://www.volue.com/energy-market-data-and-forecasts |
| **Energy Exemplar (PLEXOS)** | Production-cost optimization; day-ahead clearing to long-term; bid formation options from cost-based SRMC to game-theoretic/heuristic bidding; models each generator's marginal cost, maintenance, emissions | https://www.energyexemplar.com/price-forecasting |
| **Amperon** | ML-first: hybrid of regression + gradient-boosted models for load, price, and renewables; claims up to 3x accuracy; 15-day short-term price forecasts, plus a new tool to 7 months ahead | https://www.amperon.co/newsroom/amperon-launches-ai-powered-price-forecasting ; https://www.amperon.co/blog/why-a-hybrid-regression-ml-approach-outperforms-in-energy-forecasting |
| **Enverus** | Long-term zonal via fundamentals-based hourly production-cost model; nodal via ML (demand, transmission, renewables); short-term P&R for grid-constraint/congestion (PJM, ERCOT) | https://www.enverus.com/products/long-term-power-market-forecasting/ |
| **LSEG / Refinitiv** | Morning spot-price forecasts before market open with analyst commentary; hourly generation forecasts (renewable + conventional) and price forecasts to 2030; OTC price assessments for UK/DE/FR/NL/PL/CZ/HU | https://www.lseg.com/en/data-analytics/financial-data/commodities-data/energy-data/power-data |
| **ICIS** | 14-day European price/supply/demand forecasts from 2M+ data points, updated 6x daily on outages+weather; long-term to 2050; German power forecast distributed on the Bloomberg Terminal | https://www.icis.com/explore/commodities/energy/power/ ; https://www.icis.com/explore/press-releases/icis-power-forecast-on-bloomberg-terminal/ |
| **Kayrros** | Satellite geoanalytics (20+ constellations) for ground-truth supply intelligence (e.g. tracking every US utility-scale battery, claimed 95% accuracy); US Power Intelligence / ERCOT monitor. Acquired by Energy Aspects (closed ~21 May 2026) | https://services.kayrros.com/en/ercot-impact-monitor ; https://www.kayrros.com/press_release/energy-aspects-completes-acquisition-of-kayrros/ |
| **Pexapark** | Focused on PPA valuation and **capture prices** for renewables (see Topic C); publishes solar/wind capture-factor tracking and PPA price/volume data | https://pexapark.com/blog/european-solar-capture-factors-collapse-as-april-oversupply-triggers-wave-of-negative-prices/ |

Note: Montel/EnAppSys and Energy Exemplar/Aurora are both offered under overlapping ownership webs now (Energy Exemplar resells an "Aurora" forecasting product name that is distinct from Aurora Energy Research — a naming collision worth flagging).

---

## TOPIC B — Negative prices and spikes (with hard numbers)

### Germany, EPEX day-ahead negative-price HOURS per year (authoritative, Bundesnetzagentur/SMARD)

| Year | Negative hours | Note / source |
|---|---|---|
| 2015 | 126 | SMARD https://www.smard.de/page/en/topic-article/5892/15618 |
| 2016 | 97 | same (min price −€130.09/MWh) |
| 2017 | 146 | same |
| 2018 | 134 | same |
| 2019 | 211 | same |
| 2020 | 298 | COVID low demand + high renewables. https://www.pv-magazine.com/2025/01/06/germany-records-457-hours-of-negative-electricity-prices-in-2024/ |
| 2021 | 139 | gas-crisis high price level suppressed negatives. (same pv-magazine / Montel) |
| 2022 | 69 | gas-crisis peak year. FfE https://www.ffe.de/en/publications/german-electricity-prices-on-epex-spot-2024/ |
| 2023 | 301 | FfE (as above) and Bundesnetzagentur |
| 2024 | **457** (official BNetzA) / **459** (FfE) | BNetzA 2025 release https://www.bundesnetzagentur.de/SharedDocs/Pressemitteilungen/EN/2026/20260104_SMARD.html ; FfE cites 459 — minor methodology gap, both ≈457-459 |
| 2025 | **573** (out of 8,760 h) | BNetzA official (above); FfE said "almost 575" https://www.ffe.de/en/publications/german-electricity-prices-on-the-epex-spot-exchange-in-2025/ |

Supporting detail:
- **2024:** of the 457-459 negative hours, >92% fell under the "3-hour rule" (EEG market premium set to zero after 3+ consecutive negative hours; threshold drops to 2 hours in 2026 and 1 hour in 2027). Max 2024 day-ahead price €936/MWh (Nov-Dec dark doldrums); min −€135.45/MWh. https://www.ffe.de/en/publications/german-electricity-prices-on-epex-spot-2024/
- **2025 intra-year path:** H1 2025 = 389 negative hours (May alone 162 h, June 141 h); 453 h year-to-date by 26 Aug; 573 h full year. Record low ≈ −€250/MWh on 11 May 2025. https://www.pv-magazine.com/2025/06/30/germanys-day-ahead-market-posts-389-hours-of-negative-prices-in-h1/ ; https://www.pv-magazine.com/2025/08/26/germany-records-453-hours-of-year-to-date-negative-electricity-prices/
- **2025 averages (BNetzA):** day-ahead base €89.32/MWh, +13.8% vs €78.51/MWh in 2024; renewables 58.8% of generation; prices >€300/MWh in only 40 h (vs 41 h in 2024). (BNetzA 2025 release, above.)

### ERCOT (Texas) — negative prices, West/Panhandle, curtailment

- **2024 real-time prices fell ~46% YoY** (day-ahead ~−49%) on mild weather, flat demand, and solar+storage growth. By end-2024 >29 GW solar and >10 GW storage installed. https://modoenergy.com/research/en/ercot-power-prices-2024-energy-arbitrage-ancillary-services-hub-load-zone-west-north-south-houston-panhandle
- **Curtailment 2024: ERCOT curtailed over 8 TWh of wind + solar**; 22% of all renewable curtailment was driven by the **West Texas Export constraint**. West Texas solar is regularly curtailed midday because local demand is far below generation. https://modoenergy.com/research/en/ercot-curtailment-crisis-solar-wind-data-battery-colocated-trends-maps-texas
- The **West zone had the highest number of intervals with negative prices and the greatest frequency of price spikes** of any load zone; the Panhandle also runs frequently negative from wind oversupply + transmission limits (Potomac Economics 2024 State of the Market for ERCOT). https://www.potomaceconomics.com/wp-content/uploads/2025/06/2024-State-of-the-Market-Report.pdf
- **FLAG (unverified):** no single authoritative *count/percentage* of negative real-time hours could be confirmed system-wide or for West/Panhandle in 2024 — the ERCOT IMM report states West "highest number of negative-price intervals" qualitatively without giving the exact number. Treat the ERCOT negative-price *hour count* as not yet confirmed; the curtailment (>8 TWh) and directional facts are confirmed.

### CAISO (California) — negative prices, curtailment, duck curve

- **Negative-price hours (SP15, Southern California hub): ~1,180 hours in 2024 (~13% of all hours), up from ~530 hours in 2023 (~6%).** Median negative price ~−$17 in 2024 vs ~−$10 in 2023. https://resurety.com/article-negative-prices-in-caiso/
- **Curtailment 2024: 3.4 million MWh (3.4 TWh) of utility-scale wind+solar curtailed, +29% vs 2023; solar = 93% of curtailed energy**, concentrated in spring. EIA. https://www.eia.gov/todayinenergy/detail.php?id=65364 ; https://www.utilitydive.com/news/solar-wind-curtailments-increasing-california-caiso/749420/
- **Duck curve:** average midday (9am-3pm) net demand fell ~45% from 2020 to 2024; utility-scale solar +~8 GW 2020-2024; battery capacity rose from ~4 GW (Dec 2022) to >11 GW (Jun 2024), and on peak 2024 days storage supplied ~15% of capacity (up from 2% in 2022). https://www.ascendanalytics.com/blog/caiso-market-outlook-persistent-negative-energy-prices-spreading-curtailment

### Spikes and scarcity: the 2021-2022 gas crisis peaks

- **Germany day-ahead:** peaked at **€850/MWh (absolute)** in Aug 2022; weekly average €586/MWh (week 34, late Aug 2022); Jan-Oct 2022 average €240/MWh (EWI). A widely-cited daily figure is **€699.4/MWh on 26 Aug 2022**. https://www.ewi.uni-koeln.de/en/news/mo-tool-2022-update/ ; https://gmk.center/en/news/electricity-prices-in-germany-have-risen-to-a-record-e700/
- **France day-ahead spot** peaked at **€743.84/MWh on 30 Aug 2022**; the French **year-ahead future exceeded €1,100/MWh** (that four-figure number was the forward contract, not spot — French nuclear fleet corrosion outages drove it). https://www.france24.com/en/economy/20220826-europe-s-electricity-prices-hit-record-high-as-supply-cuts-begin-to-bite
- **Driver:** gas hit >€200/MWh-thermal; the marginal gas plant set clearing prices for all producers, giving coal/nuclear large infra-marginal margins (EWI, above).
- **FLAG:** German day-ahead *hourly* peaks in Aug 2022 were higher than the €699.4 daily figure; the confirmed absolute peak is €850/MWh (EWI). Some trade press cites individual hours above €870/MWh; no precise hourly maximum is confirmed.

---

## TOPIC C — Renewables cannibalization of capture prices

### Precise definitions

- **Capture price** (a.k.a. captured price, achieved price): the **generation-weighted average wholesale price** a technology actually earns = Σ(price_h × generation_h) / Σ(generation_h) over all hours h.
- **Capture rate = capture factor = value factor = market value factor**: capture price divided by the **time-weighted average (baseload) price**. Lion Hirth's canonical definition: "the ratio of the [generation]-weighted average wholesale price and its time-weighted average (base price)" = market value / base price. A capture rate of 1.0 (100%) means the technology earns exactly the average price; below 1.0 means it produces disproportionately in low-price hours (cannibalization). https://neon.energy/Hirth-2013-Market-Value-Renewables-Solar-Wind-Power-Variability-Price.pdf

### Foundational cannibalization findings (academic)

- **Hirth (2013), "The Market Value of Variable Renewables":** solar value factor falls from ~1.3 at low penetration to ~0.6 at 15% market share; wind falls from ~110% of average price at zero penetration to 50-75% at 30% penetration. https://neon.energy/Hirth-2013-Market-Value-Renewables-Solar-Wind-Power-Variability-Price.pdf
- **López Prol, Steininger & Zilberman (2020), "The cannibalization effect of wind and solar in the California wholesale electricity market," Energy Economics vol. 85:** using CAISO day-ahead data Jan 2013-Jun 2017, they confirm both absolute (unit revenue) and relative (value factor) cannibalization for solar and wind, stronger at low consumption and high penetration; cross-effect is asymmetric — wind penetration lowers solar's value factor, while solar penetration *raises* wind's value factor at high penetration/low load. https://www.sciencedirect.com/science/article/pii/S0140988319303470
  - **FLAG:** the exact regression coefficients (value-factor decline per percentage-point of penetration) sit behind the ScienceDirect paywall, so the precise per-point elasticity is not extractable. The qualitative findings above are confirmed from the abstract.

### Germany — solar capture rate decline (concrete)

- **Annual/monthly capture factors (Pexapark):** German solar capture factor ~**0.77 in March 2024 → 0.53 in March 2025 (−24% YoY)**; the April monthly figure fell further to **~0.40 (April 2025) → ~0.26 (April 2026)** as negative-price hours rose from 75 to 123 (April). Note these April figures are a low-season monthly trough, not the annual capture rate. https://www.pv-magazine.com/2026/05/13/solar-capture-factors-fall-across-europe-as-negative-price-hours-surge-in-key-markets/ ; https://pexapark.com/blog/european-solar-capture-factors-collapse-as-april-oversupply-triggers-wave-of-negative-prices/
- **Absolute capture price (S&P Global, full-year 2024):** German solar volume-weighted capture price **€54.64/MWh, −31% YoY**. Source (headline confirmed via search; the page itself returns 403 to automated retrieval): https://www.spglobal.com/energy/en/news-research/latest-news/electric-power/013125-deflating-capture-prices-pull-solar-wind-market-values-down-across-europe-in-2024
- Driver: ~17 GW new German solar added in 2024; solar generation rose from 4.5 TWh (Mar 2024) to 6.6 TWh (Mar 2025). Solar PPA offtake volumes collapsed ~84% YoY as cannibalization widened the buyer-seller price gap (Pexapark). https://balkangreenenergynews.com/pexapark-ppa-activity-in-europe-drops-in-first-half-of-2025/

### Spain — solar capture rate decline (concrete)

- **Record low monthly capture rate ~40% in April 2024**; Pexapark April monthly factors then ~0.30 (Apr 2025) → ~0.28 (Apr 2026), and a startling February collapse from ~0.71 (Feb 2025, 0 negative hours) to ~0.18 (Feb 2026, 148 negative hours). https://pexapark.com/blog/european-solar-capture-factors-collapse-as-april-oversupply-triggers-wave-of-negative-prices/
- **Absolute capture price (S&P Global, full-year 2024):** Spanish solar volume-weighted capture price **€45.56/MWh, −40% YoY** (steepest among major EU markets). Same S&P URL as above.
- Spain saw negative/very-low prices ~22% of the time in 2024; ~10 GW solar added since Jan 2023 (+55% capacity in 18 months). One 2025 estimate: Spanish solar captured only ~54% of the average price. https://www.leveltenenergy.com/post/spain-solar-cannibalization (the 54% figure is approximate/annual — flag as a secondary estimate).

### California / CAISO — solar capture value decline (concrete)

- **LBNL "Utility-Scale Solar" (Berkeley Lab):** solar's average market value was lowest in **CAISO at $27/MWh in 2023** (the market with the highest solar share); the US national-average solar market value fell to **$32/MWh in 2024** as energy prices fell. (The exec-summary PDF returns 403 to automated retrieval; figures confirmed via search of LBNL materials.) https://emp.lbl.gov/publications/utility-scale-solar-2024-edition
- **SP15 annual solar capture rate fell below 30% in 2024** as negative prices proliferated. https://resurety.com/article-negative-prices-in-caiso/

### Wind (for context)

- European wind capture prices also fell in 2024 (S&P Global "deflating capture prices pull solar, wind market values down across Europe in 2024," same URL). Wind cannibalizes less steeply than solar because wind output is less time-concentrated (Hirth: wind 110%→50-75% at 30% penetration vs solar 1.3→0.6 at just 15%). Cross-border cannibalization is now measurable: Enervis and a 2025 Energy Economics paper document wind/solar in one country depressing capture prices in interconnected neighbours. https://www.pv-magazine.com/2025/02/28/solar-growth-drives-cross-border-cannibalization-in-europe-says-enervis/

---

## Summary of flagged / unconfirmed items

1. **ERCOT negative-price hour count/percentage (2024):** not confirmed with a single authoritative number. Confirmed: >8 TWh curtailment, 22% of curtailment from West Texas Export constraint, West zone highest negative-price interval count (qualitative, Potomac Economics IMM).
2. **Prol/Steininger/Zilberman (2020) exact coefficients:** paywalled; only qualitative findings confirmed. Hirth (2013) supplies concrete value-factor numbers instead.
3. **Germany 2024 negative-hour count:** 457 (official Bundesnetzagentur/SMARD) vs 459 (FfE) — a minor methodology gap.
4. **German 2022 day-ahead hourly peak:** confirmed absolute peak €850/MWh (EWI) and daily €699.4 (26 Aug 2022); a precise single-hour maximum above that is not confirmed.
5. **Spanish 2025 solar capture ~54%:** secondary/annual estimate (LevelTen), less authoritative than the S&P full-year 2024 absolute price (€45.56/MWh).
6. **Pexapark April capture factors** are single-month troughs (April/February are the worst months); do not read them as annual capture rates, which run higher.

All other figures (German negative-hour series 2015-2025, CAISO 1,180/530 hours and 3.4 TWh curtailment, crisis peaks, S&P 2024 capture prices, LBNL solar values, Hirth definitions) are directly sourced and quoted above.
