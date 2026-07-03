<!-- Compiled 2026-07-12. -->

Every number carries its source URL, the as-of date of the figure, and an access date of 2026-07-12. Conflicting sources and paywalled values are flagged.

---

# Current valuation reference values (verified 2026-07-12)

## 1. Equity risk premium in current use

**Aswath Damodaran — implied ERP.** At the January 1, 2026 anchor he computed an expected return on stocks of 8.41% against an S&P 500 level of 6,845.5. Measured against the 10-year T-bond rate of 4.18%, the implied ERP was **4.23%**; measured against his default-free dollar risk-free rate of 3.95% (the T-bond stripped of the 0.23% US default spread), the same premium reads **4.46%** as the "US ERP" he uses for country build-ups. As of Jan 5, 2026 the US carried a Moody's Aa1 rating, so his US ERP (4.46%) sits 0.23% above the mature-market ERP (4.23%).
- Source (primary): https://aswathdamodaran.substack.com/p/data-update-2-for-2026-a-testing — as-of Jan 1, 2026; accessed 2026-07-12.
- Country framing: https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html — as-of Jan 5, 2026; accessed 2026-07-12.

His **July 2026 mid-year update** pulled premiums down slightly: mature-market ERP **4.17%**, US ERP **4.45%**, with an equity-volatility multiplier of 1.5545 across 157 country entries.
- Source: https://www.linkedin.com/pulse/equity-risk-premiums-country-july-2026-update-aswath-damodaran-zti8c — as-of July 1, 2026; accessed 2026-07-12.
- Flag: his `histimpl.html` page returned 4.33% / 4.58% for Jan 2026 via automated retrieval, which conflicts with the 4.23% / 4.18% he states in prose. The substack prose figure is authoritative here, and the page-parse discrepancy is noted.

**Kroll — recommended US ERP and normalized risk-free rate.** Kroll cut its recommended US ERP from 5.5% to **5.0%** effective September 2, 2025, and reaffirmed 5.0% at that date. It recommends the **higher of a 3.5% normalized US risk-free rate or the spot 20-year Treasury yield**. Because the 20-year sits at ~5.07% today (section 2), the spot yield currently governs, so Kroll's effective USD risk-free input is ~5.07% and an average-risk (beta = 1) cost of equity lands near 10.1%.
- Sources: https://www.kroll.com/en/reports/cost-of-capital/recommended-us-equity-risk-premium-and-corresponding-risk-free-rates and https://www.bvresources.com/articles/bvwire/kroll-lowers-recommended-us-erp-to-50 — last change Sep 2, 2025; accessed 2026-07-12. 2025 path: raised 5.0%→5.5% on April 15, 2025, then back to 5.0% on Sep 2, 2025.

**KPMG (DACH Cost of Capital Study 2025).** Average applied WACC **8.5%** (up from 8.2% prior year), average market risk premium held at **6.7%**, average risk-free rate stable at **2.5%**. Applied WACCs ranged 5.2% to 10.4%.
- Source: https://kpmg.com/ch/en/insights/deals/cost-capital-study.html (study PDF too large to fetch directly; figures via search of KPMG's own summary) — reporting period to mid-2025; accessed 2026-07-12.

---

## 2. Risk-free rate environment (July 2026)

| Instrument | Level | As-of |
|---|---|---|
| US 10-year Treasury | ~4.54%–4.56% | July 10, 2026 |
| US 20-year Treasury | 5.07% | July 10, 2026 |
| Government of Canada 10-year | ~3.44% (touched 3.55%, highest since May 2026) | July 2026 |

- US 10-yr: https://tradingeconomics.com/united-states/government-bond-yield and https://www.etftrends.com/fixed-income-content-hub/treasury-yields-snapshot-july-10-2026/ — accessed 2026-07-12.
- US 20-yr: https://tradingeconomics.com/united-states/20-year-bond-yield — accessed 2026-07-12.
- GoC 10-yr: https://tradingeconomics.com/canada/government-bond-yield — accessed 2026-07-12.
- Note: US 10-yr rose since Damodaran's Jan 1 anchor of 4.18%; the curve is upward-sloping with the 20-yr ~50bps over the 10-yr.

---

## 3. WACC ranges by sector

**Damodaran cost of capital by industry (US), data as of January 2026.** https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/wacc.html — accessed 2026-07-12.

