---
name: brand-kit
description: |
  Turn client brand material (site CSS, guidelines PDF, logo SVGs) into the exact
  token sets the design and make-videos skills consume. Trigger on:
  "brand kit", "client brand tokens", "extract the brand", "apply their branding",
  "brand the demo", "/brand-kit". Begin at GATE BK-1 of THE CONTRACT. Every value
  is extracted from a source file, never eyeballed, and every text-on-surface pair
  passes scripts/check_contrast.py before the kit ships.
---

# Brand kit

One extraction, one output format, consumed everywhere: the design gate card cites the kit as `brand-<client>`, the deck generator reads its constants, and the video palette maps role for role. The failure this skill prevents is the eyeballed brand: hexes guessed from screenshots, contrast never measured, and a client noticing their own blue is wrong.

Set `SKILL_DIR=$HOME/.claude/skills/brand-kit` (fallback: `/path/to/skills/brand-kit`).

## Scope gate

IF the request adds or corrects one value in an existing `clients/<name>/` kit: update both output files, re-run `check_contrast.py` on the affected pairs, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE BK-1** | Fill the intake card: sources, font licensing, consuming skills | BK-1 intake card (template below) | Card printed; no `<`, `TODO`, `TBD`; at least one machine-readable source |
| **GATE BK-2** | Extract values from the source files themselves (CSS custom properties, SVG fills, PDF swatch values) | The extraction ledger (template below) | Every value has a source cell (file and selector, or PDF page); zero eyeballed values |
| **GATE BK-3** | Map extracted values onto the design roles, video roles, and deck constants | The three mapping tables, filled | Every role filled; every mapping names its source value |
| **GATE BK-4** | Validate: contrast on every text-on-surface pair, saturation cap on accents | `check_contrast.py` proof line as a tool result, plus the adjustment ledger | Zero AA-body failures; every adjustment recorded with original, adjusted, reason |
| **GATE BK-5** | Write the outputs: `clients/<name>/brand-tokens.css` and `clients/<name>/brand-kit.md` | The two files on disk | CSS carries the CONTRACT comment and `@keep:tokens`; the palette row matches the design table format |
| **GATE BK-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during BK-2 and BK-4: every hex is copied from a source file, screenshots and memory are a failed gate (BK1); every text-on-surface pair runs through `check_contrast.py` with the proof pasted (BK3); a colour that had to change gets an adjustment-ledger row the client can read, silent changes are a failed gate (BK4).

## Values

**Design roles (light UI default).** Seven roles, mapped from brand values:

| Role | Maps from | Requirement |
|---|---|---|
| bg | lightest brand neutral | body-text ink holds 4.5:1 on it |
| surface | white, or one step off bg | 4.5:1 with ink |
| border | mid-light brand neutral | visible on bg and surface |
| ink | darkest brand neutral | 4.5:1 on bg and surface |
| muted | mid brand neutral | 4.5:1 on bg and surface |
| accent | primary brand colour | 4.5:1 for on-accent text; HSV saturation at most 80 |
| on-accent | white or brand dark | 4.5:1 on accent |
| ELSE | a role with no brand value | take the mono-pop value from the design skill and record it in the adjustment ledger |

**Video roles (dark stage default).** Six roles:

| Role | Maps from | Requirement |
|---|---|---|
| bg | darkest brand neutral, deepened to near-black in its own hue | never #000000 |
| surface | one step lighter than bg | no border needed at video resolution |
| text | lightest brand neutral | ratio at least 7.00 on bg (read the PAIR line) |
| muted | mid neutral, same hue family as text | legible kickers and captions |
| accent | primary brand colour, desaturated one step when saturation exceeds 80 | one accent element on screen at a time |
| accent2 | secondary brand colour | only for a second data series; never a purple plus blue pairing with accent |
| ELSE | a role with no brand value | take the Brand-Neutral Slate value from make-videos and record it |

**Deck constants.** `HEADER_FILL` = brand dark neutral; `ACCENT` = brand primary; `INK` = ink role; PPTX font = a web-safe face (Calibri, Georgia, Arial) named in brand-kit.md, with the brand face reserved for the HTML preview.

**Contrast thresholds.**

| Pair type | Threshold |
|---|---|
| UI body text on any surface it sits on | 4.5:1 (AA-body) |
| UI large text: 24px and up, or 19px bold | 3:1 (AA-large) |
| Video text on stage bg | 7.00, read from the PAIR line |
| ELSE | 4.5:1 |

**The saturation check.** HSV saturation of an accent, one command, no judgment:

