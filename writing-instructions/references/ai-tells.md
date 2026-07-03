# The catalogue of AI writing tells

Every entry: what the pattern is, why models produce it, and a rewrite. The bad examples are written the way frontier models actually write, so some of them will feel comfortable to produce. That comfort is the warning.

Two sources anchor this file. Wikipedia's "Signs of AI writing" page, maintained by editors who have cleaned thousands of AI-generated passages, documents the observable patterns; their statement of the mechanism is worth keeping whole: "LLMs use statistical algorithms to guess what should come next. The result tends toward the most statistically likely result that applies to the widest variety of cases." The research literature adds the second half: models are tuned toward text human raters find familiar and fluent, and raters reward typicality independent of correctness, so the model's house style is the average of everyone's house style. Kobak and colleagues (Science Advances, 2025) measured the result at population scale across 15 million biomedical abstracts: an excess-vocabulary surge after 2023 larger than the shift COVID caused, with "delves" running at 28 times its expected frequency.

Two reading rules before the catalogue. First, co-occurrence is the signal: any one tell appears in plenty of human writing, and the Wikipedia editors flag text on the pile-up, never the single instance. Second, word tells decay and pattern tells last: the loud words of 2023 ("delve", "tapestry") are already trained out, and the editors' era tables show the mid-2025 survivors are quiet ones ("emphasizing", "enhance", "highlighting", "showcasing"). Word lists are this year's symptoms; the structural patterns (manufactured contrast, trailing participles, copula avoidance, uniform rhythm) come from the training objective and age far better.

## A. Framing and argument tells

### A1. Contrast framing and negative parallelism (hard ban, every variant)

The model manufactures depth by denying a claim nobody made, then asserting its own. Variants: "It's not X, it's Y", "This isn't about X. It's about Y", "X isn't the point. The point is Y", "More than just X", "not merely X but Y", "not only X but also Y", "The question isn't X, the question is Y", "less about X than about Y", "The real story isn't X", and the reversed form "prioritizing Y rather than X", which newer models favour because it hides the same move inside a participle. Wikipedia's editors describe the habit precisely: the model frames contrasts "as if clearing misconceptions" that no one held.

- Bad: *"The outage wasn't a technology failure. It was a process failure."*
- Good: *"The outage started with a config push that skipped review because the on-call engineer had merge rights nobody had audited since 2024."*

The rewrite states the actual finding with its mechanism. If a genuine misconception needs correcting, name who holds it and show the evidence: *"The post-mortem blamed the database, but the database logs show it stayed healthy for the first nine minutes."*

The quiet variants are the same move at lower volume, and they survive after the loud ones are trained away: "rather than", "instead of", "as opposed to", "unlike X", and the appositive "X, not Y". Each defines the thing by the shadow of an alternative nobody proposed.

- Bad: *"We make sure every model is deployed individually rather than one big push."*
- A first rewrite usually keeps the disease: *"Each model deploys on its own schedule, so a bad rollout stops one model instead of all of them."* The "instead of" clause rides along and has to go too.
- Good: *"Each model deploys on its own schedule; a bad rollout stops at one model."*

The test: delete the contrast clause and check what the reader lost. A clause whose deletion costs nothing was a shadow. When two real options were actually weighed, report the decision with its reason as its own sentence ("We shipped per-model deploys because the March incident took every model down at once"); a reported decision carries evidence and needs no frame.

### A2. The manufactured pivot

Fragment-question then reveal: "The result?", "The catch?", "The problem?", "Here's the thing:", "The kicker?". Advertising cadence standing in for a transition.

- Bad: *"We doubled the marketing budget. The result? Sign-ups fell."*
- Good: *"We doubled the marketing budget and sign-ups fell 12%, because the new spend went to a channel whose audience we had already saturated."*

### A3. Hollow causal claims

A restated definition dressed as analysis: "demand drives price", "growth creates opportunities", "efficiency reduces costs", "trust takes time to build". Each is true by definition and empty of information. Real analysis names the actors, the mechanism, and the magnitude.

- Bad: *"Prices rose because demand outstripped supply."*
- Good: *"Prices rose 40% in six weeks because two of the four fabs were down for retooling while handset makers double-ordered against the shortage they expected."*

