"""Constrained production schedule: week-by-week fill simulation.

For each of the next N weeks, compare component availability (on-hand stock,
open POs as they arrive, and rolling replenishment orders assumed placed from
today, which land after each supplier's lead time) against forecast demand
through the BOM. Inside a component's lead window, only stock and already-open
POs exist — that is the committed horizon nothing ordered today can fix. Each
model builds at the rate of its scarcest component; options (take-rate BOM
lines) gate only their optioned share; stock is consumed and the gating
component recorded. This is the S&OP view: not "how much stock do we hold" but
"how many buses can we actually build, and what stops us".
"""

import sqlite3

import stock


def production_plan(con: sqlite3.Connection, weeks: int = 13) -> dict:
    s = stock._load(con)
    demand = {
        mid: [p["mean"] for p in stock.model_forecast(con, mid, horizon=weeks)["forecast"]]
        for mid in s["models"]
    }
    arrivals: dict[int, dict[int, float]] = {}
    for cid, plist in s["pos"].items():
        for p in plist:
            arrivals.setdefault(cid, {})[p["eta_weeks"]] = (
                arrivals.get(cid, {}).get(p["eta_weeks"], 0) + p["qty"]
            )
    level = dict(s["on_hand"])
    lead = {
        cid: s["sups"][s["comps"][cid]["supplier_id"]]["lead"]
        for cid in s["bom"]
    }

    out = []
    for t in range(weeks):
        for cid in level:
            level[cid] += arrivals.get(cid, {}).get(t, 0)
        # Rolling replenishment: a weekly order placed today (and every week
        # after) arrives once the supplier lead time has passed.
        for cid, per in s["bom"].items():
            if t + 1 >= lead[cid]:
                level[cid] += sum(qty * demand[mid][t] for mid, qty in per.items())
        required = {
            cid: sum(qty * demand[mid][t] for mid, qty in per.items())
            for cid, per in s["bom"].items()
        }
        ratio = {
            cid: (level.get(cid, 0) / req) if req > 0 else 99.0
            for cid, req in required.items()
        }
        # Per-model fill: a model builds at the rate of its scarcest component.
        # Mandatory components (qty >= 1) gate the whole model; options
        # (qty < 1 = take rate) gate only their optioned share, so a lift
        # shortage cannot idle the un-optioned buses. Consumption is clamped
        # at availability, which keeps the simulation conservative-adjacent
        # (documented approximation).
        fill_m, gate_m = {}, {}
        for mid in demand:
            worst_f, worst_c = 1.0, None
            for cid, per in s["bom"].items():
                qty = per.get(mid)
                if not qty:
                    continue
                r = min(1.0, max(0.0, ratio[cid]))
                f = (1.0 - qty) + qty * r if qty < 1.0 else r
                if f < worst_f:
                    worst_f, worst_c = f, cid
            fill_m[mid] = worst_f
            gate_m[mid] = worst_c if worst_f < 0.999 else None
        built = {mid: demand[mid][t] * fill_m[mid] for mid in demand}
        for cid, per in s["bom"].items():
            level[cid] -= sum(qty * built[mid] for mid, qty in per.items())
            level[cid] = max(0.0, level[cid])
        week_demand = sum(demand[mid][t] for mid in demand)
        week_built = sum(built.values())
        lost_by_gate = {}
        for mid in demand:
            if gate_m[mid] is not None:
                name = s["comps"][gate_m[mid]]["name"]
                lost_by_gate[name] = lost_by_gate.get(name, 0) + demand[mid][t] - built[mid]
        gate = max(lost_by_gate, key=lost_by_gate.get) if lost_by_gate else None
        out.append({
            "week_offset": t + 1,
            "demand": round(week_demand, 1),
            "buildable": round(week_built, 1),
            "fill_pct": round(100 * week_built / week_demand, 1) if week_demand else 100.0,
            "gating_component": gate,
            "gates_by_model": {
                s["models"][m]["name"]: (s["comps"][gate_m[m]]["name"] if gate_m[m] else None)
                for m in demand
            },
            "by_model": {s["models"][m]["name"]: round(built[m], 1) for m in built},
            "demand_by_model": {s["models"][m]["name"]: round(demand[m][t], 1) for m in demand},
        })

    lost = sum(w["demand"] - w["buildable"] for w in out)
    revenue_lost = 0.0
    for w in out:
        for mid in s["models"]:
            name = s["models"][mid]["name"]
            revenue_lost += (w["demand_by_model"][name] - w["by_model"][name]) * s["models"][mid]["price"]
    return {
        "as_of": s["as_of"],
        "weeks": out,
        "buses_lost": round(lost),
        "revenue_lost_cad": round(revenue_lost),
        "worst_week": min(out, key=lambda w: w["fill_pct"])["week_offset"],
    }
