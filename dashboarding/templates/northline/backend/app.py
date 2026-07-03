"""Northline Coachworks inventory-intelligence API: view endpoints + SSE agents.

Run: python seed.py && uvicorn app:app --port 8000
The frontend dev server proxies /api here, so no CORS setup is needed in dev.
"""

import json
import os
import sqlite3
from datetime import date, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fastapi.responses import StreamingResponse

import agent
import insights
import production
import stock

DB = os.path.join(os.path.dirname(__file__), "northline.db")
app = FastAPI(title="Northline Coachworks inventory intelligence")


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


@app.get("/api/kpis")
def kpis():
    con = _connect()
    st = stock.inventory_status(con)
    demand_13w = sum(
        sum(p["mean"] for p in stock.model_forecast(con, mid)["forecast"])
        for (mid,) in con.execute("SELECT model_id FROM bus_models")
    )
    con.close()
    return {
        "skus_tracked": len(st["components"]),
        "critical": st["counts"]["critical"],
        "warning": st["counts"]["warning"],
        "service_level_pct": st["service_level_pct"],
        "at_risk_cad": st["exposure_cad"],
        "avg_cover_weeks": st["avg_cover_weeks"],
        "forecast_orders_13w": round(demand_13w),
        "as_of": st["as_of"],
    }


@app.get("/api/insights")
def get_insights():
    con = _connect()
    st = stock.inventory_status(con)
    findings = insights.compute_findings(con, st)
    con.close()
    return {"as_of": st["as_of"], "findings": findings}


@app.get("/api/demand")
def demand():
    con = _connect()
    out = []
    for mid, name, category, price in con.execute("SELECT * FROM bus_models"):
        rows = con.execute(
            "SELECT week, orders FROM demand_weekly WHERE model_id=? ORDER BY week",
            (mid,),
        ).fetchall()
        cur = sum(r["orders"] for r in rows[-13:]) / 13
        yoy = sum(r["orders"] for r in rows[-65:-52]) / 13
        out.append({
            "model_id": mid,
            "name": name,
            "category": category,
            "price_cad": price,
            "weekly_avg_13w": round(cur, 1),
            "yoy_pct": round(100.0 * (cur - yoy) / yoy, 1) if yoy else None,
            "series": [{"week": r["week"], "orders": r["orders"]} for r in rows[-104:]],
        })
    con.close()
    return {"models": out}


@app.get("/api/demand-forecast")
def demand_forecast(model_id: int, weeks: int = 13):
    con = _connect()
    name = con.execute(
        "SELECT name FROM bus_models WHERE model_id=?", (model_id,)
    ).fetchone()
    if not name:
        con.close()
        raise HTTPException(404, f"no bus model {model_id}")
    hist = con.execute(
        "SELECT week, orders FROM demand_weekly WHERE model_id=? ORDER BY week",
        (model_id,),
    ).fetchall()
    result = dict(stock.model_forecast(con, model_id, horizon=weeks))
    con.close()
    result["model_id"] = model_id
    result["name"] = name["name"]
    result["history"] = [{"week": r["week"], "orders": r["orders"]} for r in hist[-104:]]
    return result


@app.get("/api/inventory")
def inventory():
    con = _connect()
    st = stock.inventory_status(con)
    st["suppliers"] = stock.supplier_concentration(con, st)
    con.close()
    return st


class WhatIfRequest(BaseModel):
    demand_pct: float = 0.0
    lead_delta_weeks: int = 0
    service_level: str = "95"
    risk_tolerance: str = "medium"
    budget_cad: float | None = None
    demand_pct_by_model: dict[int, float] = {}
    lead_delta_by_supplier: dict[int, int] = {}


@app.post("/api/whatif")
def whatif(req: WhatIfRequest):
    con = _connect()
    baseline = stock.inventory_status(con)
    scenario = stock.inventory_status(
        con,
        demand_pct=req.demand_pct,
        lead_delta_weeks=req.lead_delta_weeks,
        service_level=req.service_level,
        risk_tolerance=req.risk_tolerance,
        budget_cad=req.budget_cad,
        demand_pct_by_model=req.demand_pct_by_model,
        lead_delta_by_supplier=req.lead_delta_by_supplier,
    )
    con.close()

    def slim(st):
        return {
            "counts": st["counts"],
            "exposure_cad": st["exposure_cad"],
            "service_level_pct": st["service_level_pct"],
            "avg_cover_weeks": st["avg_cover_weeks"],
            "order_plan_cost": st["order_plan_cost"],
            "units_at_risk": st["units_at_risk"],
        }

    return {
        "as_of": baseline["as_of"],
        "baseline": slim(baseline),
        "scenario": slim(scenario),
        "order_plan": scenario["order_plan"],
        "params": scenario["params"],
    }