```
python3 -c "h='1a73e8'; r,g,b=int(h[0:2],16),int(h[2:4],16),int(h[4:6],16); mx,mn=max(r,g,b),min(r,g,b); print(round((mx-mn)/max(mx,1)*100))"
```

IF the printed value exceeds 80: desaturate one step (move the extreme channels toward each other), re-run, and record the change in the adjustment ledger.

**Fonts.** Brand fonts load locally, and only after the user confirms the licence covers the deliverable. ELSE: the design skill's system stacks, with the substitution named in brand-kit.md.

**Output file shapes.** `brand-tokens.css`:

```css
/* CONTRACT skill=brand-kit client=<name> */
/* @keep:tokens */
:root {
  --bg: <hex>; --surface: <hex>; --border: <hex>;
  --ink: <hex>; --muted: <hex>; --accent: <hex>; --on-accent: <hex>;
  --danger: #b42318; --success: #067647; --warning: #b54708;
  --font-sans: <licensed face or system stack>, ui-sans-serif, system-ui, sans-serif;
  --font-mono: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
  --radius: 6px; --space: 8px;
}
/* @keep:eof */
```

`brand-kit.md` MUST contain, in this order: the palette row in exactly the design skill's table format, so gate cards can cite it:

```
| brand-<name> | <bg> | <surface> | <border> | <ink> | <muted> | <accent> | <on-accent> |
```

then the video mapping table, the deck constants, the font decision with its licence note, the extraction ledger, and the adjustment ledger.

## Artifact templates

```gate-card
GATE BK-1 - brand intake
client: <name>
sources: <each source with type and location: site CSS URL, guidelines PDF path, logo SVG path>
fonts-licensed: <yes, licence named | no | unknown: ask before shipping fonts>
consumers: <which of design, make-videos will use this kit>
end-of-card
```

The extraction ledger, printed at GATE BK-2:

```extraction-ledger
| value | role candidate | where found (file and selector, or PDF page) |
|---|---|---|
| #0a3d62 | accent | site.css --color-primary, line 14 |
end-of-ledger
```

The adjustment ledger, printed at GATE BK-4 (empty is a valid state, printed anyway):

```adjustment-ledger
| original | adjusted | reason |
|---|---|---|
| #2ee6a8 | #29c294 | saturation 84 over the 80 cap; video accent |
end-of-ledger
```

## Rules

| ID | Rule |
|---|---|
| BK1 | Every hex is copied from a source file: a CSS custom property, an SVG fill, a PDF swatch value. Screenshots, memory, and "close enough" are a failed gate. |
| BK2 | A value with no extraction-ledger row does not enter the kit. |
| BK3 | Every text-on-surface pair in the kit runs through `check_contrast.py` at its threshold row, and the proof line is pasted as a tool result. |
| BK4 | A brand colour that fails contrast or the saturation cap gets adjusted, and the adjustment ledger records original, adjusted, and reason, in language the client can read. |
| BK5 | accent and accent2 are never a purple plus blue pairing. |
| BK6 | The video bg is never #000000; deepen the darkest brand neutral within its own hue. |
| BK7 | Brand fonts ship only with the licence confirmed by the user; the PPTX path always names a web-safe fallback. |
| BK8 | The palette row in brand-kit.md matches the design skill's palette table format exactly, under the name `brand-<client>`. |
| BK9 | Semantic colours (danger, success, warning) stay the design defaults unless the brand defines its own AND those pass their contrast rows. |
| BK10 | The kit changes only through this skill; a hand-edited token without a ledger row is a failed gate. |
| BK11 | ELSE: brand sources missing, contradictory, or image-only: ask the user for the authoritative source, then stop. |

## Checks

```
python3 $SKILL_DIR/scripts/check_contrast.py <fg-hex> <bg-hex> [<fg> <bg> ...]
```

One PAIR line per pair: `PAIR #fg on #bg ratio=N.NN AA-body=PASS/FAIL AA-large=PASS/FAIL`. AA-body failures exit 1 and print `FAIL BK3` lines. Video pairs MUST show `ratio=` at 7.00 or higher. On success the output ends `PASS check_contrast v1 pairs=N sha=<8hex>`; paste that line into the delivery block. The run MUST appear as a tool result; a missing or crashing checker is a blocking failure to report.

## Delivery block

```delivery-block
DELIVERY brand-kit
files:
  clients/<name>/brand-tokens.css  (<size> B)
  clients/<name>/brand-kit.md  (<size> B)
gates: <BK-1..BK-6 status, skips recorded>
checks:
  <check_contrast proof line, pasted verbatim>
allows: <count> (<list or none>)
adjustments: <count of adjustment-ledger rows>
end-of-delivery
```
