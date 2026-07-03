---
name: writing-instructions
description: |
  House style for all written deliverables. MANDATORY whenever producing written content
  for a deck, presentation, document, report, proposal, UI, email, web page, chart, or any
  written output that goes into a file that is not a README or code documentation.
  Begin at GATE W1 of THE CONTRACT before drafting a word. The sweep checker
  scripts/sweep.py is mandatory and its proof line goes in the delivery block.
  Covers: Canadian English, banned AI writing patterns with rewrites, full-sentence
  assertion titles, number discipline, and the read-aloud test.
---

# Writing instructions

Language models write in a recognizable house style, and that style reads as machine output to anyone who has seen it twice. The patterns banned here come from thousands of observed cases, and the quiet ones survive in frontier models after the loud ones are trained away. Because your defaults will pull toward those patterns while you write, every phase below asks for evidence that the rules ran: a printed card, a checker result, a named link between sentences. This file obeys its own rules; banned patterns appear only inside quoted specimens, so the prose around the quotes is safe to imitate.

Set `SKILL_DIR=$HOME/.claude/skills/writing-instructions` (fallback: `/path/to/skills/writing-instructions`).

## Scope gate

IF the request edits at most two sentences of an existing swept document: make the edit, run the sweep on the file, paste the proof line, stop. IF the file is a README or code documentation: rules A1 (contrast framing), E4 (em dashes), E5 (emoji), and CAN (Canadian spelling) still bind; the contract does not. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT. Do not start a phase until the previous artifact exists.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE W1** | Fill the pre-flight card: reader, register, the one claim | W1 gate card (template below) | Card printed; no `<`, `TODO`, `TBD` |
| **GATE W2** | Write ONLY the first 120 to 180 words to the target file; run the sweep on it | Sweep tool output on the sample, plus one-line fixes for every hit | Tool result visible; hits fixed before more prose exists |
| **GATE W3** | Write the rest. IF the document exceeds 800 words: first read `references/exemplars.md` and name in one line the two exemplar behaviours you are applying | The full draft on disk | Draft complete; no placeholder text |
| **GATE W4** | Run the sweep on the full file; fix every FAIL; re-run until exit 0. Then the read-aloud pass (rewrite every sentence you could not say to a colleague across a table) and the thread pass: for every paragraph, name the word in each sentence that picks up the sentence before; an unlinked sentence moves to its own paragraph or dies | Final sweep proof line | `PASS sweep` as a tool result; zero FAILs or each `allow:` justified; no unlinked sentences remain |
| **GATE W5** | Deliver | DELIVERY block | Proof line pasted; block ends the message |

Restated because they are the three most-violated rules, binding during W2 and W3: contrast framing is banned in every variant, loud and quiet ("rather than", "instead of", "X, not Y" all count; rule A1); every sentence picks up something from the sentence before it (rule V8); em dashes are banned (rule E4).

## Values

### Canadian English

All output uses Canadian spelling. The sweep flags the US and UK forms.

| Pattern | Canadian | Flagged |
|---|---|---|
| -our | colour, behaviour, favour, honour, labour, neighbour | color, behavior, favor, honor, labor |
| -re | centre, metre, fibre, theatre, litre | center, meter, fiber, theater, liter |
| -ize kept | organize, recognize, analyze, optimize | organise, recognise, analyse, optimise |
| Doubled L | travelled, labelled, modelling, cancelled, signalling | traveled, labeled, modeling, canceled |
| -ce nouns | defence, offence, licence (noun), practice (noun) | defense, offense |
| Other | cheque (payment), grey, catalogue, dialogue, tire, curb, aluminum | check (payment), gray, catalog, tyre, kerb, aluminium |

Two pairs sit beyond the sweep's reach: you hold a licence and are licensed to operate, and you keep a practice while you practise daily. The -our words drop the u before suffixes, so humour produces humorous. Write dates unambiguously (3 July 2026 or 2026-07-03) and use metric units by default.

### The kill list

Replace or cut each of these before the draft goes out:

