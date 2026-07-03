# Creativity methods: the research and the drills

This file explains why a language model's unassisted ideation is narrow, which techniques measurably widen it, and exactly how to run each technique. Evidence tags: **[PR]** peer-reviewed, **[PP]** preprint or working paper, **[AN]** practitioner or anecdotal.

## Why the default output is narrow

The model's first answer is the centroid of what most people would say. Treat it as a map of the obvious, never as a candidate.

- **Individually better, collectively the same.** Doshi and Hauser (Science Advances, 2024) had ~300 writers draft stories with and without AI idea seeds. AI access raised a writer's novelty about 8% and usefulness about 9%, with the weakest writers gaining most. The pool of stories, though, became about 10.7% more similar between writers. Individually rational AI use converges everyone on the same region of idea space. [PR]
- **Group convergence is measurable.** Anderson, Shah, and Kreminski (ACM Creativity & Cognition, 2024) found different users ideating with ChatGPT produced semantically less distinct idea sets than users of a different creativity tool, even though ChatGPT users generated more ideas and felt more productive. Feeling creative and being collectively creative come apart. [PR]
- **A peer-reviewed replication in brainstorming.** "ChatGPT decreases idea diversity in brainstorming" (Nature Human Behaviour, 2025) confirms the narrowing at the idea-pool level. [PR]
- **Alignment tuning is a root cause.** Padmakumar and He (ICLR 2024) showed feedback-tuned InstructGPT reduced essay content diversity while the base model did not, and the homogenization came from the model's inserted text, with human-written spans staying diverse. Kirk et al. (ICLR 2024) found RLHF trades output diversity for generalization across lexical, syntactic, and semantic measures. [PR]
- **The mechanism has a name: typicality bias.** Human preference raters systematically reward familiar, fluent, predictable text independent of correctness (modelled on 6,874 preference pairs, "Verbalized Sampling", 2025). Models trained on those preferences collapse toward attractor outputs. [PP]
- **The gap to humans is large.** Across 22 LLMs and 102 humans on divergent-thinking tests, models scored far below humans on every variety measure (for example 0.459 vs 0.738 on Alternative Uses), models converged on the same ideas regardless of vendor, and a "be creative" system prompt closed only a fraction of the gap (0.459 to 0.576). [PP] On the Torrance Test of Creative Writing, professionally written stories passed 3 to 10 times more expert creativity tests than LLM stories (Chakrabarty et al., CHI 2024). [PR]
- **Models cannot referee their own creativity.** In the same CHI 2024 study, no LLM's creativity judgments correlated positively with expert raters. Never let the model rank its own ideas for novelty without external criteria. [PR]

The meta-pattern that survives all of this: **separate divergence from convergence.** Explore widely with the techniques below, using explicit mechanisms rather than vibes, and only then evaluate, using the feasibility gauntlet in SKILL.md rather than the model's taste.

## Techniques that measurably widen the search

### 1. Over-generate, then push past the early ideas

The serial-order effect is one of the most robust findings in creativity research: originality rises across an ideation session while fluency falls, because the first responses are retrieved from memory and the later ones are constructed (Beaty and Silvia, 2012). [PR] Quantity instructions beat quality instructions for producing good ideas (Rietzschel, Nijstad, Stroebe, 2006, quantity-quality correlation r = .893). [PR] With LLMs specifically, Girotra, Meincke, Terwiesch, and Ulrich found GPT-4 ideas were about 7 times more likely than student ideas to land in the top decile of a pooled quality ranking, purely on volume and selection. [PP]

**Drill:** Generate 20 candidates minimum. Number them. Mark 1 through 3 as "the obvious ones" by default. Expect the interesting material after item 10; if items 15 to 20 feel hard to produce, that is the point where retrieval ends and construction starts, so keep going.

### 2. Verbalized sampling: ask for candidates with probabilities