| Sector | Cost of equity | WACC |
|---|---|---|
| Software (System & Application) | 9.64% | 9.34% |
| Software (Internet) | 11.48% | 10.66% |
| Semiconductor | 10.72% | 10.55% |
| Food Processing (staples) | 6.66% | 5.79% |
| Household Products (staples) | 7.59% | 7.03% |
| Machinery (industrials) | 8.25% | 7.70% |
| Utility (General) | 5.02% | 4.36% |
| Utility (Water) | 5.79% | 4.93% |
| Healthcare Products | 8.00% | 7.54% |
| Healthcare Info & Tech | 8.89% | 8.22% |
| Retail (General) | 7.54% | 7.27% |
| Oil/Gas (Production & Exploration) | 7.17% | 6.25% |
| Oil/Gas (Integrated) | 5.29% | 5.07% |

These run low because Damodaran's January build used a mature ERP near 4.2% and a modest cost of debt; utilities and integrated energy sit near 4-5%, software and semis near 9-11%.

**KPMG Cost of Capital Study 2025 (DACH) sector WACCs.** Highest averages: Industrial Manufacturing 9.4%, Technology 9.4%, Automotive 9.0%. Lowest: Energy & Natural Resources 6.3%, Real Estate 7.0%. Overall average 8.5%, range 5.2%–10.4%.
- Source: https://kpmg.com/ch/en/insights/deals/cost-capital-study.html — reporting period to mid-2025; accessed 2026-07-12.
- The gap between KPMG (~8.5% average, MRP 6.7%, rf 2.5%, euro-based) and Damodaran (lower WACCs, USD, mature ERP ~4.2%) is a methodology and currency difference worth stating in any comps memo.

---

## 4. Multiples

**Trading EV/EBITDA by sector — Damodaran, data as of January 2026 (positive-EBITDA firms).** https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/vebitda.html — accessed 2026-07-12.

| Sector | EV/EBITDA |
|---|---|
| Software (System & Application) | 24.48 |
| Software (Internet) | 30.26 |
| Semiconductor | 34.75 |
| Food Processing | 10.01 |
| Household Products | 13.17 |
| Machinery | 16.22 |
| Utility (General) | 13.73 |
| Healthcare Products | 19.78 |
| Retail (General) | 17.38 |
| Oil/Gas (Production & Exploration) | 5.15 |
| Total Market | 19.73 |

**M&A transaction multiple medians.** Bain's 2026 M&A Report puts strategic-M&A valuations at a median **11.6x EV/EBITDA** for 2025 (flat year-over-year); at mid-2026 the global median was ~10.7x on a trailing basis, the highest since 2021. PE-led deals paid ~12.6x versus ~9.8x for corporate buyers.
- Sources: https://www.bain.com/insights/looking-back-m-and-a-report-2026/ and https://www.bain.com/insights/private-equity-midyear-report-2026/ — 2025 full-year and mid-2026; accessed 2026-07-12.
- PitchBook: US PE buyout medians near **12x** ("the new norm"); $1B+ buyouts reached 15.5x in 2024 versus 12.8x for sub-$1B deals; North American middle market ~9.6x (TTM to Q1 2025). https://pitchbook.com/news/articles/median-us-pe-buyout-multiples-of-12x-may-be-the-new-norm — accessed 2026-07-12.

**Software/SaaS EV/Revenue.** The universe you pick drives the number:
- Broad public software median EV/NTM revenue **~2.3x** (July 12, 2026). https://multiples.vc/insights/software-saas-valuation-multiples
- SaaS Capital Index median **~3.2x–4.8x ARR** in June 2026 (a June low described as the weakest reading since 2011, with a partial rebound toward 4.8x). https://www.saas-capital.com/the-saas-capital-index/ (exact live figure is image-gated; range from secondary trackers) and https://saasvaluationmultiple.com/public-saas-multiples
- Bessemer/BVP Emerging Cloud Index median **~6.1x** revenue (June 26, 2026). https://cloudindex.bvp.com/ and https://saasvaluationmultiple.com/cloud-index
- Versus the 2021 peak: the SaaS Capital Index peaked at **16.9x** (August 2021), so current levels represent roughly a 70-80% compression. A source flags an early-2026 AI-driven software repricing (large cloud market-cap drawdown), which explains multiples sitting below the post-2022 trough for some indices.
- All accessed 2026-07-12.

---

## 5. Other reference values

**Size premium (Kroll CRSP decile).** The concept remains in active use and Kroll still publishes CRSP decile size premia in its Cost of Capital Navigator for build-up and modified-CAPM work. A 2025 study (Crain, ASA conference) cautions against subdividing decile 10 into micro-cap slices, since the smallest listed firms are often "small for a reason." Historical CRSP decile-10 (smallest) premia run in the ~5%+ range, with micro-cap composites lower; exact current values are subscription-gated behind the Navigator, so the precise 2025/2026 figures are unverified.
- Sources: https://www.bvresources.com/products/faqs/cost-of-capital-professional and https://www.hectelion.com/en-us/publications/size-premium-wacc-and-business-valuation — accessed 2026-07-12.
- Flag: exact current decile premia not verifiable without a paid Kroll subscription.

