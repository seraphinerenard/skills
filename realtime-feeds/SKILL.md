---
name: realtime-feeds
description: |
  Live feed clients that survive the real network: SignalR, SSE, and WebSocket
  consumers with reconnect, gap handling, recording, and latency measurement.
  Trigger on: "connect to the feed", "WebSocket client", "subscribe to live data",
  "SSE stream", "SignalR", "stream the market", "/realtime-feeds". Begin at
  GATE RF-1 of THE CONTRACT: the feed card cites its protocol row before any code.
  Verification is a pasted session log showing a forced reconnect recovering, plus
  the head of the raw recording file; the runbook passes the writing sweep.
---

# Realtime feeds

A feed client that only handles the happy path corrupts data the first night the network blinks: it reconnects without resubscribing, papers over the gap, and stores one timestamp so nobody can later tell server time from arrival time. The rules below come from running clients across the three protocol families in the table: a SignalR Core timing feed, an SSE price stream, and a WebSocket order book. Record first, mark every gap, keep both clocks.

Set `SKILL_DIR=$HOME/.claude/skills/realtime-feeds` (fallback: `/path/to/skills/realtime-feeds`).

## Scope gate

IF the request tunes one number in an existing client (backoff cap, buffer size, rotation): make the edit, re-run the RF-5 verify session, paste the evidence, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE RF-1** | Identify the feed: protocol, expected message rate, staleness tolerance | RF-1 feed card citing its protocol row verbatim | Card printed; no `<`, `TODO`, `TBD` |
| **GATE RF-2** | Design the client against the numbers table: reconnect, gaps, staleness, clocks, backpressure | RF-2 client design card, every row answered with numbers | No row answered with an adjective |
| **GATE RF-3** | Implement record-first: raw frames appended with receive timestamps BEFORE parsing; rotation stated | The recorder in code plus its rotation rule | Recording path and rotation named in the card |
| **GATE RF-4** | Implement parse, gap detection, staleness watchdog, latency capture | The client code | Parse errors quarantine the frame and count; they never kill the read loop |
| **GATE RF-5** | Verify live: connect, receive, force a disconnect, watch recovery | Pasted session log head (connect, N messages, forced reconnect, resubscribe, resume) plus `head -3` of the recording file | Both pastes are tool results |
| **GATE RF-6** | Write the runbook and deliver | Runbook + DELIVERY block | Runbook passes the sweep; proof lines pasted |

Restated because they are the three most-violated rules, binding during RF-3 and RF-4: raw frames hit disk before the parser touches them (RF3); a gap is backfilled or explicitly marked, silent continuation is the banned move (RF4); every stored message carries BOTH the server timestamp and the local receive time in UTC (RF5).

## Values

Protocol table (the RF-1 card cites one row):

| Protocol | Connection shape | Keepalive | Resume |
|---|---|---|---|
| SignalR Core | POST /negotiate for the token, then wss upgrade; JSON handshake `{"protocol":"json","version":1}`; every record terminated by 0x1e | Server pings (type 6) about every 15 s; reply type 6 | Subscriptions are per-connection: resubscribe after every reconnect |
| SSE | GET with `Accept: text/event-stream`; frames split on blank line; fields data:, event:, id:, retry: | Comment keepalives (lines starting ":") | Send `Last-Event-ID` on reconnect; EventSource cannot POST, use a fetch reader when the subscribe needs a body |
| WebSocket | wss handshake; auth via header at connect or first message after open | RFC 6455 ping/pong control frames; answer pings | No protocol resume: resubscribe, then gap-check by sequence |
| ELSE | Ask the user for the feed's docs, then stop until answered | | |

Client numbers table (the RF-2 card answers every row with these or better):

