# Architecture selection

Run this table before naming an approach to the client. Check the disqualifying conditions first: a single hit removes the row, whatever its other virtues. Then take the least complex surviving row, baseline it, and escalate only on a measured eval failure.

## The decision table

### Classical ML (gradient boosting, regression, time-series models)

| Dimension | Assessment |
|---|---|
| Good at | Tabular prediction, scoring, ranking, forecasting with a labelled history and a numeric or categorical target |
| Cost profile | Cheapest to run by orders of magnitude; training is a laptop job for most client datasets; no per-call token cost |
| Latency profile | Microseconds to milliseconds per prediction; never the bottleneck |
| Risk profile | Well understood; explainability tooling mature (SHAP, feature importance); drift is the main operational risk |
| Disqualifying conditions | No labelled history exists and none can be back-filled; the input is open-ended text or images the client will not pre-process; the target changes definition quarter to quarter |

### RAG (retrieval-augmented generation)

| Dimension | Assessment |
|---|---|
| Good at | Question answering over the client's own documents with citations; grounding outputs in a controlled corpus; policies, manuals, contracts, knowledge bases |
| Cost profile | One model call per request plus embedding and index costs; predictable; caching the system prompt cuts repeat cost |
| Latency profile | Retrieval adds 100–500 ms over a bare call; acceptable in almost every interactive surface |
| Risk profile | Answers are only as current as the index; retrieval misses look like model failures; chunking and index refresh are the real engineering |
| Disqualifying conditions | The corpus is under ~50 documents (put them in the prompt instead); the corpus is stale and nobody owns refreshing it; the task needs actions or multi-step reasoning over live systems, not lookup |

### Agent (tool-use loop)

| Dimension | Assessment |
|---|---|
| Good at | Tasks that need live systems mid-flight: database queries, API lookups, calculations, then a decision that depends on what came back |
| Cost profile | Calls per request multiply 3–10× over a single call; cost is variable and must be capped and logged per request |
| Latency profile | Steps are serial; a 5-step loop at 2 s a step is a 10 s answer; fits batch and back-office queues, dies in typeahead and call-centre screens |
| Risk profile | Failure modes compound across steps; needs step caps, tool-call logging, and an eval that scores the end-to-end outcome, not single calls |
| Disqualifying conditions | A fixed 2–3 step pipeline covers every observed case (build the pipeline, skip the loop); the shipping surface has a sub-2-second budget; no tool the agent needs can be exposed safely |

### Fine-tuning

| Dimension | Assessment |
|---|---|
| Good at | Exact output formats, house tone, narrow classification where prompting has measurably plateaued below target |
| Cost profile | Training cost plus a hosting premium; every base-model upgrade re-raises the question of re-training |
| Latency profile | Same as the base model; no inherent penalty |
| Risk profile | Least reversible option; encodes today's requirements into weights; quality depends on example quality more than count |
| Disqualifying conditions | Fewer than ~500 clean examples exist; requirements are still moving; prompting and RAG were never measured against the same eval (they go first, always) |

### Buy, do not build

| Dimension | Assessment |
|---|---|
| Good at | Commodity capabilities: transcription, OCR, translation, generic support deflection, meeting summaries |
| Cost profile | Subscription; usually under the cost of one engineer maintaining a bespoke pipeline |
| Latency profile | Vendor-controlled; test it, do not trust the datasheet |
| Risk profile | Roadmap and pricing sit with the vendor; data leaves the client's boundary unless contracted otherwise |
| Disqualifying conditions | The workflow is the client's competitive edge; data cannot leave the tenancy under any contract; the vendor fails your eval set on the client's real cases |

## The decision procedure

1. Write the task as input → output with three real examples.
2. Strike every row with a disqualifying condition hit.
3. Baseline the least complex surviving row against the eval set (for LLM rows, that baseline is one prompt with no retrieval and no tools).
4. Escalate one row at a time, only when the current row's measured score misses the client's target, and record the score that justified each escalation.
5. Re-run the table when scope changes. A new document type, a new language, or a new latency budget can flip a disqualifier.

The score that justified each escalation goes in the engagement log. Six months later, when someone asks why the system is an agent and not a prompt, the answer is a number, not a memory.
