import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useDrawer } from "./Drawer.jsx";

/* Linear-style command palette: Cmd/Ctrl+K, fuzzy filter over views,
   components, suppliers, and actions. */
const VIEWS = [
  { label: "Overview", to: "/" },
  { label: "Demand forecast", to: "/demand" },
  { label: "Inventory health", to: "/inventory" },
  { label: "AI recommendations", to: "/recommendations" },
  { label: "Suppliers", to: "/suppliers" },
  { label: "Production plan", to: "/production" },
  { label: "What-if simulator", to: "/whatif" },
  { label: "Agent hub", to: "/agents" },
];

export default function CommandPalette({ theme, setTheme }) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [items, setItems] = useState([]);
  const [sel, setSel] = useState(0);
  const inputRef = useRef(null);
  const navigate = useNavigate();
  const { openComponent } = useDrawer();

  useEffect(() => {
    const onKey = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        setOpen((o) => !o);
        setQ("");
        setSel(0);
      }
      if (e.key === "Escape") setOpen(false);
    };
    addEventListener("keydown", onKey);
    return () => removeEventListener("keydown", onKey);
  }, []);

  useEffect(() => {
    if (!open) return;
    setTimeout(() => inputRef.current?.focus(), 0);
    fetch("/api/inventory")
      .then((r) => r.json())
      .then((d) =>
        setItems(
          d.components.map((c) => ({
            kind: "component",
            label: c.name,
            hint: `${c.status} · ${c.effective_cover_weeks} wks cover`,
            run: () => openComponent(c.component_id),
          })),
        )
      )
      .catch(() => {});
  }, [open]);

  const commands = useMemo(
    () => [
      ...VIEWS.map((v) => ({ kind: "view", label: `Go to ${v.label}`, hint: "view", run: () => navigate(v.to) })),
      {
        kind: "action", label: `Switch to ${theme === "dark" ? "light" : "dark"} mode`, hint: "action",
        run: () => setTheme(theme === "dark" ? "light" : "dark"),
      },
      { kind: "action", label: "Run the goal optimizer", hint: "action", run: () => navigate("/agents") },
      { kind: "action", label: "Generate AI recommendations", hint: "action", run: () => navigate("/recommendations") },
      ...items,
    ],
    [items, theme, navigate],
  );

  const filtered = useMemo(() => {
    const needle = q.trim().toLowerCase();
    if (!needle) return commands.slice(0, 9);
    return commands
      .filter((c) => c.label.toLowerCase().includes(needle))
      .slice(0, 9);
  }, [q, commands]);

  if (!open) return null;

  function runSel(i) {
    const c = filtered[i];
    if (!c) return;
    setOpen(false);
    c.run();
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center bg-black/30 pt-[16vh]" onClick={() => setOpen(false)}>
      <div className="panel anim-pop w-[560px] overflow-hidden" onClick={(e) => e.stopPropagation()}>
        <input
          ref={inputRef}
          value={q}
          onChange={(e) => { setQ(e.target.value); setSel(0); }}
          onKeyDown={(e) => {
            if (e.key === "ArrowDown") { e.preventDefault(); setSel((s) => Math.min(s + 1, filtered.length - 1)); }
            if (e.key === "ArrowUp") { e.preventDefault(); setSel((s) => Math.max(s - 1, 0)); }
            if (e.key === "Enter") runSel(sel);
          }}
          placeholder="Jump to a view, component, or action"
          className="w-full border-b border-edge bg-transparent px-4 py-3 text-sm outline-none"
        />
        <div className="max-h-80 overflow-y-auto py-1">
          {filtered.length === 0 && <p className="px-4 py-3 text-sm text-muted">No matches.</p>}
          {filtered.map((c, i) => (
            <button
              key={c.label + i}
              onMouseEnter={() => setSel(i)}
              onClick={() => runSel(i)}
              className={`flex w-full items-baseline justify-between px-4 py-2 text-left text-sm ${
                i === sel ? "bg-accent/10 text-accent" : ""
              }`}
            >
              <span>{c.label}</span>
              <span className="text-xs text-muted">{c.hint}</span>
            </button>
          ))}
        </div>
        <div className="border-t border-edge px-4 py-1.5 text-[11px] text-muted">
          Up and down to move, Enter to run, Esc to close
        </div>
      </div>
    </div>
  );
}
