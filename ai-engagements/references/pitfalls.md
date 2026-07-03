# The demo-to-prod gap catalogue

Every entry below follows the same arc: the engagement looked healthy, one unexamined assumption surfaced late, and the fix cost more than checking would have. All clients are fictional. Read this before the design review, and again before UAT.

## The demo that was never measured

A logistics client saw a routing assistant answer eight hand-picked questions perfectly in the sales demo. The build phase reused those eight questions as the informal test. In UAT, dispatchers asked their own questions and the pass rate was near half, discovered live, in front of the sponsor who had shown the demo to her board. The gap was always there; nobody had counted it.

Countermeasure: the eval set exists before the demo, is sampled from real inputs, and the demo runs cases FROM the set. The first number the client hears is the measured pass rate, so the number can only improve from there.

## The data dictionary that described a wish

A benefits administrator described a clean "member table" in discovery. Week 6 revealed three regional systems, two active migrations, and a spreadsheet a coordinator updated by hand on Fridays. The extraction work consumed the budget that had been priced for modelling.

Countermeasure: the week-1 data audit opens real extracts. For each source, read a 50-row sample yourself, check label quality, confirm the refresh cadence, and get the access path working before the estimate is signed. A dictionary is a claim; rows on your screen are evidence.

## The chatbot that should have been a button

A property manager asked for a chat assistant for maintenance requests. The inputs turned out to be enumerable: unit, category, urgency, photo. Tenants had to type a paragraph where four taps would do, adoption stalled, and the client read the stall as "AI does not work" rather than "the interface was wrong".

Countermeasure: if the inputs are enumerable, ship a form and put the model behind it (classification, routing, drafting the work order). Chat earns its friction only when the input space is genuinely open.

## The latency nobody budgeted

A call-centre assistant for an insurer passed every accuracy check. It answered in 9 to 14 seconds, because the design chained five model calls. Agents handle calls in under four minutes and stopped using it in the second week. Accuracy was never the problem.

Countermeasure: name the shipping surface at design time and set the latency budget from that surface. Count serial calls against the budget before choosing the architecture; an agent loop that cannot fit gets replaced with a shorter pipeline or moved to a pre-call batch step.

## The agent loop that billed like a department

A procurement assistant was allowed to call tools until it was satisfied. Median requests made 4 calls; the tail made 30 or more, and one runaway class of requests looped on a failing tool. The monthly invoice arrived at roughly six times the estimate, and the client's first question was who approved that.

Countermeasure: cap steps per request in code, log cost per request from day one, and alert on outliers. Present cost to the client as a range with the multiplier shown, per the cost model in the main skill file, so the invoice can never be the first time they see the tail.

## The invented number in the client's PDF

A quarterly summary generator for a wealth manager produced fluent reports, and one of them stated a portfolio return that appeared nowhere in the source data. A client noticed before the adviser did. Every report the system had ever produced then had to be re-checked by hand, which cost more than the system had saved.

Countermeasure: client-facing numbers come from retrieved or computed values only, never free generation; every figure carries a source reference; outputs with numbers route through a human review queue until the eval set shows a sustained clean run, and spot-audits continue after.

## The fine-tune that froze last quarter's rules

A telecom client wanted responses in an exact house format and the team went straight to fine-tuning. The format spec changed twice during the training data build, the tuned model shipped encoding the middle version, and each correction round took weeks. A prompt with three worked examples, tested later, hit the same format accuracy.

Countermeasure: prompting and RAG get measured against the eval set before any fine-tune is proposed, and fine-tuning waits until requirements have stopped moving and ~500 clean examples exist. Escalation is justified by a score gap, per the decision procedure in `architecture-selection.md`.
