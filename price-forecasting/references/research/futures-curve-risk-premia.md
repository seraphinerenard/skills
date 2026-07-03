<!-- Compiled 2026-07-12. -->

---

# Commodity price forecasting: the futures curve as forecast, and commodity risk premia

Note on sourcing: the primary PDFs were read directly for Erb-Harvey (2006), Gorton-Rouwenhorst (2006), Bhardwaj-Gorton-Rouwenhorst (2015), Chinn-Coibion (2013), Koijen-Moskowitz-Pedersen-Vrugt "Carry" (2018), and the Baumeister Bank of Canada Review (2014). The IMF working paper server (Reichsfeld-Roache) returned 403 on every attempt, so those specifics rest on the published abstract plus citing papers and are flagged below.

---

## TOPIC 1 — The futures curve as a forecast of spot

### Fama & French (1987), "Commodity Futures Prices: Some Evidence on Forecast Power, Premiums, and the Theory of Storage," Journal of Business 60(1), 55-73

Exact abstract finding (verified): "The second model splits a futures price into an expected premium and a forecast of the maturity spot price. We find evidence of forecast power for 10 of 21 commodities and time-varying expected premiums for five commodities." Source: https://ideas.repec.org/a/ucp/jnlbus/v60y1987i1p55-73.html

So the decomposition is F − S = E[premium] + E[ΔS]. Their empirical result: the basis carries statistically detectable power to forecast the future spot price change for only about half the commodities (10 of 21), and detectable time-varying risk premiums for only 5. This is the origin of the central distinction: the basis is a weak and uneven predictor of spot price changes, and premium information is even harder to detect. Fama-French also confirmed the theory of storage (the basis moves with interest rates and seasonal convenience yields). A single verified magnitude: Gorton-Rouwenhorst (2006, footnote 15) reports that Fama-French (1987) found a continuously compounded risk premium of 0.45% per month (t = 1.57, so insignificant) on an equally weighted portfolio of 21 commodities, 1966-1984 — roughly 5.4% per annum but not statistically distinguishable from zero. Source (GR2006 NBER PDF): https://www.nber.org/system/files/working_papers/w10595/w10595.pdf

### Alquist & Kilian (2010), "What Do We Learn from the Price of Crude Oil Futures?" Journal of Applied Econometrics 25(4), 539-573

Core conclusion (verified via publisher abstract and multiple summaries): oil futures prices are LESS accurate than the no-change (random walk) forecast in the mean-squared-prediction-error sense. The inaccuracy is driven by the variability of the futures price about the spot price (the oil futures spread), which reflects the marginal convenience yield of oil inventories rather than a clean expectation of the future spot price. Source: https://onlinelibrary.wiley.com/doi/10.1002/jae.1159

Practical reading: the WTI futures curve is not an unbiased or efficient point forecast of future spot oil; using it does not beat simply assuming today's price persists.

### Reichsfeld & Roache (2011), "Do Commodity Futures Help Forecast Spot Prices?" IMF WP/11/254

Verified conclusions (IMF abstract + citing literature; primary PDF was inaccessible, exact RMSE tables UNVERIFIED): they assess 10 commodity futures at horizons up to two years. In-sample tests reject efficiency, but out-of-sample "the forecast from the futures market is hard to beat" — i.e., futures are roughly random-walk-equivalent, not systematically superior. Two robustness findings: forecasting performance does NOT depend on the slope of the futures curve, and it is invariant to whether prices are in an upswing or a downswing. Source (abstract): https://www.imf.org/en/publications/wp/issues/2016/12/31/do-commodity-futures-help-forecast-spot-prices-25325 and https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1956401

Secondhand specifics that could not be verified against the primary tables (flagged): citing summaries state that base metals show little predictive content (futures squared errors no smaller than random walk), energy commodities predict the direction of price changes better especially at longer horizons but yield little squared-error improvement, and futures beat the random walk mainly around the 3-month horizon. Treat these as indicative, not confirmed. Source (secondhand): search aggregation around https://users.ssc.wisc.edu/~mchinn/commodityfutures.pdf

