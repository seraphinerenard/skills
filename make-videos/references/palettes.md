# Video palettes

One palette per video. The palette is chosen at GATE V-1, before any scene is built, and every scene draws from it. Changing palettes mid-video reads as two videos spliced together. The binding hex values live in SKILL.md's Values table (the authority) and as typed constants in `assets/palette.ts`; this file carries the usage rules per palette.

Every palette obeys the design blacklist: no pure `#000000` backgrounds, no purple-blue gradient pairs, accents under 80% saturation, and no glow effects. Emphasis comes from the accent used sparingly, never from adding colours.

## Roles

| Role | Job | Rule |
|---|---|---|
| `bg` | Stage background | Constant for the whole video. Never pure black or pure white. |
| `surface` | Cards, frames, lower-third bars | One step off `bg`, no borders needed at video resolution. |
| `text` | Titles and body | Contrast ratio against `bg` of at least 7:1. |
| `muted` | Kickers, baselines, captions | Same hue family as `text`, dropped saturation and lightness. |
| `accent` | The one emphasis colour | Numbers, underlines, the CTA. At most one accent element on screen at a time. |
| `accent2` | Second data series, secondary highlight | Only when two things must be told apart; never decoration. |

## The five palettes

### Broadcast Dark

The newsroom look: near-black blue-grey stage, warm signal red for the number that matters. The default for GTM videos aimed at a technical or financial audience.

| Role | Hex |
|---|---|
| bg | `#0B0E13` |
| surface | `#151A22` |
| text | `#E9EDF2` |
| muted | `#8B95A5` |
| accent | `#E0483E` |
| accent2 | `#E5B84B` |

Usage: red carries the headline stat, amber the comparison series. Keep both off screen in the same shot unless a chart needs two series.

### Paper Light

Cool print editorial: light neutral stage, ink text, cobalt emphasis. The default for instructional videos and anything that will be watched in a bright office. The background is a cool grey, not cream; warm paper tones with brass or clay accents are on the banned list.

| Role | Hex |
|---|---|
| bg | `#F4F5F7` |
| surface | `#FFFFFF` |
| text | `#1F242C` |
| muted | `#667085` |
| accent | `#2B59C3` |
| accent2 | `#B0492C` |

Usage: cobalt for interactive elements and stats, terracotta only as a second chart series. Shadows stay light (10% opacity or less) on light stages.

### Terminal Green

Dark developer look: green-cast near-black, phosphor green emphasis. For developer tools, CLI products, and infrastructure stories.

| Role | Hex |
|---|---|
| bg | `#0C1210` |
| surface | `#141C17` |
| text | `#D9E5DE` |
| muted | `#7E8F85` |
| accent | `#46C97E` |
| accent2 | `#D9B44A` |

Usage: pair with a monospace face for code and URLs. Green means success or the product; amber means the "before" state or a warning.

### Midnight Editorial

Deep navy with warm off-white type and a coral accent. For brand films and executive-audience GTM where Broadcast Dark reads too much like news.

| Role | Hex |
|---|---|
| bg | `#101624` |
| surface | `#1B2334` |
| text | `#ECE9E1` |
| muted | `#8E97AB` |
| accent | `#E36756` |
| accent2 | `#7FA8C9` |

Usage: coral for the claim being made now, steel blue for context and history. The warm text on cold ground is the signature; do not cool the text down.

### Brand-Neutral Slate

The placeholder system: neutral dark greys with a restrained teal. Use when the client's brand palette will be swapped in later; every role maps one-to-one onto a brand colour system.

| Role | Hex |
|---|---|
| bg | `#17191E` |
| surface | `#22252C` |
| text | `#E7E9ED` |
| muted | `#9AA1AC` |
| accent | `#1B8A7D` |
| accent2 | `#C86A2C` |

Usage: build the whole video on this palette, then swap the six values once brand hexes arrive. Nothing else should need to change; if a scene breaks under the swap, the scene was leaning on a specific colour rather than a role.

## Swapping in a brand palette

Map the brand's darkest neutral to `bg`, next step to `surface`, lightest neutral to `text`, mid neutral to `muted`, primary brand colour to `accent`, secondary to `accent2`. Then check: accent saturation under 80%, text-on-bg contrast at least 7:1, and no purple-plus-blue pairing across accent and accent2. A brand colour that fails these checks gets adjusted for video (darker stage, desaturated accent) and the adjustment is noted for the client.
