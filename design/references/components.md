# Component patterns

Copy-paste patterns that already obey the skill. Each block is self-contained: paste the token block once per page, then any pattern below it. Values reference the Monochrome-plus-pop set; swap tokens, never inline values.

## Token block

```html
<style>
  :root {
    --bg: #fafafa; --surface: #ffffff; --border: #e4e4e7;
    --ink: #18181b; --muted: #52525b; --accent: #1f4ed8; --on-accent: #ffffff;
    --danger: #b42318; --success: #067647; --warning: #b54708;
    --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    --radius: 6px; --space: 8px;
  }
  body { background: var(--bg); color: var(--ink); font: 16px/1.5 var(--font-sans); margin: 0; }
  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
  @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
</style>
```

## Data table

Real `<table>` markup, sticky header, tabular right-aligned numbers, hover row. Status badges use one tint per semantic colour, never a rainbow.

```html
<style>
  .tbl { width: 100%; border-collapse: collapse; background: var(--surface);
         border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .tbl th { position: sticky; top: 0; background: var(--surface); text-align: left;
            font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: .04em;
            color: var(--muted); padding: 10px 12px; border-bottom: 1px solid var(--border); }
  .tbl td { padding: 10px 12px; border-bottom: 1px solid var(--border); font-size: 14px; }
  .tbl tr:last-child td { border-bottom: 0; }
  .tbl tbody tr:hover { background: color-mix(in srgb, var(--ink) 4%, transparent); }
  .tbl .num { text-align: right; font-variant-numeric: tabular-nums; }
  .badge { display: inline-block; padding: 1px 8px; border-radius: 999px; font-size: 12px; font-weight: 500; }
  .badge.ok   { background: color-mix(in srgb, var(--success) 10%, var(--surface)); color: var(--success); }
  .badge.warn { background: color-mix(in srgb, var(--warning) 12%, var(--surface)); color: var(--warning); }
  .badge.err  { background: color-mix(in srgb, var(--danger) 9%, var(--surface)); color: var(--danger); }
</style>
<table class="tbl">
  <thead><tr><th>Route</th><th class="num">Riders</th><th class="num">On time</th><th>Status</th></tr></thead>
  <tbody>
    <tr><td>17 Harbourfront</td><td class="num">4,182</td><td class="num">93.4%</td><td><span class="badge ok">Normal</span></td></tr>
    <tr><td>32 Millbrook</td><td class="num">2,057</td><td class="num">81.2%</td><td><span class="badge warn">Delayed</span></td></tr>
  </tbody>
</table>
```

## Form with validation states

Label above input, help text below, error replaces help text and colours the border. The submit button stays enabled; validation explains instead of disabling.

```html
<style>
  .field { display: grid; gap: 4px; max-width: 360px; margin-bottom: 16px; }
  .field label { font-size: 14px; font-weight: 600; }
  .field input { font: inherit; padding: 8px 10px; border: 1px solid var(--border);
                 border-radius: var(--radius); background: var(--surface); color: var(--ink); }
  .field input:focus-visible { border-color: var(--accent); }
  .field .help { font-size: 13px; color: var(--muted); }
  .field.invalid input { border-color: var(--danger); }
  .field.invalid .help { color: var(--danger); }
  .btn { font: inherit; font-weight: 600; padding: 8px 16px; border-radius: var(--radius);
         border: 1px solid transparent; background: var(--accent); color: var(--on-accent); cursor: pointer; }
  .btn.secondary { background: var(--surface); color: var(--ink); border-color: var(--border); }
</style>
<div class="field">
  <label for="email">Work email</label>
  <input id="email" type="email" value="dispatch@fernline">
  <div class="help">Enter a full address, like dispatch@fernline.ca.</div>
</div>
<!-- invalid variant: <div class="field invalid"> ... <div class="help">That address is missing its domain.</div> -->
<button class="btn">Save changes</button>
```

## Empty, loading, error, and zero-data states

Text first, one action, no illustration. Loading skeletons are static dim blocks (no shimmer, rule D19), appear only past 300 ms, and match the final layout.

```html
<style>
  .state { border: 1px dashed var(--border); border-radius: var(--radius); background: var(--surface);
           padding: 32px; text-align: center; max-width: 480px; }
  .state h3 { margin: 0 0 4px; font-size: 16px; }
  .state p { margin: 0 0 16px; font-size: 14px; color: var(--muted); }
  .skeleton { border-radius: 4px; background: color-mix(in srgb, var(--ink) 6%, var(--surface)); height: 14px; }
</style>

<!-- Empty: nothing exists yet -->
<div class="state"><h3>No saved views yet</h3>
  <p>Views you pin from the chat panel appear here.</p>
  <button class="btn">Pin your first view</button></div>

<!-- Zero data: the query ran and matched nothing -->
<div class="state"><h3>No trips match these filters</h3>
  <p>Route 32 has no departures between 02:00 and 04:00. Widen the time range to see results.</p>
  <button class="btn secondary">Clear filters</button></div>

<!-- Error: say what failed and what to do -->
<div class="state"><h3>The ridership feed did not respond</h3>
  <p>The last successful sync was 09:41. Retry now or check the feed status page.</p>
  <button class="btn">Retry</button></div>
```

The skeleton animation is the one permitted loop, and it must stop when content arrives; the reduced-motion rule in the token block already disables it for users who ask.

## Card

A card takes a border or a shadow, never both, and earns its existence by grouping unlike content. Like content goes in a table.

```html
<style>
  .card { background: var(--surface); border: 1px solid var(--border);
          border-radius: var(--radius); padding: 16px; }
  .card h3 { margin: 0 0 8px; font-size: 14px; font-weight: 600; }
</style>
<div class="card">
  <h3>Fleet availability</h3>
  <p style="margin:0; font-size:28px; font-variant-numeric:tabular-nums;">62 of 68</p>
  <p style="margin:4px 0 0; font-size:13px; color:var(--muted);">Six coaches in scheduled maintenance until Friday.</p>
</div>
```

## Nav

One line, 64px maximum, name on the left, actions on the right. The active link is marked by weight and an underline, never by a pill of accent colour.

```html
<style>
  .nav { display: flex; align-items: center; gap: 24px; height: 56px; padding: 0 20px;
         background: var(--surface); border-bottom: 1px solid var(--border); }
  .nav .brand { font-weight: 700; margin-right: 8px; }
  .nav a { color: var(--muted); text-decoration: none; font-size: 14px; padding: 4px 0; }
  .nav a[aria-current="page"] { color: var(--ink); font-weight: 600;
                                border-bottom: 2px solid var(--accent); }
  .nav .spacer { flex: 1; }
</style>
<nav class="nav">
  <span class="brand">Fernline</span>
  <a href="#" aria-current="page">Operations</a>
  <a href="#">Forecasts</a>
  <a href="#">Reports</a>
  <span class="spacer"></span>
  <button class="btn secondary">Settings</button>
</nav>
```
