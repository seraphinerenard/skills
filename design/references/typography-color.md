# Typography and colour

Pick one pairing and one palette before writing markup, and record both as custom properties. Improvised hex values and reflex font choices are how the machine look creeps back in.

## Font stacks

**Self-contained deliverables (single-file HTML, demos, internal tools) use system stacks.** No network fetch, no layout shift, and modern system faces are good:

```css
--font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
--font-mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
```

**Projects with a build step pick a loaded face.** The sans pool, in rough order of range:

| Face | Character | Use for |
|---|---|---|
| Geist | Neutral, engineered | Product UI, dashboards |
| Source Sans 3 | Warm workhorse | Long-form product surfaces, docs |
| Public Sans | Plain, civic | Internal tools, forms |
| IBM Plex Sans | Technical, slightly warm | Data-heavy tools |
| Space Grotesk | Display personality | Marketing headings for technical products |
| Outfit | Geometric, friendly | Consumer-leaning marketing |
| Satoshi / Cabinet Grotesk | Contemporary grotesque | Brand-forward marketing |

Inter is allowed only when the brand already mandates it. As a reflex pick it is the default face of machine output and reads accordingly.

**The serif rule.** A serif must be earned by the brief (editorial content, print heritage, a luxury brand with evidence). Fraunces and Instrument Serif are banned as defaults; they are the most-tested serif tells in production review. When a serif is justified, rotate within this pool: PP Editorial New, GT Sectra, Reckless Neue, Tiempos, Recoleta. Emphasis inside a headline is italic or bold of the same family, never a serif word injected into a sans sentence. Italic descenders need clearance: line height 1.1 minimum plus bottom padding on words containing y, g, j, p, q.

## Pairings

| Surface | Heading | Body | Numbers |
|---|---|---|---|
| Product UI / dashboard | Same as body, heavier weight | Geist or system stack | Same family, `tabular-nums` |
| Internal tool | System stack throughout | System stack | Mono for IDs and hashes |
| Technical marketing | Space Grotesk | IBM Plex Sans or Source Sans 3 | Heading family |
| Editorial marketing (earned serif) | Pool serif above | Source Sans 3 or Public Sans | Body family |

One family with two weights beats two families in most product work. Add a second family only when headings need a register the body face cannot reach.

## Type scale

Declare 4 to 5 sizes as tokens and use nothing in between. A working default for product UI:

```css
--text-xs: 12px;   /* table captions, footnotes; the absolute floor */
--text-sm: 14px;   /* dense table cells, secondary labels */
--text-base: 16px; /* body, inputs, buttons */
--text-lg: 20px;   /* section headings */
--text-xl: 28px;   /* page title */
```

Marketing pages shift the top of the scale up (40 to 72px heroes) and keep the same floor.

## Banned hex families

The "premium consumer" cream-and-brass palette is banned as a default; it is a documented machine signature. Do not ship these values or near neighbours:

- Backgrounds: `#f5f1ea` `#f7f5f1` `#fbf8f1` `#efeae0` `#ece6db` `#faf7f1` `#e8dfcb`
- Accents: `#b08947` `#b6553a` `#9a2436` `#9c6e2a` `#bc7c3a` `#7d5621`
- Text inks: `#1a1714` `#1a1814` `#1b1814`

Pure `#000000` is banned everywhere (backgrounds and text). Use the off-blacks in the ramps below.

## Palette rotation sets

**Vivid enterprise primaries (the Google set).** When the brief asks for energy rather than restraint: blue `#1a73e8` (text) / `#4285f4` (fill), red `#d93025` / `#ea4335`, yellow-orange `#e8710a` (text) / `#fbbc04` (fill), green `#188038` / `#34a853`, on white with `#202124` ink and `#dadce0` hairlines. Rules that keep it from turning carnival: fills run at full strength (opacity-washing a vivid palette produces pastels, the worst of both), text tones sit one step darker than fills for contrast, blue stays the only brand colour, and red/yellow/green appear only with semantic meaning.

Pick one set per surface. Each lists background, raised surface, border, text ink, muted text, accent, and the accent's on-colour. All pass 4.5:1 for body text.

**Cold Luxury** — steel and ink, for premium product UI.
`bg #f7f8f9 · surface #ffffff · border #e2e5e9 · ink #16181d · muted #5b616e · accent #2f4156 · on-accent #ffffff`

**Forest** — deep green base, for sustainability or field-ops tools.
`bg #f4f6f3 · surface #ffffff · border #dde3da · ink #1a201b · muted #566055 · accent #2d5a3d · on-accent #ffffff`

**Black-and-Tan** — dark marketing surface with warm restraint.
`bg #141311 · surface #1d1b18 · border #2e2b26 · ink #ece7de · muted #a39c8f · accent #c8a26a · on-accent #16140f`

**Cobalt and Cream** — light, confident, for product marketing.
`bg #fafaf7 · surface #ffffff · border #e6e4dd · ink #191a1e · muted #5d5f66 · accent #1f4ed8 · on-accent #ffffff`

**Terracotta and Slate** — warm accent on cool ground.
`bg #f6f7f8 · surface #ffffff · border #e3e6e9 · ink #1c2126 · muted #5c646d · accent #b4553c · on-accent #ffffff`

**Olive, Brick and Paper** — editorial, for content-led pages.
`bg #f8f7f2 · surface #ffffff · border #e5e3d8 · ink #21211c · muted #62625a · accent #6b6b33 · accent-2 #9e4a3a · on-accent #ffffff`

**Monochrome plus pop** — greys with one loud accent, for internal tools.
`bg #fafafa · surface #ffffff · border #e4e4e7 · ink #18181b · muted #52525b · accent #e11d48 (or #1f4ed8 / #0d9488) · on-accent #ffffff`

## Dark-mode protocol

1. **Base is an off-black**, zinc-950 class: `#09090b` or `#0a0a0b`. Never `#000000`.
2. **Elevation is lightness.** Raised surfaces step up (`#131316`, `#1b1b1f`); drop shadows do almost nothing on dark ground.
3. **Desaturate and lighten the accent one step** so it holds contrast without glowing. No outer glows.
4. **Text is off-white** (`#e7e7ea` body, `#a1a1aa` muted), never pure white at body sizes.
5. **Ship both directions.** Default from `prefers-color-scheme`, override with a `data-theme` attribute on the root, and the attribute wins both ways:

```css
:root { color-scheme: light dark; }
@media (prefers-color-scheme: dark) { :root { /* dark tokens */ } }
:root[data-theme="dark"] { /* dark tokens */ }
:root[data-theme="light"] { /* light tokens */ }
```

6. **Re-check contrast in both themes.** A palette passes only when body text holds 4.5:1 on every surface it sits on.
