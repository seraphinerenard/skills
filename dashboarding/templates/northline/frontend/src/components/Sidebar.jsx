import { NavLink } from "react-router-dom";
import {
  SquaresFour, TrendUp, Package, Truck, Factory, Sparkle, Sliders, Robot,
} from "./icons.jsx";

const NAV = [
  { to: "/", label: "Overview", end: true, Icon: SquaresFour, c: "var(--color-accent-vivid)" },
  { to: "/demand", label: "Demand forecast", Icon: TrendUp, c: "var(--color-good-vivid)" },
  { to: "/inventory", label: "Inventory health", Icon: Package, c: "var(--color-warn-vivid)" },
  { to: "/suppliers", label: "Suppliers", Icon: Truck, c: "var(--color-alert-vivid)" },
  { to: "/production", label: "Production plan", Icon: Factory, c: "var(--color-accent-vivid)" },
  { to: "/recommendations", label: "AI recommendations", Icon: Sparkle, c: "var(--color-good-vivid)" },
  { to: "/whatif", label: "What-if simulator", Icon: Sliders, c: "var(--color-warn-vivid)" },
  { to: "/agents", label: "Agent hub", Icon: Robot, c: "var(--color-alert-vivid)" },
];

/* Floating rail: the sidebar is a card on the canvas, Gmail-tinted, with a
   Phosphor icon per view coloured by the Google primary it owns. */
export default function Sidebar() {
  return (
    <aside className="rail m-3 mr-0 flex w-60 shrink-0 flex-col">
      <div className="border-b border-edge px-5 py-5">
        <div className="flex items-center gap-2.5">
          <svg width="28" height="28" viewBox="0 0 26 26" aria-hidden="true">
            <rect x="3" y="6" width="20" height="11" rx="2.5" fill="none" stroke="var(--color-accent)" strokeWidth="1.8" />
            <line x1="3" y1="12" x2="23" y2="12" stroke="var(--color-accent)" strokeWidth="1.4" />
            <circle cx="8.5" cy="19.5" r="2" fill="none" stroke="var(--color-accent)" strokeWidth="1.6" />
            <circle cx="17.5" cy="19.5" r="2" fill="none" stroke="var(--color-accent)" strokeWidth="1.6" />
          </svg>
          <div>
            <div className="display text-sm font-semibold leading-tight tracking-tight">
              Northline Coachworks
            </div>
            <div className="text-[10px] uppercase tracking-widest text-muted">
              Inventory intelligence
            </div>
          </div>
        </div>
      </div>

      <nav className="flex-1 px-3 py-3">
        {NAV.map(({ to, label, end, Icon, c }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `mb-1 flex items-center gap-3 rounded-full px-3.5 py-2 text-[13.5px] transition-all duration-150 ${
                isActive
                  ? "font-medium text-ink"
                  : "text-muted hover:translate-x-0.5 hover:bg-accent/10 hover:text-ink"
              }`
            }
            style={({ isActive }) => (isActive ? { background: "var(--chip-active)" } : undefined)}
          >
            <Icon size={18} color={c} className="glow" style={{ "--glow": c }} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-edge px-5 py-3 text-[11px] leading-relaxed text-muted">
        Reference build for the dashboarding skill. Fictional company, synthetic data.
      </div>
    </aside>
  );
}