Asking the model for k outputs each tagged with an estimated probability ("give five approaches, with how likely each is to be anyone's first suggestion") recovers a large share of the diversity that alignment removed: roughly 1.6 to 2.1 times more diverse than direct prompting, restoring about two thirds of base-model diversity, with quality held (2025). Larger models gain more. [PP]

**Drill:** For each round, produce candidates with an explicit "how predictable is this" tag. Discard or quarantine everything tagged highly predictable. Keep the tail.

### 3. Ban the just-used approach (denial prompting)

Iteratively prohibiting the technique used in the previous solution forces genuinely new strategies each round (NeoCoder, NAACL 2025). [PR]

**Drill:** After listing the obvious answers, write one sentence naming the mechanism they share ("all of these are subscription SaaS sold to the same buyer"). Then require every further idea to differ on mechanism, customer, or channel, and repeat the ban each round with the newly used mechanism added to the banned list.

### 4. Far-domain analogy

Dahl and Moreau (Journal of Marketing Research, 2002) showed far analogies produce more novel product concepts than near analogies or none, and originality scales with analogical distance. [PR] Engineering-design replications agree, with the caveat that far analogies raise variance: more duds alongside the novel hits. [PR]

**Drill:** Name three fields that face the same shaped problem under different economics (perishable inventory: airlines, bakeries, ad exchanges). For each, write down the mechanism that field uses, in that field's own terms, then port the mechanism, keeping its logic and swapping the nouns. Mid-to-far distance is the target; adjacent fields produce variations, and random fields produce noise.

### 5. Distant conceptual combination

Combining dissimilar concepts yields more emergent properties (features belonging to neither parent) than combining similar ones, because dissimilarity forces relational linking instead of property-mixing (Wilkenfeld and Ward). [PR]

**Drill:** Take the problem noun and force-combine it with a concept from an unrelated list (auction, quarantine, apprenticeship, escrow, fermentation, air-traffic control). Write the combination out until it produces a property neither side had alone; discard combinations that only stack features.

### 6. Shift the abstraction level

People inventing new things follow the path of least resistance: they retrieve a standard exemplar and tweak it (Ward, 1994). Prompting at a higher abstraction level (the function to be served, the environment to survive in) produces more novel output than prompting with concrete exemplars (Ward, Patterson, Sifonis, 2004). [PR]

**Drill:** Before ideating, restate the problem twice: once one level more abstract ("who benefits from grid congestion" instead of "which transformer supplier wins the contract"), once one level more concrete ("what does the plant electrician buy twice a year"). Ideate at all three levels; the abstract level breaks exemplar-copying and the concrete level breaks hand-waving.

### 7. Persona panels, with specific personas

A generic "be creative" instruction barely moves divergence scores. Simulating several specific, distinct perspectives helps: Solo Performance Prompting (NAACL 2024) and multi-agent role-play discussion (2024) both raised creative-task performance over single-voice prompting. [PR]/[PP]

**Drill:** Ideate the same question three times as three named, opinionated stances with different loss functions: a sceptical CFO hunting for what breaks, an operator who has run this exact process for a decade, a regulator who will audit the outcome. Keep the ideas that only one persona could have produced.

### 8. Constraint injection and inversion

Arbitrary hard constraints block the default retrieval path, the same mechanism as denial prompting. SCAMPER-style structured constraint sets show fluency and originality gains in applied studies, mostly education-context and of modest quality. [PR, applied] Inversion ("design the worst version, then negate its properties") is the practitioner analogue, and it works for the same reason: the worst version is easy to retrieve, and its negation is usually off the beaten path. [AN]

**Drill:** Re-run one ideation round under each of: capital under $5K, no software allowed, must work for exactly one customer, must be embarrassing to a large incumbent to copy. Then one inversion round: describe the idea guaranteed to fail, list why, and flip each property.

### 9. Parallel seeds, never one long thread (brainwriting)

Interactive brainstorming underperforms the same people working silently in parallel, mostly through production blocking: each utterance interferes with the next person's retrieval (Diehl and Stroebe, 1987). [PR] The LLM analogue: a single sequential conversation anchors each idea on the previous ones.

