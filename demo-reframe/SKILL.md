---
name: demo-reframe
description: |
  Retarget a built demo (the Northline reference app or any other) to a new client's
  vertical: swap the story, the labels, and the synthetic data while keeping the
  architecture. Trigger on: "reframe the demo", "retarget the demo for <client>",
  "make the Northline demo about X", "demo for a <vertical> meeting", "/demo-reframe".
  Begin at GATE DR-1 of THE CONTRACT. Verification is mechanical: the stale-term grep
  returns zero hits and the writing sweep passes on all visible copy.
---

# Demo reframe

The most-repeated consulting move: one reference demo, retargeted per client. The architecture stays; the story, labels, and data become the client's world. A demo in the wrong frame loses the room, so the concept map, not the string replace, is the work: "asset health" for an equipment-rental buyer means lifecycle and utilization, not the stockouts the source demo was built around.

Set `SKILL_DIR=$HOME/.claude/skills/demo-reframe` (fallback: `/path/to/skills/demo-reframe`).

## Scope gate

IF the request changes one label or one dataset value in an already-reframed demo: make the edit, re-run the stale-term grep and the sweep on the touched files, paste both, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DR-1** | Fill the vertical card: client, fictional demo company, name check, vertical, audience, base demo | DR-1 vertical card (template below) | Card printed; demo company is invented per the naming rules; name-check result recorded |
| **GATE DR-2** | Build the concept map: demo concepts to their concepts to their metrics | The concept-map table, at least 6 rows | Every row names the metric in the client's units; no demo concept left unmapped |
| **GATE DR-3** | Build the rename ledger: every string to replace, and the brand tokens | The rename-ledger table | Old term, new term, and files for every visible string; token source cited (brand-kit or a design palette row) |
| **GATE DR-4** | Reshape the synthetic data: seed script edited to the vertical per the seed-shape rules | The edited seed script on disk | Fixed seed kept; seasonality matches the vertical's calendar; one dated event present; units in column names |
| **GATE DR-5** | Verify: run the app, check one view against the concept map, run the stale-term grep | The grep output as a tool result, plus one line naming the checked view | Zero stale-term hits; the view shows the client's concepts and units |
| **GATE DR-6** | Deliver: sweep the visible copy | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during DR-1 through DR-4: demo companies are fictional archetypes, a real company's name anywhere is a failed gate (DR1, the Bluebird correction); the concept map relabels concepts, not strings, and each row carries the client's metric (DR2); the seed stays fixed so screenshots reproduce across rebuilds (DR5).

## Values

**The concept-map exemplar.** The recorded reframe of the Northline school-bus demo for an AV and live-event rental client. Match this depth:

| Demo concept (Northline) | Their concept (AV rental) | Metric that matters to them |
|---|---|---|
| Component stockout risk | Asset health across the lifecycle | Utilization %, idle days per kit |
| Weekly demand forecast per bus model | Booking pipeline per equipment class | Confirmed bookings per week, 8-week outlook |
| Supplier concentration risk | Vendor and venue dependency | Share of revenue through the top venue |
| Bill of materials per bus | Equipment kit per event type | Kit completeness % before load-out |
| Production plan (S&OP view) | Event-calendar capacity plan | Crew-hours booked vs available |
| PO approval queue | Rental purchase and cross-hire approvals | Spend at stake, CAD |
| Weeks of cover vs supplier lead time | Maintenance turnaround vs next booking | Days to next deployment |

**Fictional naming rules.** The demo company name is an invented archetype, never a real company. The standing correction: a demo was once named "Bluebird" while Blue Bird Corporation is a real bus manufacturer; it shipped as Northline.

| Rule | Requirement |
|---|---|
| Shape | An invented word plus a trade noun (Northline Coachworks, Kestrel Freight, Ledgerline), or two invented words |
| Verification | Run one web search for `"<name>" <vertical>`; record the result in the vertical card ("no active company of this name found in the vertical", or pick again) |
| ELSE: no web tool available | Record "name unverified; coined compound" in the vertical card and use a clearly coined compound |
| Never | A real company, the client's own name, "Acme", "Jane Doe", or any name a competitor in the vertical holds |