class ChatRequest(BaseModel):
    messages: list[dict]


def _sse(gen_factory):
    async def gen():
        try:
            async for event in gen_factory():
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as e:  # surfaced to the UI as a sentence, not a 500 mid-stream
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


@app.post("/api/chat")
def chat(req: ChatRequest):
    return _sse(lambda: agent.stream_chat(req.messages))


RECOMMEND_PROMPT = """Produce the procurement recommendation list for this week.
Call get_inventory_status first. Then write numbered recommendations (at most six),
each on this exact format:

N. [CRITICAL or NORMAL] <one-sentence action with quantity, component, and supplier>
   <one sentence of justification with the numbers: cover vs lead time, cost, exposure removed>

Order them critical first, then by cost-effectiveness. End with one sentence giving
the total spend and the exposure it removes. No preamble before recommendation 1."""


@app.post("/api/recommendations")
def recommendations():
    return _sse(
        lambda: agent.stream_chat([{"role": "user", "content": RECOMMEND_PROMPT}])
    )


class OptimizeRequest(BaseModel):
    service_target_pct: float = 95.0
    budget_cad: float = 3_000_000
    risk_tolerance: str = "medium"


@app.post("/api/optimize")
def optimize(req: OptimizeRequest):
    con = _connect()
    result = stock.goal_optimize(
        con,
        service_target_pct=req.service_target_pct,
        budget_cad=req.budget_cad,
        risk_tolerance=req.risk_tolerance,
    )
    con.close()
    return result


# ---------------------------------------------------------------- PO drafts
# The one sanctioned write path. Agents and the optimizer draft; a person
# approves; approval writes a real purchase order and the whole dashboard
# reprices from the store.

def _connect_rw() -> sqlite3.Connection:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


class DraftRequest(BaseModel):
    items: list[dict]  # [{component_id, qty}]
    source: str = "plan"


@app.get("/api/po-drafts")
def list_drafts():
    con = _connect()
    rows = con.execute(
        """SELECT d.draft_id, d.component_id, c.name, s.name AS supplier,
                  s.lead_time_weeks, d.qty, d.cost_cad, d.source, d.status, d.created_at
           FROM po_drafts d
           JOIN components c ON c.component_id = d.component_id
           JOIN suppliers s ON s.supplier_id = c.supplier_id
           ORDER BY d.status = 'draft' DESC, d.draft_id DESC"""
    ).fetchall()
    con.close()
    return {"drafts": [dict(r) for r in rows]}


@app.post("/api/po-drafts")
def create_drafts(req: DraftRequest):
    con = _connect_rw()
    as_of = con.execute("SELECT MAX(week) FROM demand_weekly").fetchone()[0]
    created = []
    for item in req.items:
        cid, qty = int(item["component_id"]), int(item["qty"])
        cost = con.execute(
            "SELECT unit_cost_cad FROM components WHERE component_id=?", (cid,)
        ).fetchone()
        if not cost or qty <= 0:
            continue
        cur = con.execute(
            "INSERT INTO po_drafts (component_id, qty, cost_cad, source, status, created_at)"
            " VALUES (?,?,?,?, 'draft', ?)",
            (cid, qty, qty * cost[0], req.source, as_of),
        )
        created.append(cur.lastrowid)
    con.commit()
    con.close()
    return {"created": created}


