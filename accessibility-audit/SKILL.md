---
name: accessibility-audit
description: |
  WCAG 2.2 AA vetting of shipped UIs with honest language. Trigger on: "accessibility
  audit", "a11y review", "WCAG check", "is this accessible", "audit this dashboard",
  "/accessibility-audit", and as the QA pass on design or dashboarding deliverables.
  Begin at GATE AA-1 of THE CONTRACT: the scope card with its coverage denominator
  comes before any scanning. The report never certifies compliance; the mandatory
  wording is in the Values section. The final report passes the writing sweep.
---

# Accessibility audit

An audit is a coverage claim, and most published ones overclaim twice: they run an automated scanner and call it an audit, and they call the result "compliant". Automated checks find only about half of WCAG issues (Deque's own 2021 study measured roughly 57% by volume), and no audit certifies anything. This skill produces the honest version: a scoped scan, a manual pass with named criteria, findings with evidence, and a report that states what was not tested.

Set `SKILL_DIR=$HOME/.claude/skills/accessibility-audit` (fallback: `/path/to/skills/accessibility-audit`).

## Scope gate

IF the request is to re-verify one prior finding: re-test that criterion, paste the evidence, update the findings table, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE AA-1** | Fix the scope: which pages/views are audited, which are not, and the denominator | AA-1 scope card | Card printed; coverage stated as "N of M routes"; no `<`, `TODO`, `TBD` |
| **GATE AA-2** | Automated pass: run axe-core against each in-scope page IF a runner is available; ELSE record "automated scan unavailable" and continue manual-only | Pasted head of the scanner output per page, or the unavailability line | Tool output is a tool result, not typed text |
| **GATE AA-3** | Manual pass: walk the inline checklist below, criterion by criterion, on each in-scope page | Checklist verdicts per page (pass / fail / not applicable, each fail with evidence) | Every checklist row has a verdict; contrast pairs measured, not eyeballed |
| **GATE AA-4** | Compile findings | The findings table: criterion (SC number), severity, where, evidence, fix | Every finding carries an SC number and evidence |
| **GATE AA-5** | Write the report with the mandatory honesty wording and the coverage section | The report on disk | Mandatory sentence present verbatim; remediation ordered by severity; sweep passes |
| **GATE AA-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during AA-2 and AA-5: an automated-only pass is not an audit, the manual checklist runs every time (AA3); every count carries its denominator, "12 issues on 4 of 30 routes" (AA2); the report never claims certification or "fully accessible" (AA1).

## Values

The manual checklist. Every row gets a verdict per page:

| Criterion | SC (WCAG 2.2) | Test |
|---|---|---|
| Keyboard reachable and operable | 2.1.1 | Tab through the whole page; every interactive element reachable and usable with Enter/Space/arrows |
| No keyboard trap | 2.1.2 | Focus can always leave any widget with Tab or Escape |
| Focus visible | 2.4.7 | A visible indicator (2px minimum) on every focused element |
| Text contrast | 1.4.3 | 4.5:1 body, 3:1 for text 24px+ (or 18.5px+ bold); measure the 5 highest-risk pairs |
| Non-text contrast | 1.4.11 | 3:1 for control borders, focus rings, chart marks against adjacent colours |
| Labels and names | 3.3.2, 4.1.2 | Every input has a label; every icon-only button has an accessible name |
| Errors identified in text | 3.3.1, 1.4.1 | Errors named in words, never colour alone |
| Target size | 2.5.8 | Interactive targets at least 24 by 24 CSS px, or spaced to that footprint |
| Zoom to 200% | 1.4.4 | No loss of content or function at 200% zoom |
| Reflow at 320px | 1.4.10 | Content reflows to one column; no two-dimensional scrolling for text |
| Heading order | 1.3.1, 2.4.6 | One h1; levels never skip; headings describe their sections |
| Alt text | 1.1.1 | Informative images described; decorative images alt="" |
| Moving content | 2.2.2 | Anything auto-moving longer than 5 s has pause/stop/hide; reduced-motion honoured (house rule, aligned with 2.3.3) |
| ELSE | n/a | A criterion not listed here that the surface plainly needs: add it to the table in the report and test it |

Contrast measurement: `python3 $HOME/.claude/skills/brand-kit/scripts/check_contrast.py <fg-hex> <bg-hex>`, output pasted for each measured pair. IF that script is missing: record "contrast tool unavailable" and mark those pairs unverified in the findings; unverified is a reportable state, a guess is not.

Severity definitions: blocker (an affected user cannot complete the task), major (the task completes only with serious difficulty or a workaround), minor (friction or polish). Remediation lists blockers first.

Mandatory report wording, verbatim: "This audit supports conformance work; it does not certify compliance." Coverage wording, always with the denominator: "Scanned N of M routes; not tested: <list>." The ~57% automated-coverage fact appears in the method section whenever an automated pass ran.

Banned phrases in the report and anywhere near it: "certified compliant", "WCAG certified", "fully accessible", "100% accessible", "guarantees compliance".

## Artifact templates

```gate-card
GATE AA-1 - audit scope
surface: <app or site name, fictional names for demos>
in scope: <routes/views audited, listed>
out of scope: <routes/views not audited, listed>
coverage: <N of M routes>
automated runner: <axe via <runner> | unavailable>
end-of-card
```

Findings row format (one row per finding in the AA-4 table):

```markdown
| 1.4.3 text contrast | major | /settings, save button | 3.1:1 measured (check_contrast output) | raise --muted to #5b616e on white |
```

### Inlined from writing-instructions (full skill wins on conflict)

The report's headings are full sentences in sentence case. No contrast framing, no em dashes, no emoji. Every count carries its denominator and period. Canadian spelling: colour, behaviour, centre.

## Rules

| ID | Rule |
|---|---|
| AA1 | The report never certifies: the banned-phrase list above is absolute, and the mandatory sentence appears verbatim. |
| AA2 | Every issue count and every claim of coverage carries its denominator. |
| AA3 | The manual checklist runs in full on every audit; an automated-only pass is recorded as "scan, not audit" and says so in the report title. |
| AA4 | Every finding cites its SC number and carries evidence (a measurement, a keystroke sequence, or a quoted attribute). |
| AA5 | Remediation is ordered blockers, majors, minors; each fix names the exact change. |
| AA6 | Contrast is measured with a tool or the WCAG formula, never judged by eye; unmeasured pairs are reported as unverified. |
| AA7 | The report passes the writing sweep before delivery. |
| AA8 | ELSE: a situation these rules do not cover gets stated in the report's method section and taken to the user. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <report.md>
python3 $HOME/.claude/skills/brand-kit/scripts/check_contrast.py <fg> <bg>   (per measured pair)
```

The sweep MUST pass as a tool result after the last edit of the report. Contrast outputs are pasted into the findings evidence column. A missing tool is recorded, never silently skipped.

## Delivery block

```delivery-block
DELIVERY accessibility-audit
files:
  <report path>  (<size> B)
gates: <AA-1..AA-6 status, skips recorded>
checks:
  <sweep proof line, pasted>
  <contrast outputs count: N pairs measured, M unverified>
coverage: <N of M routes; automated pass ran: yes/no>
allows: <count> (<list or none>)
end-of-delivery
```
