import { useEffect, useRef, useState } from "react";
import { Warning, WarningCircle, ArrowDown } from "./icons.jsx";
import { useDrawer } from "./Drawer.jsx";

/* Live status ticker: every component below its safety band scrolls across the
   top of the canvas. Driven by requestAnimationFrame in whole pixels — a CSS
   keyframe on a track this wide becomes an oversized GPU layer that flickers
   on Retina displays, and sub-pixel motion shimmers the text. Hover pauses;
   click opens the component drawer. The scroll runs under OS reduce-motion
   too: the strip is requested content, and rAF pixel-stepping cannot strobe
   the way a clamped CSS animation can. */
const SPEED_PX_S = 36;

export default function Ticker() {
  const [items, setItems] = useState([]);
  const { openComponent } = useDrawer();
  const trackRef = useRef(null);
  const copyRef = useRef(null);
  const pausedRef = useRef(false);

  useEffect(() => {
    fetch("/api/inventory")
      .then((r) => r.json())
      .then((d) =>
        setItems(d.components.filter((c) => c.status !== "ok").map((c) => ({
          id: c.component_id,
          name: c.name,
          status: c.status,
          cover: c.effective_cover_weeks,
          lead: c.lead_weeks,
        }))),
      )
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (items.length === 0) return;
    let x = 0;
    let last = null;
    let raf;
    const tick = (t) => {
      if (last == null) last = t;
      const dt = Math.min((t - last) / 1000, 0.1);
      last = t;
      if (!pausedRef.current && trackRef.current && copyRef.current) {
        x += SPEED_PX_S * dt;
        const w = copyRef.current.offsetWidth;
        if (w > 0 && x >= w) x -= w;
        trackRef.current.style.transform = `translateX(${-Math.round(x)}px)`;
      }
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [items]);

  if (items.length === 0) return null;

  const copy = (k, ref) => (
    <div key={k} ref={ref} className="flex items-center gap-8 whitespace-nowrap pr-8">
      {items.map((c) => (
        <button
          key={`${k}-${c.id}`}
          onClick={() => openComponent(c.id)}
          className="flex items-center gap-1.5 text-xs text-muted hover:text-ink"
        >
          {c.status === "critical" ? (
            <WarningCircle size={14} color="var(--color-alert-vivid)" />
          ) : (
            <Warning size={14} color="var(--color-warn-vivid)" />
          )}
          <span className="font-medium text-ink">{c.name}</span>
          <ArrowDown size={11} color="var(--color-muted)" />
          <span className="font-mono">{c.cover}w / {c.lead}w lead</span>
        </button>
      ))}
    </div>
  );

  return (
    <div
      className="panel mx-3 mt-3 overflow-hidden py-1.5"
      onMouseEnter={() => { pausedRef.current = true; }}
      onMouseLeave={() => { pausedRef.current = false; }}
    >
      <div ref={trackRef} className="flex w-max">
        {[copy(0, copyRef), copy(1, null)]}
      </div>
    </div>
  );
}