| Banned | Write instead |
|---|---|
| delve into | examine, read, dig into |
| leverage (verb), utilize | use |
| robust | the tested behaviour ("survives a region outage") |
| seamless | delete, or say what did not break |
| streamline | cut steps (say which) |
| foster, facilitate | build, fund, run, allow |
| landscape, ecosystem, tapestry, journey (figurative) | the market, the field, the actual sequence |
| testament to | evidence of, then give the evidence |
| pivotal, crucial, game-changer, transformative | the number or consequence that makes it matter |
| unlock, unleash, elevate, empower, supercharge | the concrete verb for what happens |
| cutting-edge, state-of-the-art, best-in-class | the capability, dated |
| holistic, comprehensive (as praise) | list what is covered |
| actionable insights | the recommendation itself |
| stakeholders | the specific people (the ops team, the lenders) |
| synergies | the specific saving or cross-sale |
| navigate (figurative) | handle, comply with, survive |
| meticulous, multifaceted, vibrant, boasts | delete, or the detail that earned it |
| named owner(s), key/growth/value drivers, "drivers of" | the person's role, or the actual causes, named |
| ship, ships, shipped (software jargon) | deliver, release, send, or the dated event |
| gate, ledger, artifact, sweep (process jargon in client prose) | the plain word for what happens in the client's world; this skill's vocabulary stays in the build process |

### Titles and headings (rule T1)

Every title and heading is a complete sentence stating a position or finding, written in sentence case without colon constructions. A reader who reads only the headings gets the full argument. "Q3 results" fails because it names a topic; "Q3 revenue doubled while support costs stayed flat" passes because it makes the argument.

### Numbers (rule N1)

Every number carries units, a baseline, and a source. "Grew significantly" is banned; the working format reads "grew 34% year over year, from $890K to $1.19M (Stripe dashboard, Jan to Dec 2025)". A number without a comparison is decoration.

### The thread rule, shown (V8)

Machine paragraphs stack disconnected declaratives and cap them with fake causality:

> Nine lands hang on the tree, and the gods keep the wars burning. History runs in five ages, and the game is set in the fourth: Óðinn stokes mortal wars to fill Valhöll before the last battle. That is why adventurers exist.

Nothing in sentence two picks up anything from sentence one; the colon crams two facts into one breath; "That is why" announces a chain the paragraph never built. The threaded version starts each sentence from the last one's payload:

> The game is set in the fourth of five ages, the age in which Óðinn already knows the last battle is coming. He needs dead warriors to fill Valhöll before it arrives, so he keeps the mortal wars burning. Those wars are where adventurers come from: fighters whose deaths are worth collecting.

The paragraph now moves in one chain, from the fourth age to Óðinn, from Óðinn to the wars, from the wars to the adventurers. Its causality lives in "so" and "where", and it needs no capstone. Run this test on every paragraph you write: name each sentence's link to the one before, and when a sentence has no link, move it to its own paragraph or cut it.

### The register, shown (V11, V12, A11)

The trailer register makes three moves at once: it counts things it declines to name, it chops thoughts short for punch, and it asserts laws it has no evidence for.

> Three curves crossed at once. For a decade the technology was early, the rules were unwritten, and margins were fat enough to wait. All three conditions ended together, and the window to lead is open now.

The professional version names the things, lets sentences run as long as the thought, and claims only what it can carry:

> Capability, regulation, and economics sit at the heart of a successful AI implementation. AI capability is growing exponentially, yet many financial institutions are slow to adapt. The window to lead AI transformation is still wide open.

The rewrite is calmer and says more, because the three referents arrive in the first sentence, the tension between fast capability and slow adoption is an observation a reader can check, and nothing rhymes.

## Artifact templates

```gate-card
GATE W1 - pre-flight
reader: <the one pictured reader, named or typed: "the COO who pays for this">
register: <spoken-professional | technical | executive>
claim: <the single sentence this document exists to prove>
length: <target words or pages>
exemplars: <"n/a under 800 words" | the two behaviours you will apply>
end-of-card
```

## Rules

Voice rules, all MUST:

