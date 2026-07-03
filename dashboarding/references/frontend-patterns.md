# Frontend patterns

The reference implementation is `templates/northline/frontend/`. Stack: Vite + React + Tailwind v4 (`@tailwindcss/vite` plugin), dev server proxying `/api` to the backend so there is no CORS handling in development. Dark, dense, tabular-nums throughout; the design skill governs everything visual.

## App skeleton

A BI replacement is a multi-view product: left sidebar navigation, a thin top bar with the tracked/critical counts and the as-of stamp, one route per view, and the chat dock on every view.

```
┌──────────┬───────────────────────────────────────────┐
│ Brand    │ 26 components tracked · 4 critical    as of│
│ block    ├───────────────────────────────────────────┤
│          │                                            │
│ Overview │   The active view                          │
│ Demand   │   (Overview: insight feed → KPI row →      │
│ Inventory│    status by category → demand snapshot)   │
│ Recomms  │                                            │
│ What-if  │                                            │
│ Agent hub│                                            │
│          │                        [Ask the analyst]───┼─ ChatDock pill
└──────────┴───────────────────────────────────────────┘
```

Routing is `react-router-dom` with `NavLink` for the active state; the sidebar carries the brand block, the view list, and a one-line provenance note. The top bar repeats the two numbers an executive checks first.

## KPI header

One row of monochrome tiles. Each tile: small uppercase label (11px, tracking-wide, muted), the number large in tabular nums, and the delta as text with sign ("−4.1% vs prior 28d"). The single accent colour goes only on the tile whose delta crossed a threshold; the rest stay neutral. No icons, no per-tile colours, no sparkline unless the tile's question has a time shape.

## Charts

Inline SVG, hand-sized to the panel, following make-charts: full-sentence title, subtitle carrying the backtest stat, direct labels at line ends instead of a legend, muted quarter-line gridlines at most. The forecast band is the accent colour at 12–15% opacity; the forecast mean is dashed; history is the solid, brighter line. Compute the title text from the data ("Ridership is down 4.1% over 28 days; the forecast holds the decline") so the panel never states a stale claim.

## Data table

Plain `<table>` with sticky header, right-aligned numeric columns in tabular nums, units in the column header ("Eff. cover, wks"), one row per item, sorted by the column that answers the panel's question (the reference app sorts components by cover-to-lead ratio, so the most urgent row is first). Row click selects and repoints the detail chart where one exists: the table is the navigation, so no separate picker widget is needed.

## Chat dock

Collapsed: a small fixed pill, bottom-right, labelled "Ask the analyst". Expanded: a 400px column, max 70vh, with header, scrolling transcript, and input. It sits beside the panels; the dashboard stays visible and interactive.

Streaming consumption, the part juniors get wrong: `EventSource` cannot POST, so read the stream with `fetch` and parse SSE frames by hand.

```jsx
const res = await fetch("/api/chat", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ messages }),
});
const reader = res.body.getReader();
const decoder = new TextDecoder();
let buf = "";
for (;;) {
  const { value, done } = await reader.read();
  if (done) break;
  buf += decoder.decode(value, { stream: true });
  let i;
  while ((i = buf.indexOf("\n\n")) >= 0) {
    const frame = buf.slice(0, i); buf = buf.slice(i + 2);
    const line = frame.split("\n").find((l) => l.startsWith("data: "));
    if (line) handleEvent(JSON.parse(line.slice(6)));
  }
}
```

Rendering rules:

- `delta` events append to the current assistant bubble; the bubble exists from the first token.
- `tool` events insert a step row: collapsed shows `run_sql — 8 rows`; expanded shows the exact SQL in a `<pre>` and the summary. Steps arrive before the answer and stay in the transcript as the audit trail.
- `error` events render as a plain sentence in the transcript, never a toast.
- While waiting for the first event, show a single quiet "thinking" line, no spinner animation loops.

## Pin as panel

Each completed assistant answer gets a "Pin as panel" action. Pinning appends `{question, answer, steps, pinnedAt}` to dashboard state and renders a card in the Pinned answers section: the question as the card title, the answer text, and a collapsed "show working" that reveals the tool steps. Persist pins to `localStorage` in the template; a real deployment persists them server-side per user. This is the growth mechanism of the dashboard, so make the action obvious and the unpin equally easy.

## States

Every panel and the dock implement all four states before the happy path ships:

- **Loading:** dim skeleton block, static, no shimmer sweep.
- **Empty:** one sentence stating what will appear and what feeds it ("Pinned answers from the analyst appear here").
- **Error:** the failed request named, with a retry action ("Could not load the forecast. Retry").
- **Zero-data:** distinct from error ("No components below their safety band").
