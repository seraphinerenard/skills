---
name: backtest-gauntlet
description: |
  Vet a trading-strategy backtest before believing it, and gate the path to live money.
  Trigger on: "is this backtest real", "vet this strategy", "should this go live",
  "backtest results look great", "run the gauntlet", "/backtest-gauntlet". Begin at
  GATE BG1 of THE CONTRACT. Honest backtests are the mandatory gate: a strategy passes
  the gauntlet before paper, and paper passes its own pre-registered gate before live.
  The FEATURE TIMING table and the pre-registered verdict card are the checks; there is
  no checker script because the discipline is procedural.
---

# Backtest gauntlet

Backtests fail in one direction: they flatter. Lookahead leaks, mid-price fills, uncounted fees, and post-hoc criteria each add imaginary edge, and the market removes it with real money. The two failure modes that reach live accounts are an order-size formula nobody asserted against the balance, and an edge that existed only in the sample it was tuned on. The house rule stands: honest backtests are the mandatory gate. A line that passes its gate earns paper trading; a line that fails is halted rather than rationalized. This skill is that gate, written down.

Set `SKILL_DIR=$HOME/.claude/skills/backtest-gauntlet` (fallback: `/path/to/skills/backtest-gauntlet`).

## Scope gate

IF the request is to interpret an already-gauntleted result (the verdict card exists in the repo or conversation): answer from the card and the artifacts, stop. ELSE: run the full contract. A "quick look at my backtest" is the full contract; quick looks at flattering numbers are how money leaves.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE BG1** | Fill the spec card: strategy, venue, data, frequency, cost model in numbers | BG1 gate card (template below) | Card printed; every cost line a number, not "approximately zero" |
| **GATE BG2** | Lookahead audit of every feature and signal | The FEATURE TIMING table: `feature | information timestamp | decision timestamp | gap` | Every gap strictly positive; any leak kills the run here |
| **GATE BG3** | Fill realism audit against the fill-rules table | The fill audit: one line per order type stating the fill model and the code line asserting size against balance and venue limits | Size assertion exists in code (pasted); no mid-price taker fills |
| **GATE BG4** | Out-of-sample protocol: split dates, walk-forward for anything tuned, costs inside the metric | The split record: train/validate/final dates, the final window's single touch date, results per window | Final window touched once; result includes costs; calibration reported for probabilistic strategies |
| **GATE BG5** | Verdict against PRE-REGISTERED criteria | The verdict card: criteria (written before results were seen) beside outcomes, GO or NO-GO | NO-GO halts the line; any rework restarts at BG1 as a new run, recorded |
| **GATE BG6** | Paper gate before live: duration, trade count, kill criteria pre-registered | The paper-gate card | Live only after paper meets its own card; kill criteria wired, not aspirational |

Restated because they are the three most-violated rules, binding throughout: information time strictly precedes decision time for every input (BG-R1); every fill pays the spread and the fees, and every order size is asserted in code against balance and limits (BG-R3); pass criteria are written before results are seen, and a failed gate halts the line instead of retuning until green (BG-R5).

## Values

**Classic leaks (BG2 kills).**

| Leak | How it sneaks in |
|---|---|
| Resolution or settlement price as a feature | "Current price" pulled after the outcome is known |
| Same-bar high/low/close used for a decision inside that bar | Bar aggregates exist only when the bar closes |
| Indicator computed over the full series | Normalization, z-scores, or minima/maxima that saw the future |
| Survivor universe | Backtesting only instruments that still exist at the end |
| Repainted or revised data | Source restates history; the live feed never showed those values |
| Fill assumed at signal price | The book moved between signal and order; live latency is not zero |
| ELSE | Any feature whose information timestamp cannot be established gets treated as a leak |

**Cost model (BG1 card MUST fill every row).**

| Line | Format |
|---|---|
| Venue fees | maker and taker, in bps or absolute per contract |
| Spread cost | half-spread per taker fill, from measured quotes in the data period |
| Slippage / depth | fill price at quoted depth for your size, not top-of-book for infinite size |
| Funding, borrow, gas, withdrawal | whatever the venue charges; zero is written as "0 (verified)" |

