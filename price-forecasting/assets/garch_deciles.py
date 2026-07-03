"""GARCH(1,1)-t price deciles at a procurement horizon.

pip install numpy pandas arch
Tested with arch 8.0, numpy 2.5, pandas 3.0.

Procurement clients act on levels ("what could the Q4 average be"), so the
deliverable is a decile table of the PRICE at the horizon, from simulated
GARCH paths compounded from today's level. Two arch-package specifics that
cost time when missed:

  1. Scale. Feed returns in percent (multiply log returns by 100) or pass
     rescale=True; raw decimal returns trigger DataScaleWarning and a fragile
     optimization.
  2. Simulated paths live at forecast.simulations.values with shape
     (n_origins, n_sims, horizon). With reindex=False and a forecast from the
     last observation, n_origins = 1. Analytic forecasts give variance only;
     deciles of the level need the simulated paths.

A Student-t distribution is the default here because commodity and power
returns carry fat tails that a normal GARCH understates at the deciles the
client actually hedges (P10/P90).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from arch import arch_model


def simulate_garch_returns(n: int, rng: np.random.Generator) -> pd.Series:
    """Daily log returns in percent from a GARCH(1,1)-t generator.

    omega 0.05, alpha 0.08, beta 0.90 (persistence 0.98), t dof 6, giving
    unconditional daily vol of about 1.58% and vol clustering.
    """
    omega, alpha, beta, nu = 0.05, 0.08, 0.90, 6.0
    scale = np.sqrt((nu - 2.0) / nu)         # unit-variance t shocks
    h = omega / (1.0 - alpha - beta)
    r = np.empty(n)
    for t in range(n):
        z = rng.standard_t(nu) * scale
        r[t] = np.sqrt(h) * z
        h = omega + alpha * r[t] ** 2 + beta * h
    return pd.Series(r, index=pd.bdate_range("2022-01-03", periods=n))


def price_deciles(returns_pct: pd.Series, spot: float, horizon: int,
                  n_sims: int = 20000, seed: int = 0) -> pd.DataFrame:
    """Fit GARCH(1,1)-t and return price deciles at the horizon.

    returns_pct: daily log returns in percent. spot: today's price level.
    """
    am = arch_model(returns_pct, mean="Constant", vol="GARCH",
                    p=1, q=1, dist="t")
    res = am.fit(disp="off")
    fc = res.forecast(horizon=horizon, method="simulation",
                      simulations=n_sims, reindex=False,
                      random_state=np.random.RandomState(seed))
    paths = fc.simulations.values[0]              # (n_sims, horizon), in %
    terminal = spot * np.exp(paths.sum(axis=1) / 100.0)
    qs = np.arange(0.1, 1.0, 0.1)
    table = pd.DataFrame({
        "decile": [f"P{int(q * 100)}" for q in qs],
        "price": np.quantile(terminal, qs),
    })
    table["vs_spot_pct"] = (table["price"] / spot - 1.0) * 100.0
    return table, res


if __name__ == "__main__":
    rng = np.random.default_rng(3)
    returns = simulate_garch_returns(1250, rng)   # ~5 years daily
    spot = 74.50                                   # e.g. USD/bbl

    table, res = price_deciles(returns, spot=spot, horizon=63)  # ~3 months
    p = res.params
    persistence = p["alpha[1]"] + p["beta[1]"]
    print(f"fitted GARCH(1,1)-t: omega {p['omega']:.4f}  "
          f"alpha {p['alpha[1]']:.3f}  beta {p['beta[1]']:.3f}  "
          f"persistence {persistence:.3f}  t-dof {p['nu']:.1f}")
    ann_vol = float(np.sqrt(res.conditional_volatility.iloc[-1] ** 2 * 252))
    print(f"current conditional vol: {ann_vol:.1f}% annualized")

    print(f"\n63-day price deciles from spot {spot:.2f} "
          f"({len(table)} rows, 20000 simulated paths):")
    print(table.round(2).to_string(index=False))

    p10 = table.loc[table.decile == "P10", "price"].item()
    p90 = table.loc[table.decile == "P90", "price"].item()
    print(f"\nprocurement read: 80% band [{p10:.2f}, {p90:.2f}]; the P90 is "
          f"the budget-risk number, the P10 prices the option value of waiting.")
