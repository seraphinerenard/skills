#!/usr/bin/env python3
"""Out-of-fold target encoder with m-estimate smoothing.

pip install: numpy pandas scikit-learn

The encoding for category c is
    enc(c) = (n_c * ybar_c + m * prior) / (n_c + m)
where n_c is the category's row count, ybar_c its target mean, prior the
global target mean, and m the smoothing weight in pseudo-observations
(Micci-Barreca 2001). A category seen 8 times pulls most of the way to the
prior at m=20; a category seen 2000 times keeps its own mean.

Training rows receive out-of-fold encodings: fold k's rows are encoded with
statistics computed on the other folds only, so no row's own target reaches
its feature. Inference rows receive full-training-data encodings. Skipping
the OOF step feeds each row a lightly averaged copy of its own label and
inflates validation scores on high-cardinality columns; the demo below
measures the inflation on pure noise.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, KFold


class OOFTargetEncoder:
    def __init__(self, cols, m=20.0, n_splits=5, group_col=None, seed=0):
        self.cols = list(cols)
        self.m = float(m)
        self.n_splits = n_splits
        self.group_col = group_col
        self.seed = seed
        self.prior_ = None
        self.stats_ = {}

    def _encode(self, series, stats):
        n = series.map(stats["n"]).fillna(0.0).to_numpy(dtype=float)
        s = series.map(stats["sum"]).fillna(0.0).to_numpy(dtype=float)
        return (s + self.m * self.prior_) / (n + self.m)

    @staticmethod
    def _stats(series, y):
        g = y.groupby(series, observed=True)
        return {"n": g.size().astype(float), "sum": g.sum().astype(float)}

    def fit_transform(self, X, y):
        X, y = X.reset_index(drop=True), pd.Series(np.asarray(y, dtype=float))
        self.prior_ = float(y.mean())
        out = pd.DataFrame(index=X.index)
        if self.group_col is not None:
            splits = GroupKFold(self.n_splits).split(X, y, X[self.group_col])
        else:
            splits = KFold(self.n_splits, shuffle=True, random_state=self.seed).split(X)
        splits = list(splits)
        for c in self.cols:
            enc = np.full(len(X), np.nan)
            for tr, va in splits:
                enc[va] = self._encode(X[c].iloc[va], self._stats(X[c].iloc[tr], y.iloc[tr]))
            out[f"{c}_te"] = enc
            self.stats_[c] = self._stats(X[c], y)
        return out

    def transform(self, X):
        out = pd.DataFrame(index=X.index)
        for c in self.cols:
            out[f"{c}_te"] = self._encode(X[c], self.stats_[c])
        return out


if __name__ == "__main__":
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score

    # worked smoothing arithmetic, prior=0.20, m=20
    prior, m = 0.20, 20.0
    for n_c, ybar in [(8, 0.50), (2000, 0.31)]:
        enc = (n_c * ybar + m * prior) / (n_c + m)
        print(f"n={n_c:>4} mean={ybar:.2f} -> enc={enc:.4f}")

    # leakage measurement: 300-level categorical with NO relation to y
    rng = np.random.default_rng(0)
    n = 6000
    df = pd.DataFrame({"cat": rng.integers(0, 300, n).astype(str)})
    y = pd.Series(rng.normal(size=n))
    tr, ho = np.arange(4000), np.arange(4000, n)

    # naive: fit on all training rows, encode the same rows (own label included)
    te = OOFTargetEncoder(["cat"], m=0.0)
    te.prior_ = float(y.iloc[tr].mean())
    te.stats_["cat"] = te._stats(df["cat"].iloc[tr], y.iloc[tr])
    naive_tr = te.transform(df.iloc[tr])
    naive_ho = te.transform(df.iloc[ho])

    oof = OOFTargetEncoder(["cat"], m=20.0)
    oof_tr = oof.fit_transform(df.iloc[tr], y.iloc[tr])
    oof_ho = oof.transform(df.iloc[ho])

    for label, ftr, fho in [("naive", naive_tr, naive_ho), ("oof", oof_tr, oof_ho)]:
        corr = np.corrcoef(ftr["cat_te"], y.iloc[tr])[0, 1]
        mdl = LinearRegression().fit(ftr, y.iloc[tr])
        r2_tr = r2_score(y.iloc[tr], mdl.predict(ftr))
        r2_ho = r2_score(y.iloc[ho], mdl.predict(fho))
        print(f"{label:>5}: train corr(feat,y)={corr:+.3f}  "
              f"train R2={r2_tr:+.3f}  holdout R2={r2_ho:+.3f}")
    print("noise categorical: naive encoding manufactures in-sample signal; "
          "OOF encoding reports none")
