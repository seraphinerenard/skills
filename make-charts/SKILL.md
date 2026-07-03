---
name: make-charts
description: |
  Design, build, and critique data visualizations on Tufte's principles. Trigger on:
  creating any chart, graph, plot, sparkline, or diagram for a deck, report, dashboard,
  or page; critiquing or improving an existing visualization; "reduce chartjunk";
  "/make-charts". Begin at GATE C-1 of THE CONTRACT: print the chart gate card before
  writing any chart code. HTML charts start as a cp of assets/chart-skeleton.html and
  MUST pass scripts/check_chart.py plus the writing sweep before delivery. PPTX charts
  are native objects only. Wording prerequisites inlined; full writing-instructions wins.
---

# Make charts

A chart has two failure modes: the ink can lie, and the words can say nothing. Every rule below guards one of the two. The title states the finding with its number, the geometry keeps the lie factor at 1.0, the palette is greys plus one accent, and checkers gate delivery.

Set `SKILL_DIR=$HOME/.claude/skills/make-charts` (fallback: `/path/to/skills/make-charts`).

## Scope gate

IF the request edits an existing chart that already carries `@keep:tokens` and a CONTRACT comment: make the edit, run the checks, paste the proof lines, stop.
IF the request is a critique of an existing visualization: score it against rules C9 to C22 in order, compute the lie factor when proportions look off (size of effect in ink divided by size of effect in data), list every violation with its rule ID, rewrite the title and subtitle as a before/after pair, and stop.
ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE C-1** | Fill the gate card: the claim sentence, the form row cited verbatim, axes with units, the comparison, the source line | C-1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD`; form row quoted from the Values table |
| **GATE C-2** | Copy the starter for the medium and form (IF/THEN in Values); write the CONTRACT comment into it | The copied file on disk with its CONTRACT comment | `cp` ran as a tool call; IF `cp` fails, stop and report the path |
| **GATE C-3** | Build: data, then scales, then labels | The drawn chart | Bars start at zero (C12); series labelled directly at their ends (C14); greys plus one accent (C15) |
| **GATE C-4** | Wording pass: title, subtitle, axis labels, source line | The four text elements in place | Title is the C-1 claim with its number; subtitle carries population, period, baseline, caveat |
| **GATE C-5** | Run the checks for the medium; fix every FAIL; re-run to exit 0 | Proof lines as tool results | Zero FAILs, or each `allow:` justified in one line |
| **GATE C-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during C-3: bars start at zero (C12); no legend under four series, label the lines at their ends (C14); greys plus ONE accent, the accent on the finding (C15).

## Values

**Form selection.** The gate card quotes the matched row verbatim.

| IF the data story is | THEN the form is |
|---|---|
| Change over time | Line chart, horizontal gridlines only |
| Comparison across categories | Sorted horizontal bars, values on the bars |
| Comparison of the same variable across groups or periods | Small multiples on identical scales |
| Ranking | Sorted horizontal bars |
| Part-to-whole | Sorted bars or a table with a share column; never pie or donut |
| Relationship between two variables | Scatter plot |
| Many metrics at a glance | Table with sparklines, one row per metric |
| Distribution | Histogram with square-edged bars |
| ELSE | Ask the user what comparison matters, then stop until answered |

**Starters (copy, don't create).**

| IF the medium is | THEN start from |
|---|---|
| Self-contained HTML chart | `cp $SKILL_DIR/assets/chart-skeleton.html <name>.html`, replace the plot group; the tokens, text zones, and sentinels stay |
| Dense scientific display like the demos | `cp` the nearest file in `$SKILL_DIR/demos/` and swap the data |
| Chart inside a PPTX deck | No cp; native `add_chart` per the code below, placed on the slide grid |
| Chart inside a design surface or dashboard | Draw inline SVG using that page's existing tokens; no new palette |
| ELSE | Ask the user for the medium, then stop until answered |

**Geometry and styling.**

| Element | Value |
|---|---|
| Data series stroke | 2.5px solid, the accent or ink token |
| Context or baseline series | 1.5px, the muted token |
| Gridlines | Horizontal only, 1px, the border token, at most 5; no boxed plot area |
| Bars | Square-edged, start at zero, gap 20 to 40% of bar width |
| Title | 20px bold, sentence case |
| Subtitle | 13px, muted token |
| Axis labels and tick text | 12px, with units; 12px is the floor for all chart text |
| Source line | 12px, muted token, bottom of the chart |
| Sparklines | 14 to 20px tall, no axes, endpoint value labelled |
| Colour | Greys for context, ONE accent on the finding; red and green only as bad and good |
| ELSE | An element this table does not name inherits the design skill's tokens |

**Wording formats.** Title: the finding as one full sentence with its number ("P99 latency stays under 40 ms until the cache is disabled."). Subtitle: population, period, versus baseline, caveat. Axis: `Quantity (unit)`. Source: `Source: <system or dataset>, <period covered>, retrieved <date>.`

**Native PPTX chart code.** Charts in decks are native chart objects placed on the slide grid, never images pasted onto a slide.

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

data = CategoryChartData()
data.categories = ['Jan', 'Feb', 'Mar', 'Apr']
data.add_series('Forecast error (%)', (21.4, 18.9, 12.2, 9.1))
frame = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                               Inches(0.8), Inches(2.2), Inches(6.5), Inches(4.2), data)
chart = frame.chart
chart.has_legend = False
plot = chart.plots[0]
plot.has_data_labels = True
plot.data_labels.number_format = '0.0'
plot.data_labels.font.size = Pt(12)
```