| Concern | Number |
|---|---|
| Reconnect backoff | base 1 s, factor 2, cap 60 s, jitter plus or minus 20%, reset after 60 s healthy |
| Gap detection | sequence numbers when the feed has them; ELSE a timestamp jump over 3x the median interval |
| On gap | backfill from the REST endpoint when one exists; ELSE write an explicit gap record `{"type":"gap","from":A,"to":B,"detected":<utc>}` |
| Staleness watchdog | no message for 2x the expected interval (minimum 5 s): mark stale, force reconnect |
| Clocks | store server timestamp AND local receive time, both UTC ISO 8601 with milliseconds, on every message; never overwrite one with the other |
| Recording rotation | rotate at 100 MB or daily, whichever first; name files `<feed>-<utc-date>-<seq>.ndjson` |
| Backpressure | bounded queue, 10,000 messages; on overflow drop oldest and increment a dropped counter; the socket read loop never blocks on downstream work |
| Latency report | server ts minus receive ts, p50/p95/p99 after the first session; negative values mean clock skew, report the skew, never clamp to zero |
| ELSE | a concern this table does not cover: state it in the card and ask the user |

## Artifact templates

```gate-card
GATE RF-1 - feed card
feed: <name and endpoint>
protocol: <SignalR Core | SSE | WebSocket>    [row: "<the protocol row, pasted verbatim>"]
auth: <ENV_VAR_NAME and where it enters (header | first message | query token)>
expected rate: <messages per second or per minute>
staleness tolerance: <seconds; 2x the expected interval, minimum 5 s>
backfill path: <REST endpoint | none, gaps marked>
end-of-card
```

```gate-card
GATE RF-2 - client design
reconnect: <base/factor/cap/jitter/reset>
gap detection: <sequence field name | timestamp rule>
on gap: <backfill endpoint | explicit gap record>
clocks: <server ts field name; receive ts always added>
recording: <path, rotation rule>
backpressure: <queue bound, drop policy, counter name>
end-of-card
```

Runbook format (GATE RF-6): `endpoint | auth env var | expected rate | staleness threshold | backfill path | recording path | replay command | owner`.

### Inlined from writing-instructions (full skill wins on conflict)

The runbook uses plain sentences: no em dashes, no emoji, numbers with units ("about 4 msg/s, p95 latency 180 ms"), Canadian spelling (behaviour, synchronize stays -ize).

## Rules

| ID | Rule |
|---|---|
| RF1 | Auth material comes from a named environment variable; it never appears in code, logs, recordings, or the runbook. |
| RF2 | One writer per recording file; concurrent clients get their own files, never interleaved writes. |
| RF3 | Raw frames are appended to the recording with their receive timestamp BEFORE parsing; replaying the file reproduces the parsed output deterministically. |
| RF4 | Gaps are backfilled or explicitly marked in the stored data; a client that silently continues past a gap is broken even when it looks healthy. |
| RF5 | Every stored message carries both server time and receive time, UTC, milliseconds. |
| RF6 | A parse error quarantines the frame (copied to a reject file with the error) and increments a counter; the read loop never dies on bad input. |
| RF7 | The staleness watchdog and the reconnect path are exercised in RF-5 by forcing a disconnect, not assumed. |
| RF8 | ELSE: a feed behaviour these rules do not cover gets recorded in the runbook and taken to the user. |

## Checks

```
<run the client; force a disconnect mid-session; paste the log head showing recovery>
head -3 <recording file>
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <runbook.md>
```

The session evidence and the recording head MUST appear as tool results at GATE RF-5. The sweep MUST pass on the runbook after its last edit. A feed that cannot be reached during the session is a blocking fact to report with the connection error pasted, never a reason to fabricate a session log.

## Delivery block

```delivery-block
DELIVERY realtime-feeds
files:
  <client path>  (<size> B)
  <runbook path>  (<size> B)
gates: <RF-1..RF-6 status, skips recorded>
checks:
  <session log head: connect, messages, forced reconnect, recovery>
  <recording head, 3 lines>
  <latency p50/p95/p99 line>
  <sweep proof line on the runbook>
allows: <count> (<list or none>)
end-of-delivery
```
