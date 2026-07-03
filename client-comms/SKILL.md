---
name: client-comms
description: |
  Client-facing messages: status updates, meeting recaps, follow-ups with an ask,
  bad news, and handoffs. Trigger on: "email the client", "status update", "meeting
  recap", "follow up with", "draft a reply to", "/client-comms". Fixed templates per
  message type, a subject line that carries the claim or ask, a date on every ask,
  and the writing sweep on every message. Begin at GATE CC-1; the sweep proof line
  and the word count are mandatory checks.
---

# Client comms

A client message earns its read in the subject line and pays it off in the first sentence. The machine default (warm filler, buried asks, undated "next steps") trains clients to skim you. Every message this skill produces is one of five shapes, filled slot by slot, written to a file, swept, counted, and dated.

Set `SKILL_DIR=$HOME/.claude/skills/client-comms` (fallback: `/path/to/skills/client-comms`).

## Scope gate

IF the request is a one-line factual reply with no ask (a confirmation, an answer to a direct question): write it, run the sweep on the file, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE CC-1** | Match the message to a type row | CC-1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD`; type row quoted verbatim |
| **GATE CC-2** | Write the body to a file by filling that type's template from Values | The message file on disk | Every template slot filled; asks carry dates and named people |
| **GATE CC-3** | Write the subject line | The subject line, printed with one line naming the claim or ask it carries | Subject states the claim or ask with its date; no banned openers |
| **GATE CC-4** | Run the sweep and the word count | Sweep proof line and `wc -w` output, both as tool results | Sweep exit 0; body within the type row's length |
| **GATE CC-5** | Deliver | DELIVERY block | Proof line pasted; block ends the message |

Restated because they are the three most-violated rules, binding during CC-2 and CC-3: the ask or the fact lands in sentence one, context after it (CC1); every ask carries a date and a named person (CC2); the subject line is the claim or the ask, never "Update" or "Following up" (CC4).

## Values

**Type table.** The gate card quotes the matched row.

| IF the message must | Type | Length |
|---|---|---|
| Report progress on running work | status-update | at most 200 words |
| Record what a meeting decided | meeting-recap | as long as the decisions and actions require, no filler |
| Get one thing from the reader | follow-up | at most 150 words |
| Tell the client something went wrong | bad-news | at most 200 words |
| Hand work to another person or team | handoff | at most 250 words plus the artifact list |
| ELSE | Ask the user what the message must cause, then stop until answered | |

**Templates.** Fill every slot; a slot that does not apply is written out as such ("Blocked: nothing blocked"), never deleted.

```message-template
STATUS UPDATE
Done: <each item with its completion date>
Next: <each item with its expected date>
Blocked: <each blocker with who unblocks it and what was asked of them, or "nothing blocked">
Decisions needed: <each with the options, your recommendation, and the date you need it, or "none">
```

```message-template
MEETING RECAP  (sent the same day as the meeting)
Decisions made: <each decision as one sentence>
Actions: <action, owner, date; one line each>
Open questions: <question and who owes the answer>
Next meeting: <date, time with zone, purpose>
```

```message-template
FOLLOW-UP
Sentence one: the ask, with the date you need it.
Then: the minimum context that lets the reader say yes.
Close: the reply expectation ("a one-line yes works", or "need your call by <date>").
```

```message-template
BAD NEWS
Sentence one: the fact, with numbers.
Sentence two: the cause, plainly stated.
Sentences three and four: the plan and its date.
No softening adverbs, no good-news bundling, no "unfortunately" cushions.
```

```message-template
HANDOFF
State: where the work stands, in numbers.
Artifacts: each file or link with its path.
Next actions: what the receiver does first.
Questions: who to ask about what.
```

**Banned openers**, banned outright in any type: "Hope this finds you well", "Just checking in", "Just following up", "Touching base", "Quick question", "Sorry to bother you", "As per my last email", "Per my last email".

**Subject lines.** The subject is the claim or the ask with its date. "Forecast slipped 3 days: decision needed on scope by Friday 10 July" passes. "Update", "Following up", "Quick sync", "Checking in" fail.

## Artifact templates

```gate-card
GATE CC-1 - message type
recipient: <who reads this, and their stake>
purpose: <what this message must cause, as one sentence>
type: <status-update | meeting-recap | follow-up | bad-news | handoff>    [row: "<the type row, quoted verbatim>"]
end-of-card
```

### Inlined from writing-instructions (full skill wins on conflict)

Sentence one carries the point. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Commit to claims; numbers carry units and baselines. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, stakeholders, cutting-edge, transformative, journey, landscape (figurative). Canadian spelling: colour, centre, behaviour, labelled. Dates unambiguous: 10 July 2026 or 2026-07-10, with a time zone whenever a time matters.

## Rules

| ID | Rule |
|---|---|
| CC1 | The ask or the fact is sentence one; context follows the ask, never precedes it. |
| CC2 | Every ask carries a date and a named person; "soon" and "when you get a chance" are failed gates. |
| CC3 | Dates are unambiguous (10 July 2026 or 2026-07-10); times carry their zone. |
| CC4 | The subject line states the claim or the ask; "Update" class subjects are failed gates. |
| CC5 | One message, one primary ask; a second ask gets its own message or a numbered list the reader can answer inline. |
| CC6 | Every message states its reply expectation: what response is needed and by when, or "no reply needed". |
| CC7 | Meeting recaps go out the same day as the meeting. |
| CC8 | Bad news leads with the fact and is never bundled with good news to soften it. |
| CC9 | Length rows bind; when technical detail is the point, the detail moves to an attachment or linked document and the body stays within the row. |
| CC10 | ELSE: a message that fits no type takes the follow-up shape (ask first, context after), or ask the user. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <message file>
wc -w <message file>
```

Both run as tool results after the last edit. The sweep MUST exit 0 (or each `allow:` is justified in one line); the word count MUST sit within the matched type row. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY client-comms
files:
  <path>  (<size> B)
gates: <CC-1..CC-5 status, skips recorded>
checks:
  <sweep proof line, pasted>
  <wc -w output, pasted>
allows: <count> (<list or none>)
end-of-delivery
```