### A4. False ranges

"From X to Y" implying a scale that does not exist: "from solo developers to global enterprises", "from the Big Bang to dark matter", "from onboarding to offboarding". List the actual items or name the actual dimension.

- Bad: *"The platform serves everyone from students to Fortune 500 companies."*
- Good: *"The platform's paying accounts are mostly mid-size accounting firms; the free tier skews to students."*

### A5. The rule of three

Triads as the default rhythm of completeness: "fast, reliable, and secure", "innovation, inspiration, and insight". Three items feel finished to the model regardless of how many items reality contains. Count the real items and list those. When one matters most, spend the sentence on it.

### A6. Both-sidesing and manufactured concessions

"Of course, no approach is perfect." "While challenges remain, the trajectory is promising." "It's a balance." The model hedges into symmetry to avoid being wrong in either direction. If the evidence favours a side, take the side, and give the strongest specific objection rather than a ritual one.

- Bad: *"Both build and buy have pros and cons, and the right answer depends on context."*
- Good: *"Buy it. Our two attempts to build in-house each died at the maintenance handoff, and the vendor's worst-case pricing is under one engineer-year."*

### A7. Significance inflation

"Marks a pivotal moment", "stands as a testament to", "underscores the importance of", "represents a paradigm shift", "in the ever-evolving landscape of". Importance is asserted instead of shown. Show the consequence: who did what differently, and what number moved.

### A8. Portentous closers and applause lines

"The future belongs to those who adapt." "The organizations that master this will define the next decade." "One thing is certain: change is coming." Endings written for imaginary applause. End on the last piece of content: the final number, the decision, the date.

### A9. Disconnected declaratives and the causal capstone

The lore-dump paragraph: sentences that share a paragraph but no argument, each one a compressed aphorism introducing a new topic, capped with "That is why X" to fake a chain the paragraph never built.

- Bad: *"Nine lands hang on the tree, and the gods keep the wars burning. History runs in five ages, and the game is set in the fourth: Óðinn stokes mortal wars to fill Valhöll before the last battle. That is why adventurers exist."*
- Good: *"The game is set in the fourth of five ages, the age in which Óðinn already knows the last battle is coming. He needs dead warriors to fill Valhöll before it arrives, so he keeps the mortal wars burning. Those wars are where adventurers come from: fighters whose deaths are worth collecting."*

Two mechanisms fix it. First, the thread rule (given-new, Joseph Williams' cohesion principle): every sentence begins from something the reader just received (the previous sentence's subject or object, or a this/that reference to it) and adds one new thing; a sentence with no link starts its own paragraph or dies. Second, causality lives inside the sentences (because, so, where) at each link; "That is why", "This is why", and "Which is why" are announcements standing in for a chain, and a chain that exists needs no announcement. Related tell: the colon splice that crams a second fact into a sentence that has not finished its first ("the game is set in the fourth: Óðinn stokes mortal wars...").

## B. Sentence-level tells

### B1. Punchy fragments

"Faster approvals. Lower costs. Real results." Also the one-word paragraph. ("Powerful.") Fragments simulate emphasis while removing the subject and verb that would make the claim checkable. Write complete sentences; put the emphasis in the content.

### B1a. The verbless catalogue (trailer prosody)

Parallel noun phrases with the verb deleted, balanced on a comma: *"Each rule with its own gate, and each account with a named owner."* *"Every deploy, gated."* *"No dashboards. No delays. Just answers."* The problem lives in the prosody: preference training rewarded the cadence of keynote and trailer copy, where rhythm signals confidence, and the model reaches for that cadence in the landing slot (paragraph ends, summaries, commit messages) to signal completion. Every individual word is innocent, which is why vocabulary lists miss the pattern; the frame carries the guilt. The pattern also survives because the model cannot hear its own register, the same self-judging failure documented for novelty, so the fix has to be external: the sweep's B10 frames plus the drill below. An instruction to "sound less like a trailer" fails on a model that cannot hear the trailer.

The drill: restore the elided verb, then ask whether the sentence still earns its place.

