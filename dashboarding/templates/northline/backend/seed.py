"""Seed northline.db: Northline Coachworks, a fictional school-bus manufacturer.

This file is the executable data contract. Fixed seed so every rebuild produces
identical numbers. The domain follows the demand-to-inventory chain:

  bus_models      what the factory sells (price, category)
  demand_weekly   three years of weekly order intake per model (the series we forecast)
  suppliers       who provides components (lead time in weeks)
  components      purchasable SKUs with unit cost, category, supplier
  bom             components consumed per bus built, by model (fractional = take rate)
  inventory       on-hand units per component
  purchase_orders open POs with quantity and arrival week
"""

import sqlite3
from datetime import date, timedelta

import numpy as np

DB = "northline.db"
RNG = np.random.default_rng(11)
START = date(2023, 7, 3)  # a Monday
WEEKS = 157  # three years of Mondays, ending 2026-06-29

BUS_MODELS = [
    # (id, name, category, price_cad, base_weekly_orders, yearly_trend)
    (1, "N45 Legacy", "Type C diesel", 148000, 36.0, -0.03),
    (2, "N30 Micro", "Type A diesel", 84000, 21.0, 0.00),
    (3, "NE Volt", "Type C electric", 318000, 7.0, 0.28),
]

# School districts buy in winter and spring for September delivery, so order
# intake peaks January to May and softens through late summer.
MONTH_SHAPE = {1: 1.25, 2: 1.30, 3: 1.28, 4: 1.18, 5: 1.05, 6: 0.90,
               7: 0.72, 8: 0.70, 9: 0.85, 10: 0.95, 11: 1.02, 12: 0.80}

SUPPLIERS = [
    # (id, name, lead_time_weeks)
    (1, "Marlow Drivetrain", 6),
    (2, "Voltcore Energy", 10),
    (3, "Prairie Steel Fabrication", 5),
    (4, "TrueNorth Glass", 3),
    (5, "Beacon Safety Systems", 4),
    (6, "Cyrus Electrics", 6),
    (7, "Redpoll Interiors", 4),
    (8, "Harbour Coatings", 2),
    (9, "Lakehead Rubber", 3),
    (10, "Keldan Composites", 6),  # deliberately concentrated: supplies 4 SKUs
]

COMPONENTS = [
    # (id, name, category, supplier_id, unit_cost_cad)
    (1, "Diesel engine 6.7L", "Powertrain", 1, 14200),
    (2, "Automatic transmission", "Powertrain", 1, 6900),
    (3, "EV battery pack 210kWh", "Powertrain", 2, 48500),
    (4, "Electric drive unit", "Powertrain", 2, 17800),
    (5, "Axle set", "Powertrain", 1, 3600),
    (6, "Chassis rail pair", "Chassis", 3, 4100),
    (7, "Brake kit", "Chassis", 3, 1450),
    (8, "Suspension kit", "Chassis", 3, 2200),
    (9, "Steering assembly", "Chassis", 1, 1900),
    (10, "Tire set", "Chassis", 9, 1650),
    (11, "Body panel set", "Body", 10, 5200),
    (12, "Floor panel set", "Body", 10, 2350),
    (13, "Roof hatch pair", "Body", 10, 640),
    (14, "Entry door assembly", "Body", 10, 1880),
    (15, "Glass kit", "Body", 4, 2100),
    (16, "Exterior paint kit", "Body", 8, 780),
    (17, "Seat set", "Interior", 7, 6400),
    (18, "Seat belt kit", "Safety", 5, 940),
    (19, "Stop arm", "Safety", 5, 380),
    (20, "Crossing gate", "Safety", 5, 420),
    (21, "Camera system", "Safety", 6, 1250),
    (22, "Wheelchair lift", "Safety", 5, 5600),
    (23, "Wiring harness", "Electrical", 6, 2750),
    (24, "LED lighting kit", "Electrical", 6, 560),
    (25, "Telematics unit", "Electrical", 6, 890),
    (26, "HVAC unit", "Electrical", 7, 3900),
]

