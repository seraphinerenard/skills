#!/usr/bin/env python3
"""Brand share decomposition: distribution x velocity, with ACV-velocity curves.

pip install numpy pandas

Identities. For a brand in one category, one market, one period:

    dollars = TDP * SPPD
    TDP  = sum over items of %ACV          (total distribution points)
    SPPD = dollars / TDP                   (sales per point of distribution)
    share = dollars / category dollars

Growth decomposition between periods 0 and 1 uses logs, which split exactly
with no interaction term:

    ln(D1/D0) = ln(TDP1/TDP0) + ln(SPPD1/SPPD0)

so the distribution contribution is ln(TDP1/TDP0) / ln(D1/D0) of the growth,
and velocity gets the rest. The arithmetic split (dTDP*SPPD0 + TDP0*dSPPD
+ dTDP*dSPPD) is also provided because clients ask for it; the interaction
term goes to whichever story the analyst is selling, so report it separately.

ACV-velocity curve. As distribution expands past the best-fit stores,
velocity falls. Fit ln(velocity) = a - b*ln(ACV) on the brand's own
expansion path; projected dollars at a target ACV scale as ACV^(1-b).
A brand with b near 0 expands almost loss-free; b above ~0.5 means new
doors dilute quickly and the whitespace math needs the curve, never the
current velocity.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

RNG = np.random.default_rng(11)


def brand_metrics(items: pd.DataFrame, category_dollars: float) -> dict:
    """items: one row per item with columns dollars, pct_acv."""
    dollars = float(items["dollars"].sum())
    tdp = float(items["pct_acv"].sum())
    return {
        "dollars": dollars,
        "tdp": tdp,
        "max_acv": float(items["pct_acv"].max()),
        "sppd": dollars / max(tdp, 1e-9),
        "share": dollars / category_dollars,
    }


def growth_decomposition(m0: dict, m1: dict) -> dict:
    """Split dollar growth into distribution and velocity contributions."""
    g = np.log(m1["dollars"] / m0["dollars"])
    g_dist = np.log(m1["tdp"] / m0["tdp"])
    g_vel = np.log(m1["sppd"] / m0["sppd"])
    d_tdp = m1["tdp"] - m0["tdp"]
    d_sppd = m1["sppd"] - m0["sppd"]
    return {
        "growth_pct": float(np.expm1(g)),
        "log_dist_share": float(g_dist / g) if g else np.nan,
        "log_vel_share": float(g_vel / g) if g else np.nan,
        "arith_dist": d_tdp * m0["sppd"],
        "arith_vel": m0["tdp"] * d_sppd,
        "arith_interaction": d_tdp * d_sppd,
    }


def fit_acv_velocity_curve(path: pd.DataFrame) -> dict:
    """path: columns pct_acv, velocity (SPPD), one row per period or market.

    Fits ln(velocity) = a - b ln(ACV) by least squares. Returns a, b and a
    projection function for dollars at a target ACV.
    """
    x = np.log(path["pct_acv"].to_numpy(dtype=float))
    y = np.log(path["velocity"].to_numpy(dtype=float))
    b_neg, a = np.polyfit(x, y, 1)
    b = -float(b_neg)

    def project_dollars(acv_now: float, dollars_now: float,
                        acv_target: float) -> float:
        return dollars_now * (acv_target / acv_now) ** (1.0 - b)

    resid = y - (a - b * x)
    return {"a": float(a), "b": b, "r2": 1 - resid.var() / max(y.var(), 1e-12),
            "project_dollars": project_dollars}


def expansion_screen(brands: pd.DataFrame, acv_ceiling: float = 40.0,
                     resid_threshold: float = 0.25) -> pd.DataFrame:
    """Flag high velocity at low ACV within a category table.

    brands: columns brand, dollars, pct_acv, tdp. Raw velocity quantiles
    mislead in both directions because velocity falls with ACV across a
    category (low-ACV brands hold only their best doors). The screen fits
    the category's own cross-sectional curve ln(SPPD) = c - g ln(ACV) and
    flags brands whose log-velocity residual exceeds resid_threshold while
    ACV sits below the ceiling, so there are still doors to win.
    """
    b = brands.copy()
    b["sppd"] = b["dollars"] / b["tdp"].clip(lower=1e-9)
    x = np.log(b["pct_acv"].to_numpy(dtype=float))
    y = np.log(b["sppd"].to_numpy(dtype=float))
    slope, intercept = np.polyfit(x, y, 1)
    b["vel_residual"] = y - (intercept + slope * x)
    b["expansion_signal"] = ((b["pct_acv"] < acv_ceiling)
                             & (b["vel_residual"] > resid_threshold))
    return b.sort_values("vel_residual", ascending=False)


# ---------------------------------------------------------------- demo ----

def _demo() -> None:
    category_dollars = 100e6

    # insurgent brand, two periods a year apart, 3 items
    p0 = pd.DataFrame({"dollars": [520e3, 340e3, 140e3],
                       "pct_acv": [22, 18, 9]})
    p1 = pd.DataFrame({"dollars": [980e3, 610e3, 410e3],
                       "pct_acv": [38, 31, 22]})
    m0, m1 = brand_metrics(p0, category_dollars), brand_metrics(p1, category_dollars)
    d = growth_decomposition(m0, m1)
    print("insurgent brand, year over year")
    print(f"  dollars {m0['dollars']/1e6:.2f}M -> {m1['dollars']/1e6:.2f}M "
          f"({d['growth_pct']:+.0%})")
    print(f"  TDP {m0['tdp']:.0f} -> {m1['tdp']:.0f}   "
          f"SPPD {m0['sppd']/1e3:.1f}k -> {m1['sppd']/1e3:.1f}k")
    print(f"  log split: distribution {d['log_dist_share']:.0%}, "
          f"velocity {d['log_vel_share']:.0%}")
    print(f"  arithmetic: dist {d['arith_dist']/1e6:+.2f}M, "
          f"vel {d['arith_vel']/1e6:+.2f}M, "
          f"interaction {d['arith_interaction']/1e6:+.2f}M")

    # expansion path: velocity decays as ACV grows, true b = 0.25
    acv_path = np.array([8, 14, 22, 30, 38, 49])
    vel_path = 60e3 * (acv_path / 8.0) ** -0.25 * np.exp(RNG.normal(0, 0.04, 6))
    curve = fit_acv_velocity_curve(
        pd.DataFrame({"pct_acv": acv_path, "velocity": vel_path}))
    proj = curve["project_dollars"](49.0, m1["dollars"], 80.0)
    print(f"\nACV-velocity curve: b = {curve['b']:.2f} (true 0.25), "
          f"r2 = {curve['r2']:.2f}")
    print(f"  dollars at 80 ACV, curve-adjusted: {proj/1e6:.2f}M "
          f"(naive linear scaling says "
          f"{m1['dollars'] * 80/49 / 1e6:.2f}M)")

    # category screen: 11 incumbents ON the category's velocity curve
    # (SPPD falls with ACV), plus the insurgent sitting well above it
    acv = RNG.uniform(45, 95, 11)
    tdp = acv * RNG.uniform(1.8, 3.2, 11)
    sppd = 25e3 * (acv / 10.0) ** -0.35 * RNG.lognormal(0, 0.2, 11)
    brands = pd.DataFrame({
        "brand": [f"B{i}" for i in range(11)] + ["Insurgent"],
        "dollars": list(sppd * tdp) + [m1["dollars"]],
        "pct_acv": list(acv) + [m1["max_acv"]],
        "tdp": list(tdp) + [m1["tdp"]],
    })
    screened = expansion_screen(brands)
    print("\nexpansion screen (velocity residual > +0.25 vs category curve, "
          "ACV < 40):")
    print(screened[["brand", "pct_acv", "sppd", "vel_residual",
                    "expansion_signal"]]
          .to_string(index=False, float_format=lambda x: f"{x:,.2f}"))


if __name__ == "__main__":
    _demo()