**Drill:** Generate idea batches as independent restarts with different openings (different persona, different abstraction level, different banned list) rather than one continuous list, then merge and dedupe. In a multi-agent setting, fan out independent ideators and merge afterwards.

### 10. Question-storm before answering

Problem-construction ability predicts the originality and quality of eventual solutions; how the problem gets framed caps everything downstream (Reiter-Palmon and Mumford). [PR]

**Drill:** Before generating any answers, write 10 different one-sentence versions of what the question actually is ("where does the client's AI budget leak", "which bottleneck outlasts 2027", "what does the client already own that this touches"). Pick the two most generative framings and ideate under each.

## What does not work

- **Temperature as the creativity knob.** Temperature correlates weakly with novelty and moderately with incoherence; it does not move the model into new semantic regions (Peeperkorn et al., ICCC 2024). [PR]
- **"Be more creative."** Closes a fraction of the human gap at best; specific mechanisms above do the work. [PP]
- **Chain-of-thought for single-piece originality.** Reasoning scaffolds increase the diversity of a batch of ideas (Meincke, Mollick, Terwiesch, 2024 [PP]) yet do little for the originality of one crafted artifact, and may suppress it. Use CoT to widen a pool, never to make one idea more original.
- **Letting the model judge novelty.** No positive correlation with expert judgment (CHI 2024). Judge with external criteria: the feasibility gauntlet, distance-from-obvious tags, and the user's knowledge of the domain.

## The combined loop

1. Question-storm the framing (technique 10); pick two framings.
2. Widen the frame per SKILL.md Part 1 Step 1 (levels up, sideways, second-order).
3. Three independent seed batches (technique 9), each using a different opener: persona panel (7), far-domain analogy (4), constraint round (8). Twenty candidates minimum across batches, probability-tagged (2).
4. Ban rounds: name the shared mechanism of the predictable cluster, ban it, generate again (3). Repeat twice.
5. Merge, dedupe, mark the obvious.
6. Converge with the feasibility gauntlet in SKILL.md. Creativity work ends where the gauntlet begins; nothing below survives on novelty alone.

## Sources

- Doshi, Hauser. Science Advances 10(28), 2024. science.org/doi/10.1126/sciadv.adn5290
- Anderson, Shah, Kreminski. C&C 2024. dl.acm.org/doi/10.1145/3635636.3656204
- Nature Human Behaviour, 2025. nature.com/articles/s41562-025-02173-x
- Padmakumar, He. ICLR 2024. arxiv.org/abs/2309.05196
- Kirk et al. ICLR 2024. arxiv.org/abs/2310.06452
- Chakrabarty et al. CHI 2024. arxiv.org/abs/2309.14556
- Verbalized Sampling, 2025. arxiv.org/html/2510.01171v2
- "We're Different, We're the Same", 2025. arxiv.org/html/2501.19361v1
- Beaty, Silvia. "Why do ideas get more creative across time?" 2012.
- Rietzschel, Nijstad, Stroebe. 2006.
- Girotra, Meincke, Terwiesch, Ulrich. Wharton working paper, 2023.
- Denial Prompting / NeoCoder. NAACL 2025. aclanthology.org/2025.naacl-long.141/
- Dahl, Moreau. JMR 39(1), 2002. journals.sagepub.com/doi/10.1509/jmkr.39.1.47.18930
- Wilkenfeld, Ward. Journal of Memory and Language, 2001.
- Ward. Cognitive Psychology, 1994; Ward, Patterson, Sifonis. CRJ, 2004.
- Wang et al. Solo Performance Prompting. NAACL 2024. aclanthology.org/2024.naacl-long.15/
- Diehl, Stroebe. JPSP, 1987.
- Reiter-Palmon, Mumford. digitalcommons.unomaha.edu/psychfacpub/52/
- Peeperkorn et al. ICCC 2024. arxiv.org/abs/2405.00492
- Meincke, Mollick, Terwiesch. 2024. arxiv.org/abs/2402.01727
