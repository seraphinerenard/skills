#!/usr/bin/env python3
# pip install numpy pandas scikit-learn
"""Store clustering for assortment localization, with bootstrap-stability k.

Feature blocks: category sales-mix shares (compositional, so CLR-transformed
before scaling), trade-area demographics, and store attributes. The number
of clusters comes from bootstrap stability (mean adjusted Rand index across
resampled refits, after Hennig 2007) with silhouette and GMM BIC printed
beside it for contrast; stability is the criterion that tracks whether the
segmentation will survive next year's refresh.

Output per cluster: size, and the features that over- or under-index
against the chain average, which is the part category managers act on.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler

CATS = ["produce", "meat", "dairy", "bakery", "frozen", "snacks",
        "beverages", "alcohol", "household", "health"]
DEMO = ["median_income_k", "pct_families", "pop_density_k", "competitors",
        "store_sqft_k"]


def simulate_stores(n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Four latent store archetypes with distinct mix and trade areas."""
    arch = rng.integers(0, 4, n)
    # Dirichlet concentration per archetype over the 10 categories.
    base = np.array([
        [8, 5, 6, 4, 4, 5, 6, 8, 4, 5],   # urban premium: produce, alcohol
        [6, 6, 7, 4, 6, 7, 6, 3, 6, 5],   # suburban family: frozen, snacks
        [4, 6, 5, 3, 7, 6, 6, 3, 8, 5],   # rural value: household, frozen
        [3, 3, 4, 3, 5, 9, 9, 7, 3, 4],   # campus: snacks, beverages
    ], float)
    mix = np.vstack([rng.dirichlet(base[a] * 6) for a in arch])
    income = np.array([rng.normal([95, 82, 54, 48][a], 8) for a in arch])
    families = np.array([rng.normal([0.28, 0.52, 0.42, 0.12][a], 0.05)
                         for a in arch])
    density = np.array([rng.normal([9.5, 2.2, 0.4, 5.0][a], 0.8)
                        for a in arch]).clip(0.05)
    comp = np.array([rng.poisson([6, 3, 1, 4][a]) for a in arch])
    sqft = np.array([rng.normal([28, 55, 42, 22][a], 5) for a in arch])
    df = pd.DataFrame(mix, columns=CATS)
    df[DEMO] = np.column_stack([income, families, density, comp, sqft])
    df["true_archetype"] = arch
    return df


def feature_matrix(df: pd.DataFrame) -> np.ndarray:
    """CLR for the mix block (log share minus row mean log), z-score all."""
    clr = np.log(df[CATS].to_numpy() + 1e-9)
    clr = clr - clr.mean(axis=1, keepdims=True)
    raw = np.column_stack([clr, df[DEMO].to_numpy()])
    return StandardScaler().fit_transform(raw)


def bootstrap_stability(X: np.ndarray, k: int, rng: np.random.Generator,
                        b: int = 40) -> float:
    """Mean ARI between the full-data clustering and cluster labels induced
    by refits on bootstrap resamples (assignment via nearest centroid)."""
    ref = KMeans(k, n_init=20, random_state=0).fit(X)
    aris = []
    for _ in range(b):
        idx = rng.choice(len(X), len(X), replace=True)
        km = KMeans(k, n_init=10,
                    random_state=int(rng.integers(1e6))).fit(X[idx])
        labels = km.predict(X)
        aris.append(adjusted_rand_score(ref.labels_, labels))
    return float(np.mean(aris))


if __name__ == "__main__":
    rng = np.random.default_rng(5)
    df = simulate_stores(200, rng)
    X = feature_matrix(df)

    print(f"{'k':>2} {'stability(ARI)':>15} {'silhouette':>11} "
          f"{'GMM BIC':>10} {'min cluster':>12}")
    results = {}
    for k in range(2, 9):
        stab = bootstrap_stability(X, k, rng)
        km = KMeans(k, n_init=20, random_state=0).fit(X)
        sil = silhouette_score(X, km.labels_)
        bic = GaussianMixture(k, covariance_type="diag",
                              random_state=0).fit(X).bic(X)
        min_frac = np.bincount(km.labels_).min() / len(X)
        results[k] = (stab, min_frac)
        print(f"{k:>2} {stab:>15.3f} {sil:>11.3f} {bic:>10.0f} "
              f"{min_frac:>11.1%}")

    # Choose the largest k that still reclusters almost identically under
    # resampling (ARI >= 0.95) with no runt cluster (<5% of stores).
    # A looser bar (0.80) admits ks that split real archetypes into
    # fragments that will not reproduce at the next refresh.
    ok = [k for k, (s, mf) in results.items() if s >= 0.95 and mf >= 0.05]
    k_star = max(ok) if ok else 2
    print(f"\nchosen k = {k_star} (largest k with ARI >= 0.95 and every "
          f"cluster >= 5% of stores)")

    km = KMeans(k_star, n_init=50, random_state=0).fit(X)
    df["cluster"] = km.labels_
    ari_truth = adjusted_rand_score(df.true_archetype, km.labels_)
    print(f"ARI against the true archetypes: {ari_truth:.2f}\n")

    grand = df[CATS + DEMO].mean()
    for c in range(k_star):
        sub = df[df.cluster == c]
        index = (sub[CATS + DEMO].mean() / grand * 100).round(0)
        over = index.sort_values(ascending=False).head(3)
        under = index.sort_values().head(2)
        desc = ", ".join(f"{f} {v:.0f}" for f, v in over.items())
        udesc = ", ".join(f"{f} {v:.0f}" for f, v in under.items())
        print(f"cluster {c}: {len(sub)} stores | over-indexes (chain=100): "
              f"{desc} | under: {udesc}")
