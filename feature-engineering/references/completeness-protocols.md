# Completeness protocols and the five stopping checks, step by step

Depth note behind SKILL.md section 5. Each protocol names its threshold and the
threshold's provenance; conventions marked "working default" come from practice,
carry no citation, and deserve tightening for regulated work. URLs in `sources.md`.

## 1. Adversarial validation

Procedure: concatenate train features (label 0) and test or serving features (label
1), drop the target, fit a gradient-boosted classifier under stratified 5-fold, read
the out-of-fold AUC, and rank features by permutation importance on the validation
folds (`assets/adversarial_validation.py` implements this).

| OOF AUC | Reading | Action |
|---|---|---|
| Under 0.55 | Exchangeable; CV estimates deserve trust | Record the number and stop |
| 0.55 - 0.70 | Mild shift, usually time proxies | Repair top culprits: difference them, ratio them, rank them within date |
| Over 0.70 | Material shift | Drop or transform culprits; or reweight train rows by p/(1-p); or build validation from the most test-like train rows |
| ELSE (AUC near 1.0) | A feature is a row-order or era fingerprint (date ordinal, autoincrement ID) | Remove it; it also breaks extrapolation (SKILL.md 3.4) |

Run it twice per engagement at minimum: train vs test at build time, and training
matrix vs logged serving payloads before go-live (the second run catches
train-serve skew that no offline split sees). Thresholds follow published
practitioner writeups (FastML origin; UnfoldAI practice guide).

## 2. Null importances

Procedure: fit the screening model on the true target and record per-feature
importance; refit n times on a shuffled target and record the null importances;
keep features whose actual importance clears the null distribution's upper tail.

Numbers: Grellier's protocol shuffles ~80 times and scores
`log(1e-10 + actual / (1 + p75(null)))` (keep positive scores) plus a percentile
score `100 * mean(null < p25(actual))`; Altmann's PIMP (Bioinformatics 26(10):1340,
2010) fits a parametric null and reports p-values. The asset defaults to 30 shuffles
and the null p95 rule, which screens adequately; raise to 80+ for a production
selection that will not be revisited.

Implementation trap (found while building the asset): sklearn's
`feature_importances_` normalize to sum to one across features, so one strong
feature depresses a weak-but-real feature's share below the equal-share null and
the test rejects it spuriously. Read unnormalized per-tree gains
(`tree_.compute_feature_importances(normalize=False)`), the same quantity LightGBM
exposes as gain importance. The asset demo shows a true feature at 2.7% of target
variance surviving the unnormalized test after failing the normalized one.

## 3. Permutation plateau with a noise probe

Procedure: append one `N(0,1)` probe column, fit, compute permutation importance on
holdout (never on train: train permutation importance rewards overfit splits), and
drop every feature at or below the probe. Correlated features share importance and
can both read dead while jointly necessary, so cluster correlated features
(|rho| > 0.9 working default) and drop by cluster, then refit and re-check. Two
consecutive passes with no drops end the check.

## 4. Learning curves on two axes

Samples axis: plot train and validation scores against training-set size under the
final CV scheme. Rising validation with a wide train-validation gap reads variance:
prune features, raise regularization, and expect new features to widen the gap.
Both curves flat and low reads bias: transforms of existing columns are exhausted,
and only new information (a join, a new measurement, a finer grain) moves the
ceiling.

Features axis: fix an ordering of feature families (canon first, speculative last),
add one family at a time under identical CV folds, and plot mean score with a band
of one fold standard deviation. Stop at the first family whose gain sits inside the
band; later families almost never recover (working default; re-order and re-run
once if a domain argument says the ordering buried a good family behind a dead one).

## 5. Residual diagnostics

Run on holdout residuals only; in-sample residuals from a boosted model are
whitened by construction.

- Ljung-Box per series at the seasonal lag m and at 2m
  (`assets/residual_diagnostics.py::per_group_ljung_box`). Aggregate to the
  rejection share across series: near the 5% false-alarm rate is clean; past ~20%
  says lags or seasonal terms are missing (working convention; the asset demo reads
  100% rejection with a missing day-of-week feature and 0% after adding it).
- Candidate scan: for each unused column, bin it (deciles for continuous, levels
  for categorical), compute the binned mean-residual profile and eta-squared (the
  between-bin share of residual variance). eta^2 past ~0.02 on holdout marks a
  candidate worth building (working default); the profile's shape tells you the
  transform (monotone: use raw; V-shaped: distance from the vertex; step: threshold
  flag).
- Bias tables: mean residual by group, calendar slice, and price band, always with
  counts. Weight findings by volume: a 2% bias on the largest store costs more than
  a 20% bias on a store selling ten units a week.

The scan-then-build loop terminates by check 4's feature-axis curve and check 6's
economics; the residual scan alone always finds another candidate at eta^2 = 0.01
and will run forever if it owns the stopping decision.

## 6. Family ablation and pricing

Ablate families, never single columns: correlated columns alibi each other, and a
family (all price features, all weather features) is also the unit you would
actually delete from a pipeline. Same temporal CV folds throughout; report
`mean delta +/- fold std`; keep a family when the mean exceeds one fold std
(working default).

Then convert the surviving delta to money before keeping the family, per the
worked example in SKILL.md 5.6: value = (relative metric gain) x (client's own
dollars-per-metric-point figure); cost = data licensing + pipeline maintenance at
consulting rates + one skew incident per new external join in year one. A family
with positive fold-std-cleared accuracy and negative expected value still dies.
The client's dollars-per-metric-point figure is the one number to extract in
discovery; without it every stopping argument reverts to taste.
