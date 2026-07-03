#!/usr/bin/env python3
"""Price-volume-mix revenue bridge that reconciles exactly, with new and
exited SKUs booked explicitly.

pip install: pandas numpy

The two-term split every first-year analyst writes,
    volume_i = (q1_i - q0_i) * p0_i,   price_i = (p1_i - p0_i) * q1_i,
reconciles per SKU and silently buries mix at the portfolio level: when
customers shift toward cheaper SKUs, the naive split books the damage as
"volume" even in a period when total units grew. The decomposition below
separates the three effects for continuing SKUs and books new and exited
SKUs in their own terms.

For continuing SKUs (units > 0 in both periods), with Q = total continuing
units and Pbar0 = continuing revenue / Q0 (the prior average realized price):

    volume effect = (Q1 - Q0) * Pbar0
    mix effect    = sum_i q1_i * p0_i  -  Q1 * Pbar0
    price effect  = sum_i q1_i * (p1_i - p0_i)

New SKUs add sum(p1*q1); exited SKUs subtract sum(p0*q0). The five terms sum
to (R1 - R0) exactly; the function asserts the reconciliation at 1e-9 of
revenue scale.

Unit discipline: the volume/mix split has meaning only when units are
commensurable across SKUs (all cubic yards, all seats, all tonnes). With
heterogeneous units, run the bridge inside each unit-consistent segment and
add the segment bridges. Multi-year gaps hide offsetting moves; chain
year-over-year bridges and sum the effects.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def pvm_bridge(
    period0: pd.DataFrame,
    period1: pd.DataFrame,
    sku: str = "sku",
    units: str = "units",
    revenue: str = "revenue",
) -> dict:
    """Decompose R1 - R0 into volume, mix, price, new, and exited effects.

    Each period is a DataFrame with one row per SKU carrying units sold and
    realized revenue (so price = revenue / units absorbs discounts and
    rebates; use gross price columns only if the bridge should exclude
    discounting, and then bridge discounts separately).

    Returns a dict with the five effects, the reconciliation check, and a
    per-SKU price-effect attribution table sorted by absolute impact.
    """
    a = period0[[sku, units, revenue]].set_index(sku)
    b = period1[[sku, units, revenue]].set_index(sku)
    if (a[units] <= 0).any() or (b[units] <= 0).any():
        raise ValueError("units must be positive; drop zero-unit rows first")

    both = a.index.intersection(b.index)
    new = b.index.difference(a.index)
    exited = a.index.difference(b.index)

    r0_total, r1_total = float(a[revenue].sum()), float(b[revenue].sum())

    a0, b1 = a.loc[both], b.loc[both]
    p0 = a0[revenue] / a0[units]
    p1 = b1[revenue] / b1[units]
    q0_tot, q1_tot = float(a0[units].sum()), float(b1[units].sum())
    pbar0 = float(a0[revenue].sum()) / q0_tot

    volume = (q1_tot - q0_tot) * pbar0
    mix = float((b1[units] * p0).sum()) - q1_tot * pbar0
    price = float((b1[units] * (p1 - p0)).sum())
    new_effect = float(b.loc[new, revenue].sum())
    exited_effect = -float(a.loc[exited, revenue].sum())

    total = volume + mix + price + new_effect + exited_effect
    delta = r1_total - r0_total
    scale = max(abs(r0_total), abs(r1_total), 1.0)
    assert abs(total - delta) < 1e-9 * scale, (total, delta)

    price_detail = (
        pd.DataFrame({
            "units_1": b1[units],
            "price_0": p0,
            "price_1": p1,
            "price_effect": b1[units] * (p1 - p0),
        })
        .sort_values("price_effect", key=np.abs, ascending=False)
    )

    return {
        "revenue_0": r0_total,
        "revenue_1": r1_total,
        "delta": delta,
        "volume": volume,
        "mix": mix,
        "price": price,
        "new_skus": new_effect,
        "exited_skus": exited_effect,
        "price_detail": price_detail,
    }


def naive_bridge(period0: pd.DataFrame, period1: pd.DataFrame,
                 sku: str = "sku", units: str = "units",
                 revenue: str = "revenue") -> dict:
    """The two-term split, for contrast: mix lands inside 'volume'."""
    a = period0.set_index(sku)
    b = period1.set_index(sku)
    both = a.index.intersection(b.index)
    p0 = a.loc[both, revenue] / a.loc[both, units]
    p1 = b.loc[both, revenue] / b.loc[both, units]
    dq = b.loc[both, units] - a.loc[both, units]
    return {
        "volume_naive": float((dq * p0).sum()),
        "price_naive": float((b.loc[both, units] * (p1 - p0)).sum()),
    }


if __name__ == "__main__":
    # Premium units fall, economy units rise, total units GROW 5%.
    # Prices on both continuing SKUs are unchanged, one SKU launches,
    # one SKU exits, and one SKU takes a real price increase.
    y0 = pd.DataFrame({
        "sku": ["premium", "economy", "legacy"],
        "units": [100.0, 100.0, 40.0],
        "revenue": [10_000.0, 6_000.0, 2_000.0],
    })
    y1 = pd.DataFrame({
        "sku": ["premium", "economy", "launch"],
        "units": [80.0, 130.0, 25.0],
        "revenue": [8_000.0, 8_190.0, 2_250.0],  # economy price +5%
    })

    out = pvm_bridge(y0, y1)
    print("exact bridge:")
    for k in ["revenue_0", "revenue_1", "delta", "volume", "mix",
              "price", "new_skus", "exited_skus"]:
        print(f"  {k:>12}: {out[k]:>10,.0f}")

    naive = naive_bridge(y0, y1)
    print("\nnaive two-term split on continuing SKUs:")
    print(f"  volume_naive: {naive['volume_naive']:>10,.0f}"
          f"   (books the mix shift as volume)")
    print(f"  price_naive:  {naive['price_naive']:>10,.0f}")

    print("\nreading: continuing units grew "
          f"{(80 + 130) / (100 + 100) - 1:+.0%}, so true volume is positive "
          f"({out['volume']:+,.0f}); the naive split calls volume "
          f"{naive['volume_naive']:+,.0f} because the shift to the cheaper "
          "SKU hides inside it. The mix term carries the damage: "
          f"{out['mix']:+,.0f}.")

    print("\nper-SKU price attribution:")
    print(out["price_detail"].to_string(float_format=lambda x: f"{x:,.2f}"))
