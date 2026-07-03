#!/usr/bin/env python3
"""Null-importance screen: shuffled-target baselines for feature importance.

pip install: numpy pandas scikit-learn

Impurity importances from tree ensembles reward cardinality and variance
even when a column carries no signal: a random 2000-level ID column earns
splits by chance. The null distribution prices that inflation. Shuffle the
target n_null times, refit, and record each feature's importance under a
target it cannot predict (Altmann et al. 2010; Grellier's null-importances
protocol). Keep a feature only when its actual importance clears the upper
tail of its own null distribution.

One trap this module works around: sklearn's feature_importances_ are
normalized to sum to one across features, so a strong feature pushes a
weak-but-real feature's share below the equal-share null and the test
rejects it spuriously. The screen therefore reads unnormalized impurity
gains from each tree (compute_feature_importances(normalize=False)), the
same quantity LightGBM reports as gain importance.
"""

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor


def _raw_gain(model, X, y):
    m = clone(model).fit(X, y)
    trees = getattr(m, "estimators_", None)
    if trees is not None and hasattr(trees[0], "tree_"):
        return np.mean(
            [t.tree_.compute_feature_importances(normalize=False) for t in trees],
            axis=0,
        )
    return m.feature_importances_


def null_importance(X, y, model=None, n_null=30, keep_pct=95.0, seed=0):
    """Returns a frame with actual importance, the null distribution summary,
    and a keep flag per feature. `model` defaults to a RandomForest sized for
    the screen; any tree ensemble or estimator with feature_importances_
    works, with the unnormalized-gain path used whenever trees are exposed."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y)
    if model is None:
        cls = len(np.unique(y)) <= 20 and np.issubdtype(y.dtype, np.integer)
        Est = RandomForestClassifier if cls else RandomForestRegressor
        model = Est(n_estimators=100, max_depth=10, max_features=0.5,
                    n_jobs=-1, random_state=seed)

    actual = _raw_gain(model, X, y)
    nulls = np.empty((n_null, X.shape[1]))
    for i in range(n_null):
        nulls[i] = _raw_gain(model, X, rng.permutation(y))

    thresh = np.percentile(nulls, keep_pct, axis=0)
    out = pd.DataFrame({
        "feature": list(X.columns),
        "actual": actual,
        "null_mean": nulls.mean(axis=0),
        f"null_p{keep_pct:.0f}": thresh,
        "ratio": actual / np.maximum(thresh, 1e-12),
        "keep": actual > thresh,
    })
    return out.sort_values("actual", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    n = 5000
    X = pd.DataFrame({
        "x1": rng.normal(size=n),
        "x2": rng.normal(size=n),
        "x3": rng.normal(size=n),
        "high_card_id": rng.integers(0, 2000, size=n).astype(float),
        "noise_a": rng.uniform(size=n),
        "noise_b": rng.uniform(size=n),
    })
    y = X["x1"] + 0.5 * X["x2"] + 0.25 * X["x3"] + rng.normal(0, 1.0, size=n)

    res = null_importance(X, y, n_null=30)
    with pd.option_context("display.float_format", "{:.4f}".format):
        print(res.to_string(index=False))
    r = res.set_index("feature")
    print(f"\nhigh_card_id: actual={r.loc['high_card_id', 'actual']:.4f} vs "
          f"null_p95={r.loc['high_card_id', 'null_p95']:.4f} -> "
          f"keep={bool(r.loc['high_card_id', 'keep'])}")
    print(f"x3 (weak but real): actual={r.loc['x3', 'actual']:.4f} vs "
          f"null_p95={r.loc['x3', 'null_p95']:.4f} -> "
          f"keep={bool(r.loc['x3', 'keep'])}")
    print(f"kept: {sorted(res.loc[res.keep, 'feature'])}")