# Units consumed per bus built. Fractional values are option take rates
# (e.g. 35% of N30 Micro orders include a wheelchair lift).
BOM = {
    #  component: {model_id: qty per bus}
    1: {1: 1, 2: 1},            # diesel engine
    2: {1: 1, 2: 1},            # transmission
    3: {3: 1},                  # EV battery pack
    4: {3: 1},                  # electric drive unit
    5: {1: 1, 2: 1, 3: 1},      # axle set
    6: {1: 1, 2: 1, 3: 1},
    7: {1: 1, 2: 1, 3: 1},
    8: {1: 1, 2: 1, 3: 1},
    9: {1: 1, 2: 1, 3: 1},
    10: {1: 1, 2: 1, 3: 1},
    11: {1: 1, 2: 0.8, 3: 1},
    12: {1: 1, 2: 1, 3: 1},
    13: {1: 2, 2: 1, 3: 2},
    14: {1: 1, 2: 1, 3: 1},
    15: {1: 1, 2: 0.7, 3: 1},
    16: {1: 1, 2: 1, 3: 1},
    17: {1: 1, 2: 1, 3: 1},
    18: {1: 1, 2: 1, 3: 1},
    19: {1: 1, 2: 1, 3: 1},
    20: {1: 1, 2: 1, 3: 1},
    21: {1: 1, 2: 1, 3: 1.5},
    22: {1: 0.15, 2: 0.35, 3: 0.6},
    23: {1: 1, 2: 1, 3: 1.4},
    24: {1: 1, 2: 1, 3: 1},
    25: {1: 1, 2: 1, 3: 1},
    26: {1: 1, 2: 0.6, 3: 1},
}

# On-hand inventory expressed in weeks of current consumption, chosen so the
# demo opens with a believable mix: four critical shortfalls (the EV battery
# pack is the star, near-stockout against a 10-week lead), a warning band with
# no buffer for a late PO, and healthy stock elsewhere. Values are calibrated
# against forecast consumption, which runs ~0.7x recent actuals in the July
# seasonal trough.
COVER_WEEKS = {
    3: 0.3,   # EV battery pack: critical, 10-week lead
    12: 2.7,  # floor panels (Keldan): critical
    14: 2.8,  # entry doors (Keldan): critical
    22: 1.3,  # wheelchair lifts: critical
    1: 5.0, 4: 6.2, 11: 5.4, 15: 2.9, 17: 4.0, 21: 5.8, 23: 5.0, 26: 3.6,  # warning band
    2: 7.2, 5: 7.2, 6: 6.5, 7: 6.1, 8: 6.8, 9: 6.8, 10: 3.6, 13: 7.2,
    16: 2.5, 18: 4.7, 19: 5.0, 20: 5.0, 24: 7.2, 25: 6.8,                  # healthy
}

# Open purchase orders: (component_id, qty_in_weeks_of_use, weeks_until_arrival)
OPEN_POS = [
    (3, 5.0, 6),   # battery packs en route, still leaves a lead-window gap
    (12, 1.0, 4), (14, 1.0, 3), (10, 2.0, 2), (1, 1.0, 5),
    (21, 1.0, 7), (4, 2.0, 8), (17, 1.0, 6),
]


