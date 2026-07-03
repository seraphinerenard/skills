<!-- Compiled 2026-07-12. -->

Every figure below is verified against primary documentation.

---

# AREA 5 — Weather data joins for demand and energy models

## Station selection from GHCN-Daily
- GHCN-Daily (GHCNd) holds daily records from **>100,000 stations across 180 countries/territories**, reconstructed weekly from ~30 source datasets; core elements are TMAX, TMIN, PRCP, SNOW, SNWD [S4][S5].
- Prefer **airport stations** because they carry automated, well-maintained ASOS/METAR instrumentation. In GHCNd these enter through source flags `A` (US ASOS), `B` (US ASOS Oct 2000–Dec 2005), and `W` (WBAN/ASOS Summary-of-Day from Integrated Surface Data); ASOS records are keyed by WBAN ID and matched to a COOP ID via NCEI's Master Station History Record [S5]. US airport stations also appear in the WMO/GHCNd inventory with `USW`-prefixed IDs.
- **Completeness screening**: `ghcnd-inventory.txt` lists, per station and per element, the FIRSTYEAR and LASTYEAR of coverage; use it plus the daily QC flags to compute a **% of days present** over your window and drop stations below a threshold (a common practice cutoff is ≥80–90% non-missing for the target element) [S5]. This is a practitioner threshold, not a NOAA-mandated one.
- **Inverse-distance weighting (IDW)** to interpolate the nearest qualifying stations to a target lat/lon: value(x) = Σ wᵢ·vᵢ / Σ wᵢ with wᵢ = 1/dᵢ^p, p typically 2 (d = great-circle distance). IDW originates in Shepard (1968) [S23]. Practical join: pick the k nearest airport stations that pass completeness screening, weight by 1/d², optionally add a lapse-rate elevation correction. IDW is a general method, not a GHCNd-specific NOAA recommendation.

## HDD / CDD definitions
- Daily mean temperature: **T_mean = (T_max + T_min) / 2** [S6][S8].
- **Heating Degree Days**: HDD = max(0, T_base − T_mean). **Cooling Degree Days**: CDD = max(0, T_mean − T_base) [S6][S8].
- Standard base is **65 °F = 18.3 °C** (Europe commonly uses 15.5 °C base / 18 °C internal-comfort variants); "HDD 16" or "HDD 18" bases are used to account for internal heat gains [S6][S7][S8]. Annual ΣHDD or ΣCDD is roughly proportional to annual heating/cooling energy at a site [S7][S8].
- **Demand-specific (non-65 °F) base**: the base temperature is really the building/portfolio **balance point** — the outdoor temperature at which internal gains offset envelope losses — and it varies by building stock and end use, so fitting it beats assuming 65 °F [S7]. Standard approach is **change-point / balance-point regression** (piecewise-linear "variable-base degree day" fit): regress observed load on candidate bases and pick the base that maximizes fit, or fit a segmented model load = α + β·max(0, T_base − T) [+ γ·max(0, T − T_base,c)] and let T_base be a free knot [S7]. degreedays.net documents driving the base off regression against actual consumption rather than assuming 65 °F [S7].

## Forecast-vs-actual (train/serve skew)
- Core trap: **at training you have observed actuals** (station obs or reanalysis), **but at inference/serving you only have a forecast**. A model trained on perfect actuals sees degraded, biased inputs in production, so train on the **archived forecast product you will actually serve on**, aligned by issue-time and lead-time.
- **NOAA NDFD archive** (gridded operational NWS forecasts of Tmax/Tmin, cloud, wind, etc.): archived at NCEI via THREDDS/AWS; data before **2008-10-06** is retrieved through NCEI's Archive Information Request System (AIRS), limited to one day per request [S9][S10].
- **GEFS v12 reforecast** (retrospective forecasts spanning **2000–2019**, free on AWS): 00 UTC init, 5 members daily, an 11-member run once weekly extending to **+35 days** lead — designed precisely for training/calibrating models on a consistent forecast distribution [S11][S12]. Operational **GFS** is a rolling **~4-week** 0.25° archive in `s3://noaa-gfs-bdp-pds` [S13].
- **ECMWF HRES / IFS**: open-data real-time HRES output at steps **0–144 h by 3 h and 150–240 h by 6 h**, replicated to AWS/Azure/GCP; the full operational forecast history lives in the **MARS** archive (semantic query language, GRIB/NetCDF) [S14][S15]. Commercial vendors (e.g. weather-data APIs) also sell archived point forecasts for the same purpose.

