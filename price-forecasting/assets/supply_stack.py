"""Minimal merit-order supply stack for hourly power price simulation.

pip install numpy pandas
Tested with numpy 2.5, pandas 3.0.

The stack clears residual load (load minus wind minus solar) against thermal
units sorted by marginal cost. Marginal costs come from named inputs:

    CCGT  = gas / 0.55 + 0.36 * carbon      (0.36 tCO2/MWh_e at 55% efficiency)
    OCGT  = gas / 0.38 + 0.52 * carbon
    coal  = coal_fuel / 0.40 + 0.90 * carbon
    lignite: cheap fuel, 1.10 tCO2/MWh_e, so carbon sets its position

which is why a structural model converts a gas or carbon view into a power
view mechanically, something no reduced-form model does. Negative prices
appear when residual load falls below the must-run floor (inflexible plant
plus subsidized renewables bidding down to their opportunity cost), and
spikes appear when residual load climbs into the scarcity segment.

The demo prices two solar build-outs over the same fortnight and computes the
solar capture rate under each, reproducing cannibalization: more solar moves
the clearing point down exactly in the hours solar produces.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

VOLL = 3000.0           # scarcity price cap, EUR/MWh
NEG_BID = -50.0         # subsidized renewables / must-run negative bid floor
MUST_RUN_GW = 3.0       # inflexible thermal that stays on through the night


def build_stack(gas: float, carbon: float, coal_fuel: float = 12.0) -> pd.DataFrame:
    """Thermal stack (name, capacity GW, marginal cost EUR/MWh), sorted."""
    units = [
        ("nuclear", 4.0, 9.0),
        ("lignite", 3.0, 6.0 / 0.38 + 1.10 * carbon),
        ("coal", 4.0, coal_fuel / 0.40 + 0.90 * carbon),
        ("ccgt", 6.0, gas / 0.55 + 0.36 * carbon),
        ("ocgt", 2.5, gas / 0.38 + 0.52 * carbon),
        ("oil_peaker", 1.0, 180.0 + 0.65 * carbon),
    ]
    df = pd.DataFrame(units, columns=["unit", "gw", "mc"]).sort_values("mc")
    df["cum_gw"] = df["gw"].cumsum()
    return df.reset_index(drop=True)


def clear(stack: pd.DataFrame, residual_gw: float) -> float:
    """Clearing price for one hour of residual load (GW)."""
    if residual_gw <= MUST_RUN_GW:
        # Surplus must-run and renewables compete to stay online.
        depth = (MUST_RUN_GW - residual_gw) / MUST_RUN_GW
        return max(NEG_BID, NEG_BID * depth) if residual_gw < MUST_RUN_GW else stack["mc"].iloc[0]
    if residual_gw > stack["cum_gw"].iloc[-1]:
        return VOLL
    row = stack[stack["cum_gw"] >= residual_gw].iloc[0]
    return float(row["mc"])


def simulate_fortnight(solar_gw: float, gas: float = 35.0, carbon: float = 80.0,
                       seed: int = 5) -> pd.DataFrame:
    """336 hourly prices with sinusoidal load, random wind, diurnal solar."""
    rng = np.random.default_rng(seed)
    stack = build_stack(gas, carbon)
    hours = np.arange(336)
    hod = hours % 24
    load = 12.0 + 2.5 * np.sin((hod - 9) / 24 * 2 * np.pi) \
        + 1.0 * np.sin((hod - 18) / 24 * 2 * np.pi) + rng.normal(0, 0.4, 336)
    wind = np.clip(rng.gamma(2.0, 1.2, 336), 0, 6.0)
    solar_shape = np.clip(np.sin((hod - 6) / 12 * np.pi), 0, None) * (hod < 21)
    solar = solar_gw * solar_shape * rng.uniform(0.6, 1.0, 336)
    residual = load - wind - solar
    price = np.array([clear(stack, r) for r in residual])
    return pd.DataFrame({"hour": hours, "load": load, "wind": wind,
                         "solar": solar, "residual": residual, "price": price})


def capture_rate(df: pd.DataFrame) -> float:
    """Solar generation-weighted price over the time-weighted average price."""
    gen = df["solar"].to_numpy()
    if gen.sum() == 0:
        return float("nan")
    capture = (df["price"].to_numpy() * gen).sum() / gen.sum()
    return float(capture / df["price"].mean())


if __name__ == "__main__":
    stack = build_stack(gas=35.0, carbon=80.0)
    print("=== Merit order (gas 35 EUR/MWh, carbon 80 EUR/t) ===")
    print(stack.round(1).to_string(index=False))

    print("\n=== Same fortnight, two solar build-outs ===")
    for solar_gw in (2.0, 8.0):
        df = simulate_fortnight(solar_gw=solar_gw)
        neg = int((df["price"] < 0).sum())
        spikes = int((df["price"] > 200).sum())
        print(f"solar {solar_gw:.0f} GW: mean {df['price'].mean():6.1f}, "
              f"median {df['price'].median():6.1f}, "
              f"negative hours {neg:3d}, hours >200 {spikes:2d}, "
              f"solar capture rate {capture_rate(df):.2f}")

    print("\n=== Gas sensitivity at 8 GW solar (structural pass-through) ===")
    for gas in (25.0, 35.0, 50.0):
        df = simulate_fortnight(solar_gw=8.0, gas=gas)
        print(f"gas {gas:4.0f} -> mean power {df['price'].mean():6.1f} "
              f"(CCGT mc {gas / 0.55 + 0.36 * 80:.1f})")
    print("mean power moves with gas because CCGT sets the margin in most "
          "hours; the pass-through ratio ~ (hours CCGT is marginal) / 0.55.")
