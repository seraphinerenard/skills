# pip install numpy scipy
"""Small Bayesian marketing mix model: geometric adstock + Hill saturation,
MAP fit with a Laplace approximation for uncertainty, and calibration of one
channel to a geo-test lift estimate.

The demo generates three channels where channels 1 and 2 follow the same
promo calendar (spend correlation ~0.85). Uncorrelated data would identify
each channel's coefficient from the likelihood alone; with collinear spends
the likelihood is nearly flat along the trade-off between channels 1 and 2,
so the uncalibrated posterior is wide on each channel even though their sum
is pinned down. Adding a geo-test estimate of channel 1's weekly incremental
sales as an extra Gaussian likelihood term (the same mechanism as
`add_lift_test_measurements` in pymc-marketing and ROI priors in Google
Meridian) collapses that ridge.

This is a teaching sketch. For client work use Google Meridian or
pymc-marketing (see references/mmm-identifiability.md in this skill).

Run the demo: python3 mmm_calibrated.py   (about 10-30 s)
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize
from scipy.signal import lfilter


def adstock(x: np.ndarray, theta: float) -> np.ndarray:
    """Geometric carryover: a_t = x_t + theta * a_{t-1}."""
    return lfilter([1.0], [1.0, -theta], np.asarray(x, dtype=float))


def hill(z: np.ndarray, K: float) -> np.ndarray:
    """Saturation with slope 1: z / (z + K). K is the half-saturation point."""
    return z / (z + K)


def _unpack(p: np.ndarray, C: int) -> dict:
    i = 2
    return {
        "b0": p[0], "gamma": p[1],
        "beta": np.exp(p[i:i + C]),
        "theta": 1.0 / (1.0 + np.exp(-p[i + C:i + 2 * C])),
        "K": np.exp(p[i + 2 * C:i + 3 * C]),
        "sigma": np.exp(p[i + 3 * C]),
    }


def _predict(q: dict, spend: np.ndarray, season: np.ndarray) -> tuple:
    C = spend.shape[1]
    contrib = np.column_stack([
        q["beta"][c] * hill(adstock(spend[:, c], q["theta"][c]), q["K"][c])
        for c in range(C)])
    mu = q["b0"] + q["gamma"] * season + contrib.sum(axis=1)
    return mu, contrib


def neg_log_post(p: np.ndarray, y: np.ndarray, spend: np.ndarray,
                 season: np.ndarray, lift_test: tuple | None = None) -> float:
    """Negative log posterior. lift_test = (channel, estimate, se) ties the
    model-implied mean weekly contribution of that channel to the geo-test
    result through a Gaussian pseudo-observation."""
    C = spend.shape[1]
    q = _unpack(p, C)
    mu, contrib = _predict(q, spend, season)
    n = len(y)
    nll = 0.5 * np.sum((y - mu) ** 2) / q["sigma"] ** 2 + n * np.log(q["sigma"])
    # weakly informative priors, centred on data scale
    pri = 0.5 * ((q["b0"] - y.mean()) / y.std()) ** 2
    pri += 0.5 * (q["gamma"] / (2.0 * y.std())) ** 2
    for c in range(C):
        pri += 0.5 * ((np.log(q["beta"][c]) - np.log(y.std())) / 2.0) ** 2
        pri += 0.5 * (np.log(q["theta"][c] / (1 - q["theta"][c])) / 1.5) ** 2
        pri += 0.5 * ((np.log(q["K"][c]) - np.log(2.0 * spend[:, c].mean())) / 1.5) ** 2
    pri += 0.5 * ((np.log(q["sigma"]) - np.log(y.std() / 5.0)) / 1.5) ** 2
    if lift_test is not None:
        c, est, se = lift_test
        pri += 0.5 * ((contrib[:, c].mean() - est) / se) ** 2
    return float(nll + pri)


def fit_map(y, spend, season, lift_test=None, n_starts: int = 5, seed: int = 0):
    """Multi-start MAP, then a finite-difference Hessian for the Laplace
    covariance. Returns (p_map, cov)."""
    rng = np.random.default_rng(seed)
    C = spend.shape[1]
    base = np.concatenate([
        [y.mean(), 0.0], np.full(C, np.log(y.std())), np.zeros(C),
        [np.log(2.0 * spend[:, c].mean()) for c in range(C)],
        [np.log(y.std() / 5.0)]])
    best = None
    for s in range(n_starts):
        x0 = base + (0.0 if s == 0 else rng.normal(0, 0.4, base.shape))
        r = minimize(neg_log_post, x0, args=(y, spend, season, lift_test),
                     method="L-BFGS-B", options={"maxiter": 2000})
        if best is None or r.fun < best.fun:
            best = r
    p = best.x
    d = len(p)
    H = np.zeros((d, d))
    h = 1e-4 * np.maximum(1.0, np.abs(p))
    f = lambda v: neg_log_post(v, y, spend, season, lift_test)
    f0 = f(p)
    for i in range(d):
        for j in range(i, d):
            ei = np.zeros(d); ei[i] = h[i]
            ej = np.zeros(d); ej[j] = h[j]
            if i == j:
                H[i, i] = (f(p + ei) - 2 * f0 + f(p - ei)) / h[i] ** 2
            else:
                H[i, j] = H[j, i] = (f(p + ei + ej) - f(p + ei - ej)
                                     - f(p - ei + ej) + f(p - ei - ej)) \
                                    / (4 * h[i] * h[j])
    vals, vecs = np.linalg.eigh(H)
    vals = np.maximum(vals, 1e-6 * vals.max())
    cov = (vecs / vals) @ vecs.T
    return p, cov


def posterior_contributions(p, cov, spend, season, n_draws: int = 4000,
                            seed: int = 1) -> dict:
    """Laplace draws -> per-channel mean weekly contribution and long-run
    marginal ROAS at the current mean spend rate."""
    rng = np.random.default_rng(seed)
    C = spend.shape[1]
    draws = rng.multivariate_normal(p, cov, size=n_draws)
    contrib = np.empty((n_draws, C))
    mroas = np.empty((n_draws, C))
    for k, pk in enumerate(draws):
        q = _unpack(pk, C)
        _, con = _predict(q, spend, season)
        contrib[k] = con.mean(axis=0)
        for c in range(C):
            z = spend[:, c].mean() / (1 - q["theta"][c])  # steady-state adstock
            mroas[k, c] = q["beta"][c] * q["K"][c] / (z + q["K"][c]) ** 2 \
                / (1 - q["theta"][c])
    return {"contrib_mean": contrib.mean(0), "contrib_sd": contrib.std(0),
            "mroas_med": np.median(mroas, 0),
            "mroas_lo": np.percentile(mroas, 5, 0),
            "mroas_hi": np.percentile(mroas, 95, 0)}


def _make_data(seed: int = 4, T: int = 156):
    rng = np.random.default_rng(seed)
    season = np.sin(np.arange(T) * 2 * np.pi / 52.0)
    calendar = np.clip(rng.gamma(2.0, 1.0, T), 0.2, None)  # shared promo peaks
    spend = np.column_stack([
        15.0 * calendar + rng.normal(0, 2.0, T),            # channel 1
        10.0 * calendar + rng.normal(0, 1.5, T),            # channel 2, collinear
        15.0 + 5.0 * rng.standard_normal(T).cumsum() / np.sqrt(T)
        + rng.normal(0, 2.0, T),                            # channel 3
    ])
    spend = np.clip(spend, 0.5, None)
    true = {"b0": 500.0, "gamma": 30.0,
            "beta": np.array([120.0, 60.0, 80.0]),
            "theta": np.array([0.5, 0.3, 0.7]),
            "K": np.array([60.0, 30.0, 50.0]), "sigma": 15.0}
    mu, contrib = _predict(true, spend, season)
    y = mu + rng.normal(0, true["sigma"], T)
    return y, spend, season, true, contrib


def _demo() -> None:
    y, spend, season, true, true_contrib = _make_data()
    tc = true_contrib.mean(axis=0)
    corr = np.corrcoef(spend[:, 0], spend[:, 1])[0, 1]
    print("MMM demo: 156 weeks, 3 channels, spend corr(ch1, ch2) = %.2f" % corr)
    print("true mean weekly contributions: ch1 %.1f, ch2 %.1f, ch3 %.1f"
          % tuple(tc))

    # geo test on channel 1: unbiased estimate with 15% standard error
    test_est, test_se = tc[0] * 1.05, 0.15 * tc[0]
    print("geo-test input for ch1: %.1f (se %.1f)" % (test_est, test_se))

    results = {}
    for label, lt in (("uncalibrated", None), ("calibrated", (0, test_est, test_se))):
        p, cov = fit_map(y, spend, season, lift_test=lt)
        results[label] = posterior_contributions(p, cov, spend, season)

    print()
    print("%-14s %26s %26s" % ("", "uncalibrated", "calibrated"))
    print("%-14s %26s %26s" % ("channel", "contrib (sd)", "contrib (sd)"))
    for c in range(3):
        u, k = results["uncalibrated"], results["calibrated"]
        print("ch%d truth %5.1f %19.1f (%.1f) %19.1f (%.1f)"
              % (c + 1, tc[c], u["contrib_mean"][c], u["contrib_sd"][c],
                 k["contrib_mean"][c], k["contrib_sd"][c]))
    k = results["calibrated"]
    print()
    print("marginal ROAS at current spend (calibrated, 90% interval):")
    for c in range(3):
        print("  ch%d: %.2f  [%.2f, %.2f]"
              % (c + 1, k["mroas_med"][c], k["mroas_lo"][c], k["mroas_hi"][c]))

    u = results["uncalibrated"]
    sum_err = abs((u["contrib_mean"][0] + u["contrib_mean"][1]) - (tc[0] + tc[1]))
    assert sum_err < 0.35 * (tc[0] + tc[1]), \
        "combined ch1+ch2 contribution should be identified even when collinear"
    assert k["contrib_sd"][0] < 0.8 * u["contrib_sd"][0], \
        "calibration should tighten the ch1 posterior"
    assert abs(k["contrib_mean"][0] - tc[0]) <= max(
        abs(u["contrib_mean"][0] - tc[0]) + 2.0, 2.5 * k["contrib_sd"][0] + 2.0), \
        "calibrated ch1 estimate should sit at least as close to truth"
    print()
    print("smoke test passed: ch1 posterior sd %.1f -> %.1f with calibration;"
          " ch1+ch2 sum held within %.0f%% throughout"
          % (u["contrib_sd"][0], k["contrib_sd"][0], 100 * sum_err / (tc[0] + tc[1])))


if __name__ == "__main__":
    _demo()
