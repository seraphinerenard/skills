---
name: design
description: |
  Frontend design without the machine look. Trigger on: "design this page", "build a UI",
  "make this look good", "unslop this frontend", "/design", or any request to produce
  product UI, dashboards, internal tools, settings pages, data tables, or marketing pages.
  Begin at GATE D1 of THE CONTRACT: print the design gate card before writing any markup.
  Deliverables start as a cp of a shipped demo, colours exist only in the :root token
  block, and scripts/check_design.py plus the writing sweep MUST pass before delivery.
  Prerequisites inlined below; full writing-instructions and make-charts win on conflict.
---

# Design

A designed interface is a set of decisions: one type family, one accent, one grid, states planned before the happy path. The machine default (purple gradients, glass cards, three equal feature tiles, improvised hex values) gets rebuilt on sight. This skill removes the improvisation: every colour comes from a named palette row, every deliverable starts from a compliant file, and two checkers gate delivery.

Set `SKILL_DIR=$HOME/.claude/skills/design` (fallback: `/path/to/skills/design`).

## Scope gate

IF the request edits an existing file that already contains `@keep:tokens` and a `CONTRACT` comment: make the edit, run both checks (below), paste the proof lines, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE D-1** | Fill the gate card: surface type, the one question the page answers, palette row cited verbatim, type, signature element | D-1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD`; palette row quoted from the Values table |
| **GATE D-2** | Copy the starter for the surface type (IF/THEN table below) with `cp`; write the CONTRACT comment into it | The copied file on disk with its CONTRACT comment | `cp` ran as a tool call; IF `cp` fails, stop and report the path |
| **GATE D-3** | Write all visible copy first, into the file, obeying the inlined writing rules below | The copy in place | Every heading a full sentence in sentence case; numbers carry units and baselines |
| **GATE D-4** | Build: layout, states (empty, loading, error, zero-data), then motion last | The finished page | All four states exist; no colour literal outside `:root`; no repeated identical modules |
| **GATE D-5** | Run `check_design.py` AND `sweep.py`; fix every FAIL; re-run to exit 0 | Both proof lines as tool results | Zero FAILs, or each `allow:` justified in one line |
| **GATE D-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during D-3 and D-4: every colour of any syntax lives in `:root` only (D2); no gradients, glass, or glow anywhere (D1, D3); body text 16px, nothing under 12px (D8).

## Values

**Starters (copy, don't create).**

| IF the surface is | THEN start from |
|---|---|
| Product UI, internal tool, settings, forms | `cp $SKILL_DIR/demos/product-settings.html <name>.html` |
| A data-dense table view | `cp $SKILL_DIR/demos/data-table.html <name>.html` |
| Marketing or landing page | `cp $SKILL_DIR/demos/marketing-page.html <name>.html` |
| A dashboard or BI surface | Load the dashboarding skill; its Northline template is the starter |
| ELSE | Ask the user which surface this is, then stop until answered |

**The token block.** Every page's colours live here and nowhere else. Swap the six palette values; never add colour declarations outside `:root` rules. Opacity variants use `color-mix(in srgb, var(--x) N%, transparent)`.

```css
/* @keep:tokens */
:root {
  --bg: #fafafa; --surface: #ffffff; --border: #e4e4e7;
  --ink: #18181b; --muted: #52525b; --accent: #1f4ed8; --on-accent: #ffffff;
  --danger: #b42318; --success: #067647; --warning: #b54708;
  --font-sans: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --radius: 6px; --space: 8px;
}
```

**Palettes.** Pick ONE row; the gate card quotes it verbatim. All pass 4.5:1 for body text.

| Name | bg | surface | border | ink | muted | accent | on-accent |
|---|---|---|---|---|---|---|---|
| mono-pop | #fafafa | #ffffff | #e4e4e7 | #18181b | #52525b | #1f4ed8 | #ffffff |
| cold-luxury | #f7f8f9 | #ffffff | #e2e5e9 | #16181d | #5b616e | #2f4156 | #ffffff |
| forest | #f4f6f3 | #ffffff | #dde3da | #1a201b | #566055 | #2d5a3d | #ffffff |
| cobalt-cream | #fafaf7 | #ffffff | #e6e4dd | #191a1e | #5d5f66 | #1f4ed8 | #ffffff |
| terracotta-slate | #f6f7f8 | #ffffff | #e3e6e9 | #1c2126 | #5c646d | #b4553c | #ffffff |
| olive-brick | #f8f7f2 | #ffffff | #e5e3d8 | #21211c | #62625a | #6b6b33 | #ffffff |
| black-tan | #141311 | #1d1b18 | #2e2b26 | #ece7de | #a39c8f | #c8a26a | #16140f |
| graphite-dark | #09090b | #131316 | #26262b | #e7e7ea | #a1a1aa | #6d8aff | #0b0b0e |
| vivid-enterprise | #ffffff | #ffffff | #dadce0 | #202124 | #5f6368 | #1a73e8 | #ffffff |
| ELSE (brand palette supplied) | map brand values onto these seven roles, note the mapping in the gate card | | | | | | |

Rules that keep vivid-enterprise from turning carnival: red #d93025, yellow #e8710a, green #188038 appear only with semantic meaning; blue stays the only brand colour; fills at full strength, never opacity-washed.

**Banned hex families (D5).** Never these or near neighbours: backgrounds #f5f1ea #f7f5f1 #fbf8f1 #efeae0 #ece6db #faf7f1 #e8dfcb; accents #b08947 #b6553a #9a2436 #9c6e2a #bc7c3a #7d5621; inks #1a1714 #1a1814 #1b1814. Pure #000000 and #000 banned everywhere (D4).

**Type scale.** Declare as tokens; use nothing between the steps.

| Token | Product UI / tool | Marketing |
|---|---|---|
| --text-xs | 12px (captions, footnotes; absolute floor) | 14px |
| --text-sm | 14px (dense table cells, secondary labels) | 16px |
| --text-base | 16px (body, inputs, buttons) | 18px |
| --text-lg | 20px (section headings) | 24px |
| --text-xl | 28px (page title) | 40 to 72px (hero) |

Fonts: self-contained single-file deliverables use the system stacks in the token block. Projects with a build step pick ONE loaded face from: Geist (product UI), Source Sans 3 (long-form), Public Sans (internal tools), IBM Plex Sans (data-heavy), Space Grotesk (technical marketing headings), Outfit (consumer marketing). Inter, Fraunces, Instrument Serif, Poppins, and Roboto are banned as chosen faces (D14). A serif requires an editorial brief; when earned, rotate within: PP Editorial New, GT Sectra, Tiempos, Recoleta.

**Density.**

| Surface | Body | Table cells | Row height | Section padding |
|---|---|---|---|---|
| Product UI / internal tool | 16px | 14px | 40 to 48px | 16 to 24px |
| Dashboard | 16px | 13 to 14px, tabular-nums | 36 to 44px | 12 to 20px |
| Marketing | 18px | n/a | n/a | 64 to 120px between sections |
| ELSE | ask the user | | | |

**Motion.** Entrances only: 150 to 250ms, ease-out, `transform` and `opacity` only, one entrance per element, nothing loops (the one sanctioned loop is a dashboard status dot, marked `allow:D11`). Focus rings: 2px solid `var(--accent)`, offset 2px, on every interactive element. `prefers-reduced-motion` disables everything (the token-block starters already include the media query; keep the `/* @keep:reduced-motion */` line).

**Dark mode.** Base #09090b or #0a0a0b, never #000000. Elevation is lightness (#131316, #1b1b1f), not shadow. Accent lightened one step (graphite-dark row). Text #e7e7ea body, #a1a1aa muted, never pure white. Ship both directions: `@media (prefers-color-scheme: dark)` plus `:root[data-theme="dark"]` and `:root[data-theme="light"]` overrides that win both ways.

**The expressive tier.** Unlocked only when the brief asks for it ("stunning", "vibrant", "delightful", a client-facing demo) AND the deliverable is an app with a build step; single-file HTML deliverables stay on the base rules and the checker. The shipped exemplar of this tier is the Northline app (References). Its binding values:

| Element | Value |
|---|---|
| Palette | vivid-enterprise row, plus fills blue #4285f4, red #ea4335, yellow #fbbc04, green #34a853; text tones one step darker than fills (#1a73e8, #d93025, #e8710a, #188038) |
| Tonal surfaces, light | blue #e8f0fe, red #fce8e6, yellow #fef7e0, green #e6f4ea as card faces and chips |
| Tonal surfaces, dark | `color-mix(in srgb, <fill> 14-16%, <panel>)` on a #09090b-family base |
| Fill strength | Fills at 100% opacity, always; opacity-washing a vivid fill produces a pastel and is banned in this tier |
| Chart-area gradient | Same hue as the line, top stop at most 0.35 opacity fading to about 0; data areas only, never page backgrounds |
| Dark glow | `drop-shadow`/`text-shadow` mixed from the element's own colour at most 60% and at most 10px, on data marks, icons, and hero numerals only |
| Motion | One easing curve `cubic-bezier(0.2, 0.7, 0.2, 1)`; entrances 200 to 500ms with a 60ms stagger; chart draw-on at most 900ms; number count-up at most 700ms; everything runs once on entry |
| Shell | Sidebar as a floating card on a tinted canvas; one stroke icon set (for example the Hugeicons free set, MIT, from the `@hugeicons/core-free-icons` npm package), one primary per view; active item a rounded tonal chip; hero bento cell carries the headline number at 56 to 64px over a live area chart |
| Ticker | rAF integer-pixel stepping only (see D26); at most one per app |
| ELSE | An expressive move this table does not name stays out until the user approves it by name |

## Artifact templates

```gate-card
GATE D-1 - design contract
surface: <product-ui | internal-tool | data-table | marketing | dashboard>
question: <the one question this page answers, as a sentence>
palette: <name>    [row: "<the palette row, pasted verbatim from the Values table>"]
type: <system stack | one named face> at 12/14/16/20/28 (or the marketing column)
density: <row cited verbatim from the Density table>
signature: <the ONE bold element this page gets>
states: empty, loading, error, zero-data
end-of-card
```

The CONTRACT comment, written into the file at GATE D-2, first line after `<!doctype html>`:

```
<!-- CONTRACT skill=design surface=product-ui palette=mono-pop body=16px accent=#1f4ed8 -->
```

`check_design.py` cross-validates this comment against the shipped CSS: the accent must equal the named palette's accent, and the declared body size must appear on `body`.

### Inlined from writing-instructions (full skill wins on conflict)

Every heading is a complete sentence in sentence case. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Numbers carry units and baselines ("62 of 68 coaches available; six in maintenance until Friday"). Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, stakeholders, cutting-edge, transformative, journey, landscape (figurative), AI-powered. Canadian spelling: colour, centre, behaviour, labelled. Fictional companies and uneven numbers only; never real firms, never "Acme" or "Jane Doe".

### Inlined from make-charts (full skill wins on conflict)

Any chart on the page: title is a full sentence stating the finding (with its number); axis labels carry units; source line under the chart; bars start at zero; direct labels, legend only when four or more series cross; greys plus the one accent; no pie, donut, or gauge; the loaded make-charts skill governs anything more complex.

## Rules

Mechanical rules (checker-enforced):

| ID | Rule |
|---|---|
| D1 | No gradients of any kind (linear, radial, conic), no glow, no mesh, no orbs. Solid fills. |
| D2 | Colour literals of ANY syntax (hex, rgb(), hsl(), oklch(), named colours as values, Tailwind colour classes) exist only inside `:root` rules. Everything else uses `var(--x)` or `color-mix()` on vars. |
| D3 | No `backdrop-filter`, no `blur()`, no glassmorphism. Surfaces separate by border or elevation, never both on one card. |
| D4 | No #000000 or #000 anywhere. |
| D5 | None of the banned hex families above. |
| D6 | No emoji anywhere in the file, including the favicon (favicon is a brand-mark SVG). |
| D7 | No em or en dashes in visible copy. |
| D8 | No `font-size` below 12px. Body is 16px minimum (18px marketing). |
| D9 | No Tailwind slop classes: `from-*`/`to-*`/`via-*` colour stops, `backdrop-blur`, `blur-3xl`, `bg-gradient-*`. |
| D10 | No custom cursors, no `cursor: none`. |
| D11 | No infinite animation (`animation-iteration-count: infinite` or `infinite` in shorthand). One `allow:D11` permitted for a dashboard status dot. |
| D12 | No `addEventListener("scroll")` driving style; use IntersectionObserver or CSS scroll-driven animations. |
| D13 | No external resource loads (`src`, `srcset`, `<link href>` to http/https). Self-contained files; local assets or data URIs. |
| D14 | No Inter, Fraunces, Instrument Serif, Poppins, or Roboto in `font-family` (brand mandate = `allow:D14` with the mandate named). |
| D15 | `@keep:tokens` and `@keep:eof` sentinels present (proof the starter was copied). |
| D16 | CONTRACT comment present; its palette accent and body size match the shipped CSS. |

Build rules (MUST, verified by eye at GATE D-4):

| ID | Rule |
|---|---|
| D17 | Three or more items sharing structure are rows of one table or list, never sibling cards. Cards exist only to group unlike content, and take a border or a shadow, never both. |
| D18 | One signature element per page; everything else stays quiet. On marketing pages, no two adjacent sections share a layout family. |
| D19 | Empty, loading, error, and zero-data states exist before delivery, text-first, one action each. Loading skeletons are static dim blocks (no shimmer), shown only past 300ms, matched to final layout. |
| D20 | Semantic colours reserved: red = destructive/error, green = success, amber = warning, nowhere else. |
| D21 | Tables: real `<th>` header cells, right-aligned numbers with `font-variant-numeric: tabular-nums`, units in the column header. |
| D22 | Buttons stay enabled with validation messages; no disabled buttons without an adjacent reason. Modals only for destructive confirmation; routine edits are inline or in a side panel. |
| D23 | Every edge aligns to the grid (`--space` multiples). Icons come from one set, extracted once into a project-local `icons/` directory (the Hugeicons free set is the default: kebab-case filenames, 24x24 viewBox, `stroke="currentColor"` so an inlined icon inherits the surrounding text colour), never hand-rolled SVG paths, never emoji. |
| D24 | ELSE: a pattern this table does not cover gets decided by the nearest demo; when no demo answers it, ask the user. |
| D25 | The `prefers-reduced-motion` block MUST set `animation-iteration-count: 1 !important` alongside the 0.01ms duration clamp: clamping an infinite animation to 0.01ms restarts it thousands of times a second and strobes. Content the user asked to move (a ticker) runs under reduce-motion via rAF; decorative motion collapses. |
| D26 | Marquees and tickers are never CSS keyframe animations: a multi-thousand-pixel track becomes one GPU texture that exceeds compositor limits on high-DPI displays and flickers. Drive them with requestAnimationFrame in whole pixels (sub-pixel motion shimmers text), wrap at a measured copy width using two identical copies each carrying its own trailing gap, and pause from the stationary wrapper, never the moving track (items sliding under the cursor toggle :hover). |
| D27 | A keyframe that fades an element to a non-full opacity MUST end at `var(--target-opacity)`, never `opacity: 1`: a generic fade-in overrides the element's opacity attribute and renders a low-opacity band as a solid blob. |
| D28 | SVG elements animated with `scaleY` (growing bars) MUST set `transform-box: fill-box` with `transform-origin: bottom`, or the transform resolves against the viewport and the bars fly. |

## Checks

```
python3 $SKILL_DIR/scripts/check_design.py <file.html> [...]
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <file.html> [...]
```

Both MUST pass, as tool results, after the last edit. `check_design.py` prints `FAIL D<n> file:line` per violation, honours `allow:D<n> <reason>` markers (counted), cross-validates the CONTRACT comment, and ends `PASS check_design v1 file=<name> sha=<8hex>`. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY design
files:
  <path>  (<size> B)
gates: <D-1..D-6 status, skips recorded>
checks:
  <check_design proof line, pasted>
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/typography-color.md`: pairing rationale, the serif rules, extended dark-mode protocol, vivid-palette usage notes.
- `references/components.md`: copy-paste patterns already on the tokens: data table, form with validation, the four states, card, nav.
- `references/northline-exemplar.md`: the shipped exemplar of the expressive tier, with screenshots (`northline-light.png`, `northline-dark.png`) and the decisions to imitate. The running app lives at `/path/to/skills/dashboarding/templates/northline`.
- `demos/`: the three starters; they pass both checkers and are the quality bar.