## ERA5 reanalysis (Copernicus/ECMWF) — training feature, not a live feature
- ERA5 is a **reanalysis** (a fixed model + data assimilation applied retrospectively to observations), hourly, **1940–present**; ideal for building historical training features because it is spatially complete and gap-free [S2].
- **Latency limits for live serving** (from the ECMWF ERA5 data documentation) [S2]:
  - Preliminary **ERA5T** is "data no more than **three months** behind real time"; daily ERA5T updates land **~5 days** behind real time (typically by 12 UTC on D-5).
  - Final **ERA5 overwrites ERA5T about two months** after the month in question (on both CDS and MARS).
  - So effective latency runs **~5 days (ERA5T preliminary) to ~2–3 months (final)** — Copernicus itself headlines the "five days behind real time" update [S3].
- Consequence: **ERA5 cannot be an inference-time feature for near-real-time or future demand/energy models** — it is neither live nor a forecast. Use it for training/backtesting only, and note the ERA5T-vs-final revision as a small train/serve consistency risk if you mix the two vintages.

---

# AREA 6 — Geospatial features

## Uber H3 resolutions (verified full-precision from H3 docs)
Areas computed on a **sphere using the WGS84/EPSG:4326 authalic radius**; every resolution has exactly **12 pentagons** at icosahedron vertices; total cells = 2 + 120·7^r [S1].

| Res | Avg hexagon area (km²) | Avg edge length (km) | Scale |
|-----|------------------------|----------------------|-------|
| 5 | 252.903858182 | 9.854090990 | large district |
| 6 | 36.129062164 | 3.724532667 | town |
| 7 | 5.161293360 | 1.406475763 | neighbourhood |
| 8 | 0.737327598 | 0.531414010 | few city blocks |
| 9 | 0.105332513 | 0.200786148 | city block |

All five area figures match the published reference values exactly (res 7 = 5.16, res 8 = 0.737, res 9 = 0.105 km²) [S1].
- **Trade-area / retail-catchment / demand-tiling work typically uses res 7–9** (neighbourhood to city-block granularity): res 8 (~0.74 km²) and res 9 (~0.105 km²) are the common choices for urban catchment and ride/demand tiling; res 7 (~5.2 km²) for coarser metro views. This range is a practitioner convention, not a figure stated in the H3 docs [S1].

