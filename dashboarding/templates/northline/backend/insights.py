"""Computed findings for the Overview insight feed.

Each finding is a rule over the inventory engine's output with the numbers that
triggered it: {severity: "alert"|"warning"|"watch"|"good", title, body}. Rules
fire only when their thresholds are crossed, so the feed length varies with the
state of the operation.
"""

import sqlite3

import stock


def compute_findings(con: sqlite3.Connection, status: dict | None = None) -> list[dict]:
    st = status or stock.inventory_status(con)
    findings: list[dict] = []
    comps = st["components"]

    # Immediate stockout risk: worst critical component against its lead time.
    critical = [c for c in comps if c["status"] == "critical"]
    if critical:
        # Headline the starkest raw position: on-hand cover relative to lead time.
        w = min(critical, key=lambda c: c["cover_weeks"] / max(c["lead_weeks"], 1))
        findings.append({
            "severity": "alert",
            "title": f"{len(critical)} components risk a stockout before replenishment",
            "body": (
                f"{w['name']} holds {w['cover_weeks']} weeks of cover against a "
                f"{w['lead_weeks']}-week lead time from {w['supplier']} — the line stops "
                f"without an emergency order. Shortfall over the lead window: "
                f"{w['shortfall_units']:,} units."
            ),
        })

    # Revenue exposure.
    if st["exposure_cad"] > 0:
        short = [c for c in comps if c["shortfall_units"] > 0]
        worst_model = max(st["units_at_risk"], key=st["units_at_risk"].get)
        findings.append({
            "severity": "alert" if st["exposure_cad"] > 3_000_000 else "warning",
            "title": f"${st['exposure_cad'] / 1e6:.1f}M of production value is at risk",
            "body": (
                f"Shortfalls across {len(short)} components block an estimated "
                f"{sum(st['units_at_risk'].values()):.0f} buses over the current lead windows, "
                f"led by {worst_model} ({st['units_at_risk'][worst_model]:.0f} units). Funding the "
                f"critical order plan (${sum(p['cost_cad'] for p in st['order_plan'] if p['priority'] == 'critical') / 1e6:.2f}M) removes most of it."
            ),
        })

    # Supplier concentration.
    sups = stock.supplier_concentration(con, st)
    if sups and sups[0]["critical"] >= 2:
        s = sups[0]
        findings.append({
            "severity": "warning",
            "title": f"{s['supplier']} holds {s['critical']} of the critical shortfalls",
            "body": (
                f"{s['supplier']} supplies {s['components']} tracked components on a "
                f"{s['lead_weeks']}-week lead. A disruption at this single supplier would "
                f"cascade across production lines; a second source is worth pricing."
            ),
        })

    # Warning band: components with no buffer for a late PO.
    warning = [c for c in comps if c["status"] == "warning"]
    if warning:
        findings.append({
            "severity": "watch",
            "title": f"{len(warning)} components run without a buffer",
            "body": (
                f"{', '.join(c['name'] for c in warning[:4])}"
                f"{' and others' if len(warning) > 4 else ''} sit between 1.0x and 1.5x "
                f"their lead time. One late PO moves them into the critical band."
            ),
        })

    # Healthy tail, so the feed is honest rather than alarmist.
    ok = [c for c in comps if c["status"] == "ok"]
    if ok:
        findings.append({
            "severity": "good",
            "title": f"{len(ok)} components hold healthy stock",
            "body": (
                f"Average effective cover across the healthy band is "
                f"{sum(c['effective_cover_weeks'] for c in ok) / len(ok):.1f} weeks, "
                f"comfortably past their reorder points at the current service level of "
                f"{st['service_level_pct']:.0f}%."
            ),
        })

    return findings
