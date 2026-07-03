# Mobility and traffic data, field notes

Working notes on the foot-traffic data supply as of mid-2026, and on the corrections that matter when the deliverable depends on visit counts. Sources with URLs and access dates live in sources.md.

## The supply after SafeGraph

SafeGraph exited the raw foot-traffic business: its Patterns product moved to Advan Research on the Dewey platform in January 2023, and SafeGraph now sells places (POI) data. Placer.ai became the default retail buyer's choice (about US$100 million ARR by 2024 per the GrowthFactor comparison). Unacast and Gravy Analytics merged (announced December 2023). In January 2025 the FTC finalized an order prohibiting Gravy Analytics and its subsidiary Venntel from selling sensitive location data (visits to health facilities, places of worship, and similar categories). The enforcement matters commercially because it shrank the pool of raw ping supply and pushed every surviving vendor toward modelled, aggregated outputs, so buyers in 2026 mostly receive extrapolated estimates and see the raw panel only under special licences.

Apple's App Tracking Transparency (2021 onward) collapsed opt-in rates on iOS, so panels skew Android, which in the US skews younger and lower-income. Any analysis that compares venues with different customer demographics inherits this skew unless the vendor's re-weighting removed it, and vendors rarely publish enough detail to check.

## Failure modes worth pricing in

- Home-location attribution assigns each device a home census block group from nighttime dwell patterns. Shift workers, students, and multi-home households get misassigned, which corrupts both the demographic weights and any trade-area demographics built on device homes.
- Device churn: panels turn over as SDK-carrying apps are installed and deleted. Year-over-year comparisons at one venue partly measure panel composition change. Vendors correct with overlapping-cohort adjustments; ask how, and test against a stable ground-truth venue.
- Visit attribution fails predictably at malls, multi-storey buildings, dense urban blocks, and stores that share a wall or a parking lot with a busier neighbour. GPS error of 10-30 m dominates the geometry of a storefront.
- Drive-by misattribution: POIs adjacent to arterial roads collect phantom visits from traffic. Dwell-time thresholds (commonly 4-5 minutes minimum) trade this against missing quick trips (coffee, convenience).
- Coverage bias: the Coston et al. FAccT 2021 audit (see sources.md, VERIFY before quoting numbers) found older and minority populations under-covered in a mobility panel matched to voter rolls. Post-stratification to census demographics by home block group is the standard correction; it fixes who is in the panel and cannot fix which of their visits get captured.

## The usage doctrine

Panels earn trust for relative statements and lose it for absolute ones. Safe uses: year-over-year change at one venue, rank ordering of venues within a chain, hourly and daily shape, trade-area draw shares, cross-shopping. Unsafe uses: absolute visit counts, single small-POI reads (weekly device counts under a few dozen are noise), demographic composition of visitors to small venues, and any comparison across venues whose customer bases differ in age or income mix.

When absolute counts matter, anchor the panel to ground truth: door counters or POS transactions at a subset of stores give a per-store panel-to-visit multiplier, the panel then supplies the hourly shape and the cross-store comparisons, and the anchor supplies the level. POS transactions are the strongest anchor available in retail because every store has them, they are exact, and transactions = traffic x conversion, so a stable conversion assumption converts one into the other.

## Door counters

Door counters carry their own errors and the direction is knowable. Single-beam infrared counters undercount groups (two people crossing together break the beam once) and double-count loiterers in the threshold. Staff crossings inflate counts unless the system supports exclusion zones or staff tags. Stereo-camera and thermal systems cut both errors and, as a practitioner rule of thumb, run within a few percent of manual counts when mounted and calibrated properly; beam systems can miss 10-20% on busy doors (rule of thumb, no published audit in hand, verify on site with a one-hour manual count). Calibrate any counter against a manual count before using it as the anchor for a panel.