| ID | Rule |
|---|---|
| V1 | Commit to claims. State the thing, and name real uncertainty with its size ("untested on categories launched after January; 4% of sample"). Fog such as "could potentially" is banned. |
| V2 | Concrete over abstract: replace every abstract noun (efficiency, alignment, scalability) with the actor, the action, and the number. |
| V3 | Finish every sentence. Fragments and one-word paragraphs are banned. |
| V4 | Use "is" and "are". "The gallery is the exhibition space" beats "serves as". |
| V5 | One idea per sentence; one argument per paragraph. |
| V6 | Vary rhythm by following the thought: let a sentence run long where the reasoning chains, and let it stop short where the point is simple. Decorative fragments are banned. |
| V7 | Verbs over nominalizations: "we decided" beats "a decision was made". |
| V8 | The thread rule: every sentence after a paragraph's first begins from something the reader just got (the previous sentence's subject, object, or a this/that reference to it) and adds ONE new thing. Test mechanically by naming the linking word; a sentence with no link starts a new paragraph or dies. A paragraph is one argument passing through connected hands, and a stack of separate facts belongs in a table or a list. |
| V9 | Describe. Write as if answering a colleague's question; trailer narration and sales copy are banned. Assurance verbs ("make sure", "ensure", "guarantee") give way to the thing that happens and the mechanism behind it. Portent ("the gods keep the wars burning", "change is coming") gives way to the fact and its consequence. |
| V10 | Every clause gets a finite verb you would speak. A balanced verbless pair ("each X with its Y, and each Z with its W") is prosody standing in for content, so restore the verbs or merge the facts into the argument. Imitate the register of a senior engineer's incident report, which runs on verbs, actors, numbers, and full stops. End on a fact whenever you feel the pull to end on rhythm. |
| V11 | Long sentences are allowed and often right, because sentence length follows the size of the thought. Chopping a thought into short clauses for punch is banned, and so is trimming three parallel clauses to matching lengths; a matched-length triple with an idiom tail ("...releases capacity that funds the rest") is prosody, and people do not speak in it. |
| V12 | Confidence means evidenced precision. Certainty without evidence reads as arrogance, and the one sceptic in the room will test it. A universal present-tense business law ("the front office wins revenue", "X drives the result") carries a scope and a source or stays out of the draft ("across the 14 deployments we reviewed, front-office tools recovered their cost first"). Voice advice as a recommendation with its reasons, because the writer reports results and advises, and holds no monopoly on what is right. |

Pattern bans, enforced by the sweep (IDs match `references/ai-tells.md`):

