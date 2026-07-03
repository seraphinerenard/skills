import { createContext, useContext, useEffect, useState } from "react";
import { StatusBadge, fmtCad } from "./ui.jsx";
import { useToast } from "./Toast.jsx";

const DrawerCtx = createContext({ openComponent: () => {} });
export const useDrawer = () => useContext(DrawerCtx);

/* Stripe-style right drawer: click any component anywhere and get its full
   position — status, cover vs lead, BOM usage, open POs, and a draft-PO action. */
export function DrawerProvider({ children }) {
  const [componentId, setComponentId] = useState(null);
  return (
    <DrawerCtx.Provider value={{ openComponent: setComponentId }}>
      {children}
      {componentId != null && (
        <ComponentDrawer componentId={componentId} onClose={() => setComponentId(null)} />
      )}
    </DrawerCtx.Provider>
  );
}

function Row({ label, children }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-edge/60 py-2 text-sm">
      <span className="shrink-0 text-muted">{label}</span>
      <span className="text-right">{children}</span>
    </div>
  );
}

function ComponentDrawer({ componentId, onClose }) {
  const [d, setD] = useState(null);
  const [qty, setQty] = useState(0);
  const toast = useToast();

  useEffect(() => {
    setD(null);
    fetch(`/api/component/${componentId}`)
      .then((r) => r.json())
      .then((data) => {
        setD(data);
        setQty(data.suggested_order?.qty ?? Math.round(data.weekly_use * 4));
      })
      .catch(() => onClose());
  }, [componentId]);

  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, [onClose]);

  async function draft() {
    await fetch("/api/po-drafts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ items: [{ component_id: componentId, qty }], source: "plan" }),
    });
    toast(`Drafted ${qty.toLocaleString("en-CA")} x ${d.name} — approve it in the Agent hub`, "good");
    onClose();
  }

  return (
    <>
      <div className="anim-pop fixed inset-0 z-30 bg-black/30" onClick={onClose} />
      <aside className="anim-drawer fixed right-0 top-0 z-40 flex h-full w-[420px] flex-col overflow-y-auto border-l border-edge bg-panel">
        {!d ? (
          <div className="p-5 text-sm text-muted">loading</div>
        ) : (
          <>
            <div className="border-b border-edge px-5 py-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold tracking-tight">{d.name}</h2>
                  <p className="mt-0.5 text-xs text-muted">
                    {d.category} · {d.supplier} · {d.lead_weeks}-week lead
                  </p>
                </div>
                <button className="text-xs text-muted hover:text-ink" onClick={onClose}>
                  Close
                </button>
              </div>
              <div className="mt-3 flex items-center gap-3">
                <StatusBadge status={d.status} />
                <span className="text-sm font-mono">
                  {d.effective_cover_weeks} wks cover / {d.lead_weeks} wks lead
                </span>
              </div>
              {/* cover vs lead, drawn to scale */}
              <div className="mt-2 h-2 w-full rounded-sm bg-ink/10">
                <div
                  className={`h-2 rounded-sm ${
                    d.status === "critical" ? "bg-alert-vivid" : d.status === "warning" ? "bg-warn-vivid" : "bg-good-vivid"
                  }`}
                  style={{ width: `${Math.min(100, (d.effective_cover_weeks / (d.lead_weeks * 2)) * 100)}%` }}
                />
                <div className="relative">
                  <span className="absolute -top-2 h-3 w-px bg-ink/50" style={{ left: "50%" }} />
                  <span className="absolute top-1 text-[10px] text-muted" style={{ left: "50%", transform: "translateX(-50%)" }}>
                    lead time
                  </span>
                </div>
              </div>
            </div>

            <div className="px-5 pb-2 pt-4">
              <Row label="On hand">{d.on_hand.toLocaleString("en-CA")} units</Row>
              <Row label="On order">{d.incoming ? `${d.incoming.toLocaleString("en-CA")} units` : "none"}</Row>
              <Row label="Weekly use, forecast">{d.weekly_use} units</Row>
              <Row label="Shortfall over lead window">
                {d.shortfall_units ? (
                  <span className="text-alert">{d.shortfall_units.toLocaleString("en-CA")} units</span>
                ) : (
                  "none"
                )}
              </Row>
              <Row label="Unit cost">{fmtCad(d.unit_cost)}</Row>
            </div>

            <div className="px-5 py-3">
              <h3 className="text-[11px] uppercase tracking-wide text-muted">Used by</h3>
              {d.bom.map((b) => (
                <Row key={b.model} label={b.model}>
                  {b.qty_per_bus < 1 ? `${Math.round(b.qty_per_bus * 100)}% take rate` : `${b.qty_per_bus} per bus`}
                </Row>
              ))}
            </div>

            <div className="px-5 py-3">
              <h3 className="text-[11px] uppercase tracking-wide text-muted">Open purchase orders</h3>
              {d.open_pos.length === 0 ? (
                <p className="py-2 text-sm text-muted">None on the way.</p>
              ) : (
                d.open_pos.map((p, i) => (
                  <Row key={i} label={`arrives ${p.eta_week}`}>{p.qty.toLocaleString("en-CA")} units</Row>
                ))
              )}
            </div>

            <div className="mt-auto border-t border-edge px-5 py-4">
              <h3 className="text-[11px] uppercase tracking-wide text-muted">Draft a purchase order</h3>
              <div className="mt-2 flex items-center gap-2">
                <input
                  type="number"
                  min="1"
                  value={qty}
                  onChange={(e) => setQty(Number(e.target.value))}
                  className="w-28 rounded border border-edge bg-bg px-2 py-1.5 font-mono text-sm"
                />
                <span className="text-xs text-muted">units · {fmtCad(qty * d.unit_cost)}</span>
                <button
                  onClick={draft}
                  className="btn-primary ml-auto px-3 py-1.5 text-sm"
                >
                  Draft for approval
                </button>
              </div>
              {d.suggested_order && (
                <p className="mt-2 text-xs text-muted">
                  The order plan suggests {d.suggested_order.qty.toLocaleString("en-CA")} units
                  ({fmtCad(d.suggested_order.cost_cad)}, {d.suggested_order.priority} priority).
                </p>
              )}
            </div>
          </>
        )}
      </aside>
    </>
  );
}