## Drive-time isochrone tooling
- **OSRM** exposes exactly **six services** — `route`, `nearest`, `table`, `match`, `trip`, `tile` — and has **no native isochrone endpoint**. The `table` service returns a `durations[i][j]` matrix **in seconds**; isochrones are built on top by sampling many destinations through repeated `table` calls (e.g. the R `osrm` package's `osrmIsochrone()` does exactly this) [S16].
- **Valhalla** has a **first-class Isochrone service**: it builds a 2-D lat/lon grid around the origin, runs a **breadth-first least-cost (Dijkstra) search** to fill travel time/cost per grid cell, then returns **GeoJSON contour lines or polygons** for the requested time (or distance) intervals; supports auto/bicycle/pedestrian/multimodal costing and can return the raw grid as GeoTIFF [S17][S18].
- **openrouteservice (ORS)** has a dedicated **Isochrones endpoint** returning reachability areas as **GeoJSON polygons** for time or distance, up to **5 locations and 10 intervals per request**, driving/cycling/walking profiles; hosted-API caps: **120 km** max distance, and time ranges of **20 h foot / 5 h cycling / 1 h driving** [S19].

## Encoding location for tree-based models
- **Raw lat/lon into trees works but is awkward**: trees make **axis-aligned splits** (thresholds on one coordinate at a time), so a diagonal or curved geographic boundary is approximated by a staircase of many splits — costly and coarse near the boundary. Raw lat/lon still beats linear models for spatial targets because trees need no scaling and can carve regions, but it is not efficient [S22].
- **Coordinate rotation helps trees directly**: adding rotated coordinates (e.g. 45°, or PCA-derived axes) gives the tree extra axis-aligned directions to split on, so diagonal region boundaries need fewer splits — a widely used Kaggle geospatial trick [S21][S22]. Practical recipe: keep raw lat/lon, add one or two rotated pairs, plus distances/bearings to key anchor points [S21][S22].
- **Hex cell IDs as categoricals**: H3 (or geohash) cell IDs discretize space into compact regions a tree can select cleanly, but a raw H3 ID is a **high-cardinality nominal** value with no meaningful ordering, so splitting on its integer value is meaningless. Feed it either as a native categorical (LightGBM/CatBoost) or via encoding.
- **Target (mean) encoding** of cell IDs is the standard fix: replace each cell with a smoothed mean of the target for that cell, **empirical-Bayes shrunk toward the global mean** for sparse cells — the canonical scheme is **Micci-Barreca (2001), SIGKDD Explorations 3(1):27–32** [S20]. This turns a high-cardinality location category into a single monotone numeric feature trees split cleanly, and is implemented in scikit-learn `TargetEncoder`, category_encoders, CatBoost, and H2O [S20]. Watch for **target leakage**: fit the encoding out-of-fold (or with CatBoost's ordered scheme), or you overstate CV performance.
- Net practice: raw lat/lon + rotated coords for smooth spatial signal; H3/geohash cell IDs + out-of-fold target encoding for discrete catchment/neighbourhood effects; the two are complementary [S20][S21][S22].

---

# SOURCES (accessed 2026-07-12)

- **[S1] Tables of Cell Statistics Across Resolutions — H3** — https://h3geo.org/docs/core-library/restable/ — Authoritative per-resolution average hexagon area and edge length (res 5 = 252.90 km², res 8 = 0.737 km², res 9 = 0.105 km²), sphere/authalic-radius model, 12 pentagons per resolution.
- **[S2] ERA5: data documentation — ECMWF Confluence (Copernicus Knowledge Base)** — https://confluence.ecmwf.int/spaces/CKB/pages/76414402/ERA5+data+documentation — ERA5T is preliminary "no more than three months behind real time," daily updates ~5 days behind, final ERA5 overwrites ERA5T ~2 months after the month.
- **[S3] Key update to climate dataset brings data at five days behind real time — Copernicus** — https://climate.copernicus.eu/key-update-climate-dataset-brings-data-five-days-behind-real-time — Copernicus's own statement of the ~5-day ERA5 near-real-time latency.
- **[S4] Global Historical Climatology Network daily (GHCNd) — NOAA NCEI** — https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily — GHCNd covers >100,000 stations in 180 countries, weekly reconstruction from ~30 sources, core daily elements.
- **[S5] GHCN-Daily README — NOAA NCEI** — https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt — Station file formats, source flags (A/B/W = ASOS), ghcnd-inventory.txt first/last-year coverage for completeness screening, WBAN-to-COOP matching.
- **[S6] Heating and Cooling Degree Days: Technical Documentation — US EPA** — https://www.epa.gov/sites/default/files/2021-03/documents/heating-cooling_td.pdf — HDD/CDD definitions with base 65 °F and T_mean = (Tmax+Tmin)/2.
- **[S7] Base Temperature (Balance Point) for Heating & Cooling Degree Days — Degree Days.net** — https://www.degreedays.net/base-temperature — Base = building balance point; fit it from regression against actual consumption instead of assuming 65 °F (variable-base degree days).
- **[S8] Degree Day Description — Midwestern Regional Climate Center** — https://mrcc.purdue.edu/CLIMATE/Station/Daily/degreeday_description.html — HDD/CDD formulas, 65 °F base, annual sums proportional to heating/cooling energy.
- **[S9] National Digital Forecast Database (NDFD) — NOAA NCEI** — https://www.ncei.noaa.gov/products/weather-climate-models/national-digital-forecast-database — Archived operational NWS gridded forecasts; pre-2008-10-06 via NCEI AIRS (one day per request).
- **[S10] NOAA NDFD — Registry of Open Data on AWS** — https://registry.opendata.aws/noaa-ndfd/ — Cloud access to archived/real-time NDFD forecast grids for train/serve alignment.
- **[S11] NOAA GEFS Re-forecast — Registry of Open Data on AWS** — https://registry.opendata.aws/noaa-gefs-reforecast/ — GEFSv12 retrospective forecasts 2000–2019, free, for calibrating/training on a consistent forecast distribution.
- **[S12] Description of GEFSv12 Reforecast Data (PDF)** — https://noaa-gefs-retrospective.s3.amazonaws.com/Description_of_reforecast_data.pdf — 00 UTC init, 5 members daily, weekly 11-member run to +35 days lead.
- **[S13] NOAA GFS (BDP) — Registry of Open Data on AWS** — https://registry.opendata.aws/noaa-gfs-bdp-pds/ — Rolling ~4-week 0.25° operational GFS archive in s3://noaa-gfs-bdp-pds.
- **[S14] ECMWF open data: real-time forecasts from IFS and AIFS — ECMWF Confluence** — https://confluence.ecmwf.int/display/DAC/ECMWF+open+data:+real-time+forecasts+from+IFS+and+AIFS — HRES open-data steps 0–144 h/3 h and 150–240 h/6 h; replicated to AWS/Azure/GCP.
- **[S15] Operational archive — ECMWF** — https://www.ecmwf.int/en/forecasts/dataset/operational-archive — Full IFS/AIFS forecast history via MARS (semantic query, GRIB/NetCDF).
- **[S16] OSRM API Documentation (v5.5.1)** — https://project-osrm.org/docs/v5.5.1/api/ — Six services (route/nearest/table/match/trip/tile); table returns durations[i][j] in seconds; no native isochrone endpoint.
- **[S17] Isochrone API reference — Valhalla Docs** — https://valhalla.github.io/valhalla/api/isochrone/api-reference/ — First-class isochrone service returning GeoJSON contour lines/polygons for time/distance intervals; auto/bike/ped/multimodal.
- **[S18] Isochrones algorithm (thor) — Valhalla Docs** — https://valhalla.github.io/valhalla/thor/isochrones/ — Isochrones built from a 2-D lat/lon grid filled by breadth-first least-cost (Dijkstra) search.
- **[S19] Isochrones Endpoint — openrouteservice** — https://giscience.github.io/openrouteservice/api-reference/endpoints/isochrones/ — GeoJSON reachability polygons, ≤5 locations / ≤10 intervals; hosted caps 120 km, 20 h foot / 5 h bike / 1 h drive.
- **[S20] A preprocessing scheme for high-cardinality categorical attributes — Micci-Barreca (2001), SIGKDD Explorations 3(1):27–32** — https://dl.acm.org/doi/10.1145/507533.507538 — Canonical empirical-Bayes target/mean encoding that turns high-cardinality categoricals (ZIP, cell IDs) into a smoothed numeric feature.
- **[S21] Good Feature Building Techniques and Tricks for Kaggle — KDnuggets** — https://www.kdnuggets.com/2018/12/feature-building-techniques-tricks-kaggle.html — Coordinate rotation (incl. PCA) gives tree models extra axis-aligned split directions for diagonal spatial boundaries.
- **[S22] Feature engineering with coordinates — Kaggle (phongnguyen1)** — https://www.kaggle.com/code/phongnguyen1/feature-engineering-with-coordinates — Worked example: raw lat/lon works for trees (XGBoost) not linear models; rotation/clustering add signal.
- **[S23] A two-dimensional interpolation function for irregularly-spaced data — Shepard (1968), ACM National Conf.** — https://dl.acm.org/doi/10.1145/800186.810616 — Origin of inverse-distance weighting, w = 1/d^p, used to interpolate station values to a target location.

Notes on confidence: every H3 area/edge value and the ERA5 latency numbers were read directly from the primary docs [S1][S2] and match. The GHCN completeness cutoff (80–90%) and the "res 7–9 for trade areas" convention are practitioner norms, flagged as such rather than doc-stated figures. IDW and change-point base-fitting are standard methods cited to their canonical sources, not NOAA-specific mandates.