| ID | Banned pattern | Write instead |
|---|---|---|
| A1 | Contrast framing, every variant, loud or quiet: "it's not X, it's Y", "more than just X", "not only X but Y", "rather than Y", "instead of Y", "as opposed to Y", "X, not Y". Each defines a thing by the shadow of an alternative nobody proposed; "deployed individually rather than one big push" invents the big push it disowns | State what it IS, with the mechanism: "each model deploys on its own schedule, so a bad rollout stops one model" |
| A9 | Causal capstones bolted onto sentences that established no cause: "That is why X", "This is why", "Which is why" | Build the chain inside the sentences with because and so; a chain that exists needs no announcement |
| B9 | Assurance voice: "we make sure", "we ensure", "guaranteed" | The thing that happens and the mechanism that makes it happen |
| B10 | The verbless catalogue: "Each rule with its own gate, and each account with a named owner", "Every deploy, gated", "No dashboards. No delays." Elided verbs and balanced noun pairs make trailer prosody, and nobody says it across a table | Restore the verb and let the sentence carry content: "every rule has its own gate, and the account list names an owner for each one". End the paragraph on a fact: a number, a consequence, a date |
| A11 | Withheld-referent openers: "Three curves crossed at once.", "Two forces collided." A count of unnamed things is a cliffhanger, and cliffhangers belong to advertising | Name the things in the same sentence: "Capability, regulation, and economics decide whether an AI programme succeeds" |
| B11 | Punch-idiom clause tails: "...that funds the rest", "pays the bill", "moves the needle", "carries the day", "sells the idea" | The fact with its number: "...which freed 11 analyst-hours a week, enough to staff the review queue" |
| B12 | Aphorism titles: "Intelligence, compounded." Cadence carrying no proposition | A title that says something: "How to become a frontier financial firm in the age of AI" carries content without straining |
| A2 | Manufactured pivots: "The result?", "Here's the thing:" | A full sentence with the consequence in it |
| A3 | Hollow causal claims: "demand drives price" | The actors, the mechanism, the magnitude |
| A5 | The rule of three: "innovation, inspiration, and insight" | Count the real items and list those |
| A6 | Both-sidesing: "no approach is perfect", "it's a balance" | Take the side the evidence favours and give the strongest specific objection |
| A7 | Significance inflation: "pivotal moment", "testament to", "marks a shift" | The consequence in numbers or events |
| A8 | Portentous closers and empty openers: "The future belongs to...", "In today's fast-paced world" | End on the last piece of content |
| B1 | Punchy fragments: "Faster approvals. Lower costs. Real results." | Complete sentences carrying the numbers |
| B2 | Trailing "-ing" analysis: ", highlighting the importance of..." | End at the fact, and give real significance its own evidenced sentence |
| B3 | Copula avoidance: "serves as", "stands as", "boasts" | "is", "has" |
| B5 | Hedging stacks: "could potentially", "may possibly" | Commit, or state the uncertainty with a size |
| B6 | Throat-clearing: "Crucially,", "It's worth noting that" | Delete the adverb and promote the evidence |
| D1 | Vague authority: "experts argue", "studies show" | Name the person, institution, document, and date, or cut the claim |
| D2 | Numberless intensifiers: "significant growth", "vast majority" | Fetch the number or drop the claim |
| E2 | Title Case Headings | Sentence case, full-sentence headings (T1) |
| E3 | Colon headlines: "Latency: The Hidden Cost of Scale" | One full sentence: "Tail latency costs more than median latency at scale" |
| E4 | Em dashes | Commas, colons, full stops, parentheses |
| E5 | Emoji and decorative glyphs | Banned everywhere |
| E1 | Bold leads, bullet or paragraph: "**Speed:** the system is fast", "**The proof, and the standing invariant.** I ran the sweep..." | Sentences under a real heading; the paragraph starts in regular type with its point in the first sentence |
| F3 | The essay shell: "In this document we will explore...", "In conclusion..." | State the finding in sentence one and end on content |
| CAN | US or UK spellings per the table above | Canadian forms |
| ELSE | A pattern that smells machine-made but matches no row | Apply the governing test below and rewrite in spoken words |

### The governing test

If a person could not say the sentence out loud to a colleague across a table, it does not belong in the document. Write the draft, then ask of every sentence whether this is how you would say it, and when the answer is no, rewrite it the way you would say it.

## Checks

```
python3 $SKILL_DIR/scripts/sweep.py <file> [more files...]
```

Scans prose (markdown, text, and the visible text of HTML) for every pattern ID above. D2 intensifiers are flagged only on lines without a digit, so evidenced claims pass. Escape a deliberate use with `allow:<ID> <reason>` in a comment near the line. Output ends with `PASS sweep v<n> file=<name> sha=<8hex>` per clean file and exit 0. The run MUST appear as a tool result; typed output is a failed gate, and any edit after the run voids it.

## Delivery block

```delivery-block
DELIVERY writing-instructions
files:
  <path>  (<size> B)
gates: <W1..W5 status, skips recorded>
checks:
  <sweep proof line(s), pasted verbatim>
allows: <count> (<list or none>)
end-of-delivery
```

## References

- `references/ai-tells.md`: the full pattern catalogue with before/after rewrites and the research behind it. The rule IDs above index into it.
- `references/exemplars.md`: real human writing (Churchill, Orwell, Buffett, Feynman, Graham, and others) with the five behaviours they converge on. Mandatory read before any document over 800 words (GATE W3).