- Bad: *"Each rule with its own gate, and each account with a named owner."*
- Restored: *"Every rule has its own gate, and every account has a named owner."* Grammatical now, and exposed as two facts already stated elsewhere; in most drafts the restored sentence merges into the sentence that introduced the rules, or dies.

End paragraphs on a fact with a unit, a consequence, or a date. A paragraph that ends on rhythm is a paragraph whose last sentence carried nothing.

Three siblings of the same prosody disease, all from observed deck copy:

- **The withheld-referent opener**: *"Three curves crossed at once."* A count of unnamed things is a cliffhanger; the reader is made to wait for nouns the writer already has. Name them in the same sentence: *"Capability, regulation, and economics sit at the heart of a successful AI implementation."*
- **The isocolon punch triple**: *"The front office wins revenue and loyalty, the middle office cuts loss and risk, and the back office releases capacity that funds the rest."* Three clauses trimmed to matching length, near-rhyme, and an idiom tail ("funds the rest", "pays the bill", "moves the needle", "sells the idea"). Humans do not speak in matched triples; let each clause run the length its content needs, and end on the fact.
- **The aphorism title**: *"Intelligence, compounded."* Cadence with no proposition. A title earns punch by carrying content: *"How to become a frontier financial firm in the age of AI."*
- **The omniscient register**: *"X sets the bill, Y drives the result."* Universal present-tense law with no evidence and no scope. A report states results and an adviser recommends with reasons, so a general claim ships with its scope and source, and advice arrives voiced as a recommendation. Confidence means evidenced precision; certainty without evidence reads as arrogance and invites the one sceptic in the room to test it.

### B2. Trailing "-ing" analysis clauses

A fact, then a bolted-on clause claiming unearned meaning: "…, highlighting the importance of robust governance", "…, underscoring the company's commitment to quality", "…, cementing its position as a leader". End the sentence at the fact. If the implication is real, give it its own sentence with its own evidence.

- Bad: *"Claims triage time fell to 90 seconds, demonstrating the power of the new platform."*
- Good: *"Claims triage time fell to 90 seconds. Most of the gain came from pre-filling the intake form from the policy record; the model contributed the last 15 seconds."*

### B3. Copula avoidance

"Serves as", "stands as", "functions as", "acts as", "represents", "boasts", "features", "offers" doing the job of "is" and "has". Plain copulas are the strongest verbs in analytical prose because they commit.

- Bad: *"The facility serves as the company's primary distribution hub and boasts 300,000 square feet."*
- Good: *"The facility is the company's main distribution hub, at 300,000 square feet."*

### B4. Nominalization stacks

Actions frozen into abstract nouns: "the implementation of the migration achieved a reduction in latency". Un-freeze them: "migrating cut latency". Watch for -tion, -ment, -ance nouns chained with "of".

### B5. Hedging stacks

"Could potentially", "may possibly", "it could be argued that", "tends to suggest". Alignment training makes models hedge reflexively; readers read hedges as either ignorance or evasion. Commit, and where uncertainty is real, state it as a fact with a size: "untested on accounts opened after the CRM migration; those were 4% of the sample".

### B6. Sentence-adverb throat-clearing

"Crucially,", "Importantly,", "Notably,", "Interestingly,", "It's worth noting that". If the sentence that follows matters, it will demonstrate that itself. Delete the adverb; promote the evidence.

### B7. Over-signposting

"First… Second… Third… Finally…" scaffolding on content that has no sequential logic, plus meta-commentary: "Let's break this down", "Now that we've covered X, let's turn to Y". Prose for readers holds together through its argument, and needs a map only when it is genuinely long.

### B8. Restating the question and defining the undisputed

Opening an answer by paraphrasing the prompt, or defining terms no reader disputes ("Risk management, the practice of identifying and mitigating risks, …"). Start at the first sentence that adds information.

## C. Vocabulary

### C1. The kill list, with replacements