def main() -> None:
    con = sqlite3.connect(DB)
    con.executescript(
        """
        DROP TABLE IF EXISTS bus_models;
        DROP TABLE IF EXISTS demand_weekly;
        DROP TABLE IF EXISTS suppliers;
        DROP TABLE IF EXISTS components;
        DROP TABLE IF EXISTS bom;
        DROP TABLE IF EXISTS inventory;
        DROP TABLE IF EXISTS purchase_orders;

        CREATE TABLE bus_models (
            model_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price_cad REAL NOT NULL
        );
        CREATE TABLE demand_weekly (
            model_id INTEGER NOT NULL REFERENCES bus_models(model_id),
            week TEXT NOT NULL,          -- ISO date of the Monday
            orders INTEGER NOT NULL,     -- buses ordered that week
            PRIMARY KEY (model_id, week)
        );
        CREATE TABLE suppliers (
            supplier_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            lead_time_weeks INTEGER NOT NULL
        );
        CREATE TABLE components (
            component_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            supplier_id INTEGER NOT NULL REFERENCES suppliers(supplier_id),
            unit_cost_cad REAL NOT NULL
        );
        CREATE TABLE bom (
            component_id INTEGER NOT NULL REFERENCES components(component_id),
            model_id INTEGER NOT NULL REFERENCES bus_models(model_id),
            qty_per_bus REAL NOT NULL,
            PRIMARY KEY (component_id, model_id)
        );
        CREATE TABLE inventory (
            component_id INTEGER PRIMARY KEY REFERENCES components(component_id),
            on_hand INTEGER NOT NULL
        );
        CREATE TABLE purchase_orders (
            po_id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER NOT NULL REFERENCES components(component_id),
            qty INTEGER NOT NULL,
            eta_week TEXT NOT NULL       -- ISO date of the arrival Monday
        );
        DROP TABLE IF EXISTS po_drafts;
        CREATE TABLE po_drafts (
            draft_id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id INTEGER NOT NULL REFERENCES components(component_id),
            qty INTEGER NOT NULL,
            cost_cad REAL NOT NULL,
            source TEXT NOT NULL,        -- 'analyst' | 'optimizer' | 'plan'
            status TEXT NOT NULL DEFAULT 'draft',  -- draft | approved | rejected
            created_at TEXT NOT NULL
        );
        """
    )

    con.executemany("INSERT INTO bus_models VALUES (?,?,?,?)",
                    [(m[0], m[1], m[2], m[3]) for m in BUS_MODELS])
    con.executemany("INSERT INTO suppliers VALUES (?,?,?)", SUPPLIERS)
    con.executemany("INSERT INTO components VALUES (?,?,?,?,?)", COMPONENTS)
    con.executemany(
        "INSERT INTO bom VALUES (?,?,?)",
        [(cid, mid, qty) for cid, per in BOM.items() for mid, qty in per.items()],
    )

    # Weekly demand: seasonality by month, trend by model, a supply-chain dip
    # in autumn 2024, and noise last.
    for mid, _, _, _, base, trend in BUS_MODELS:
        for w in range(WEEKS):
            monday = START + timedelta(weeks=w)
            level = base * (1 + trend) ** (w / 52.18) * MONTH_SHAPE[monday.month]
            if date(2024, 9, 1) <= monday <= date(2024, 11, 30):
                level *= 0.82  # industry-wide chassis shortage that autumn
            orders = max(0, int(round(RNG.normal(level, level * 0.16))))
            con.execute("INSERT INTO demand_weekly VALUES (?,?,?)",
                        (mid, monday.isoformat(), orders))

    # Current weekly consumption per component (recent 13-week demand average),
    # used to translate cover-weeks targets into on-hand units.
    recent = {
        mid: con.execute(
            "SELECT AVG(orders) FROM (SELECT orders FROM demand_weekly "
            "WHERE model_id=? ORDER BY week DESC LIMIT 13)", (mid,)
        ).fetchone()[0]
        for mid, *_ in BUS_MODELS
    }
    weekly_use = {
        cid: sum(qty * recent[mid] for mid, qty in per.items())
        for cid, per in BOM.items()
    }

    last_monday = START + timedelta(weeks=WEEKS - 1)
    for cid, cover in COVER_WEEKS.items():
        on_hand = int(round(weekly_use[cid] * cover * RNG.normal(1.0, 0.05)))
        con.execute("INSERT INTO inventory VALUES (?,?)", (cid, on_hand))
    for cid, qty_weeks, eta_weeks in OPEN_POS:
        qty = int(round(weekly_use[cid] * qty_weeks))
        eta = last_monday + timedelta(weeks=eta_weeks)
        con.execute(
            "INSERT INTO purchase_orders (component_id, qty, eta_week) VALUES (?,?,?)",
            (cid, qty, eta.isoformat()),
        )

    con.commit()
    n = con.execute("SELECT COUNT(*) FROM demand_weekly").fetchone()[0]
    print(f"Seeded {DB}: {len(BUS_MODELS)} bus models, {len(COMPONENTS)} components, "
          f"{n} demand weeks, {START.isoformat()} to {last_monday.isoformat()}")
    con.close()


if __name__ == "__main__":
    main()
