import CountUp from "./CountUp.jsx";
import { WarningCircle, Warning, Eye, CheckCircle } from "./icons.jsx";

const SEVERITY = {
  alert: { edge: "border-l-alert", label: "text-alert", tint: "var(--tint-alert)", Icon: WarningCircle, ic: "var(--color-alert-vivid)" },
  warning: { edge: "border-l-warn", label: "text-warn", tint: "var(--tint-warn)", Icon: Warning, ic: "var(--color-warn-vivid)" },
  watch: { edge: "border-l-accent", label: "text-accent", tint: "var(--tint-accent)", Icon: Eye, ic: "var(--color-accent-vivid)" },
  good: { edge: "border-l-good", label: "text-good", tint: "var(--tint-good)", Icon: CheckCircle, ic: "var(--color-good-vivid)" },
};

const TILE_TINT = {
  alert: "var(--tint-alert)",
  warn: "var(--tint-warn)",
  good: "var(--tint-good)",
  accent: "var(--tint-accent)",
};

export function Panel({ title, subtitle, children, className = "" }) {
  return (
    <div className={`panel p-4 ${className}`}>
      {title && <h2 className="text-sm font-medium">{title}</h2>}
      {subtitle && <p className="mt-0.5 text-xs text-muted">{subtitle}</p>}
      {children}
    </div>
  );
}

export function StatTile({ label, value, note, tone, format, Icon }) {
  const toneClass =
    tone === "alert" ? "text-alert" : tone === "warn" ? "text-warn" : tone === "good" ? "text-good" : "";
  const iconColor =
    tone === "alert" ? "var(--color-alert-vivid)" : tone === "warn" ? "var(--color-warn-vivid)"
    : tone === "good" ? "var(--color-good-vivid)" : "var(--color-accent-vivid)";
  return (
    <div className="panel relative p-4" style={tone ? { background: TILE_TINT[tone], borderColor: "transparent" } : undefined}>
      {Icon && (
        <Icon size={20} color={iconColor}
          className="glow absolute right-3.5 top-3.5" style={{ "--glow": iconColor }} />
      )}
      <div className="text-[11px] uppercase tracking-wide text-muted">{label}</div>
      <div className={`display mt-2 text-[34px] font-medium leading-none tracking-tight ${toneClass} ${tone ? "glow-text" : ""}`}>
        {typeof value === "number" ? <CountUp value={value} format={format} /> : value ?? "–"}
      </div>
      {note && <div className="mt-2 text-xs text-muted">{note}</div>}
    </div>
  );
}

export function SeverityCard({ severity, title, body, style }) {
  const s = SEVERITY[severity] ?? SEVERITY.watch;
  const tag = { alert: "Immediate", warning: "Warning", watch: "Watch", good: "Healthy" }[severity];
  return (
    <div
      className={`panel border-l-2 ${s.edge} px-4 py-3`}
      style={{ background: s.tint, borderTopColor: "transparent", borderRightColor: "transparent", borderBottomColor: "transparent", ...style }}
    >
      <div className="flex items-center gap-2">
        <s.Icon size={16} color={s.ic} className="glow shrink-0" style={{ "--glow": s.ic }} />
        <span className={`text-[10px] font-semibold uppercase tracking-wider ${s.label}`}>{tag}</span>
        <h3 className="text-sm font-medium">{title}</h3>
      </div>
      <p className="mt-1 pl-6 text-[13px] leading-relaxed text-ink/85">{body}</p>
    </div>
  );
}

export function StatusBadge({ status }) {
  const cls =
    status === "critical"
      ? "bg-alert-vivid/15 text-alert"
      : status === "warning"
        ? "bg-warn-vivid/20 text-warn"
        : "bg-good-vivid/15 text-good";
  return (
    <span className={`rounded px-1.5 py-0.5 text-[11px] font-medium ${cls}`}>{status}</span>
  );
}

export function LoadingBlock({ h = "h-40" }) {
  return <div className={`${h} panel opacity-60`} />;
}

export function ErrorBlock({ children }) {
  return (
    <div className="panel p-4 text-sm text-muted">{children}</div>
  );
}

export function fmtCad(v) {
  if (v == null) return "–";
  if (Math.abs(v) >= 1e6) return `$${(v / 1e6).toFixed(1)}M`;
  if (Math.abs(v) >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${Math.round(v)}`;
}

export function Tabs({ tabs, active, onChange }) {
  return (
    <div className="flex gap-1 border-b border-edge">
      {tabs.map((t) => (
        <button
          key={t}
          onClick={() => onChange(t)}
          className={`-mb-px border-b-2 px-3 py-2 text-sm transition-colors ${
            t === active
              ? "border-accent font-medium text-accent"
              : "border-transparent text-muted hover:text-ink"
          }`}
        >
          {t}
        </button>
      ))}
    </div>
  );
}
