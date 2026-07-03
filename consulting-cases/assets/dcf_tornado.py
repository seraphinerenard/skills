#!/usr/bin/env python3
"""FCFF DCF with mid-year convention, dual terminal value with cross-checks,
and a one-at-a-time tornado on equity value per share.

pip install: numpy

Mechanics encoded here that casual DCFs get wrong:

  * Mid-year convention: operating cash arrives through the year, so year t
    discounts at (1+WACC)^-(t-0.5). The Gordon terminal value keeps the same
    mid-year timing (discount TV at N-0.5); an exit-multiple terminal value is
    a sale event at the horizon, so it discounts at the full N.
  * Terminal free cash flow is built from reinvestment economics, never by
    growing the last explicit-year FCF: FCFF_T = NOPAT_T * (1 - g/ROIC_T).
    Growing final-year FCF at g carries the explicit period's capex-to-D&A
    gap into perpetuity, which double-counts growth capex against terminal
    growth. ROIC_T defaults to WACC (economic profit fades to zero), a
    defensible conservative anchor; set it above WACC only with a stated
    moat argument.
  * Cross-checks both ways: the Gordon TV implies an exit EV/EBITDA, and the
    exit multiple implies a perpetual growth rate. When the implied multiple
    sits above today's trading multiple, the growth assumption smuggles in a
    re-rating.
  * Working capital consumes cash as revenue grows: dNWC = nwc_pct * dRevenue
    each year, including a terminal-year haircut consistent with g.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class DCF:
    revenue0: float                # last-twelve-months revenue
    growth: Sequence[float]        # per-year revenue growth, len = horizon
    ebit_margin: Sequence[float]   # per-year EBIT margin, len = horizon
    tax_rate: float
    da_pct: float                  # depreciation and amortization, % of revenue
    capex_pct: float               # capital expenditure, % of revenue
    nwc_pct: float                 # net working capital level, % of revenue
    wacc: float
    terminal_growth: float
    exit_multiple: float           # EV / terminal-year EBITDA
    net_debt: float
    shares: float
    terminal_roic: float | None = None   # defaults to wacc
    midyear: bool = True


def _explicit(d: DCF) -> dict:
    n = len(d.growth)
    assert len(d.ebit_margin) == n
    rev = d.revenue0 * np.cumprod(1 + np.asarray(d.growth, dtype=float))
    prev_rev = np.concatenate(([d.revenue0], rev[:-1]))
    ebit = rev * np.asarray(d.ebit_margin, dtype=float)
    nopat = ebit * (1 - d.tax_rate)
    da = rev * d.da_pct
    capex = rev * d.capex_pct
    dnwc = d.nwc_pct * (rev - prev_rev)
    fcff = nopat + da - capex - dnwc
    t = np.arange(1, n + 1) - (0.5 if d.midyear else 0.0)
    df = (1 + d.wacc) ** -t
    return {"rev": rev, "ebit": ebit, "nopat": nopat, "da": da,
            "capex": capex, "dnwc": dnwc, "fcff": fcff, "df": df, "n": n}


def value(d: DCF) -> dict:
    e = _explicit(d)
    n = e["n"]
    g, wacc = d.terminal_growth, d.wacc
    if wacc <= g:
        raise ValueError("WACC must exceed terminal growth")

    # terminal FCFF from reinvestment economics
    roic_t = d.terminal_roic if d.terminal_roic is not None else wacc
    nopat_t1 = e["nopat"][-1] * (1 + g)
    reinvest_rate = g / roic_t
    fcff_t1 = nopat_t1 * (1 - reinvest_rate)

    tv_gordon = fcff_t1 / (wacc - g)
    t_tv = n - 0.5 if d.midyear else n
    pv_tv_gordon = tv_gordon / (1 + wacc) ** t_tv

    ebitda_n = e["ebit"][-1] + e["da"][-1]
    tv_exit = d.exit_multiple * ebitda_n
    pv_tv_exit = tv_exit / (1 + wacc) ** n     # sale event at the horizon

    pv_explicit = float((e["fcff"] * e["df"]).sum())

    ev_gordon = pv_explicit + pv_tv_gordon
    ev_exit = pv_explicit + pv_tv_exit

    implied_exit_multiple = tv_gordon / ebitda_n
    # Conventional implied-growth cross-check: the g at which a plain
    # Gordon perpetuity on final-year FCFF matches the exit-multiple TV.
    # (Under reinvestment-consistent FCF with ROIC_T = WACC, TV is nearly
    # flat in g because growth at the cost of capital adds no value, so an
    # implied-g solve against that form has no solution.)
    fcff_n = e["fcff"][-1]
    implied_g = (wacc * tv_exit - fcff_n) / (tv_exit + fcff_n)

    return {
        "table": e,
        "pv_explicit": pv_explicit,
        "tv_gordon": tv_gordon, "pv_tv_gordon": pv_tv_gordon,
        "tv_exit": tv_exit, "pv_tv_exit": pv_tv_exit,
        "ev_gordon": ev_gordon, "ev_exit": ev_exit,
        "equity_gordon": ev_gordon - d.net_debt,
        "equity_exit": ev_exit - d.net_debt,
        "per_share_gordon": (ev_gordon - d.net_debt) / d.shares,
        "per_share_exit": (ev_exit - d.net_debt) / d.shares,
        "tv_share_of_ev": pv_tv_gordon / ev_gordon,
        "implied_exit_multiple": implied_exit_multiple,
        "implied_terminal_growth": implied_g,
        "terminal_reinvestment_rate": reinvest_rate,
    }


def _apply(d: DCF, name: str, v: float) -> DCF:
    if name == "growth_shift":
        return replace(d, growth=[x + v for x in d.growth])
    if name == "margin_shift":
        return replace(d, ebit_margin=[x + v for x in d.ebit_margin])
    return replace(d, **{name: v})


def tornado(d: DCF, spans: dict[str, tuple[float, float]],
            output: str = "per_share_gordon") -> list[dict]:
    base = value(d)[output]
    rows = []
    for name, (lo, hi) in spans.items():
        v_lo = value(_apply(d, name, lo))[output]
        v_hi = value(_apply(d, name, hi))[output]
        rows.append({"name": name, "low_in": lo, "high_in": hi,
                     "low_out": v_lo, "high_out": v_hi,
                     "swing": abs(v_hi - v_lo)})
    rows.sort(key=lambda r: -r["swing"])
    return [{"base": base, **r} for r in rows]


def print_tornado(rows: list[dict], width: int = 44) -> None:
    base = rows[0]["base"]
    max_dev = max(max(abs(r["low_out"] - base), abs(r["high_out"] - base))
                  for r in rows)
    half = width // 2
    print(f"\ntornado on equity value per share (base = {base:,.2f})")
    for r in rows:
        left = min(r["low_out"], r["high_out"]) - base
        right = max(r["low_out"], r["high_out"]) - base
        lo_n = int(round(abs(min(left, 0)) / max_dev * half))
        hi_n = int(round(max(right, 0) / max_dev * half))
        bar = " " * (half - lo_n) + "#" * lo_n + "|" + "#" * hi_n
        print(f"  {r['name']:>14} {bar:<{width + 1}} "
              f"[{min(r['low_out'], r['high_out']):>7.2f}, "
              f"{max(r['low_out'], r['high_out']):>7.2f}]  "
              f"swing {r['swing']:.2f}")


if __name__ == "__main__":
    d = DCF(
        revenue0=480.0,                                # $ millions
        growth=[0.08, 0.07, 0.06, 0.045, 0.03],
        ebit_margin=[0.140, 0.145, 0.150, 0.155, 0.160],
        tax_rate=0.26,
        da_pct=0.050,
        capex_pct=0.060,
        nwc_pct=0.12,
        wacc=0.092,
        terminal_growth=0.024,
        exit_multiple=9.0,
        net_debt=350.0,
        shares=62.0,
    )

    v = value(d)
    e = v["table"]
    print("explicit period ($M):")
    print(f"  {'year':>6} {'revenue':>9} {'EBIT':>8} {'FCFF':>8} {'DF':>7} {'PV':>8}")
    for i in range(e["n"]):
        pv = e["fcff"][i] * e["df"][i]
        print(f"  {i + 1:>6} {e['rev'][i]:>9,.1f} {e['ebit'][i]:>8,.1f} "
              f"{e['fcff'][i]:>8,.1f} {e['df'][i]:>7.4f} {pv:>8,.1f}")

    print(f"\n  PV of explicit FCFF        {v['pv_explicit']:>10,.1f}")
    print(f"  TV (Gordon, g={d.terminal_growth:.1%}, ROIC_T=WACC)"
          f"  {v['tv_gordon']:>10,.1f}  -> PV {v['pv_tv_gordon']:>8,.1f}")
    print(f"  TV (exit {d.exit_multiple:.1f}x EBITDA_N)"
          f"        {v['tv_exit']:>10,.1f}  -> PV {v['pv_tv_exit']:>8,.1f}")
    print(f"  EV Gordon {v['ev_gordon']:>10,.1f}   EV exit {v['ev_exit']:>10,.1f}")
    print(f"  equity/share Gordon {v['per_share_gordon']:>7.2f}   "
          f"exit {v['per_share_exit']:>7.2f}")
    print(f"  terminal value share of EV: {v['tv_share_of_ev']:.0%}")
    print(f"  cross-check: Gordon TV implies {v['implied_exit_multiple']:.1f}x "
          f"EBITDA_N; exit {d.exit_multiple:.1f}x implies "
          f"g = {v['implied_terminal_growth']:.2%}")

    rows = tornado(d, {
        "wacc": (0.082, 0.102),
        "terminal_growth": (0.016, 0.032),
        "margin_shift": (-0.020, 0.020),
        "growth_shift": (-0.020, 0.020),
        "capex_pct": (0.050, 0.070),
        "nwc_pct": (0.09, 0.15),
        "tax_rate": (0.23, 0.29),
    })
    print_tornado(rows)