**Control premium.** US public-company acquisitions in 2024 carried a median control premium of ~**28%** (10-year median 27%) per FactSet/BVR; technology deals ran lower at a ~**17%** median in 2024 (10-year tech median ~29-30%).
- Source: https://www.bvresources.com/products/factset-bvr-control-premium-study — 2024 data; accessed 2026-07-12.

**DLOM (private companies).** Typical range **15%–40%**, most commonly cited at **20%–35%**; restricted-stock studies center near a ~24% mean, with 30%–50% used for more restrictive fact patterns.
- Source: https://www.anvaluations.com/discount-for-lack-of-marketability-dlom-estimation-methods/ and https://intelekbusinessvaluations.com/en-us/business-valuations/discount-for-lack-of-marketability-dlom-methods-and-evidence/ — accessed 2026-07-12.

**Terminal growth rate norms.** Terminal g is anchored to long-run nominal GDP. CBO's February 2026 outlook holds long-run real GDP growth at **1.8%** with PCE inflation stabilizing near **2%**, implying long-run US nominal GDP growth of roughly **3.8%–4.0%** (CBO does not print a single terminal nominal figure). Practitioners typically set terminal g below that ceiling, commonly 2%–3% (near expected inflation up toward long-run GDP).
- Source: https://www.cbo.gov/publication/61882 — as-of Feb 2026; accessed 2026-07-12.

**Mid-year convention.** Standard practice in banker DCFs. About **75% of 2024 SEC fairness opinions** applied the (N − 0.5) discount when using a mid-year convention; it lifts a DCF ~3%–5% versus year-end discounting.
- Source: https://ctacquisitions.com/mid-year-convention/ and https://www.wallstreetprep.com/knowledge/mid-year-convention/ — accessed 2026-07-12.

---

## 6. Private markets

**PE deal multiples.** US buyout median EV/EBITDA ~**11x–12x** (PitchBook "12x new norm"); large buyouts ($1B+) reached 15.5x in 2024; middle market ~9.6x. Entry multiples averaged ~11.0x in 2024 (up from 10.8x in 2023).
- Source: https://pitchbook.com/news/articles/median-us-pe-buyout-multiples-of-12x-may-be-the-new-norm — 2024-2025; accessed 2026-07-12.

**Leverage on new LBOs.** Average pro-forma debt/EBITDA on large-corporate LBOs was ~**4.7x** in Q1 2025 (4.68x Q4 2024 → 4.70x Q1 2025), down from ~5.2x earlier in 2024. Equity contributions sit in the high-40% range, topping 50% on some deals; a 45%-55% equity band is the current benchmark.
- Sources: https://pitchbook.com/news/articles/with-lbos-scarce-leverage-in-syndicated-us-loan-market-sinks-to-7-year-low and https://pitchbook.com/news/articles/amid-investor-caution-expensive-cost-of-debt-lbo-equity-contributions-top-50 — Q1 2025; accessed 2026-07-12.

**SOFR-based borrowing cost.** Overnight SOFR was **3.53%** on July 9, 2026. Leveraged-loan pricing adds a credit spread on top (single-B term-loan spreads roughly 3.5%-4.5%), so all-in floating borrowing costs approximate ~7%-8%.
- Source: https://www.sofrrate.com/ and https://www.newyorkfed.org/markets/reference-rates/sofr — as-of July 9-10, 2026; accessed 2026-07-12. Spread add-on is an estimate from typical market ranges, not a single sourced print.

---

## Items flagged as stale, estimated, or unverified
- Damodaran `histimpl.html` auto-parse (4.33% / 4.58% for Jan 2026) conflicts with his stated 4.23% / 4.18%; the prose value is the one used here.
- Kroll exact current CRSP decile size premia: paywalled in the Cost of Capital Navigator, not verified numerically.
- SaaS Capital Index exact live median: image-gated on the source site; June 2026 figure taken from secondary trackers that vary (3.2x to 4.8x ARR), so treat as a range.
- KPMG Cost of Capital Study 2025 PDF exceeded fetch size; sector and headline figures come from KPMG's own web summary and search extracts, not the full PDF.
- LBO all-in borrowing cost (~7%-8%) and the credit-spread add-on are estimates layered on the verified SOFR print.
- Bessemer 2021 peak: a "28x" figure appears in one secondary source but Bessemer does not publish a historical median series; the cleaner verified peak is the SaaS Capital Index at 16.9x (Aug 2021).
