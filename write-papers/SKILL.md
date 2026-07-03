---
name: write-papers
description: |
  Research papers and preprints: claims first, evidence mapped, every number
  re-runnable, every citation verified. Trigger on: "write the paper", "draft the
  preprint", "write the methods section", "arXiv version", "paper revision",
  "/write-papers". Begin at GATE WP-1, the claims card, before any drafting.
  Figures follow make-charts; prose follows writing-instructions with documented
  academic allowances; the sweep checker MUST pass on the manuscript source.
---

# Write papers

A paper is a set of falsifiable claims with their evidence attached. The machine default fails in known ways: abstracts that promise instead of report, numbers nobody can regenerate, citations pasted from memory, and a limitations paragraph of ritual hedges. Each gate pins one of those down: claims before drafting, an evidence map before writing, a rerun ledger before any number ships, and a citation ledger before the reference list is trusted.

Set `SKILL_DIR=$HOME/.claude/skills/write-papers` (fallback: `/path/to/skills/write-papers`).

## Scope gate

IF the request edits at most two sentences of an existing manuscript with a maintained rerun ledger: make the edit, run the sweep on the file, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE WP-1** | Fill the claims card: one to three claims, each falsifiable, the venue row, the reader | WP-1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD`; each claim falsifiable as written |
| **GATE WP-2** | Map every claim to its evidence | The evidence-map block | Every claim has an experiment or derivation with a script path; no orphan claims, no orphan experiments |
| **GATE WP-3** | Rerun the numbers | The rerun ledger | Every number destined for the paper reran from its script as a tool call, or is cut, or becomes cited prior work |
| **GATE WP-4** | Draft per the venue's section order; figures through the inlined make-charts rules; limitations written with sizes | The full draft | Abstract reports findings with numbers; claims stated by the intro's third paragraph; limitations section present |
| **GATE WP-5** | Verify every citation by opening its source | The citation ledger | Every reference has a URL or DOI and the date opened; unverified references cut |
| **GATE WP-6** | Run the sweep on the manuscript source; fix or `allow:` each hit | Sweep proof line as a tool result | Exit 0; each `allow:B5` carries a one-line reason |
| **GATE WP-7** | Deliver | DELIVERY block | Proof line pasted; block ends the message |

Restated because they are the three most-violated rules, binding during WP-3 and WP-4: the abstract reports findings with numbers, never promises (WP1); every number in the paper traces to a script in the repro appendix (WP3); the limitations section states boundaries with sizes, never ritual hedges (WP4).

## Values

**Section order per venue.** The gate card quotes the matched row.

| Venue class | Order |
|---|---|
| ML preprint (arXiv) | Abstract, introduction (claims by paragraph 3), related work, method, experiments, discussion, limitations, references, repro appendix |
| Journal article | Abstract, introduction, methods, results, discussion with limitations inside it, references; repro material as supplementary |
| Workshop paper (4 to 8 pages) | Abstract, introduction with related work folded in, method, experiments, limitations, references |
| ELSE | Ask the user for the venue and its template, then stop until answered |

**Abstract rule.** Findings with numbers. "Weekly retraining cuts held-out forecast error 12% against a monthly baseline" ships; "we explore the dynamics of model staleness" does not.

**Limitations template.** Three to five entries, each one sentence of boundary plus a size:

```limitations
- <what the result does not cover>: <the size of the gap>.
  Example shape: "Results cover synthetic reward models only; the two production
  models tested (4% of the eval set) showed the same direction but are excluded
  for licence reasons."
end-of-limitations
```

**Repro appendix template.**

```repro-appendix
Environment: <language and library versions, hardware, seed>
Data: <source, version or date pulled, licence>
| Figure or table | Script | Command | Runtime |
|---|---|---|---|
| Fig 1 | <path> | <command> | <minutes> |
end-of-appendix
```

## Artifact templates

```gate-card
GATE WP-1 - claims card
claim 1: <the claim, falsifiable as written>
claim 2: <the second claim, or "single-claim paper">
venue: <ML preprint | journal | workshop>    [row: "<the venue row, quoted verbatim>"]
reader: <who must be convinced, and of what>
title: <working title stating the main finding>
end-of-card
```

The evidence map, printed at GATE WP-2:

```evidence-map
| Claim | Experiment or derivation | Figure or table | Script path | Status |
|---|---|---|---|---|
| 1 | <what proves it> | <Fig/Table n> | <path> | <done | to run> |
end-of-map
```

The rerun ledger, printed at GATE WP-3. A number whose rerun does not match is fixed at the source or cut; a number with no script is cut or becomes cited prior work:

```rerun-ledger
| Number in paper | Source script | Rerun date | Matched |
|---|---|---|---|
| <value and where it appears> | <path> | <date> | <y | n> |
end-of-ledger
```

The citation ledger, printed at GATE WP-5:

```citation-ledger
| Ref | Verified at (URL or DOI) | Date opened |
|---|---|---|
| <author year> | <link> | <date> |
end-of-ledger
```

### Inlined from writing-instructions (full skill wins on conflict)

Commit to claims; name uncertainty with a size. No contrast framing, no em dashes, no emoji. Numbers carry units and baselines. Kill list: delve, robust, seamless, leverage, streamline, unlock, elevate, empower, holistic, synergy, actionable, cutting-edge, transformative, journey, landscape (figurative). Canadian English binds outside quoted material; quotations keep their original spelling. Academic allowance: field-standard hedging of a genuinely uncertain result is permitted through `allow:B5 <one-line reason>` markers, counted in the delivery block.

### Inlined from make-charts (full skill wins on conflict)

Figure titles state the finding with its number; axis labels carry units; what error bars or bands show is named in the caption; the caption cites the generating script; bars start at zero; greys plus one accent; no chartjunk, no rainbow palettes. Anything more complex loads the full make-charts skill.

## Rules

| ID | Rule |
|---|---|
| WP1 | The abstract reports findings with numbers; "we explore" and "we investigate" openings are failed gates. |
| WP2 | Every claim maps to evidence and every experiment maps to a claim; orphans on either side are cut. |
| WP3 | Every number traces to a script listed in the repro appendix; the rerun ledger proves each ran. |
| WP4 | The limitations section is mandatory: three to five boundaries, each with a size; a hedge without a size is a failed gate. |
| WP5 | Related work engages the three to five closest works specifically (what each did, how this differs); citation dumps are failed gates. |
| WP6 | Every citation is verified by opening its source; the ledger records the link and the date. |
| WP7 | Figures follow the inlined make-charts rules; a figure whose caption cannot state a finding is reworked or cut. |
| WP8 | Methods carry what reimplementation needs: model, data, seeds, hyperparameters, compute. |
| WP9 | The intro states the claims by its third paragraph; a reader who stops there knows what the paper asserts. |
| WP10 | ELSE: venue-specific format questions follow the venue's own template; when it has none, ask the user. |

## Checks

```
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <manuscript source (.md or .tex)>
```

Runs as a tool result after the last edit. Exit 0, or each hit carries an `allow:` marker with a one-line reason (`allow:B5` for the academic hedging allowance). A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY write-papers
files:
  <path>  (<size> B)
gates: <WP-1..WP-7 status, skips recorded>
checks:
  <sweep proof line, pasted>
allows: <count> (<list with reasons, or none>)
end-of-delivery
```

## References

- The house exemplar is a paper repo whose figures regenerate from scripts and whose numbers carry a rerun trail back to the run that produced them. Match that standard.
