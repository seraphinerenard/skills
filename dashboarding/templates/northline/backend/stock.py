"""Inventory engine: forecast consumption, cover, status, exposure, order plan.

The chain: forecast weekly orders per bus model -> translate through the BOM
into weekly component consumption -> compare with on-hand stock and open POs
against each supplier's lead time.

Status per component (effective cover = (on_hand + POs arriving inside the
lead window) / weekly use):
  critical  effective cover < lead time            (stockout before replenishment)
  warning   effective cover < 1.5 x lead time      (no buffer for a late PO)
  ok        otherwise

Revenue exposure is an allocation approximation: each component's shortfall
over its lead window is allocated to bus models by consumption share and
converted to blocked buses; a model's units at risk is its worst component.
"""

import sqlite3
from datetime import date, timedelta

import forecast as fc

SAFETY_WEEKS = {"90": 1.0, "95": 2.0, "98": 3.0}
RISK_BAND = {"low": 1.75, "medium": 1.5, "high": 1.25}  # warning threshold multiplier

_forecast_cache: dict[int, dict] = {}


def model_forecast(con: sqlite3.Connection, model_id: int, horizon: int = 13) -> dict:
    key = (model_id, horizon)
    if key not in _forecast_cache:
        rows = con.execute(
            "SELECT week, orders FROM demand_weekly WHERE model_id=? ORDER BY week",
            (model_id,),
        ).fetchall()
        _forecast_cache[key] = fc.forecast_series(
            [r[0] for r in rows], [r[1] for r in rows], horizon=horizon
        )
    return _forecast_cache[key]


