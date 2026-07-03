#!/usr/bin/env python3
"""Monte Carlo market sizing with correlated assumptions via a Gaussian copula.

pip install: numpy scipy

Why correlation is the whole point: sizing models multiply 3-6 uncertain
inputs, and consultants routinely sample them independently. Real assumptions
co-move (a product priced high reaches fewer buyers; a bigger addressable
base usually means smaller average accounts), and independence understates
the spread of the product when correlations are positive and overstates it
when they are negative. The copula below imposes the stated correlations on
otherwise arbitrary marginals.

Mechanics:
  * Marginals: any scipy frozen distribution; helpers below build triangular,
    beta-PERT, and lognormal-from-P10/P90 marginals, which cover most sizing
    interviews ("low / most likely / high" or "I'd put 10:90 odds between
    A and B").
  * Copula: draw correlated standard normals (Cholesky), map through the
    normal CDF to uniforms, then through each marginal's inverse CDF. The
    stated matrix is the copula correlation; the achieved Spearman rank
    correlation lands within about 1% of it (rho_S = 6/pi * arcsin(rho/2)),
    close enough for assumptions elicited as ranges.
  * Inconsistent pairwise correlations: elicited matrices are often not
    positive semi-definite (A~B = 0.8, B~C = 0.8, A~C = -0.5 is impossible).
    The sampler clips negative eigenvalues and rescales to unit diagonal,
    then reports the largest adjustment so the elicitation can be revisited
    when the fix is material.
  * Presentation: report P10 / P50 / P90 rounded to two significant figures.
    A Monte Carlo on ranged assumptions carries no more precision than that,
    and quoting $4,273,518,000 from it is false precision.

Contribution to variance is the normalized squared Spearman correlation of
each input with the output; under correlated inputs the shares overlap, so
read them as a ranking, and confirm with a one-at-a-time tornado
(assets/dcf_tornado.py has the printer) before presenting.
"""
from __future__ import annotations

import numpy as np
from scipy import stats

Z_90 = 1.2815515655446004  # standard normal 90th percentile


def triangular(low: float, mode: float, high: float):
    return stats.triang(c=(mode - low) / (high - low), loc=low,
                        scale=high - low)


def pert(low: float, mode: float, high: float, lamb: float = 4.0):
    """Beta-PERT: smoother than triangular, thinner tails, same elicitation."""
    a = 1 + lamb * (mode - low) / (high - low)
    b = 1 + lamb * (high - mode) / (high - low)
    return stats.beta(a, b, loc=low, scale=high - low)


def lognormal_p10_p90(p10: float, p90: float):
    """Lognormal pinned to elicited 10th and 90th percentiles."""
    mu = (np.log(p10) + np.log(p90)) / 2
    sigma = (np.log(p90) - np.log(p10)) / (2 * Z_90)
    return stats.lognorm(s=sigma, scale=float(np.exp(mu)))


def nearest_correlation(C: np.ndarray) -> tuple[np.ndarray, float]:
    """Eigenvalue-clipped positive semi-definite repair, unit diagonal.

    Returns the repaired matrix and the largest absolute entry change, so a
    material repair (> ~0.05) sends the elicitation back to the client.
    """
    w, V = np.linalg.eigh((C + C.T) / 2)
    w = np.clip(w, 1e-10, None)
    A = V @ np.diag(w) @ V.T
    d = np.sqrt(np.diag(A))
    A = A / np.outer(d, d)
    np.fill_diagonal(A, 1.0)
    return A, float(np.max(np.abs(A - C)))


def sample_correlated(dists: dict, corr: dict[tuple[str, str], float],
                      n: int = 100_000, seed: int = 7) -> dict[str, np.ndarray]:
    """Sample named marginals under the stated pairwise copula correlations.

    corr holds the nonzero pairs only, e.g. {("adoption", "acv"): -0.35};
    unstated pairs default to independence.
    """
    names = list(dists)
    k = len(names)
    C = np.eye(k)
    pos = {nm: i for i, nm in enumerate(names)}
    for (a, b), r in corr.items():
        C[pos[a], pos[b]] = C[pos[b], pos[a]] = r
    C, adjustment = nearest_correlation(C)
    if adjustment > 0.05:
        print(f"warning: correlation matrix repaired; largest entry moved "
              f"{adjustment:.2f}. Revisit the elicited pairs.")
    L = np.linalg.cholesky(C)
    rng = np.random.default_rng(seed)
    Z = rng.standard_normal((n, k)) @ L.T
    U = stats.norm.cdf(Z)
    return {nm: dists[nm].ppf(U[:, j]) for j, nm in enumerate(names)}


def round_sig(x: float, sig: int = 2) -> float:
    if x == 0:
        return 0.0
    from math import floor, log10
    return round(x, -int(floor(log10(abs(x)))) + (sig - 1))


def summarize(y: np.ndarray, unit: str = "$", sig: int = 2) -> dict:
    p10, p50, p90 = np.percentile(y, [10, 50, 90])
    return {
        "p10": round_sig(float(p10), sig),
        "p50": round_sig(float(p50), sig),
        "p90": round_sig(float(p90), sig),
        "mean": round_sig(float(y.mean()), sig),
        "unit": unit,
    }


def contribution_to_variance(X: dict[str, np.ndarray],
                             y: np.ndarray) -> dict[str, float]:
    raw = {nm: stats.spearmanr(x, y).statistic ** 2 for nm, x in X.items()}
    total = sum(raw.values())
    return {nm: v / total for nm, v in
            sorted(raw.items(), key=lambda kv: -kv[1])}


if __name__ == "__main__":
    # Reachable-spend sizing for an ML pricing product sold to mid-market
    # manufacturers in one region. Serviceable market = accounts that fit the
    # ICP x share adopting any such tool inside the horizon x annual contract
    # value. Adoption and price co-move negatively: the cheaper the product,
    # the further it spreads.
    dists = {
        "accounts": triangular(1_800, 2_600, 3_800),
        "adoption": pert(0.04, 0.10, 0.22),
        "acv": lognormal_p10_p90(30_000, 120_000),
    }
    corr = {
        ("adoption", "acv"): -0.35,
        ("accounts", "adoption"): 0.15,
    }

    X = sample_correlated(dists, corr, n=200_000, seed=7)
    y = X["accounts"] * X["adoption"] * X["acv"]

    s = summarize(y, unit="$/yr")
    print("serviceable annual spend, correlated assumptions:")
    print(f"  P10 {s['p10']:>14,.0f}  P50 {s['p50']:>14,.0f}  "
          f"P90 {s['p90']:>14,.0f}  mean {s['mean']:>14,.0f}")

    Xi = sample_correlated(dists, {}, n=200_000, seed=7)
    yi = Xi["accounts"] * Xi["adoption"] * Xi["acv"]
    si = summarize(yi)
    print("same marginals, independence assumed:")
    print(f"  P10 {si['p10']:>14,.0f}  P50 {si['p50']:>14,.0f}  "
          f"P90 {si['p90']:>14,.0f}  mean {si['mean']:>14,.0f}")

    point = 2_600 * 0.10 * 60_000
    print(f"\npoint estimate from modes/typical price: {point:,.0f} "
          f"(sits at the {stats.percentileofscore(y, point):.0f}th "
          "percentile of the distribution)")

    print("\ncontribution to variance (rank on it; confirm with a tornado):")
    for nm, share in contribution_to_variance(X, y).items():
        print(f"  {nm:>9}: {share:5.1%}")

    r = stats.spearmanr(X["adoption"], X["acv"]).statistic
    print(f"\nachieved Spearman adoption~acv: {r:+.3f} (stated -0.35)")