| Banned | Write instead |
|---|---|
| delve into | examine, dig into, read |
| leverage (verb) | use |
| robust | tested, fault-tolerant, specific behaviour ("survives a region outage") |
| seamless | delete, or say what did not break |
| utilize | use |
| facilitate | run, help, chair |
| streamline | cut steps (say which) |
| foster | build, fund, allow |
| landscape / ecosystem (abstract) | market, field, the companies that… |
| tapestry / journey (figurative) | delete; describe the actual sequence |
| testament to | evidence of (then give the evidence) |
| pivotal / crucial / critical (as praise) | the number or consequence that makes it matter |
| unlock / unleash / supercharge / elevate / empower | the concrete verb for what actually happens |
| cutting-edge / state-of-the-art / groundbreaking | the capability, dated ("first production deployment we know of, 2025") |
| holistic / comprehensive (as praise) | list what is covered |
| game-changer / paradigm shift | what changed, for whom, by how much |
| actionable insights | the recommendation itself |
| stakeholders | the specific people (the ops team, the lenders) |
| synergies | the specific saving or cross-sale |
| navigate (figurative) | handle, comply with, survive |
| meticulous / intricate / multifaceted / commendable / paramount | delete or replace with the detail that earned it |

### C2. Why word lists rot, and the register caveat

The excess-vocabulary study (Kobak et al., 2025) found marker words surging in post-2023 abstracts, and later model generations already use "delve" less; vendors patch the symptoms, and even the em-dash habit has been declared "fixed". The categories in this file (inflation, hedging, copula avoidance, manufactured contrast) are stable because they come from the training objective, so sweep by category first and by word list second.

One fairness caveat, learned publicly in 2024: when Paul Graham called "delve" a ChatGPT signature, Nigerian and other Commonwealth English speakers pointed out the word is ordinary in their registers. Word tells are probabilistic and register-relative. This matters in reverse for your own drafting: the ban list exists because you overproduce these words, and it is a production rule for you, never a detector to accuse humans with.

## D. Attribution and evidence tells

### D1. Vague authority

"Experts argue", "industry reports suggest", "observers have noted", "studies show", "research indicates". Agreement conjured without a source. Name the person, institution, document, and date, or cut the claim. "A 2024 Uplevel study of 800 developers found no significant PR-throughput difference" is checkable; "studies show mixed results" is filler.

### D2. Numberless intensifiers

"Significant growth", "substantial savings", "a notable improvement", "vast majority". Each is a number the writer did not fetch. Fetch it or drop the claim.

### D3. Fake balance of citations

Listing outlets to borrow authority ("featured in TechCrunch, Forbes, and Wired") instead of citing one thing one outlet actually said, with a date.

## E. Formatting tells

- **E1. Bold-lead bullets.** "**Speed:** the system is fast." Outline scaffolding shipped as prose. Write sentences, or build a real table.
- **E2. Title Case Headings.** Sentence case everywhere, and headings are full-sentence assertions.
- **E3. Colon headlines.** "Latency: The Hidden Cost of Scale". A full sentence replaces it: "Tail latency costs more than median latency at scale."
- **E4. Em-dash chains.** More than one em dash in a paragraph is a signature. Prefer commas, colons, and full stops. Context for calibration: the em dash became the internet's favourite AI accusation in 2025, and the accusation alone is weak, since skilled human writers use the mark heavily. Density plus co-occurrence with other tells is what actually signals machine text. For your own output the operating rule stays strict because you overproduce the mark.
- **E5. Emoji and decorative glyphs.** Never.
- **E6. A heading for every three sentences.** Headings exist to serve navigation in long documents; short pieces read as prose.
- **E7. Uniform bullet grids.** Every bullet exactly one line, every list exactly the same depth. Real content has uneven weight; let the important item run longer, and cut the padding items entirely.
- **E8. Tables for non-tabular content.** A table with columns "Aspect / Description" is a list wearing a costume. Tables are for rows that share real fields.
- **E9. Inconsistent smart quotes.** Curly and straight quotes mixed in one document, the residue of pasting from a chat window.

## F. Rhythm and structure

### F1. Uniform sentence length

Detection literature calls the human signal burstiness: variance in sentence length and structure. Machine drafts regress to a mean sentence of 15 to 22 words, subject-verb-object, forever. The fix follows the thought: a long sentence where the reasoning is genuinely chained, a short one where the point lands. Never insert decorative fragments to fake variance (that is tell B1).

### F2. The perfectly balanced paragraph