**Fill rules (BG3).** Taker fills cross the spread at the quoted depth. Maker fills require a queue-position model or an assumption proven conservative (for example: filled only when price trades strictly through the limit). Where a vetted fill simulator already exists for the venue, it is the required adjuster and hand-rolled fill logic beside it is a failed gate. The order size formula MUST be asserted in code against available balance and venue max-order limits, and the assertion line is pasted into the BG3 artifact.

**Sample minimums (BG4/BG5).** A strategy with fewer than 100 independent trades in the final window cannot pass, whatever the numbers say; report "insufficient sample" and either extend the window or halt. Trades separated by less than the strategy's holding period are not independent; count clusters, not fills.

**Calibration (probabilistic strategies).** Brier score `B = mean((p - y)^2)` over final-window predictions, reported beside the baseline Brier of always predicting the realized base rate. A strategy whose B is not below baseline has no probabilistic edge, whatever its P&L says about the window.

**Paper-gate defaults (BG6).** Minimum 2 weeks AND minimum 100 trades on paper; kill criteria pre-registered as numbers: max daily loss, max consecutive losses, and maximum divergence of realized edge from backtest expectation (for example: realized edge below the backtest's 5th percentile for 3 consecutive days halts). ELSE: the user pre-registers different numbers in writing before paper starts.

## Artifact templates

```gate-card
GATE BG1 - spec card
strategy: <one sentence: what it does and why that should pay>
venue: <market and venue>
data: <source, period, how obtained>
frequency: <decision cadence>
costs: fees <n>, half-spread <n>, slippage model <named>, other <n or "0 (verified)">
sizing: <formula, and where the balance/limit assertion lives>
end-of-card
```

```verdict-card
VERDICT <run id, date>
pre-registered (written <date, before results>):
  edge after costs >= <n> | final-window trades >= <n> | max drawdown <= <n> | capacity >= <n>
outcomes:
  <metric>: <value> | <metric>: <value>
verdict: GO to paper | NO-GO, line halted
prior runs of this strategy: <list of run ids, so retries are visible>
end-of-card
```

## Rules

| ID | Rule |
|---|---|
| BG-R1 | Information time strictly precedes decision time for every feature; the FEATURE TIMING table proves it per feature. |
| BG-R2 | The final window is touched exactly once, and its touch date is recorded; a second touch converts the window into validation data and a new final window must be found. |
| BG-R3 | Costs live inside the headline metric, never in a footnote; fills follow the fill-rules table; sizes are asserted in code. |
| BG-R4 | Anything tuned is walk-forward tested; in-sample sharpe is not evidence. |
| BG-R5 | Criteria are pre-registered; a failed gate halts the line. Reworking and re-running is legitimate ONLY as a new, numbered run whose verdict card lists the prior runs. |
| BG-R6 | Paper before live, always; paper has its own pre-registered card; kill criteria are wired into the runner, not documented intentions. |
| BG-R7 | Results prose passes the writing sweep when it ships as a report; "significant edge" without the number is banned there too. |
| BG-R8 | ELSE: anything this table does not cover resolves toward the conservative reading (treat as leak, count as cost, do not pass); when that is unclear, ask the user. |

## Checks

No checker script; the artifacts are the checks, and their order is the enforcement:

1. The FEATURE TIMING table exists before any performance number is discussed in the conversation.
2. The sizing assertion is pasted as code, not described.
3. The verdict card shows pre-registration (its criteria carry a date before the results).
4. Any report file passes `python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <file>`; paste the proof line.

## Delivery block

```delivery-block
DELIVERY backtest-gauntlet
files:
  <artifacts / report paths>  (<size> B)
gates: <BG1..BG6 status, skips recorded>
checks:
  feature-timing rows: <count>, leaks found: <count and disposition>
  sizing assertion: <file:line>
  verdict: <GO to paper | NO-GO halted>, pre-registered <date>
  <sweep proof line if a report shipped>
allows: <count> (<list or none>)
end-of-delivery
```