**Seed-shape rules.** The seed script is the data contract made executable; edit it, never hand-edit rows:

| Rule | Requirement |
|---|---|
| Seed | Fixed (`default_rng(11)` style), so every rebuild reproduces the same numbers and screenshots stay true |
| Shape before noise | Base level per series, then a trend per line, then weekly plus annual seasonality, then noise last |
| Calendar | Seasonality matches the vertical's real calendar (school districts order in winter and spring; AV rental peaks in conference seasons, September to November and April to June) |
| Event | One dated event with visible consequences in the data (a shortage, a venue closure, a recall) |
| Units | In the column names (`unit_cost_cad`, `turnaround_days`), so agent SQL answers carry units |
| Numbers | Uneven and plausible for the vertical; round numbers read as fake |

**Rename mechanics.** BSD-safe, no `-P`: `grep -rn "OldName" <app-dir>` per term and case variant (Northline, northline, NORTHLINE), then apply edits, then re-grep to zero. The ledger drives the edits; ad-hoc replacements produce stale terms in the corner nobody greps.

### Inlined from writing-instructions (full skill wins on conflict)

All visible demo copy: full-sentence sentence-case titles, no contrast framing, no em dashes, no emoji, Canadian spelling, numbers with units and baselines, the kill-list vocabulary banned (seamless, robust, leverage, AI-powered, and kin).

## Artifact templates

```gate-card
GATE DR-1 - vertical card
client: <real client, kept private to this session>
demo-company: <invented archetype name>
name-check: <the search run and its result | "unverified; coined compound">
vertical: <their industry, in their words>
audience: <who sits in the room for this demo>
base-demo: <path to the app being reframed>
tokens: <brand-<client> via brand-kit | design palette row, pasted verbatim>
end-of-card
```

The concept map, printed at GATE DR-2:

```concept-map
| demo concept | their concept | the metric that matters to them |
|---|---|---|
| <source concept> | <their concept, their vocabulary> | <metric with units> |
end-of-map
```

The rename ledger, printed at GATE DR-3:

```rename-ledger
| old term | new term | files |
|---|---|---|
| Northline Coachworks | <demo company> | frontend/src/*, backend/seed.py, README.md |
end-of-ledger
```

## Rules

| ID | Rule |
|---|---|
| DR1 | Demo companies are fictional archetypes; a real company's name anywhere in the demo is a failed gate. |
| DR2 | The concept map has at least 6 rows, relabels concepts rather than strings, and names each metric in the client's units. |
| DR3 | The architecture does not change during a reframe. A reframe that needs new engine maths is a dashboarding-skill build, and saying so is the deliverable. |
| DR4 | Every rename-ledger row is applied everywhere it appears: UI labels, seed data, README, page titles, API field descriptions, test fixtures. |
| DR5 | The seed stays fixed; screenshots MUST reproduce across rebuilds. |
| DR6 | Numbers are uneven and plausible for the vertical. |
| DR7 | The stale-term grep for every old term returns zero hits, pasted as a tool result, before delivery. |
| DR8 | All visible demo copy passes the writing sweep. |
| DR9 | Brand tokens come from brand-kit when brand material exists; ELSE one design palette row, cited verbatim in the vertical card. |
| DR10 | The client's real name appears nowhere in the demo files; the demo company carries the story. |
| DR11 | ELSE: a reframe request with no vertical or no audience named: ask the user for both, then stop. |

## Checks

No checker ships with this skill; the checks are the stale-term grep and the writing sweep, both as tool results:

```
grep -rn "Northline" <app-dir> ; grep -rn "northline" <app-dir>
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <files with visible copy>
```

The greps MUST return zero hits for every old term in the rename ledger (repeat per term and case variant). The sweep proof line goes in the delivery block. Any edit after the runs voids them; re-run before delivering.

## Delivery block

```delivery-block
DELIVERY demo-reframe
files:
  <app dir>  (reframed in place | copied to <path>)
  <seed script path>  (<size> B)
gates: <DR-1..DR-6 status, skips recorded>
checks:
  <stale-term grep results: "0 hits for <term>" per ledger term>
  <sweep proof line, pasted verbatim>
allows: <count> (<list or none>)
end-of-delivery
```