def _load(con: sqlite3.Connection) -> dict:
    models = {r[0]: {"name": r[1], "category": r[2], "price": r[3]}
              for r in con.execute("SELECT * FROM bus_models")}
    comps = {r[0]: {"name": r[1], "category": r[2], "supplier_id": r[3], "unit_cost": r[4]}
             for r in con.execute("SELECT * FROM components")}
    sups = {r[0]: {"name": r[1], "lead": r[2]}
            for r in con.execute("SELECT * FROM suppliers")}
    bom: dict[int, dict[int, float]] = {}
    for cid, mid, qty in con.execute("SELECT * FROM bom"):
        bom.setdefault(cid, {})[mid] = qty
    on_hand = dict(con.execute("SELECT component_id, on_hand FROM inventory"))
    pos: dict[int, list] = {}
    today = date.fromisoformat(
        con.execute("SELECT MAX(week) FROM demand_weekly").fetchone()[0]
    )
    for cid, qty, eta in con.execute(
        "SELECT component_id, qty, eta_week FROM purchase_orders"
    ):
        weeks_out = max(0, (date.fromisoformat(eta) - today).days // 7)
        pos.setdefault(cid, []).append({"qty": qty, "eta_weeks": weeks_out, "eta": eta})
    return {"models": models, "comps": comps, "sups": sups, "bom": bom,
            "on_hand": on_hand, "pos": pos, "as_of": today.isoformat()}


def inventory_status(
    con: sqlite3.Connection,
    demand_pct: float = 0.0,
    lead_delta_weeks: int = 0,
    service_level: str = "95",
    risk_tolerance: str = "medium",
    budget_cad: float | None = None,
    demand_pct_by_model: dict | None = None,
    lead_delta_by_supplier: dict | None = None,
    extra_incoming: dict | None = None,
) -> dict:
    """The engine. Global levers (demand_pct, lead_delta_weeks) stack with the
    granular ones (per-model demand, per-supplier lead). extra_incoming treats
    hypothetical orders as arriving inside the lead window; the goal optimizer
    uses it to price candidate plans without touching the store."""
    s = _load(con)
    by_model = {int(k): v for k, v in (demand_pct_by_model or {}).items()}
    by_supplier = {int(k): v for k, v in (lead_delta_by_supplier or {}).items()}
    extra = {int(k): v for k, v in (extra_incoming or {}).items()}
    warn_mult = RISK_BAND.get(risk_tolerance, 1.5)
    safety = SAFETY_WEEKS.get(str(service_level), 2.0)

    # Forecast weekly orders per model (13-week average), scaled by the scenario.
    weekly_orders = {
        mid: (1.0 + (demand_pct + by_model.get(mid, 0.0)) / 100.0)
        * sum(p["mean"] for p in model_forecast(con, mid)["forecast"]) / 13
        for mid in s["models"]
    }

    rows = []
    shortfall_by_comp: dict[int, float] = {}
    for cid, per_model in s["bom"].items():
        use = sum(qty * weekly_orders[mid] for mid, qty in per_model.items())
        sup_id = s["comps"][cid]["supplier_id"]
        lead = max(1, s["sups"][sup_id]["lead"] + lead_delta_weeks + by_supplier.get(sup_id, 0))
        incoming_in_lead = extra.get(cid, 0) + sum(
            p["qty"] for p in s["pos"].get(cid, []) if p["eta_weeks"] <= lead
        )
        incoming_total = sum(p["qty"] for p in s["pos"].get(cid, []))
        oh = s["on_hand"].get(cid, 0)
        cover = oh / use if use else 99.0
        eff_cover = (oh + incoming_in_lead) / use if use else 99.0
        status = ("critical" if eff_cover < lead
                  else "warning" if eff_cover < warn_mult * lead
                  else "ok")
        shortfall = max(0.0, use * lead - (oh + incoming_in_lead))
        shortfall_by_comp[cid] = shortfall
        rows.append({
            "component_id": cid,
            "name": s["comps"][cid]["name"],
            "category": s["comps"][cid]["category"],
            "supplier_id": sup_id,
            "supplier": s["sups"][sup_id]["name"],
            "lead_weeks": lead,
            "on_hand": oh,
            "incoming": incoming_total,
            "weekly_use": round(use, 1),
            "cover_weeks": round(cover, 1),
            "effective_cover_weeks": round(eff_cover, 1),
            "status": status,
            "shortfall_units": round(shortfall),
            "unit_cost": s["comps"][cid]["unit_cost"],
        })
    rows.sort(key=lambda r: r["effective_cover_weeks"] / max(r["lead_weeks"], 1))

    # Revenue exposure: shortfalls allocated to models by consumption share.
    units_at_risk = {mid: 0.0 for mid in s["models"]}
    for cid, shortfall in shortfall_by_comp.items():
        if shortfall <= 0:
            continue
        use = sum(q * weekly_orders[m] for m, q in s["bom"][cid].items())
        if not use:
            continue
        for mid, qty in s["bom"][cid].items():
            share = qty * weekly_orders[mid] / use
            # One missing unit of an option (qty < 1) blocks exactly one bus,
            # so the divisor never drops below 1.
            blocked_buses = shortfall * share / max(qty, 1.0)
            units_at_risk[mid] = max(units_at_risk[mid], blocked_buses)
    exposure = sum(units_at_risk[m] * s["models"][m]["price"] for m in units_at_risk)
    lead_avg = sum(r["lead_weeks"] for r in rows) / len(rows)
    production_window = sum(weekly_orders.values()) * lead_avg
    service_pct = max(0.0, 100.0 * (1 - sum(units_at_risk.values()) / production_window)) \
        if production_window else 100.0

    # Order plan: bring every short component up to lead + safety weeks of use.
    plan = []
    for r in rows:
        target = r["weekly_use"] * (r["lead_weeks"] + safety)
        qty = max(0.0, target - r["on_hand"] - r["incoming"])
        if qty < 1:
            continue
        plan.append({
            "component_id": r["component_id"],
            "name": r["name"],
            "supplier": r["supplier"],
            "qty": round(qty),
            "cost_cad": round(qty * r["unit_cost"]),
            "priority": "critical" if r["status"] == "critical" else "normal",
            "lead_weeks": r["lead_weeks"],
        })
    plan.sort(key=lambda p: (p["priority"] != "critical", -p["cost_cad"]))
    if budget_cad is not None:
        spent = 0.0
        for p in plan:
            if spent + p["cost_cad"] <= budget_cad:
                p["funded"] = True
                spent += p["cost_cad"]
            else:
                p["funded"] = False

    counts = {k: sum(1 for r in rows if r["status"] == k) for k in ("critical", "warning", "ok")}
    avg_cover = sum(r["effective_cover_weeks"] for r in rows) / len(rows)
    return {
        "as_of": s["as_of"],
        "components": rows,
        "counts": counts,
        "avg_cover_weeks": round(avg_cover, 1),
        "exposure_cad": round(exposure),
        "units_at_risk": {s["models"][m]["name"]: round(u, 1) for m, u in units_at_risk.items()},
        "service_level_pct": round(service_pct, 1),
        "order_plan": plan,
        "order_plan_cost": round(sum(p["cost_cad"] for p in plan)),
        "params": {
            "demand_pct": demand_pct, "lead_delta_weeks": lead_delta_weeks,
            "service_level": str(service_level), "risk_tolerance": risk_tolerance,
            "budget_cad": budget_cad, "demand_pct_by_model": by_model,
            "lead_delta_by_supplier": by_supplier,
        },
    }


def supplier_concentration(con: sqlite3.Connection, status: dict) -> list[dict]:
    """Suppliers ranked by how much of the at-risk book they hold."""
    by_sup: dict[str, dict] = {}
    for r in status["components"]:
        e = by_sup.setdefault(r["supplier"], {"supplier_id": r["supplier_id"],
                                              "supplier": r["supplier"], "components": 0,
                                              "critical": 0, "lead_weeks": r["lead_weeks"]})
        e["components"] += 1
        if r["status"] == "critical":
            e["critical"] += 1
    return sorted(by_sup.values(), key=lambda x: (-x["critical"], -x["components"]))


def goal_optimize(
    con: sqlite3.Connection,
    service_target_pct: float = 95.0,
    budget_cad: float = 3_000_000,
    risk_tolerance: str = "medium",
) -> dict:
    """Closed-loop plan search. Greedy on marginal exposure removed per dollar:
    each round prices every remaining candidate order through the engine with
    the already-chosen orders applied, then locks in the best value. Returns the
    spend-vs-exposure frontier so the trade-off is visible, not asserted."""
    base = inventory_status(con, risk_tolerance=risk_tolerance)
    candidates = {p["component_id"]: p for p in base["order_plan"]}

    chosen: list[dict] = []
    incoming: dict[int, float] = {}
    spend = 0.0
    current = base
    frontier = [{
        "step": 0, "spend": 0, "component": None,
        "exposure_cad": base["exposure_cad"],
        "service_level_pct": base["service_level_pct"],
        "critical": base["counts"]["critical"],
    }]

    while candidates:
        best = None
        for cid, cand in candidates.items():
            if spend + cand["cost_cad"] > budget_cad:
                continue
            trial = inventory_status(
                con, risk_tolerance=risk_tolerance,
                extra_incoming={**incoming, cid: incoming.get(cid, 0) + cand["qty"]},
            )
            removed = current["exposure_cad"] - trial["exposure_cad"]
            crit_fixed = current["counts"]["critical"] - trial["counts"]["critical"]
            value = (removed + crit_fixed * 100_000) / max(cand["cost_cad"], 1)
            if best is None or value > best[0]:
                best = (value, cid, trial)
        if best is None:
            break  # nothing else fits the budget
        value, cid, trial = best
        cand = candidates.pop(cid)
        incoming[cid] = incoming.get(cid, 0) + cand["qty"]
        spend += cand["cost_cad"]
        chosen.append(cand)
        current = trial
        frontier.append({
            "step": len(chosen), "spend": round(spend), "component": cand["name"],
            "exposure_cad": trial["exposure_cad"],
            "service_level_pct": trial["service_level_pct"],
            "critical": trial["counts"]["critical"],
        })
        if (trial["service_level_pct"] >= service_target_pct
                and trial["counts"]["critical"] == 0):
            break

    return {
        "as_of": base["as_of"],
        "params": {"service_target_pct": service_target_pct,
                   "budget_cad": budget_cad, "risk_tolerance": risk_tolerance},
        "met_target": (current["service_level_pct"] >= service_target_pct
                       and current["counts"]["critical"] == 0),
        "plan": chosen,
        "spend_cad": round(spend),
        "frontier": frontier,
        "baseline": {"exposure_cad": base["exposure_cad"],
                     "service_level_pct": base["service_level_pct"],
                     "critical": base["counts"]["critical"]},
        "achieved": {"exposure_cad": current["exposure_cad"],
                     "service_level_pct": current["service_level_pct"],
                     "critical": current["counts"]["critical"]},
    }