@app.post("/api/po-drafts/{draft_id}/approve")
def approve_draft(draft_id: int):
    con = _connect_rw()
    d = con.execute(
        "SELECT * FROM po_drafts WHERE draft_id=? AND status='draft'", (draft_id,)
    ).fetchone()
    if not d:
        con.close()
        raise HTTPException(404, "no open draft with that id")
    lead = con.execute(
        "SELECT s.lead_time_weeks FROM suppliers s JOIN components c"
        " ON c.supplier_id = s.supplier_id WHERE c.component_id=?",
        (d["component_id"],),
    ).fetchone()[0]
    as_of = date.fromisoformat(
        con.execute("SELECT MAX(week) FROM demand_weekly").fetchone()[0]
    )
    eta = as_of + timedelta(weeks=lead)
    con.execute(
        "INSERT INTO purchase_orders (component_id, qty, eta_week) VALUES (?,?,?)",
        (d["component_id"], d["qty"], eta.isoformat()),
    )
    con.execute("UPDATE po_drafts SET status='approved' WHERE draft_id=?", (draft_id,))
    con.commit()
    con.close()
    return {"approved": draft_id, "eta_week": eta.isoformat()}


@app.post("/api/po-drafts/{draft_id}/reject")
def reject_draft(draft_id: int):
    con = _connect_rw()
    n = con.execute(
        "UPDATE po_drafts SET status='rejected' WHERE draft_id=? AND status='draft'",
        (draft_id,),
    ).rowcount
    con.commit()
    con.close()
    if not n:
        raise HTTPException(404, "no open draft with that id")
    return {"rejected": draft_id}


# ---------------------------------------------------------------- alerts