### Chinn & Coibion (2013/2014), "The Predictive Content of Commodity Futures," Journal of Futures Markets (read from the working-paper PDF)

This is the cleanest commodity-by-group verdict on unbiasedness and random-walk beating, using futures data since 1990 at 3-, 6-, and 12-month horizons. Verified findings:
- Precious and base metals fail most tests of unbiasedness and are poor predictors; "metals futures do not typically outperform random walks in terms of squared forecast errors" (explicitly likened to exchange-rate forwards / Meese-Rogoff).
- Energy and agricultural futures "hew more closely to the unbiasedness hypothesis" and "in some cases … significantly outperform random walk forecasts," with stronger direction-of-change prediction.
- Within energy, oil futures fare WORSE than natural gas and gasoline futures, both in MSE and in predicting the sign of price changes.
- A concrete cross-commodity number: one could have doubled the fraction of gold price changes explained at the 12-month horizon (9% → 18%) and 6-month horizon (5% → 10%) by adding the natural-gas basis to the gold basis.
- Liquidity (volume/open-interest, following Bessembinder-Seguin) explains only about 10% of the cross-sectional variation in unbiasedness.
- A broad decline in the predictive content of commodity futures since the early 2000s.
Source: https://users.ssc.wisc.edu/~mchinn/commodityfutures.pdf

### Baumeister & Kilian — real-time oil forecasting program

"Real-Time Forecasts of the Real Price of Oil" (2012, JBES 30(2), 326-336): first evidence that model-based forecasts beat the no-change benchmark in real time at short horizons. Verified magnitudes: real-time MSPE reductions as high as 25% at one month ahead and 24% at three months ahead; a recursive VAR of the global oil market has lower MSPE than oil-futures-based, AR/ARMA, and no-change forecasts at short horizons, with consistently higher directional accuracy. Source (abstract/summary): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1857364 and https://sites.google.com/site/cjsbaumeister/research

"Forecasting the Real Price of Oil in a Changing World: A Forecast Combination Approach" (2015, JBES 33(3), 338-351): equal-weighted combinations of models beat the no-change forecast and are robust to structural change. Source: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2297208

