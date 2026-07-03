# pip install numpy scipy
"""Monte Carlo risk engine with Gaussian-copula correlation, antithetic
variates, quantile standard errors, and a partial-rank-correlation tornado.

Why a copula and Spearman targets. Clients state dependence as rank
correlation ("when price is high, opex tends to be high"), and Spearman
survives the marginal transforms exactly. A Gaussian copula with latent
Pearson correlation r reproduces a Spearman target rho_s through
    r = 2 * sin(pi * rho_s / 6)
(Kruskal 1958). Feeding the Spearman target straight in as the latent
Pearson value under-correlates the sample by up to ~0.017 at mid range;
small, and free to remove.

Why quantile standard errors. A P90 quoted from 2,000 draws carries Monte
Carlo noise of its own; the asymptotic SE of the p-quantile estimate is
    se = sqrt(p (1 - p) / n) / f(q_p)
with f estimated here by a Gaussian KDE. Report the SE or raise n until the
SE is far below the precision you quote.

Why PRCC for the tornado. Classical Sobol indices assume independent inputs;
with a correlated input set the variance decomposition is no longer unique.
Partial rank correlation controls for the other inputs and stays meaningful
under the monotone-response assumption that holds for most cash-flow models.

Run the demo:  python3 monte_carlo_copula.py
The demo prices a 10-year open-pit project NPV with five correlated inputs.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


def nearest_correlation(m: np.ndarray, eps: float = 1e-10) -> np.ndarray:
    """Eigenvalue clipping to the nearest positive-definite correlation
    matrix. Elicited pairwise correlations are frequently inconsistent as a
    set; clipping is crude next to Higham (2002) alternating projections and
    close enough for elicited two-decimal inputs."""
    w, v = np.linalg.eigh((m + m.T) / 2.0)
    w = np.clip(w, eps, None)
    r = v @ np.diag(w) @ v.T
    d = np.sqrt(np.diag(r))
    r = r / np.outer(d, d)
    np.fill_diagonal(r, 1.0)
    return r


@dataclass
class GaussianCopula:
    """Sample joint draws with given marginals and a Spearman target matrix.

    marginals: list of objects exposing .ppf(u) — scipy frozen distributions
    or EmpiricalMarginal below.
    spearman: target rank-correlation matrix, shape (d, d).
    """
    marginals: list
    spearman: np.ndarray

    def __post_init__(self):
        latent = 2.0 * np.sin(np.pi * np.asarray(self.spearman) / 6.0)
        np.fill_diagonal(latent, 1.0)
        self.chol = np.linalg.cholesky(nearest_correlation(latent))

    def sample(self, n: int, rng: np.random.Generator,
               antithetic: bool = False) -> np.ndarray:
        """Return an (n, d) array. With antithetic=True, draws come in
        (z, -z) pairs; n must be even. Antithetic pairs cut the variance of
        the output MEAN when the model is monotone in its inputs; they do
        nothing useful for tail quantiles, so size n for the quantile SE
        regardless."""
        d = len(self.marginals)
        if antithetic:
            if n % 2:
                raise ValueError("antithetic sampling needs even n")
            z_half = rng.standard_normal((n // 2, d))
            z = np.vstack([z_half, -z_half])
        else:
            z = rng.standard_normal((n, d))
        u = stats.norm.cdf(z @ self.chol.T)
        return np.column_stack(
            [m.ppf(u[:, j]) for j, m in enumerate(self.marginals)])


class EmpiricalMarginal:
    """Inverse-CDF sampling from observed data by linear interpolation
    between order statistics. Use when 200+ observations exist and no
    parametric family fits the tails; below that, fit a distribution and
    defend the tail choice explicitly."""

    def __init__(self, data: np.ndarray):
        self.x = np.sort(np.asarray(data, dtype=float))
        n = len(self.x)
        self.p = (np.arange(1, n + 1) - 0.5) / n

    def ppf(self, u: np.ndarray) -> np.ndarray:
        return np.interp(u, self.p, self.x)


def quantile_se(sample: np.ndarray, p: float) -> float:
    """Asymptotic SE of the p-quantile, density estimated by Gaussian KDE."""
    q = np.quantile(sample, p)
    f = stats.gaussian_kde(sample)(q)[0]
    return float(np.sqrt(p * (1 - p) / len(sample)) / f)


def prcc(inputs: np.ndarray, output: np.ndarray) -> np.ndarray:
    """Partial rank correlation coefficient of each input with the output,
    controlling for the other inputs. Standard implementation: rank
    everything, then correlate regression residuals."""
    n, d = inputs.shape
    rx = np.apply_along_axis(stats.rankdata, 0, inputs)
    ry = stats.rankdata(output)
    out = np.empty(d)
    for j in range(d):
        others = np.column_stack(
            [np.ones(n), np.delete(rx, j, axis=1)])
        beta_x, *_ = np.linalg.lstsq(others, rx[:, j], rcond=None)
        beta_y, *_ = np.linalg.lstsq(others, ry, rcond=None)
        res_x = rx[:, j] - others @ beta_x
        res_y = ry - others @ beta_y
        out[j] = np.corrcoef(res_x, res_y)[0, 1]
    return out


# --- demo: open-pit project NPV ----------------------------------------------

def npv_model(x: np.ndarray) -> np.ndarray:
    """Vectorized 10-year DCF. Columns of x:
    0 grade (g/t), 1 recovery (fraction), 2 price (USD/oz),
    3 opex (USD/t milled), 4 capex (MUSD)."""
    grade, rec, price, opex, capex = x.T
    tonnes = 8.0e6                      # t milled per year
    ounces = tonnes * grade / 31.1035 * rec
    cash = (ounces * price - tonnes * opex) / 1e6   # MUSD per year
    annuity = (1.0 / 1.08 ** np.arange(1, 11)).sum()
    return cash * annuity - capex


if __name__ == "__main__":
    rng = np.random.default_rng(7)
    names = ["grade", "recovery", "price", "opex", "capex"]
    marginals = [
        stats.lognorm(s=0.12, scale=1.05),          # grade g/t
        stats.beta(a=40, b=8),                      # recovery ~0.83
        stats.lognorm(s=0.20, scale=2300.0),        # gold price USD/oz
        stats.norm(loc=38.0, scale=4.0),            # opex USD/t
        stats.triang(c=0.3, loc=900, scale=500),    # capex MUSD
    ]
    sp = np.eye(5)
    sp[0, 1] = sp[1, 0] = 0.30    # higher grade mills recover better
    sp[2, 3] = sp[3, 2] = 0.50    # price and opex share cost inflation
    sp[3, 4] = sp[4, 3] = 0.40    # opex and capex share input costs
    cop = GaussianCopula(marginals, sp)

    n = 20_000
    x = cop.sample(n, rng)
    npv = npv_model(x)

    print("=== correlation check (target vs achieved Spearman) ===")
    achieved = stats.spearmanr(x).statistic
    for (i, j) in [(0, 1), (2, 3), (3, 4)]:
        print(f"{names[i]:>8} ~ {names[j]:<8} target {sp[i, j]:.2f}  "
              f"achieved {achieved[i, j]:+.3f}")

    print(f"\n=== NPV distribution, n = {n:,} ===")
    for p in (0.10, 0.50, 0.90):
        q = np.quantile(npv, p)
        print(f"P{int(p * 100):02d}: {q:8,.0f} MUSD  "
              f"(quantile SE {quantile_se(npv, p):.0f} MUSD)")
    print(f"P(NPV < 0) = {(npv < 0).mean():.3f}")

    print("\n=== PRCC tornado (drivers of NPV spread) ===")
    for name, r in sorted(zip(names, prcc(x, npv)),
                          key=lambda t: -abs(t[1])):
        print(f"{name:>8}: {r:+.3f}")

    print("\n=== antithetic variates on the NPV mean ===")
    reps = 200
    m_plain = np.array([npv_model(cop.sample(1000, rng)).mean()
                        for _ in range(reps)])
    m_anti = np.array([npv_model(cop.sample(1000, rng, antithetic=True)).mean()
                       for _ in range(reps)])
    vr = m_plain.var(ddof=1) / m_anti.var(ddof=1)
    print(f"variance of the mean estimator, plain / antithetic: {vr:.1f}x "
          f"(equal n = 1,000 per estimate, {reps} repeats)")