Every paragraph three sentences, every section two paragraphs, symmetry everywhere. Human structure is lumpy because evidence is lumpy: the section with the strongest material runs longest.

### F3. The essay shell

An introduction that promises ("In this document, we will explore…"), a body, and a conclusion that re-says the body ("In conclusion, we have seen…"). In anything under a few thousand words, state the finding in the first sentence and end on the last piece of content. Recaps are for documents long enough to forget the beginning of.

### F4. Performed casualness

The overcorrection tell, common in frontier models asked to "sound human": "Look,", "Honestly?", "I'll be real with you", "*checks notes*", "chef's kiss", "wild, right?". This is a machine imitating a blogger imitating speech. Natural register comes from the choices in section G, never from catchphrases.

## G. Register: what actually reads as human

These are the levers with peer-reviewed support, from the corpus and instructional-design literature.

1. **Concreteness pays, measurably.** Packard and Berger (Journal of Consumer Research, 2021): more concrete, imageable language in service interactions raised customer satisfaction about 9% and subsequent spending about 30%. Concrete nouns and verbs signal that the writer actually looked at the thing. "The reconciliation job" beats "the process"; "re-keying data the applicant already typed" beats "manual inefficiencies".
2. **The involved register.** Biber's corpus work puts texts on a dimension from involved (spoken-like) to informational (nominalized, noun-dense). Markers of the involved pole: first and second person, contractions, present tense, private verbs (think, believe, doubt), dropped "that" ("the numbers show the pilot stayed on budget" rather than "the numbers show that the pilot stayed on budget"). Mayer's personalization studies found conversational style beats formal style for learning and attention across eleven experiments. Machine drafts default to the informational pole; pull toward involved in anything a person will read voluntarily.
3. **Commit.** Asserted claims are more credible than hedged ones, and the model's reflexive hedges ("generally", "can be seen as", "it's worth noting") read as evasion. Hedge only genuine uncertainty, and hedge it precisely, with the boundary stated.
4. **Tolerate specificity and asymmetry.** Analyses of human against LLM prose find human writing carries more local unpredictability: surprising word choices, uneven emphasis, claims that commit. The machine instinct smooths all of it out. When a detail is odd and true (the migration had two rollbacks; the vendor's CEO answered the support ticket personally), keep it: odd-and-true is what verifiable writing looks like.

## H. The sweep, expanded

Run these searches over any draft. Every hit gets fixed or justified.

**Framing:** `not just` `isn't just` `not merely` `not only` `more than just` `isn't about` `it's about` `the question is` `the real` `rather than` `instead of` `as opposed to` `, not ` `That is why` `This is why` `Which is why` `The result?` `The catch?` `Here's the thing` `no approach is perfect` `challenges remain` `it's a balance` `make sure` `ensure` `guarantee`

**Inflation:** `pivotal` `crucial` `testament` `underscores` `highlights the` `marks a` `paradigm` `landscape` `ever-evolving` `fast-paced` `journey` `tapestry` `transformative` `game-chang`

**Vocabulary:** `delve` `leverage` `robust` `seamless` `utilize` `facilitate` `streamline` `foster` `unlock` `empower` `elevate` `holistic` `synerg` `actionable` `stakeholder` `navigate` `meticulous` `multifaceted` `cutting-edge` `state-of-the-art`

**Evidence:** `experts` `observers` `industry reports` `studies show` `research indicates` `significant` `substantial` `notable` `vast majority` (each needs a name, a date, or a number)

**Sentence:** `serves as` `stands as` `functions as` `acts as` `boasts` `could potentially` `may possibly` `it could be argued` `Crucially` `Importantly` `Notably` `It's worth noting` `Let's` `we will explore` `In conclusion` `Ultimately`

**Format:** more than one `—` per paragraph; `:` inside a heading; Title Case headings; `**` label bullets; emoji; `📈` and friends anywhere.

**Spelling:** Canadian sweep for `-ize` kept, `-our`, `-re`, doubled L (`travelled`, `modelled`, `labelled`), `licence`/`license` and `practice`/`practise` by part of speech, `cheque`, `grey`, `aluminum`.

Finish with the read-aloud pass from SKILL.md. The sweep catches the patterns; the ear catches everything else.