Native types that cover the forms: `COLUMN_CLUSTERED`, `COLUMN_STACKED`, `BAR_CLUSTERED`, `LINE`, `LINE_MARKERS`, `XY_SCATTER`, `AREA`. Where PPTX has no native type, build from native shapes and tables: waterfall from stacked rectangles with connectors, funnel from centred rectangles with value labels, heatmap as a native table whose cell fills encode the values. The slide's assertion title carries the finding; a standalone chart gets its own sentence title.

### Inlined from writing-instructions (full skill wins on conflict)

Titles are complete sentences in sentence case; no colon headlines, no Title Case. Numbers carry units and baselines. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, transformative, significant (without the number), journey, landscape (figurative). Canadian spelling: colour, centre, behaviour, labelled. Vague authority ("studies show") is banned; the source line names the system and period.

## Artifact templates

```gate-card
GATE C-1 - chart contract
claim: <the full-sentence finding with its number; this becomes the title>
form: <form name>    [row: "<the matched form row, pasted verbatim>"]
x-axis: <quantity (unit)>
y-axis: <quantity (unit)>
comparison: <the baseline, benchmark, prior period, or peer shown on the chart>
source: <Source: system or dataset, period covered, retrieved date>
medium: <html | pptx | on-surface>
end-of-card
```

The CONTRACT comment, written into HTML chart files at GATE C-2:

```
<!-- CONTRACT skill=make-charts form=line source=yes -->
```

## Rules

Mechanical rules (checker-enforced on HTML):

| ID | Rule |
|---|---|
| C1 | The chart's title text contains at least one digit. A title with no number is a topic label, not a finding. |
| C2 | The file contains a `Source:` line. |
| C3 | No gradients (linear, radial, conic) and no glow or blur filters. A sequential data colour scale is the one exception, marked `allow:C3` with the encoding named. |
| C4 | No pie or donut charts. |
| C5 | No emoji; no em or en dashes in visible text. |
| C6 | No #000000 or #000. |
| C7 | `@keep:tokens` and `@keep:eof` sentinels present; CONTRACT comment present with `form=` and `source=yes`. |
| C8 | No legend markup when the chart has fewer than 4 series; series are labelled directly at their ends. |

Build rules (verified by eye at GATE C-3 and C-4):

| ID | Rule |
|---|---|
| C9 | The title is a complete sentence in sentence case stating the finding; the reader learns the conclusion from the title alone. |
| C10 | The subtitle carries population, period, baseline, and any caveat that changes interpretation. |
| C11 | Every axis label carries units. |
| C12 | Honest scales: bars start at zero; a truncated line axis is declared in the subtitle; no dual axes without the reason printed on the chart; no 3D, ever. Lie factor 1.0: the effect in ink equals the effect in data. |
| C13 | The eraser test: erase every element whose removal loses no information (duplicate encodings, redundant labels, heavy grids, borders, decorative icons). |
| C14 | Direct labels: series names at line ends, values on bars; a legend exists only when 4 or more crossing series make direct labels physically impossible. |
| C15 | Greys plus one accent; colour encodes meaning or is absent; a rainbow categorical palette is banned. |
| C16 | The collision test: no text element's bounding box crosses another element; fixes are the caption, a label strip above the plot, the outside margin, or a leader line. |
| C17 | Square-edged bars; no rounded caps, no pill bars. |
| C18 | Every chart answers "compared to what?": the baseline is drawn on the chart, not left to memory. |
| C19 | Multivariate problems show the interaction (small multiples, colour, size) instead of one collapsed average. |
| C20 | PPTX: native chart objects or native shape constructions only; never an image of a chart. The deck's verifier enforces the 12pt floor over chart text. |
| C21 | Sentence case on every label; no Title Case. |
| C22 | ELSE: a case these rules do not settle follows the Tufte test in `references/tufte-principles.md`; when that does not settle it, ask the user. |

## Checks

HTML charts, both mandatory, after the last edit:

```
python3 $SKILL_DIR/scripts/check_chart.py <file.html>
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <file.html>
```

A chart embedded in a design-skill page also passes that page's `check_design.py` run. A PPTX chart is verified by reopening the saved file with python-pptx and printing the chart type, the series count, and the smallest font size on the slide. Proof lines land in the delivery block; the runs MUST appear as tool results; any edit after a run voids it. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY make-charts
files:
  <path>  (<size> B)
gates: <C-1..C-6 status, skips recorded>
checks:
  <check_chart proof line, pasted>
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/tufte-principles.md`: graphical excellence, integrity, data-ink, chartjunk, small multiples, data density, and the 7-question Tufte test.
- `references/analytical-design.md`: the six principles of analytical design, sparklines, layering and separation, micro/macro, range-frames, causality.
- `demos/`: four dense scientific displays at the quality bar; they pass the checkers.
