#!/usr/bin/env python3
"""Adversarial validation: can a classifier tell training rows from test rows?

pip install: numpy pandas scikit-learn

Cross-validated AUC of the train-vs-test classifier measures distribution
shift over the feature set. Practitioner reading of the number:

    AUC below 0.55   train and test are exchangeable on these features
    0.55 to 0.70     mild shift; inspect the top features, usually time proxies
    above 0.70       material shift; drop or transform culprits, or reweight

Permutation importance on the adversarial model names the culprits. The
usual first finding on panel data is a raw date ordinal or a cumulative
counter: perfectly separable by construction, and the same feature that
breaks a tree model at extrapolation time.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import OrdinalEncoder


def adversarial_validation(train, test, features=None, n_splits=5, seed=0):
    """Returns (oof_auc, importance frame sorted by mean importance)."""
    features = features or [c for c in train.columns if c in test.columns]
    X = pd.concat([train[features], test[features]], ignore_index=True)
    y = np.r_[np.zeros(len(train)), np.ones(len(test))]

    obj_cols = [c for c in features if X[c].dtype == object or str(X[c].dtype) == "category"]
    if obj_cols:
        X[obj_cols] = OrdinalEncoder(
            handle_unknown="use_encoded_value", unknown_value=-1
        ).fit_transform(X[obj_cols].astype(str))
    X = X.astype(float)

    oof = np.zeros(len(X))
    imps = []
    cv = StratifiedKFold(n_splits, shuffle=True, random_state=seed)
    for tr, va in cv.split(X, y):
        mdl = HistGradientBoostingClassifier(max_iter=200, random_state=seed)
        mdl.fit(X.iloc[tr], y[tr])
        oof[va] = mdl.predict_proba(X.iloc[va])[:, 1]
        pi = permutation_importance(
            mdl, X.iloc[va], y[va], n_repeats=5, random_state=seed,
            scoring="roc_auc",
        )
        imps.append(pi.importances_mean)
    auc = roc_auc_score(y, oof)
    imp = (
        pd.DataFrame({"feature": features, "importance": np.mean(imps, axis=0)})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )
    return auc, imp


if __name__ == "__main__":
    rng = np.random.default_rng(0)
    n = 4000
    train = pd.DataFrame({
        "x1": rng.normal(size=n),
        "x2": rng.gamma(2.0, 1.0, size=n),
        "x3": rng.normal(0.0, 1.0, size=n),
        "date_ordinal": np.arange(n) // 4,          # days 0..999
    })
    test = pd.DataFrame({
        "x1": rng.normal(size=n),
        "x2": rng.gamma(2.0, 1.0, size=n),
        "x3": rng.normal(0.6, 1.0, size=n),          # mild mean shift
        "date_ordinal": 1000 + np.arange(n) // 16,   # days 1000..1249
    })

    feats = list(train.columns)
    for stage in range(3):
        auc, imp = adversarial_validation(train, test, feats)
        top = imp.iloc[0]
        print(f"features={feats}")
        print(f"  adversarial AUC={auc:.3f}  top culprit={top.feature} "
              f"(perm importance {top.importance:.3f})")
        if auc < 0.55:
            print("  verdict: exchangeable, stop here")
            break
        feats = [f for f in feats if f != top.feature]
        print(f"  dropping {top.feature} and re-running")
