---
name: publish-mcp-tools
description: |
  Author and publish MCP servers. Trigger on: "build an MCP server", "publish an MCP
  tool", "MCP server for X", "wrap this API as MCP", "/publish-mcp-tools".
  Begin at GATE M-1 of THE CONTRACT: the incumbent card decides whether this server
  deserves to exist before any code. A read-only wrapper of a commodity API dies at
  that gate. The README checker scripts/check_mcp_readme.py is mandatory and its
  proof line goes in the delivery block. READMEs and docs pass writing-instructions.
---

# Publish MCP tools

An MCP server earns its slot by doing what the incumbent servers skip, and it keeps trust by stating its limits out loud. The recurring failure is the thin wrapper: a read-only passthrough of an API that already has three wrappers, shipped with a README that promises everything and documents nothing it cannot do. Every gate below exists to kill that server before it ships, or to make the honest version of it.

Set `SKILL_DIR=$HOME/.claude/skills/publish-mcp-tools` (fallback: `/path/to/skills/publish-mcp-tools`).

## Scope gate

IF the request revises the README or docs of an already-published server: make the edit, run `python3 $SKILL_DIR/scripts/check_mcp_readme.py README.md`, paste the proof line, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE M-1** | Search what already covers this domain (registry, npm, GitHub); list incumbents and what each skips | M-1 incumbent card | Card printed with named incumbents; a read-only wrapper of a commodity API is DEAD here, no exceptions |
| **GATE M-2** | Name the server `mcp-<action>-<domain>`; check 2 or 3 candidates for collisions | M-2 naming card with pasted collision-check results | `npm view <name>` (or registry search) output shown for each candidate |
| **GATE M-3** | Design the engineering table stakes: caching, streaming, pagination, truncation, rate limits, errors, auth | M-3 engineering card, every row answered with numbers | No row answered "n/a" without a reason; truncation row quotes the exact message format |
| **GATE M-4** | Build the server; write every tool description for a model reader | The code plus a tools table (name, when to use, when NOT to use, cost note) | Each description states when NOT to use the tool |
| **GATE M-5** | Write the README from the skeleton below | README on disk | `python3 $SKILL_DIR/scripts/check_mcp_readme.py README.md` exits 0, proof pasted; sweep passes |
| **GATE M-6** | Publish: pin the version, add the changelog line, publish, smoke-test the published package | Pasted publish output and smoke-test output | `npx <name>` (or equivalent) handshakes against the published artifact |

Restated because they are the three most-violated rules, binding during M-3 and M-5: no silent truncation, every capped result says "showing N of M, refine with <param>" (M5); the README has a Limitations section that states what the server does NOT do (M1); overclaim words are banned outside Limitations (M2).

## Values

Naming pattern: `mcp-<action>-<domain>`, lowercase, hyphenated. Examples: `mcp-query-openalex`, `mcp-audit-wcag`, `mcp-fetch-sec-filings`. Collision check commands: `npm view <name> name` (an E404 means the name is free) plus a search of the MCP catalogues you publish to (the modelcontextprotocol servers list, Smithery, PulseMCP), results pasted into the M-2 card.

Engineering table stakes. Every row of the M-3 card answers with the HOW, not a yes:

| Concern | Requirement |
|---|---|
| Caching | Name what is cached and the TTL in seconds ("market metadata, 300s"). "Nothing" needs a reason (data is per-request unique). |
| Streaming | Name which tools stream. Any tool whose output exceeds 100 KB or 10 s of upstream time streams. |
| Pagination | Name which tools paginate, the default page size (50), the maximum (200), and the cursor or offset parameter. |
| Truncation | NEVER silent. A capped result carries: "showing N of M results; refine with <parameter>". Quote the exact string in the card. |
| Rate limits | Quote the upstream's published limit with its source URL and date; state your client-side limiter number under it. |
| Errors | Every error message names what failed and what the caller does next ("upstream rate limit; retry after 30 s"). Raw stack traces never leave the server. |
| Auth | One environment variable, named in the card and the README. Never a CLI flag, never hardcoded, never logged. |
| ELSE | A concern this table does not cover: state it in the card and ask the user. |