@app.get("/api/alerts")
def alerts():
    con = _connect()
    st = stock.inventory_status(con)
    events = []
    for c in st["components"]:
        if c["status"] == "critical":
            events.append({
                "severity": "alert",
                "when": "now",
                "title": f"{c['name']} runs out in {c['effective_cover_weeks']} weeks",
                "body": (f"Cover {c['effective_cover_weeks']} wks against a "
                         f"{c['lead_weeks']}-week lead from {c['supplier']}; "
                         f"shortfall {c['shortfall_units']:,} units over the lead window."),
            })
    for cid, qty, eta in con.execute(
        "SELECT component_id, qty, eta_week FROM purchase_orders ORDER BY eta_week"
    ):
        weeks_out = max(0, (date.fromisoformat(eta) - date.fromisoformat(st["as_of"])).days // 7)
        if weeks_out <= 2:
            name = con.execute(
                "SELECT name FROM components WHERE component_id=?", (cid,)
            ).fetchone()[0]
            events.append({
                "severity": "info",
                "when": f"week of {eta}",
                "title": f"PO arriving: {qty:,} x {name}",
                "body": f"Due {eta} ({'this week' if weeks_out == 0 else f'in {weeks_out} wk'})."
                if weeks_out <= 1 else f"Due {eta} (in {weeks_out} wks).",
            })
    # Demand anomaly: last actual week outside the forecast interval.
    for mid, name in con.execute("SELECT model_id, name FROM bus_models"):
        fc_prev = stock.model_forecast(con, mid)
        last = con.execute(
            "SELECT week, orders FROM demand_weekly WHERE model_id=? ORDER BY week DESC LIMIT 1",
            (mid,),
        ).fetchone()
        f0 = fc_prev["forecast"][0]
        if last and not (f0["lo"] * 0.8 <= last[1] <= f0["hi"] * 1.2):
            direction = "above" if last[1] > f0["hi"] else "below"
            events.append({
                "severity": "warning",
                "when": f"week of {last[0]}",
                "title": f"{name} intake ran {direction} its forecast band",
                "body": (f"{last[1]} orders against an expected {f0['lo']:.0f} to "
                         f"{f0['hi']:.0f}. One week is noise; two is a trend the "
                         f"forecast has not caught."),
            })
    sups = stock.supplier_concentration(con, st)
    if sups and sups[0]["critical"] >= 2:
        events.append({
            "severity": "warning",
            "when": "standing",
            "title": f"Single-source concentration at {sups[0]['supplier']}",
            "body": (f"{sups[0]['critical']} critical shortfalls sit with one supplier "
                     f"({sups[0]['components']} SKUs, {sups[0]['lead_weeks']}-week lead)."),
        })
    con.close()
    order = {"alert": 0, "warning": 1, "info": 2}
    events.sort(key=lambda e: order.get(e["severity"], 3))
    return {"as_of": st["as_of"], "events": events}


@app.get("/api/production-plan")
def production_plan(weeks: int = 13):
    con = _connect()
    result = production.production_plan(con, weeks=weeks)
    con.close()
    return result


@app.get("/api/component/{component_id}")
def component_detail(component_id: int):
    con = _connect()
    st = stock.inventory_status(con)
    row = next((c for c in st["components"] if c["component_id"] == component_id), None)
    if not row:
        con.close()
        raise HTTPException(404, f"no component {component_id}")
    bom = con.execute(
        """SELECT m.name, b.qty_per_bus FROM bom b
           JOIN bus_models m ON m.model_id = b.model_id
           WHERE b.component_id=? ORDER BY m.model_id""",
        (component_id,),
    ).fetchall()
    pos = con.execute(
        "SELECT qty, eta_week FROM purchase_orders WHERE component_id=? ORDER BY eta_week",
        (component_id,),
    ).fetchall()
    plan_row = next((p for p in st["order_plan"] if p["component_id"] == component_id), None)
    con.close()
    return {
        **row,
        "bom": [{"model": b["name"], "qty_per_bus": b["qty_per_bus"]} for b in bom],
        "open_pos": [{"qty": p["qty"], "eta_week": p["eta_week"]} for p in pos],
        "suggested_order": plan_row,
        "as_of": st["as_of"],
    }


@app.get("/api/pos")
def open_pos():
    con = _connect()
    as_of = con.execute("SELECT MAX(week) FROM demand_weekly").fetchone()[0]
    rows = con.execute(
        """SELECT p.po_id, p.component_id, c.name, s.name AS supplier, s.lead_time_weeks,
                  p.qty, c.unit_cost_cad * p.qty AS value_cad, p.eta_week
           FROM purchase_orders p
           JOIN components c ON c.component_id = p.component_id
           JOIN suppliers s ON s.supplier_id = c.supplier_id
           ORDER BY p.eta_week"""
    ).fetchall()
    con.close()
    out = []
    for r in rows:
        weeks_out = max(0, (date.fromisoformat(r["eta_week"]) - date.fromisoformat(as_of)).days // 7)
        out.append({**dict(r), "weeks_out": weeks_out,
                    "inside_lead": weeks_out <= r["lead_time_weeks"]})
    return {"as_of": as_of, "pos": out}


@app.get("/api/bom")
def bom_matrix():
    con = _connect()
    models = [r["name"] for r in con.execute("SELECT name FROM bus_models ORDER BY model_id")]
    rows = con.execute(
        """SELECT c.component_id, c.name, c.category, b.model_id, b.qty_per_bus
           FROM components c JOIN bom b ON b.component_id = c.component_id
           ORDER BY c.category, c.name"""
    ).fetchall()
    con.close()
    comps: dict[int, dict] = {}
    for r in rows:
        e = comps.setdefault(r["component_id"], {
            "component_id": r["component_id"], "name": r["name"],
            "category": r["category"], "qty": {},
        })
        e["qty"][r["model_id"]] = r["qty_per_bus"]
    return {"models": models, "components": list(comps.values())}


@app.get("/api/suppliers")
def suppliers():
    con = _connect()
    st = stock.inventory_status(con)
    by_sup: dict[int, dict] = {}
    for c in st["components"]:
        e = by_sup.setdefault(c["supplier_id"], {
            "supplier_id": c["supplier_id"], "supplier": c["supplier"],
            "lead_weeks": c["lead_weeks"], "skus": 0, "critical": 0, "warning": 0,
            "spend_at_stake_cad": 0.0, "components": [],
        })
        e["skus"] += 1
        if c["status"] == "critical":
            e["critical"] += 1
        if c["status"] == "warning":
            e["warning"] += 1
        e["spend_at_stake_cad"] += c["shortfall_units"] * c["unit_cost"]
        e["components"].append({k: c[k] for k in (
            "component_id", "name", "status", "effective_cover_weeks", "lead_weeks", "weekly_use")})
    con.close()
    sups = sorted(by_sup.values(), key=lambda s: (-s["critical"], -s["spend_at_stake_cad"]))
    for s in sups:
        s["spend_at_stake_cad"] = round(s["spend_at_stake_cad"])
        s["components"].sort(key=lambda c: c["effective_cover_weeks"] / max(c["lead_weeks"], 1))
    return {"as_of": st["as_of"], "suppliers": sups}
