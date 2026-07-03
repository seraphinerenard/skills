---
name: make-documents
description: |
  Long-form written deliverables: reports, memos, briefs, and one-pagers, as print-ready
  HTML, markdown, or native DOCX. Trigger on: "write a report", "write a memo", "draft a
  brief", "one-pager", "write this up as a document", "/make-documents". The document
  carries full-sentence assertion headings, an executive summary that answers the
  decision, and evidence with units, baselines, and sources. Begin at GATE DOC-1.
  Prose runs through the writing-instructions contract; the sweep checker MUST pass, and
  HTML output MUST also pass design/scripts/check_design.py.
---

# Make documents

A document built by this skill argues: the headings alone deliver the argument, the executive summary answers the decision on one page, and every number carries its unit, baseline, and source. The machine default (topic headings, a summary that summarizes nothing, adjectives doing the work of evidence) gets rewritten by hand. This skill removes the improvisation: an approved outline before drafting, a compliant starter file, and two checkers before delivery.

Set `SKILL_DIR=$HOME/.claude/skills/make-documents` (fallback: `/path/to/skills/make-documents`).

## Scope gate

IF the request edits at most two sentences of an existing swept document: make the edit, run the sweep on the file, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DOC-1** | Fill the pre-flight card: reader, decision, format row, length row, spine | DOC-1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD`; format and length rows quoted verbatim |
| **GATE DOC-2** | Outline: every section heading written as a full-sentence assertion; plan the executive summary | The OUTLINE block (template below) | Headings read in order deliver the whole argument; exec-summary slots filled |
| **GATE DOC-3** | Start the file per the format route (`cp` for html-print); write the CONTRACT comments into it | The file on disk with its CONTRACT comments | `cp` ran as a tool call; IF `cp` fails, stop and report the path |
| **GATE DOC-4** | Draft through the writing-instructions contract: its early-sample gate (first 120 to 180 words swept and fixed) runs before the rest; exemplars read for documents over 800 words | The full draft | Every heading an assertion; every number has unit, baseline, source; every table has a header row |
| **GATE DOC-5** | Run the checks for the format; fix every FAIL; re-run to exit 0 | Proof lines as tool results | Zero FAILs, or each `allow:` justified in one line |
| **GATE DOC-6** | Deliver | DELIVERY block | Proof lines pasted; block ends the message |

Restated because they are the three most-violated rules, binding during DOC-2 and DOC-4: every heading is a full-sentence assertion in sentence case (DOC1); the executive summary answers the decision in at most one page (DOC3); every number carries a unit, a baseline, and a source (DOC4).

## Values

**Length ladder.** The gate card quotes the matched row.

| Type | Budget | Shape |
|---|---|---|
| One-pager | 350 to 500 words | One claim, three to five evidence paragraphs, one table, no exec summary |
| Memo | 600 to 1,200 words | The opening paragraph is the executive summary; two to four sections |
| Report | Exec summary at most 1 page; sections of 300 to 600 words each | Exec summary, assertion-headed sections, appendices for detail |
| ELSE | Ask the user for the length budget, then stop until answered | |

**Format routes.**

| IF the deliverable is | THEN |
|---|---|
| Print-ready or client-facing HTML (the default) | `cp $SKILL_DIR/assets/document-skeleton.html <name>.html` |
| Markdown for a repo or wiki | Start a plain `.md`; the sweep still runs; headings still assert |
| Native DOCX | python-docx with built-in Heading 1/2 styles and real tables. Run `python3 -c "import docx"` first; IF the import fails, report BLOCKED and stop. Simulating headings with bold paragraphs is a failed gate |
| ELSE | Ask the user which format, then stop until answered |

**Spine.** Documents over 2 pages pick a spine at DOC-1: SCQA (recommendation to a senior audience), ABT (one decision, short), Monroe (proposal with an explicit ask), story spine (post-mortems and case studies). Documents of 2 pages or fewer: spine n/a. The full mechanics live in the ideation skill; the choice is recorded on the card.

**Executive summary template.** At most one page, five slots, each one to two sentences:

1. What: the finding or recommendation, with its headline number.
2. So what: the cost or consequence of the status quo, quantified.
3. What to do: the action requested, as a verb.
4. What it costs: money, people, time.
5. By when: the decision date and the first milestone.

**Print CSS (already in the skeleton).** `@page` size A4 (swap to Letter for US readers), 2cm margins, page number bottom right; print body 12pt/1.5 Georgia for read-on-paper documents, 11pt system sans for screen-first documents; `orphans: 2; widows: 2`; headings carry `page-break-after: avoid`; tables carry `page-break-inside: avoid`.

**CONTRACT comments.** The HTML file carries both lines, first thing after `<!doctype html>`; check_design validates the first, this skill's metadata lives in the second:

```
<!-- CONTRACT skill=design surface=document palette=cold-luxury body=16px accent=#2f4156 -->
<!-- CONTRACT skill=make-documents format=html-print type=memo -->
```

## Artifact templates

```gate-card
GATE DOC-1 - document pre-flight
reader: <the one pictured reader>
decision: <the decision this document serves, as a sentence>
format: <html-print | md | docx>    [row: "<the format row, quoted verbatim>"]
length: <one-pager | memo | report>    [row: "<the length-ladder row, quoted verbatim>"]
spine: <SCQA | ABT | Monroe | story spine | n/a (2 pages or fewer)>
end-of-card
```

The outline block, printed at GATE DOC-2:

```outline
OUTLINE <document name>
exec summary: <the five slots, one line each; "n/a" for one-pagers>
1. <full-sentence assertion heading> :: <the evidence this section carries, with its source>
2. <continue for every section>
horizontal-flow check: <one line confirming the headings alone deliver the argument>
end-of-outline
```

### Inlined from writing-instructions (full skill wins on conflict)

Every heading is a complete sentence in sentence case. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Commit to claims; name real uncertainty with a size. Numbers carry units, baselines, and sources. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, stakeholders, cutting-edge, transformative, journey, landscape (figurative). Canadian spelling: colour, centre, behaviour, labelled. The early-sample gate and the full sweep are part of GATE DOC-4 and GATE DOC-5.

### Inlined from make-charts (full skill wins on conflict)

Any chart in the document: the title is a full sentence stating the finding, with its number; axis labels carry units; a source line sits under the chart; bars start at zero; direct labels over legends; greys plus one accent; no pie, donut, or gauge. Anything more complex loads the full make-charts skill.

## Rules

| ID | Rule |
|---|---|
| DOC1 | Every heading is a full-sentence assertion; a heading that names a topic ("Background") is rewritten or its section is cut. |
| DOC2 | The outline passes the horizontal-flow test before drafting: headings read in order deliver the argument with no gaps and no repeats. |
| DOC3 | The executive summary answers the decision in at most one page using the five slots; it never previews ("this report will examine"). |
| DOC4 | Every number carries a unit, a baseline, and a source; a number missing any of the three is cut or footnoted as illustrative. |
| DOC5 | Every table is a real table with a header row and a source line; three or more parallel facts become a table, never prose lists. |
| DOC6 | HTML documents start from the skeleton (the `@keep` sentinels prove it) and keep every colour in `:root`. |
| DOC7 | DOCX uses native Heading and table styles only; bold-paragraph headings are a failed gate. |
| DOC8 | Documents over 800 words: read `writing-instructions/references/exemplars.md` first and name the two behaviours applied. |
| DOC9 | The body carries the argument; detail that does not serve the decision moves to an appendix or is cut. |
| DOC10 | ELSE: a case this table does not cover goes to the user as a question with your recommendation attached. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <file>
python3 $HOME/.claude/skills/design/scripts/check_design.py <file.html>
```

The sweep runs on every format (for DOCX, on the generation script's strings or a text export); check_design runs on the html-print route only. Both MUST pass as tool results after the last edit. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY make-documents
files:
  <path>  (<size> B)
gates: <DOC-1..DOC-6 status, skips recorded>
checks:
  <sweep proof line, pasted>
  <check_design proof line, pasted (html route)>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `assets/document-skeleton.html`: the html-print starter; it passes both checkers and shows the memo anatomy filled in.
- `writing-instructions/references/exemplars.md`: mandatory calibration read for documents over 800 words (DOC8).
