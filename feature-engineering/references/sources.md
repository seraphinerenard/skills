# Sources

All access dates 2026-07-12. Two researcher fact sheets carry their own
source lists, verified against primary documents by the researchers who wrote them:

- `research/practitioner-fe-canon.md`: M5 winners (IJF papers, organizer repo),
  Micci-Barreca 2001, sklearn/H2O/category_encoders target-encoding docs, CatBoost
  ordered statistics (NeurIPS 2018), Grellier null importances, Altmann PIMP 2010,
  FastML/UnfoldAI adversarial validation, Nixtla mlforecast, tsfresh, aeon, FPP3
  dynamic harmonic regression, Optiver 2023, Enefit 2023-24, Rossmann, Favorita,
  Guo & Berkhahn entity embeddings.
- `research/weather-geospatial-joins.md`: GHCN-Daily README and product pages,
  EPA and MRCC HDD/CDD documentation, degreedays.net balance-point fitting, NDFD
  archive, GEFS v12 reforecast, GFS AWS archive, ECMWF open data and MARS, ERA5
  latency documentation, H3 cell statistics, OSRM/Valhalla/openrouteservice
  isochrone docs, Micci-Barreca 2001, Shepard 1968 IDW, Kaggle coordinate-encoding
  writeups.

Sources gathered inline for the remaining sections:

## Tabular foundation models

- TabPFN v2: Hollmann et al., "Accurate predictions on small data with a tabular
  foundation model", Nature 637:319-326 (January 2025).
  https://www.nature.com/articles/s41586-024-08328-6 (volume/page metadata
  confirmed via search and the Wikipedia entry; article URL from the paper's DOI).
- TabPFN entry, Wikipedia. https://en.wikipedia.org/wiki/TabPFN (capability limits,
  publication metadata).
- TabPFN-2.5: Prior Labs, "TabPFN-2.5: Advancing the State of the Art in Tabular
  Foundation Models", arXiv 2511.08667 (November 2025).
  https://arxiv.org/html/2511.08667v1 (50k-row/2k-feature envelope, TabArena-lite
  results, AutoGluon 1.4 extreme reference line, Real-TabPFN-2.5).
- "A Closer Look at TabPFN v2: Strength, Limitation, and Extension", arXiv
  2502.17361. https://arxiv.org/html/2502.17361v1 (failure modes on large,
  high-dimensional, non-IID tables).
- HumbleBeeAI, "Benchmarking TabPFN V2 against XGBoost and CatBoost on Kaggle
  datasets" (November 2025).
  https://blog.humblebee.ai/blog/2025/11/23/benchmarking-tabpfn-v2-against-xgboost-and-catboost-on-kaggle-datasets/
  (win rates under 10k rows, degradation past the envelope).
- OpenFE: "OpenFE: Automated Feature Generation with Expert-level Performance",
  arXiv 2211.12507 (ICML 2023). https://arxiv.org/abs/2211.12507 (cited from
  knowledge; arXiv ID checked against memory only).
- CAAFE: "LLMs for Semi-Automated Data Science: Introducing CAAFE", arXiv
  2305.03403 (NeurIPS 2023). https://arxiv.org/abs/2305.03403 (cited from
  knowledge; arXiv ID checked against memory only).

## Syndicated scanner data

- NielsenIQ, "Total Distribution Points (TDP) & CPG Brands".
  https://nielseniq.com/global/en/insights/education/2022/total-distribution-points-tdp-cpg-brands/
- NielsenIQ CPG Dictionary, "All Commodity Volume (ACV)".
  https://microsites.nielseniq.com/cpg-dictionary/dictionary/all-commodity-volume-acv/
- NielsenIQ CPG Dictionary, "Total distribution points (TDP)".
  https://microsites.nielseniq.com/cpg-dictionary/dictionary/total-distribution-points-tdp/
- Circana Liquid Data Go CPG Dictionary, "All Commodity Volume (ACV)" and
  "Weighted Distribution".
  https://www.circana.com/liquid-data-go/cpg-dictionary/all-commodity-volume-(acv)
  https://www.circana.com/liquid-data-go/cpg-dictionary/weighted-distribution
- CPG Data Insights, "Total Distribution Points: Master of All Distribution
  Measures". https://www.cpgdatainsights.com/distribution/total-distribution-points-post/
  (velocity/SPPD framing, distribution-times-velocity decomposition).

## Item identity (GTIN)

- GS1, "GTIN non-reuse" (Healthcare GTIN rules page stating the general rule).
  https://www.gs1.org/1/hcgtinrules/en/gtin-non-reuse
- GS1 GSCN 18-334, non-reuse change notification (PDF).
  https://www.gs1.org/docs/barcodes/GSCN_18-334_non_reuse_never_produced.pdf
- GTIN.info, "GTIN Reuse Policy Update". https://www.gtin.info/gtin-reuse-policy-update/
  (prior 48-month general / 30-month apparel reuse windows, 2019-01-01 cutover).
- Bar Code Graphics, "New GS1 Rules: No UPC Reuse".
  https://www.barcode.graphics/gtin-standards-update-no-upc-reuse/

## Stated from practitioner knowledge, no primary URL fetched

Flagged here so a future revision can harden them:

- AVEVA/OSIsoft PI exception (ExcDev) and compression (CompDev, swinging-door)
  mechanics: vendor documentation portal at https://docs.aveva.com (PI Server
  documentation); the mechanism description in `industry-data-quirks.md` follows
  the vendor's published algorithm names and behaviour from memory.
- ERP date semantics (order/shipment/invoice), backorder release spikes, catch-weight
  UoM, and 4-4-5 calendar arithmetic (13-week quarters, 53rd week every 5 to 6
  years): standard ERP and retail-finance practice; the 4-4-5 structure is
  documented in any fiscal-calendar reference.
- POS returns/void mechanics and the price-derived promo detection recipe
  (rolling 8-week base-price median, ~95% threshold): retail analytics practice;
  thresholds are working defaults, marked as such where used.
- DST 23/25-hour day handling in hourly load data: energy forecasting practice.
