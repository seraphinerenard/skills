import { useEffect, useMemo, useState } from "react";
import { Panel, StatusBadge, Tabs, LoadingBlock, fmtCad } from "../components/ui.jsx";
import { useDrawer } from "../components/Drawer.jsx";
import { useToast } from "../components/Toast.jsx";
import { downloadCsv } from "../lib/csv.js";

const FILTERS = ["all", "critical", "warning", "ok"];
const TABS = ["Components", "Purchase orders", "BOM explorer"];

const COLUMNS = [
  { key: "name", label: "Component", align: "left" },
  { key: "supplier", label: "Supplier", align: "left" },
  { key: "lead_weeks", label: "Lead, wks", align: "right" },
  { key: "on_hand", label: "On hand", align: "right" },
  { key: "incoming", label: "On order", align: "right" },
  { key: "weekly_use", label: "Use/wk", align: "right" },
  { key: "effective_cover_weeks", label: "Eff. cover, wks", align: "right" },
  { key: "shortfall_units", label: "Shortfall", align: "right" },
  { key: "status", label: "Status", align: "right" },
];

function ComponentsTab({ inv }) {
  const [filter, setFilter] = useState("all");
  const [sort, setSort] = useState({ key: null, dir: 1 });
  const { openComponent } = useDrawer();
  const toast = useToast();

  const rows = useMemo(() => {
    let r = inv.components.filter((c) => filter === "all" || c.status === filter);
    if (sort.key) {
      r = [...r].sort((a, b) => {
        const va = a[sort.key];
        const vb = b[sort.key];
        return (typeof va === "string" ? va.localeCompare(vb) : va - vb) * sort.dir;
      });
    }
    return r;
  }, [inv, filter, sort]);

  function clickHeader(key) {
    setSort((s) => (s.key === key ? { key, dir: -s.dir } : { key, dir: 1 }));
  }

  function exportCsv() {
    downloadCsv(
      `northline-inventory-${inv.as_of}.csv`,
      rows.map((c) => ({
        component: c.name, category: c.category, supplier: c.supplier,
        lead_weeks: c.lead_weeks, on_hand: c.on_hand, on_order: c.incoming,
        weekly_use: c.weekly_use, effective_cover_weeks: c.effective_cover_weeks,
        shortfall_units: c.shortfall_units, status: c.status,
      })),
    );
    toast(`Exported ${rows.length} rows`);
  }

  return (
    <>
      <div className="mb-3 flex items-center justify-between">
        <div className="seg">
          {FILTERS.map((f) => (
            <button key={f} onClick={() => setFilter(f)}
              className={`capitalize ${f === filter ? "on" : ""}`}>
              {f}
              {f !== "all" && ` (${inv.counts[f]})`}
            </button>
          ))}
        </div>
        <button onClick={exportCsv} className="rounded border border-edge px-3 py-1.5 text-sm text-muted hover:text-ink">
          Export CSV
        </button>
      </div>

      <Panel>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
              {COLUMNS.map((c) => (
                <th
                  key={c.key}
                  onClick={() => clickHeader(c.key)}
                  className={`cursor-pointer py-1.5 font-medium hover:text-ink ${c.align === "right" ? "text-right" : ""}`}
                >
                  {c.label}
                  {sort.key === c.key && (sort.dir > 0 ? " ↑" : " ↓")}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((c) => (
              <tr
                key={c.component_id}
                onClick={() => openComponent(c.component_id)}
                className="row-hover cursor-pointer border-b border-edge/50 hover:bg-ink/[0.03]"
              >
                <td className="py-1.5">
                  {c.name}
                  <span className="ml-2 text-[11px] text-muted">{c.category}</span>
                </td>
                <td className="py-1.5 text-muted">{c.supplier}</td>
                <td className="py-1.5 text-right font-mono">{c.lead_weeks}</td>
                <td className="py-1.5 text-right font-mono">{c.on_hand.toLocaleString("en-CA")}</td>
                <td className="py-1.5 text-right font-mono">{c.incoming ? c.incoming.toLocaleString("en-CA") : "–"}</td>
                <td className="py-1.5 text-right font-mono">{c.weekly_use}</td>
                <td className={`py-1.5 text-right font-mono ${
                  c.status === "critical" ? "text-alert" : c.status === "warning" ? "text-warn" : ""
                }`}>
                  {c.effective_cover_weeks}
                </td>
                <td className="py-1.5 text-right font-mono">
                  {c.shortfall_units ? c.shortfall_units.toLocaleString("en-CA") : "–"}
                </td>
                <td className="py-1.5 text-right"><StatusBadge status={c.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>

      <div className="mt-4 grid grid-cols-2 gap-4">
        <Panel
          title={`Blocked production is worth ${fmtCad(inv.exposure_cad)} over the current lead windows`}
          subtitle="Component shortfalls translated into buses that cannot be built, by model."
        >
          <div className="mt-3 space-y-2">
            {Object.entries(inv.units_at_risk).map(([name, units]) => {
              const max = Math.max(...Object.values(inv.units_at_risk), 1);
              return (
                <div key={name} className="flex items-center gap-2 text-xs">
                  <span className="w-24 shrink-0 text-muted">{name}</span>
                  <div className="h-3 flex-1 rounded-sm bg-ink/10">
                    <div className="h-3 rounded-sm bg-alert-vivid" style={{ width: `${(units / max) * 100}%` }} />
                  </div>
                  <span className="w-20 shrink-0 text-right font-mono">{units} buses</span>
                </div>
              );
            })}
          </div>
        </Panel>

        <Panel
          title={
            inv.suppliers?.[0]?.critical >= 2
              ? `${inv.suppliers[0].supplier} concentrates ${inv.suppliers[0].critical} critical shortfalls under one roof`
              : "No single supplier concentrates the critical shortfalls"
          }
          subtitle="The full supplier board lives on the Suppliers page."
        >
          <table className="mt-3 w-full text-sm">
            <tbody>
              {inv.suppliers?.slice(0, 6).map((s) => (
                <tr key={s.supplier} className="border-b border-edge/50">
                  <td className="py-1.5">{s.supplier}</td>
                  <td className="py-1.5 text-right font-mono text-muted">{s.components} SKUs</td>
                  <td className={`py-1.5 text-right font-mono ${s.critical ? "text-alert" : "text-muted"}`}>
                    {s.critical ? `${s.critical} critical` : "–"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      </div>
    </>
  );
}

function PurchaseOrdersTab() {
  const [data, setData] = useState(null);
  useEffect(() => {
    fetch("/api/pos").then((r) => r.json()).then(setData).catch(() => {});
  }, []);
  if (!data) return <LoadingBlock h="h-64" />;
  const total = data.pos.reduce((s, p) => s + p.value_cad, 0);
  return (
    <Panel
      title={`${data.pos.length} open purchase orders worth ${fmtCad(total)} are on the way`}
      subtitle="Inside lead window means the arrival already counts toward effective cover."
    >
      <table className="mt-3 w-full text-sm">
        <thead>
          <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
            <th className="py-1.5 font-medium">Component</th>
            <th className="py-1.5 font-medium">Supplier</th>
            <th className="py-1.5 text-right font-medium">Qty</th>
            <th className="py-1.5 text-right font-medium">Value</th>
            <th className="py-1.5 text-right font-medium">Arrives</th>
            <th className="py-1.5 text-right font-medium">In</th>
            <th className="py-1.5 text-right font-medium">Window</th>
          </tr>
        </thead>
        <tbody>
          {data.pos.map((p) => (
            <tr key={p.po_id} className="border-b border-edge/50">
              <td className="py-1.5">{p.name}</td>
              <td className="py-1.5 text-muted">{p.supplier}</td>
              <td className="py-1.5 text-right font-mono">{p.qty.toLocaleString("en-CA")}</td>
              <td className="py-1.5 text-right font-mono">{fmtCad(p.value_cad)}</td>
              <td className="py-1.5 text-right font-mono">{p.eta_week}</td>
              <td className="py-1.5 text-right font-mono">
                {p.weeks_out === 0 ? "this wk" : `${p.weeks_out} wks`}
              </td>
              <td className={`py-1.5 text-right text-xs ${p.inside_lead ? "text-good" : "text-muted"}`}>
                {p.inside_lead ? "inside lead" : "beyond lead"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

function BomTab() {
  const [data, setData] = useState(null);
  const { openComponent } = useDrawer();
  useEffect(() => {
    fetch("/api/bom").then((r) => r.json()).then(setData).catch(() => {});
  }, []);
  if (!data) return <LoadingBlock h="h-64" />;
  return (
    <Panel
      title="The bill of materials: what each bus consumes"
      subtitle="Whole numbers are units per bus; percentages are option take rates. Click a row for the component's position."
    >
      <table className="mt-3 w-full text-sm">
        <thead>
          <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
            <th className="py-1.5 font-medium">Component</th>
            <th className="py-1.5 font-medium">Category</th>
            {data.models.map((m) => (
              <th key={m} className="py-1.5 text-right font-medium">{m}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.components.map((c) => (
            <tr
              key={c.component_id}
              onClick={() => openComponent(c.component_id)}
              className="row-hover cursor-pointer border-b border-edge/50 hover:bg-ink/[0.03]"
            >
              <td className="py-1.5">{c.name}</td>
              <td className="py-1.5 text-muted">{c.category}</td>
              {[1, 2, 3].map((mid) => {
                const q = c.qty[mid];
                return (
                  <td key={mid} className="py-1.5 text-right font-mono">
                    {q == null ? <span className="text-muted">–</span> : q < 1 ? `${Math.round(q * 100)}%` : q}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </Panel>
  );
}

export default function InventoryHealth() {
  const [inv, setInv] = useState(null);
  const [tab, setTab] = useState(TABS[0]);

  useEffect(() => {
    fetch("/api/inventory").then((r) => r.json()).then(setInv).catch(() => {});
  }, []);

  if (!inv) return <LoadingBlock h="h-96" />;
  const crit = inv.counts.critical;

  return (
    <div className="stagger space-y-4">
      <section>
        <h1 className="text-lg font-semibold tracking-tight">
          {crit > 0
            ? `${crit} components run out before their suppliers can deliver`
            : "Every component clears its supplier lead time"}
        </h1>
        <p className="mt-0.5 text-xs text-muted">
          Effective cover counts stock on hand plus purchase orders arriving inside the lead
          window, divided by forecast weekly consumption.
        </p>
      </section>

      <Tabs tabs={TABS} active={tab} onChange={setTab} />

      {tab === "Components" && <ComponentsTab inv={inv} />}
      {tab === "Purchase orders" && <PurchaseOrdersTab />}
      {tab === "BOM explorer" && <BomTab />}
    </div>
  );
}