Tool descriptions are written for a model reader: sentence one is when to use it; a "Do not use for" sentence follows; input constraints and one cost or latency note ("one upstream call, about 800 ms") close it.

Overclaim ban (enforced by the checker outside the Limitations section): complete coverage, all endpoints, every endpoint/API/method, fully supports, guaranteed, production-ready, enterprise-grade, blazing fast, 100%. A claim with a real scope survives by carrying its number on the same line ("covers 34 of 41 endpoints").

## Artifact templates

```gate-card
GATE M-1 - incumbent card
domain: <what this server operates on>
incumbents: <name each existing server or tool found, with where it lives>
they skip: <the specific capabilities none of them have>
differentiation: <one sentence: why this server exists>
verdict: <BUILD | DEAD (read-only commodity wrapper) | DEAD (incumbent already does it)>
end-of-card
```

```gate-card
GATE M-3 - engineering card
caching: <what, TTL seconds>    [row: "<the Caching row, pasted verbatim>"]
streaming: <which tools, or none with reason>
pagination: <tools, default 50, max 200, param name>
truncation message: "<the exact string>"
rate limit: <upstream limit, source URL, date; client limiter>
errors: <the error format, one example>
auth: <ENV_VAR_NAME>
end-of-card
```

README skeleton (M-5 writes these sections in this order):

```markdown
# mcp-<action>-<domain>

<One paragraph: what it does and who it is for.>

## Install
## Tools
<table: tool | when to use | inputs>
## Limitations
<What it does NOT do. Coverage boundaries with numbers. Data staleness.
Upstream dependence and what happens when the upstream is down.>
## Quotas and pricing
## Changelog
```

### Inlined from writing-instructions (full skill wins on conflict)

Headings in sentence case. No contrast framing ("it's not X, it's Y"). No em dashes, no emoji. Numbers carry units and baselines. Kill list applies: seamless, robust, leverage, unlock, cutting-edge, holistic, actionable. Canadian spelling: colour, behaviour, catalogue.

## Rules

| ID | Rule |
|---|---|
| M1 | The README has a `## Limitations` section stating what the server does not do, its coverage boundary with a number when one exists, staleness, and upstream dependence. |
| M2 | Overclaim phrases are banned outside Limitations unless the same line carries the scoping number. |
| M3 | The name matches `mcp-<action>-<domain>`. A grandfathered name gets an `allow:M3` marker with the history in one sentence. |
| M4 | No emoji anywhere in the README or tool output. |
| M5 | No silent truncation: every capped or paginated result states "showing N of M" and the refinement path. |
| M6 | The upstream rate limit is quoted from its published source and respected by a client-side limiter. |
| M7 | Every tool description states when NOT to use the tool. |
| M8 | Versions are pinned (exact dependency versions); every release adds one changelog line with the date. |
| M9 | Auth material lives in one named environment variable; it never appears in logs, errors, or the README's examples. |
| M10 | ELSE: a situation these rules do not cover gets stated and taken to the user before publishing. |

## Checks

```
python3 $SKILL_DIR/scripts/check_mcp_readme.py README.md
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py README.md
```

Both MUST pass as tool results after the last edit. The README checker prints `FAIL M<n> file:line` per violation, honours `allow:M<n> <reason>` markers (counted), and ends `PASS check_mcp_readme v1 file=README.md sha=<8hex>`. A missing or crashing checker is a blocking failure to report, never a licence to self-attest.

## Delivery block

```delivery-block
DELIVERY publish-mcp-tools
files:
  <path>  (<size> B)
gates: <M-1..M-6 status, skips recorded>
checks:
  <check_mcp_readme proof line, pasted>
  <sweep proof line, pasted>
  <publish + smoke-test output, first lines>
allows: <count> (<list or none>)
end-of-delivery
```
