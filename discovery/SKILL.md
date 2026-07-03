---
name: discovery
description: |
  Client discovery: turn a vague ask into a signed one-page brief. Trigger on:
  "discovery call", "client discovery", "scoping call", "prep the intake",
  "write up the discovery notes", "/discovery", or an ai-engagements engagement
  whose client cannot name a metric. Begin at GATE DI-1 of THE CONTRACT: cite the
  engagement-type row before asking anything. The brief passes the writing sweep
  (scripts/sweep.py in writing-instructions) before it goes to the client.
---

# Discovery

Discovery converts an ask like "can AI help our operations" into a one-page brief a sponsor will sign: the problem in the client's words, a metric with a baseline and a target, the data as actually seen, and the decision date. The question banks below exist because the expensive discovery failures are the questions nobody asked: the error cost, the extract nobody opened, the incumbent attempt that already died. The brief feeds ai-engagements GATE E-1 directly.

Set `SKILL_DIR=$HOME/.claude/skills/discovery` (fallback: `/path/to/skills/discovery`).

## Scope gate

IF the request updates one field of an existing brief: update it, mark the sign-off line "stale, re-confirm", re-run the sweep, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DI-1** | Classify the engagement from the type table | DI-1 gate card (template below) | Type row quoted verbatim; interviewees named. IF no row fits: ask the user, stop until answered |
| **GATE DI-2** | Run the matching question bank in the interview or async | The bank reprinted with per-question status: answered (one-line answer) or OPEN | Every question carries a status; no question deleted |
| **GATE DI-3** | Write the brief from the notes | The BRIEF artifact (template below), on disk | Every field traces to a note; nothing invented; every unresolved field listed under OPEN with the question that closes it |
| **GATE DI-4** | Sign-off | The brief's sign-off line filled | Client confirmed (name, date) or "sent-awaiting" with the send date |
| **GATE DI-5** | Deliver | DELIVERY block | Sweep proof line pasted |

Restated because they are the three most-violated rules: no invention, a field without a source note is OPEN (DI1); volumes and error costs get numbers or stay OPEN (DI2); a data claim without an opened extract is marked "described, not seen" (DI3).

## Values

**Engagement types.**

| IF the ask sounds like | Type | Bank |
|---|---|---|
| "can AI do X", feasibility, PoC, model choice, "smart assistant" | AI feasibility | A |
| Reports, KPIs, dashboards, "replace our BI", "one view of the business" | Dashboard / BI | B |
| Queue processing, document handling, "automate the X process" | Automation | C |
| Warehouse, pipelines, integrations, "single source of truth" | Data platform | D |
| ELSE | Ask the user which row is closest, then stop until answered | |

**Bank A: AI feasibility.**

1. Walk me through the task end to end as it ran last Tuesday: who touched it, in which systems, for how long?
2. How many times a month does the task run, and what does one wrong output cost, in dollars or hours?
3. When it goes wrong today, who catches it, and how long after the fact?
4. Which systems hold the inputs, and who owns access to each one?
5. Can we see 50 real rows from each source this week, handled however your privacy policy requires?
6. Who verifies outputs today, and would that person sign expected outputs for a 20-case test set?
7. What number must move for your sponsor to call this a success, from what baseline, by when?
8. Who acts on the output, and inside what time budget: seconds on a call, hours in a queue, days in a report?
9. Which privacy, residency, or procurement constraints kill options before we start?
10. What has been tried before, in-house or with a vendor, and where is the corpse?
11. If the system is wrong once in front of a customer or a regulator, what happens?
12. Who decides on this engagement, and by what date?

**Bank B: dashboard / BI.**

1. Which reports do people actually open every week, and which exist but go unread?
2. What are the five to ten questions an operator asks of the data, and what decision follows each answer?
3. Which numbers do executives check first each morning, and where do they get them today?
4. Where does the data live (warehouse, ERP, spreadsheets), at what grain, refreshed how often?
5. Who owns each source, and who can grant read access this month?
6. Which definitions are contested: what counts as "active", "on time", "revenue"?
7. When two reports disagree today, which one wins, and who arbitrates?
8. What must happen when a threshold is crossed: who is told, through what channel, how fast?
9. How many people would use this weekly, and on what screens: desk, floor, phone?
10. What does a wrong number on this surface cost: annoyance, money, or safety?
11. Which current reports must this replace outright for the project to pay for itself?
12. Which forecasting or what-if questions come up in planning that the current stack cannot answer?