The four models and the combination (verified numbers from Baumeister's Bank of Canada Review "The Art and Science of Forecasting the Real Price of Oil," Spring 2014, Table 1, source Baumeister-Kilian 2013):
- The oil FUTURES curve: "at shorter horizons, there is no significant evidence that the oil futures curve achieves gains in forecast accuracy," and at longer horizons it is INFERIOR to no-change (Alquist, Kilian, Vigfusson 2013). Explanation: oil futures embed a time-varying risk premium; Hamilton & Wu (2014) find considerable changes in oil-futures risk premia after 2005.
- Global oil-market VAR (production, real activity, inventories): more accurate than no-change at short horizons, even in real time.
- Spot price of raw industrial materials (copper/zinc): beats no-change at short horizons, degrades beyond ~3 months, but predicts direction well up to 12 months.
- Refined product spreads (gasoline / heating-oil spreads), Baumeister-Kilian-Zhou 2013: beats no-change especially at horizons of one to two years.
- Equal-weighted COMBINATION (Table 1): MSPE ratios below 1 for horizons up to 18 months, ranging from 4% to 13% MSPE reduction. Exact MSPE ratios for the RAC measure: 1mo 0.897, 3mo 0.874, 6mo 0.949, 9mo 0.939, 12mo 0.892, 15mo 0.893, 18mo 0.957, then it fails at 21mo (1.065) and 24mo (1.029). WTI ratios are similar (3mo 0.873, 12mo 0.902). Success ratios (directional accuracy) run 55%-65% for RAC (significant at all but one horizon to 18 months) and up to 62% for WTI.
Source: https://www.bankofcanada.ca/wp-content/uploads/2014/05/boc-review-spring14-baumeister.pdf

"Inside the Crystal Ball" (correction to a common miscitation): the survey/JEP piece is Baumeister & Kilian (2016), "Forty Years of Oil Price Fluctuations: Why the Price of Oil May Still Surprise Us," Journal of Economic Perspectives 30(1), 139-160. "Inside the Crystal Ball: New Approaches to Predicting the Gasoline Price at the Pump" is a separate paper (Baumeister, Kilian & Lee), Journal of Applied Econometrics 2017. There is no 2018 JEP "Crystal Ball" survey, so any citation to one is in error. Source: https://sites.google.com/site/lkilian2019/research/publications

### 2020-2026 updates (this is where the consensus has shifted)

Ellwanger & Snudden (2023), "Forecasts of the real price of oil revisited: Do they beat the random walk?" Journal of Banking & Finance vol. 154. Verified finding: the benchmark matters decisively. The standard literature used a monthly-AVERAGE no-change forecast; Ellwanger-Snudden show the END-OF-MONTH price (the true daily random-walk forecast) is "significantly more accurate," and "at the one-step-ahead prediction, all existing forecasts that outperform the monthly average no-change forecast perform worse than the end-of-month no-change forecast." In other words, much of the apparent forecastability up to one year ahead was an artifact of temporal aggregation in the benchmark. Source: https://ideas.repec.org/a/eee/jbfina/v154y2023ics0378426623001619.html

Benyo (2026), "A Reappraisal of Real-Time Forecasts of the Real Price of Oil," Economic Inquiry (published online 2025). Verified finding: replicating Baumeister-Kilian (2012) against the end-of-month no-change benchmark, there are "no consistently significant improvements in the predictive accuracy of model-based forecasts over the naive benchmark at short horizons"; "only futures-based forecasts consistently outperform the end-of-month no-change forecast, and only at longer horizons." This partially reverses the 2012 consensus and, notably, is the one recent result that gives the futures curve an edge — at long horizons only. Sources: https://onlinelibrary.wiley.com/doi/full/10.1111/ecin.70009 and ungated working paper https://www.lcerpa.org/files/LCERPA_2025_7.pdf

### CONCRETE DELIVERABLE for Topic 1

For which commodities/horizons does the futures curve beat a random walk?
- Crude oil: NO (Alquist-Kilian 2010; Chinn-Coibion; futures curve inferior at long horizons per Alquist-Kilian-Vigfusson 2013; the 2012 short-horizon model gains largely vanish against the end-of-month benchmark per Ellwanger-Snudden 2023 and Benyo 2026). What beats no-change for oil is not the curve but the global-oil-market VAR, the industrial-materials model, product spreads, and above all the equal-weighted combination — by roughly 4-13% MSPE up to 18 months (and up to ~25% at 1-3 months in the 2012 real-time study), a gain that recent benchmark-corrected work has substantially discounted.
- Precious metals (gold, silver) and base metals (copper, aluminum): NO — futures do not beat the random walk in squared errors (Chinn-Coibion; Reichsfeld-Roache base metals, flagged).
- Natural gas, gasoline, and several agricultural futures: sometimes YES, at short horizons and for direction-of-change, though squared-error gains are small (Chinn-Coibion; Reichsfeld-Roache ~3-month, flagged).

Size of the risk-premium bias (the wedge that makes futures a biased spot forecast), in % per annum:
- Diversified basket: about 5% per annum historically (Gorton-Rouwenhorst risk premium 5.23%, 1959-2004; see Topic 2), so the average futures-minus-expected-spot bias for the basket is on that order and highly time-varying.
- By commodity, the bias is far larger in either direction: Erb-Harvey roll returns range from +4.6%/yr (heating oil) to −4.9%/yr (gold) over Dec 1982-May 2004 (verified, below).
- Oil specifically: the risk premium is time-varying with large post-2005 shifts (Hamilton-Wu 2014, cited in Baumeister 2014).

---

## TOPIC 2 — Commodity risk premia, backwardation/contango, and the basis

### Gorton & Rouwenhorst (2006), "Facts and Fantasies about Commodity Futures," Financial Analysts Journal 62(2), 47-68 (read from the NBER PDF)

Verified exact numbers, equally-weighted, fully collateralized, monthly-rebalanced index, July 1959-Dec 2004:
- Average return of the futures index: 10.69% p.a. arithmetic, 9.98% geometric (Table 1). Spot commodity index: 8.42% arithmetic; inflation 4.14%.
- Risk premium (excess return over T-bills), Table 2: Commodity Futures 5.23% p.a. (t = 2.92), standard deviation 12.10%, Sharpe ratio 0.43, 55% of months positive. S&P 500: 5.65% (t = 2.57), std 14.85%, Sharpe 0.38. Bonds (corporate): 2.22%, Sharpe 0.26.
- Headline: the commodity-futures risk premium is "about 5% per annum," economically large and statistically significant, roughly equal to equities and more than double bonds. Commodity futures are negatively correlated with stocks and bonds and positively correlated with inflation.
- The roll/backwardation mechanism (Figure 2a/2b): the futures total-return index (reaching ~1400 on 1959=100, inflation-adjusted) rises far above the spot-price index (~500) precisely because the futures position earns the risk premium (T-bill rate plus the backwardation premium); expected trends in the spot price are excluded from the futures index. Historical context (footnote 15): Bodie-Rosansky (1980) found a 9.5% p.a. excess return for an EW commodity-futures portfolio, 1950-1976.
Source: https://www.nber.org/system/files/working_papers/w10595/w10595.pdf

### Erb & Harvey (2006), "The Strategic and Tactical Value of Commodity Futures," Financial Analysts Journal 62(2), 69-97 (read from the unabridged working-paper PDF)

This is the sharpest evidence for the basis/roll-yield distinction. Verified numbers, GSCI and 12 constituents, Dec 1982-May 2004 (Table 2):
- GSCI compound annualized excess return 4.49% (arithmetic 5.81%), std 16.97%, Sharpe 0.26; energy sector 7.06%, non-energy −0.12%.
- The average individual commodity excess return is essentially zero: the equally-weighted average of the 12 constituents was −1.71% geometric; no individual commodity or sector had a statistically significant excess return over the period (it would take ~57 years of GSCI data, ~78 years of energy-sector data, to reach conventional significance).
- Individual excess returns dispersed widely: heating oil +5.53%, copper +6.17%, live cattle +5.07% versus silver −8.09%, coffee −6.36%, corn −5.63%, gold −5.68%, wheat −5.39%.

The key cross-sectional result (Figure 8, verified): the roll return (term structure / basis) explains 91% of the cross-sectional variation in commodity-futures excess returns, Dec 1982-May 2004 (adjusted R² = 91.57%, roll coefficient 1.20, t = 10.97). Positive-roll commodities (copper, heating oil, live cattle) averaged +4.2% excess return; negative-roll commodities (corn, wheat, silver, gold, coffee) averaged −4.6%. The ~9% gap decomposes into a 7.5% difference in roll returns and only a 1.4% difference in spot returns.

The cleanest single illustration of "basis predicts the futures return, not the spot change" (Figure 7, verified): heating oil beat gold by 11.22% p.a. in excess return, of which 9.5% came from the roll (term structure) and only 1.72% from spot returns. Erb-Harvey: "excess returns and spot returns need not be the same if roll returns differ from zero."

And the time-series counterpart (Table 4, verified): while the CROSS-SECTION of excess returns is roll-driven, the TIME-SERIES variation of any single commodity's excess return is driven by spot-price volatility, not roll — average spot-return std 26.76%, average roll-return std 9.14%, spot-roll correlation −0.29.
Source: read from https://people.duke.edu/~charvey/Research/Working_Papers/W77_The_tactical_and.pdf

### Gorton, Hayashi & Rouwenhorst (2013), "The Fundamentals of Commodity Futures Returns," Review of Finance 17(1), 35-105

Verified findings (abstract/summary): using 31 commodity futures and physical inventory data, 1969-2006, they show the convenience yield is a decreasing, non-linear function of inventories; commodities with low inventories and high basis earn higher futures risk premiums, as the theory of storage predicts. Price-based state variables — the futures basis, prior futures returns, prior spot returns, and spot-price volatility — all proxy for the state of inventories and are informative about commodity-futures risk premiums. Sources: https://www.nber.org/papers/w13249 and https://www.nber.org/system/files/working_papers/w13249/w13249.pdf

### Bhardwaj, Gorton & Rouwenhorst (2015), "Facts and Fantasies about Commodity Futures Ten Years Later," NBER WP 21243 (read from the PDF)

This is the best source for post-2004 decay and for the basis-predicts-futures-returns distinction. Verified numbers:
- Risk premiums, Table 3: In-sample 1959-2004, commodity futures 5.23% p.a. (t = 2.92), Sharpe 0.43. Out-of-sample 2005-2014, 3.67% p.a. (t = 0.76, insignificant), std rose to 15.23%, Sharpe fell to 0.24. Full sample 1959-2014, 4.95% (t = 2.90), Sharpe 0.39. The out-of-sample premium is statistically indistinguishable from the in-sample average (and from zero); the ~1.5-point drop was in large part lower T-bill collateral returns, not a collapsed risk premium. 49% of all historical decade-blocks had a premium below 3.67%.
- Post-2004 stock-commodity correlation jumped: the one-year commodity-equity correlation went from −0.10 (in-sample) to +0.60 out-of-sample (Table 6), a financialization signature that they argue was largely a temporary crisis-driven move.
- Backwardation frequency fell: the share of commodities in backwardation averaged 37% pre-2004 and 26% post-2004 (lifetime 35%).

The decisive basis result (Table 4, verified): a portfolio that goes long high-basis and short low-basis commodities — the cross-sectional basis/carry strategy — earned a high-minus-low spread of 9.2% p.a. (t = 4.60), Sharpe 0.68 in-sample; 10.41% p.a. (t = 3.28), Sharpe 1.04 out-of-sample; 9.42% (t = 5.43), Sharpe 0.73 full sample. Hit ratio ~59%. The high-basis leg beat the index by 4.27% and the low-basis leg lagged by −4.93% in-sample. Their words: "the futures basis, an indicator of scarcity of physical inventories, has been reliably correlated with the cross-section of futures risk premiums," and the link "has been stable over time."

The other half of the distinction (Figure 5, verified): the TIME-SERIES predictability of the aggregate market risk premium by the basis is weak. Regressing next-month index return on the percentage of commodities in backwardation gives R² = 0.024 (slope t = 4.03 but economically tiny); "using the percentage of commodities [in backwardation] as a market timing signal for the market is relatively weak." Explicit summary: "The predictability of the risk premium by the basis is more robust in the cross-section of futures returns than in the time-series."

And directly on futures-vs-spot (Table 1, verified): out-of-sample 2005-2014, spot returns (9.42% nominal p.a.) EXCEEDED collateralized futures returns (5.09%), because "high spot price growth was partially anticipated by investors when setting futures prices." That is the spot-vs-futures wedge in action — the futures curve had already priced the anticipated spot rise, so it did not deliver it as a return.
Source: https://www.nber.org/system/files/working_papers/w21243/w21243.pdf

### Koijen, Moskowitz, Pedersen & Vrugt (2018), "Carry," Journal of Financial Economics 127, 197-225 (read from the PDF)

Verified commodity-carry numbers, 24 commodity futures, Feb 1980-Feb 2011:
- Commodity carry strategy (long high-carry, short low-carry): current-carry average return 11.7% p.a., Sharpe 0.62; carry1-12 (12-month-averaged carry, to strip seasonals) 13% p.a., Sharpe 0.67. A passive long commodity portfolio over the same window had a Sharpe of only 0.10.
- Carry alphas are positive and statistically significant in every asset class with betas near zero, so the commodity carry premium is not passive commodity beta.
- The diversified cross-asset carry factor (equities, bonds, currencies, commodities) has a Sharpe of 1.49 (current carry) / 0.95 (carry1-12), versus 0.75 for a diversified passive book.
- Conceptual framing that matches the distinction exactly: carry decomposes expected return into observable carry (for commodities, the convenience yield in excess of storage, read off the futures slope) plus expected price appreciation. Carry predicts commodity futures returns cross-sectionally; the price-appreciation (spot) component is the residual and is not what carry forecasts.
Source: https://w4.stern.nyu.edu/facdir/lpederse/papers/Carry.pdf (also https://spinup-000d1a-wp-offload-media.s3.amazonaws.com/faculty/wp-content/uploads/sites/3/2019/04/Carry.pdf)

### Post-2004 financialization / decay of the premium

The direct evidence is in Bhardwaj-Gorton-Rouwenhorst (2015) above: the diversified long-only premium fell from 5.23% to 3.67% p.a. (in-sample vs 2005-2014), but not significantly, and mostly because of lower collateral yields; the cross-sectional basis premium, by contrast, did NOT decay (9.2% in-sample → 10.4% out-of-sample). Stock-commodity correlations rose sharply during 2005-2014 (one-year correlation −0.10 → +0.60). The financialization literature they cite (Tang & Xiong 2012; Cheng & Xiong 2014) documents rising co-movement; their own read is that the correlation spike was largely crisis-driven and mean-reverting.

### THE KEY DISTINCTION — the basis predicts FUTURES returns well but SPOT price changes poorly

The evidence chain, strongest to supporting:
1. Mechanism (Fama-French 1987): F − S = E[premium] + E[ΔS]. Empirically the basis has spot-forecast power for only 10 of 21 commodities and time-varying premium information for 5, so the basis is a mixed spot predictor at best.
2. Spot side is weak. Oil futures/basis are LESS accurate than a random walk for spot (Alquist-Kilian 2010); metals futures do not beat a random walk for spot, and predictive content has broadly declined since the early 2000s (Chinn-Coibion 2013).
3. Futures-return side is strong and specifically cross-sectional. Erb-Harvey (2006): the roll/basis explains 91% of the cross-section of futures excess returns, and the heating-oil-vs-gold gap is 9.5% roll versus 1.7% spot. Gorton-Hayashi-Rouwenhorst (2013): the basis proxies inventory scarcity and predicts futures risk premiums. Bhardwaj-Gorton-Rouwenhorst (2015): a high-minus-low basis portfolio earns ~9-10% p.a. (Sharpe 0.68-1.04) and this is stable out-of-sample, while the SAME basis used as a time-series market-timing signal gives R² = 0.024. Koijen-Moskowitz-Pedersen-Vrugt (2018): commodity carry (the basis) earns Sharpe ~0.62-0.67, and carry is by construction the expected-return component that is orthogonal to expected price appreciation.
4. Confirmation from the wedge itself. Out-of-sample 2005-2014, commodity spot growth (9.42% p.a.) outran futures returns (5.09%) because the anticipated spot rise was already in the curve (Bhardwaj-Gorton-Rouwenhorst 2015, Table 1) — the futures curve is not where the spot appreciation shows up; the risk premium is.

Net: the basis is a risk-premium signal that sorts which commodity futures pay more, and it is a poor forecaster of where the spot price is going. That is why long-only, curve-following spot forecasts fail against a random walk while cross-sectional basis/carry strategies earn large, stable Sharpe ratios.

---

## Items flagged as unverified or corrected
- Reichsfeld-Roache (IMF WP/11/254): the exact commodity-by-horizon RMSE ratios are UNVERIFIED — the IMF PDF returned 403 on every attempt. The abstract-level conclusions (out-of-sample futures are "hard to beat," performance independent of curve slope, invariant to up/down swings) are solid; the "base metals no better than RW, energy better, ~3-month edge" specifics come from citing papers and should be confirmed against the primary tables before quoting a number.
- Brief citation correction: there is no 2018 Baumeister-Kilian "Inside the Crystal Ball" survey in the Journal of Economic Perspectives. The JEP survey is Baumeister & Kilian (2016), "Forty Years of Oil Price Fluctuations," JEP 30(1); "Inside the Crystal Ball" is a 2017 Journal of Applied Econometrics gasoline-price paper (Baumeister, Kilian & Lee).
- Recent benchmark caveat: the 2012 real-time MSPE reductions (up to ~25%) are materially discounted by Ellwanger-Snudden (2023) and Benyo (2026), which show the gains were partly an artifact of the monthly-average random-walk benchmark; against the end-of-month price, most short-horizon model advantages disappear and only futures-based forecasts beat the benchmark, and only at long horizons.
