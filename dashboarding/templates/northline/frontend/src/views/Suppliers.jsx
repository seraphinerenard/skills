import { useEffect, useState } from "react";
import { Panel, StatusBadge, LoadingBlock, fmtCad } from "../components/ui.jsx";
import { useDrawer } from "../components/Drawer.jsx";

/* Supplier risk board: scorecards ranked by criticals and spend at stake,
   with the selected supplier's book underneath. */
export default function Suppliers() {
  const [data, setData] = useState(null);
  const [sel, setSel] = useState(null);
  const { openComponent } = useDrawer();

  useEffect(() => {
    fetch("/api/suppliers")
      .then((r) => r.json())
      .then((d) => {
        setData(d);
        setSel(d.suppliers[0]?.supplier_id ?? null);
      })
      .catch(() => {});
  }, []);

  if (!data) return <LoadingBlock h="h-96" />;
  const selected = data.suppliers.find((s) => s.supplier_id === sel);
  const worstCrit = data.suppliers[0];
  const worstSpend = [...data.suppliers].sort((a, b) => b.spend_at_stake_cad - a.spend_at_stake_cad)[0];

  return (
    <div className="stagger space-y-4">
      <section>
        <h1 className="text-lg font-semibold tracking-tight">
          {worstCrit.critical > 0
            ? `${worstCrit.supplier} concentrates the most critical SKUs (${worstCrit.critical}); ${worstSpend.supplier} has the most money at stake (${fmtCad(worstSpend.spend_at_stake_cad)})`
            : "No supplier carries a critical shortfall right now"}
        </h1>
        <p className="mt-0.5 text-xs text-muted">
          Spend at stake is each supplier's shortfall over its lead window priced at unit cost.
          Click a card for their book; click a component for the full position.
        </p>
      </section>

      <div className="stagger grid grid-cols-5 gap-3">
        {data.suppliers.map((s) => (
          <button
            key={s.supplier_id}
            onClick={() => setSel(s.supplier_id)}
            className={`panel p-3.5 text-left transition-colors ${
              s.supplier_id === sel ? "border-accent/60" : "hover:border-accent/40"
            }`}
          >
            <div className="flex items-start justify-between gap-2">
              <span className="text-sm font-medium leading-tight">{s.supplier}</span>
              {s.critical > 0 && (
                <span className="rounded bg-alert/15 px-1.5 py-0.5 text-[11px] font-medium text-alert">
                  {s.critical}
                </span>
              )}
            </div>
            <div className="mt-2 font-mono text-lg">{fmtCad(s.spend_at_stake_cad)}</div>
            <div className="text-[11px] text-muted">at stake</div>
            <div className="mt-2 text-[11px] text-muted">
              {s.skus} SKUs · {s.lead_weeks}-wk lead
              {s.warning > 0 && ` · ${s.warning} warning`}
            </div>
          </button>
        ))}
      </div>

      {selected && (
        <Panel
          title={`${selected.supplier} supplies ${selected.skus} tracked components on a ${selected.lead_weeks}-week lead`}
          subtitle={
            selected.critical >= 2
              ? "Two or more criticals under one roof is single-source concentration; a second source is worth pricing."
              : "Sorted by cover-to-lead ratio, most urgent first."
          }
        >
          <table className="mt-3 w-full text-sm">
            <thead>
              <tr className="border-b border-edge text-left text-[11px] uppercase tracking-wide text-muted">
                <th className="py-1.5 font-medium">Component</th>
                <th className="py-1.5 text-right font-medium">Use/wk</th>
                <th className="py-1.5 text-right font-medium">Eff. cover, wks</th>
                <th className="py-1.5 text-right font-medium">Lead, wks</th>
                <th className="py-1.5 text-right font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {selected.components.map((c) => (
                <tr
                  key={c.component_id}
                  onClick={() => openComponent(c.component_id)}
                  className="row-hover cursor-pointer border-b border-edge/50 hover:bg-ink/[0.03]"
                >
                  <td className="py-1.5">{c.name}</td>
                  <td className="py-1.5 text-right font-mono">{c.weekly_use}</td>
                  <td className={`py-1.5 text-right font-mono ${
                    c.status === "critical" ? "text-alert" : c.status === "warning" ? "text-warn" : ""
                  }`}>
                    {c.effective_cover_weeks}
                  </td>
                  <td className="py-1.5 text-right font-mono">{c.lead_weeks}</td>
                  <td className="py-1.5 text-right"><StatusBadge status={c.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </Panel>
      )}
    </div>
  );
}
