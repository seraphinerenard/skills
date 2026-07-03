#!/usr/bin/env python3
"""Hourly foot-traffic model for labour scheduling: Poisson GLM plus
newsvendor staffing quantile.

pip install numpy pandas

Design choices this module encodes:
  * Hour-of-week dummies (168) carry the base shape; weather, paydays,
    school calendar, and holiday ramp enter as multiplicative log-linear
    terms. A Poisson GLM fit by IRLS stays fully inspectable, which matters
    when a store manager challenges the Tuesday 2pm number.
  * The scheduling decision consumes a QUANTILE of the predictive
    distribution. With understaffing cost Cu and overstaffing cost Co per
    customer of capacity, the newsvendor quantile is q* = Cu/(Cu+Co).
    Staffing to the mean forecast understaffs every peak by construction.
  * Overdispersion relative to Poisson is estimated from residuals and the
    predictive quantile comes from a negative binomial around the GLM mean.
  * Evaluation is the realized staffing cost against the same rule applied
    to a seasonal-naive forecast (same hour last week), because MAE ranks
    models differently than the money does.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(3)


# ------------------------------------------------------------- features ----

def build_features(df: pd.DataFrame) -> np.ndarray:
    """df columns: hour_of_week (0..167), temp_c, precip_mm, payday,
    school_in, days_to_holiday. Returns design matrix with intercept."""
    n = len(df)
    how = np.zeros((n, 167))
    hw = df["hour_of_week"].to_numpy()
    mask = hw > 0
    how[np.arange(n)[mask], hw[mask] - 1] = 1.0   # hour 0 is the reference
    temp = df["temp_c"].to_numpy(dtype=float)
    cols = [
        np.ones(n),
        (temp - 15.0) / 10.0,                      # centred temperature
        ((temp - 15.0) / 10.0) ** 2,               # discomfort at both ends
        np.log1p(df["precip_mm"].to_numpy(dtype=float)),
        df["payday"].to_numpy(dtype=float),
        df["school_in"].to_numpy(dtype=float),
        np.exp(-df["days_to_holiday"].to_numpy(dtype=float) / 4.0),
    ]
    return np.column_stack(cols + [how])


def fit_poisson_glm(X: np.ndarray, y: np.ndarray, n_iter: int = 30,
                    ridge: float = 1e-6) -> np.ndarray:
    """IRLS for Poisson regression with log link."""
    beta = np.zeros(X.shape[1])
    beta[0] = np.log(max(y.mean(), 0.1))
    for _ in range(n_iter):
        eta = np.clip(X @ beta, -20, 20)
        mu = np.exp(eta)
        z = eta + (y - mu) / mu
        XtW = X.T * mu
        H = XtW @ X + ridge * np.eye(X.shape[1])
        beta_new = np.linalg.solve(H, XtW @ z)
        if np.max(np.abs(beta_new - beta)) < 1e-8:
            beta = beta_new
            break
        beta = beta_new
    return beta


def predict_mean(X: np.ndarray, beta: np.ndarray) -> np.ndarray:
    return np.exp(np.clip(X @ beta, -20, 20))


def estimate_dispersion(y: np.ndarray, mu: np.ndarray) -> float:
    """NB dispersion k via moments: E[(y-mu)^2] = mu + mu^2/k."""
    alpha = float((((y - mu) ** 2 - mu).sum()) / max((mu**2).sum(), 1e-9))
    alpha = float(np.clip(alpha, 1e-6, 5.0))
    return 1.0 / alpha


def nb_quantile(mu: np.ndarray, k: float, q: float) -> np.ndarray:
    """NB quantile by recursive pmf summation, vectorized over mu."""
    mu = np.atleast_1d(np.asarray(mu, dtype=float))
    p_fail = mu / (mu + k)
    pmf = (k / (k + mu)) ** k
    cdf = pmf.copy()
    out = np.zeros_like(mu)
    done = cdf >= q
    x = 0
    while not done.all() and x < 10000:
        pmf = pmf * (x + k) / (x + 1) * p_fail
        cdf = cdf + pmf
        newly = (~done) & (cdf >= q)
        out[newly] = x + 1
        done |= newly
        x += 1
    out[~done] = x
    return out


# ------------------------------------------------------------- decision ----

def staffing_cost(traffic: np.ndarray, capacity: np.ndarray,
                  cu: float, co: float) -> float:
    """Cost of a staffing plan in customer units of capacity."""
    under = np.maximum(traffic - capacity, 0.0)
    over = np.maximum(capacity - traffic, 0.0)
    return float(cu * under.sum() + co * over.sum())


# ---------------------------------------------------------------- demo ----

def _simulate(n_weeks: int = 104) -> pd.DataFrame:
    """Two years of hourly grocery traffic with weather and calendar."""
    n = n_weeks * 168
    t = np.arange(n)
    how = t % 168
    day = (t // 24) % 7
    hour = t % 24
    doy = (t // 24) % 365

    base = np.where((hour >= 8) & (hour <= 21),
                    40 + 30 * np.exp(-((hour - 17) ** 2) / 8.0)
                    + 15 * np.exp(-((hour - 11) ** 2) / 6.0), 1.0)
    base = base * np.array([0.85, 0.85, 0.9, 0.95, 1.1, 1.35, 1.2])[day]

    temp = 12 + 12 * np.sin(2 * np.pi * (doy - 100) / 365) \
        + RNG.normal(0, 3, n)
    precip = np.where(RNG.random(n) < 0.15, RNG.exponential(2.0, n), 0.0)
    payday = np.isin((t // 24) % 14, [0, 1]).astype(float)
    school_in = (((doy > 5) & (doy < 175)) | (doy > 245)).astype(float)
    days_to_holiday = np.minimum(np.abs(doy - 359), np.abs(doy - 90))

    log_mu = (np.log(base)
              - 0.04 * ((temp - 15) / 10) ** 2
              - 0.06 * np.log1p(precip)
              + 0.13 * payday
              + 0.05 * school_in
              + 0.35 * np.exp(-days_to_holiday / 4.0))
    traffic = RNG.poisson(np.exp(log_mu) * RNG.gamma(8.0, 1 / 8.0, n))

    return pd.DataFrame({
        "traffic": traffic, "hour_of_week": how, "temp_c": temp,
        "precip_mm": precip, "payday": payday, "school_in": school_in,
        "days_to_holiday": days_to_holiday,
    })


def _demo() -> None:
    df = _simulate()
    split = 78 * 168                       # 18 months train, 6 months test
    train, test = df.iloc[:split], df.iloc[split:]

    X_tr, X_te = build_features(train), build_features(test)
    y_tr = train["traffic"].to_numpy(dtype=float)
    y_te = test["traffic"].to_numpy(dtype=float)

    beta = fit_poisson_glm(X_tr, y_tr)
    mu_te = predict_mean(X_te, beta)
    k = estimate_dispersion(y_tr, predict_mean(X_tr, beta))

    # seasonal naive: same hour last week
    naive = df["traffic"].shift(168).iloc[split:].to_numpy(dtype=float)

    # newsvendor: cu = $1.50 per unserved customer, co = $0.72 per unit of
    # excess capacity ($18/h wage over 25 customers served per staff-hour)
    cu, co = 1.50, 0.72
    q_star = cu / (cu + co)
    cap_model = nb_quantile(mu_te, k, q_star)
    cap_naive = np.ceil(naive * (1 + 0.35 * (q_star - 0.5) * 2))

    mae_model = float(np.mean(np.abs(y_te - mu_te)))
    mae_naive = float(np.mean(np.abs(y_te - naive)))
    cost_model = staffing_cost(y_te, cap_model, cu, co)
    cost_naive = staffing_cost(y_te, cap_naive, cu, co)
    cost_mean = staffing_cost(y_te, np.ceil(mu_te), cu, co)

    print(f"newsvendor quantile q* = {q_star:.2f}   NB dispersion k = {k:.1f}")
    print(f"MAE  model {mae_model:6.2f}   naive {mae_naive:6.2f}")
    print(f"cost model@q* ${cost_model:10,.0f}")
    print(f"cost naive    ${cost_naive:10,.0f}   "
          f"(+{cost_naive/cost_model - 1:.0%} vs model)")
    print(f"cost model@mean ${cost_mean:9,.0f}   "
          f"(+{cost_mean/cost_model - 1:.0%}: staffing to the mean "
          f"underserves peaks)")

    payday_lift = np.exp(beta[4]) - 1
    print(f"recovered payday lift: {payday_lift:+.1%} (true +13.9%)")


if __name__ == "__main__":
    _demo()
