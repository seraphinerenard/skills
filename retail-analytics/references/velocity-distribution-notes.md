# Distribution, velocity, and the syndicated data that measures them

Working notes for CPG brand analytics. The companion module assets/share_decomposition.py implements the math. Sources with URLs and access dates live in sources.md.

## The metrics, with the arithmetic

%ACV (all-commodity volume) weights a brand's store coverage by the stores' total sales: a brand in stores doing 30% of the market's all-commodity volume has 30 %ACV, whatever the store count. TDP (total distribution points) sums item-level %ACV across the brand's items: 4 items each at 25 %ACV give TDP = 100. TDP moves when items are added or dropped; %ACV alone hides that.

Velocity is sales per unit of distribution. The common forms: SPPD (dollars per point of distribution, dollars / TDP), dollars per point of %ACV, dollars per million dollars of ACV ($/MM-ACV), and units per store per week (UPSPW, common in natural-channel data). Pick one and keep it fixed within an analysis; providers default differently (Circana and NielsenIQ reports usually surface $/TDP or $/MM-ACV, SPINS surfaces $/TDP and UPSPW).

Worked comparison. Category dollars $100M in a market-period. Brand X sells $1.2M at 30 %ACV: $40,000 per ACV point. Brand Y sells $2.4M at 80 %ACV: $30,000 per point. Y is twice X's size; X converts its shelf presence 33% harder, and if X's velocity holds anywhere near $40k/pt as it expands, X at Y's distribution would out-sell Y. Whether it holds is the whole question, and the ACV-velocity curve answers it.

The share identity: dollars = TDP x SPPD, so share growth splits exactly in logs,

    ln(D1/D0) = ln(TDP1/TDP0) + ln(SPPD1/SPPD0)

with no interaction residue. The arithmetic split (dTDP x SPPD0 + TDP0 x dSPPD + dTDP x dSPPD) leaves an interaction term, and whoever presents chooses where it lands, so present the log split and show the arithmetic one only alongside its interaction term.

## Reading ACV-velocity curves

Distribution fills best doors first: the first 20 ACV points come from the retailers and stores where the brand's buyer lives, later points come from progressively worse fits. Velocity therefore falls as ACV rises, and the useful summary is the elasticity b in ln(velocity) = a - b ln(ACV), fit on the brand's own expansion path (time series) or across markets at different penetration. Sales at a target ACV then scale as ACV^(1-b):

- b near 0.1: expansion is nearly loss-free, the brand travels beyond its founding channel.
- b near 0.3: doubling ACV grows sales by 2^0.7 = 1.62x; whitespace projections that scale sales linearly in ACV overstate by about 23% at a doubling.
- b above 0.5: new doors dilute hard; the brand is close to its natural ceiling and further distribution pushes payback out, so the growth case must come from velocity (marketing, repeat) or new items.

Screening across a category has a trap in both directions: raw velocity quantiles crown low-ACV brands automatically (they only hold their best doors) and bury high-ACV brands. Residualize: fit the category's own cross-sectional ln(velocity) on ln(ACV) line and screen on the residual. The expansion signal is a positive residual of +0.25 log points or more at ACV below roughly 40, which reads as "out-converts the category's curve with most doors still to win". assets/share_decomposition.py implements the screen and its demo shows a raw-velocity sort placing the flagged brand mid-pack.

## What each data view catches

Retailer POS (direct data portals: Walmart Luminate, Target Partners Online, Kroger 84.51, and similar) is exact for that retailer, item-day granular, and blind to everywhere else. Syndicated POS (Circana, NielsenIQ; SPINS for the natural channel) covers the measured universe (MULO, MULO+, xAOC) with these standing gaps as of the mid-2020s: Costco, Trader Joe's, and Aldi do not provide item-level POS, and Amazon appears only through separate e-commerce measurement (see sources.md, verify per engagement). A brand born in Costco or the natural channel under-reads badly in syndicated data, and the under-read shrinks as the brand expands into measured retailers, which manufactures fake acceleration. Check channel mix before reading any growth curve.

Household panels (NielsenIQ Homescan, Numerator) add what POS cannot: penetration, repeat rate, buy rate, and leakage across retailers including the unmeasured ones. Their weakness is sample noise on small brands: a brand at 0.1% household penetration appears in roughly 100 households of a 100,000-household panel, so quarterly repeat-rate reads swing with double-digit relative error. Treat panel metrics for young brands as directional until penetration clears roughly 1%.

Nielsen/Circana operational quirks that bite: the IRI-NPD merger formed Circana (2022 merger, 2023 rebrand), so pre-2023 "IRI" and post-2023 "Circana" series are the same asset with occasional universe restatements; measured-universe definitions (MULO versus xAOC) differ between providers so cross-provider velocity comparisons need re-basing; and syndicated new-item ACV builds with a lag as store-level scans phase in, which depresses measured velocity in the first quarter after launch.

## Insurgent screening practice

Bain's insurgent-brand series is the reference screen for what "insurgent" means commercially: more than US$25M revenue in tracked channels (raised to US$35M in NIQ-tracked channels for the 2026 list), growth more than 10x the category average over five years, still growing, still independent or only recently acquired. The population is small and the prize is concentrated: insurgents held under 2% of market share while capturing about 36% of tracked-channel growth in 2025 and about 39% of incremental category growth in 2024. For screening earlier than Bain's floor, the working stack is: velocity residual versus the category curve (above), penetration-times-repeat decomposition from panel data (repeat above roughly 30% separates habits from trial spikes; treat that threshold as a practitioner prior and calibrate per category), and distribution quality (which retailers, which shelves) over distribution quantity.

## Failure modes

- Distribution outrunning velocity: a brand that doubles TDP while SPPD falls faster than the category's b-curve predicts is being pushed by sell-in, and the delist wave follows 2-4 resets later. The log decomposition makes this visible in one line: growth that is 90% distribution and 10% velocity is a countdown unless the brand is very early on its curve.
- Pipeline fill: factory shipments lead POS by weeks at launch and around resets. A shipments-based growth story with flat POS takeaway is inventory in motion. Always plot shipments against syndicated takeaway when a brand claims a step-change.
- Promo-manufactured velocity: velocity spikes bought with deep discounts read as demand in any screen that ignores price. Split base and incremental (both major providers report it), and check %ACV on deal; a brand whose velocity premium disappears at base price has no premium to expand on. Measurement of promo effects belongs to the price-optimization skill; consume its baseline decomposition.
- Adoption-curve overfitting: Bass-model fits on a young brand's short penetration series are unidentified in practice (p, q, and m trade off; confidence intervals on m span multiples), so ceiling estimates from early Bass fits are storytelling. Penetration-times-repeat with a category-informed repeat prior beats them for brands under 2-3 years of data.