**Bank C: automation.**

1. Show me the queue: how many items arrive per day, and in what pattern: steady, bursty, seasonal?
2. What fields does a person read on each item, and what do they decide?
3. What share of items are routine, and what share need judgment nobody has written down?
4. What does one mishandled item cost, and how is mishandling discovered?
5. Where do items originate (form, email, EDI, phone), and how structured are they on arrival?
6. Which systems must the automation read from and write to, and do APIs exist in both directions?
7. Who approves today, and will they staff a review queue during ramp-up?
8. What latency does the process tolerate per item: seconds, hours, or end of day?
9. Which rules are hard policy, and which are habits that can change if asked?
10. What volume growth is expected, and does the case still pay at half of it?
11. What audit trail does compliance require for each automated decision?
12. What happens on day one when the automation is down for four hours?

**Bank D: data platform.**

1. Inventory the sources: system, owner, size, grain, and how each is extracted today.
2. Which datasets are trusted, which are contested, and which live in one person's spreadsheet?
3. What breaks first when a source schema changes today, and who finds out?
4. What are the top five downstream uses, and the freshness each one needs?
5. Who owns definitions (customer, order, active), and where are they written down, if anywhere?
6. Which residency, retention, and PII rules constrain where data can live and for how long?
7. What is the monthly spend on storage, pipelines, and licences, and who signs it?
8. How do teams get access today, and how long does a new request take?
9. What volume are we designing for: rows per day, peak load, growth?
10. Which migrations or replacements are already scheduled in the next 18 months?
11. Who operates the platform after handover, and what is their current toolset?
12. Which incident in the last year best shows why this project exists?

## Artifact templates

```gate-card
GATE DI-1 - engagement type
ask: <the client's ask, one sentence, their words>
type: <AI feasibility | dashboard/BI | automation | data platform>    [row: "<the matched type row, verbatim>"]
bank: <A | B | C | D>
interviewees: <names and roles, booked or proposed>
end-of-card
```

The brief (GATE DI-3), one page, on disk, every field traced to a note:

```
CLIENT BRIEF - <client>
date: <date>    author: <name>
the problem in their words: <two or three sentences, quoted or tightly paraphrased>
metric: <name> from <baseline> to <target> by <date>
data reality (seen, not described): <sources opened, rows read, dates; anything
  not yet opened is marked "described, not seen">
constraints: <PII, residency, procurement, latency, budget ceiling>
decision maker and date: <who decides, by when>
next step: <one action, owner, date>
OPEN: <field>: <the single question that closes it>
sign-off: <client name, date | "sent-awaiting", date>
```

### Inlined from writing-instructions (full skill wins on conflict)

The brief is client prose. Full sentences; sentence case; no contrast framing; no em dashes; no emoji; numbers carry units and baselines; Canadian spelling (colour, centre, behaviour); no kill-list words (robust, seamless, leverage, unlock, holistic, stakeholders, actionable).

## Rules

| ID | Rule |
|---|---|
| DI1 | Nothing in the brief is invented. A field without a source note is listed under OPEN with the question that closes it. |
| DI2 | Volumes, costs, and dates get numbers, or the field stays OPEN. "A lot" and "soon" do not fill fields. |
| DI3 | A data claim is marked "described, not seen" until an extract has been opened; extracts beat descriptions. |
| DI4 | Bank questions are asked as written, then followed up freely; a bank question that got no answer stays in the notes as OPEN. |
| DI5 | The brief is one page. Detail beyond a page goes to an appendix the brief links, never into the brief. |
| DI6 | The incumbent-attempt question (what was tried, where is the corpse) is never skipped; prior failures price the engagement. |
| DI7 | The brief goes to the client for sign-off before any estimate or architecture conversation starts (ai-engagements GATE E-1 consumes it). |
| DI8 | ELSE: an ask that fits no type row, or an answer that contradicts the notes, goes back to the user as a question, not a guess. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <brief file>
```

The brief is a client deliverable; the sweep MUST pass as a tool result after the last edit. Zero FAILs, or each `allow:` justified in one line. A missing or crashing checker is a blocking failure to report.

## Delivery block

```delivery-block
DELIVERY discovery
files:
  <brief path>  (<size> B)
gates: <DI-1..DI-5 status, skips recorded>
checks:
  <sweep proof line, pasted>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- The ai-engagements skill: GATE E-1 consumes this brief; its matrix and metric rules govern what "scoped" means.
