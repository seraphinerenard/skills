---
name: daemon-ops
description: |
  Long-running and scheduled jobs done right: launchd on macOS, systemd on Linux,
  with health checks and the house alerting doctrine. Trigger on: "run this on
  a schedule", "keep this running", "launchd", "systemd unit", "daemonize this",
  "cron this", "/daemon-ops". Begin at GATE DO-1 of THE CONTRACT: the job card comes
  before any unit file. Units are linted (plutil -lint, systemd-analyze verify) and
  one healthy cycle is shown in the logs before the job is called installed.
---

# Daemon ops

A daemon that fails does it silently at 03:00, and a daemon that alerts badly trains its owner to ignore the phone. The recurring failures are path assumptions (launchd reads no shell profile), secrets pasted into unit files, jobs with no heartbeat so "running" and "wedged" look identical, and template alert texts that turn signal into spam. Every gate below closes one of those.

Set `SKILL_DIR=$HOME/.claude/skills/daemon-ops` (fallback: `/path/to/skills/daemon-ops`).

## Scope gate

IF the request edits one value in an existing installed unit (schedule, argument, path): make the edit, re-lint it, reload it, paste one healthy cycle from the logs, stop. ELSE: run the full contract.

## The contract

Do the phases in order. Each ends with its REQUIRED ARTIFACT.

| Phase | Work | REQUIRED ARTIFACT | Exit check |
|---|---|---|---|
| **GATE DO-1** | Fill the job card: what runs, cadence, host, owner, blast radius | DO-1 job card | Card printed; host row cited from the host table; no `<`, `TODO`, `TBD` |
| **GATE DO-2** | Write the unit from the matching template below (copy, then edit values) | The plist or unit file on disk | Every path absolute; no secrets in the file; env file mode 600 |
| **GATE DO-3** | Design health: the heartbeat the job writes, the check that reads it, log rotation | The runbook table (template below) | Heartbeat staleness threshold stated as 2x the expected interval |
| **GATE DO-4** | Install and verify with the exact host commands below | Pasted lint output, load output, and a log tail showing one healthy cycle | All three outputs are tool results |
| **GATE DO-5** | Wire alerting per the house doctrine below | The alerting row of the runbook: what events queue, who composes, the daily budget | No template strings addressed to the phone anywhere in the code |
| **GATE DO-6** | Deliver | DELIVERY block | Runbook passes the sweep; proof lines pasted |

Restated because they are the three most-violated rules, binding during DO-2 and DO-5: absolute paths everywhere, launchd provides no shell PATH (DO1); secrets live in an env file with 600 permissions, never in the unit (DO2); phone-bound alerts are LLM-composed prose, never template strings (DO6).

## Values

Host table (the DO-1 card cites one row):

| Host | Manager | Unit lives at | Logs |
|---|---|---|---|
| mac | launchd (gui domain) | ~/Library/LaunchAgents/com.<user>.<name>.plist | ~/Library/Logs/<name>/out.log and err.log |
| ec2 | systemd | /etc/systemd/system/<name>.service (+ .timer when scheduled) | journald via `journalctl -u <name>` |
| ELSE | ask the user which host owns the job, then stop | | |

launchd template (always-on shown; scheduled swaps the KeepAlive block for StartCalendarInterval). Substitute the uppercase placeholders before installing: launchd expands neither `~` nor `$HOME` inside a plist, so PROJECT_DIR and LOG_DIR are written out as full absolute paths.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.example.NAME</string>
  <key>ProgramArguments</key><array>
    <string>/usr/bin/python3</string>
    <string>PROJECT_DIR/run.py</string>
  </array>
  <key>WorkingDirectory</key><string>PROJECT_DIR</string>
  <key>RunAtLoad</key><true/>
  <key>KeepAlive</key><dict><key>SuccessfulExit</key><false/></dict>
  <!-- scheduled variant instead of KeepAlive:
  <key>StartCalendarInterval</key><dict>
    <key>Hour</key><integer>6</integer><key>Minute</key><integer>30</integer>
  </dict> -->
  <key>ThrottleInterval</key><integer>30</integer>
  <key>StandardOutPath</key><string>LOG_DIR/NAME/out.log</string>
  <key>StandardErrorPath</key><string>LOG_DIR/NAME/err.log</string>
  <key>EnvironmentVariables</key><dict>
    <key>PATH</key><string>/usr/local/bin:/usr/bin:/bin</string>
  </dict>
</dict></plist>
```

systemd templates:

```ini
# /etc/systemd/system/NAME.service
[Unit]
Description=NAME
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/PROJECT
EnvironmentFile=/home/ubuntu/PROJECT/.env
ExecStart=/usr/bin/python3 /home/ubuntu/PROJECT/run.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target

# /etc/systemd/system/NAME.timer (scheduled jobs; the service then omits [Install])
[Unit]
Description=NAME schedule
[Timer]
OnCalendar=*-*-* 06:30:00
Persistent=true
[Install]
WantedBy=timers.target
```

Health numbers: the job touches its heartbeat (a file mtime or a DB row with a UTC timestamp) once per cycle; the health check reads it and alarms when staleness exceeds 2x the expected interval (minimum 120 s). Logs are size-capped: rotate daily or at 10 MB, whichever comes first, keep 7 rotations.

Alerting doctrine (the house rule): messages that reach the phone are LLM-composed prose, composed from evidence, never deterministic template strings. The daemon's job is to append structured events (UTC timestamp, event type, evidence path, numbers) to its log or queue; an LLM session reads that and composes any phone-bound message. Exception: the user's own position, order, and ticket events notify directly. Default alert budget: 2 composed messages per job per day; past the budget, events accumulate silently for the next composed digest. Every alert names the evidence path it was composed from.

Verify commands, pasted at GATE DO-4:

| Host | Commands |
|---|---|
| mac | `plutil -lint <plist>` then `launchctl bootstrap gui/$(id -u) <plist>` then `launchctl kickstart -k gui/$(id -u)/com.example.NAME` then `tail -20 ~/Library/Logs/NAME/out.log` |
| ec2 | `systemd-analyze verify NAME.service` then `sudo systemctl daemon-reload` then `sudo systemctl enable --now NAME` then `systemctl status NAME | head -12` and `journalctl -u NAME -n 20` |
| ELSE | the host table already stopped you at DO-1 |

## Artifact templates

```gate-card
GATE DO-1 - job card
job: <what runs, one sentence>
cadence: <always-on | schedule, stated>
host: <mac | ec2>    [row: "<the host-table row, pasted verbatim>"]
owner: <who gets the alerts>
blast radius: <what breaks or goes stale when this job dies>
end-of-card
```

Runbook table (GATE DO-3 artifact, one row per job):

```markdown
| unit | start / stop | logs | health command | heartbeat threshold | alerts | owner |
| com.example.NAME | launchctl kickstart -k gui/$(id -u)/com.example.NAME / launchctl bootout gui/$(id -u)/com.example.NAME | ~/Library/Logs/NAME/ | python3 check_heartbeat.py NAME | 2x 300s | queue -> composed digest, budget 2/day | OWNER |
```

### Inlined from writing-instructions (full skill wins on conflict)

The runbook and every composed alert use plain sentences: no em dashes, no emoji, numbers with units and baselines, Canadian spelling (behaviour, colour). Alert prose names what happened, the evidence path, and the one action.

## Rules

| ID | Rule |
|---|---|
| DO1 | Every path in a unit is absolute; launchd jobs never assume a shell PATH beyond the EnvironmentVariables block. |
| DO2 | Secrets live in an env file with mode 600 referenced by the unit (EnvironmentFile on systemd; sourced by the wrapped script on launchd); no secret appears in a unit file, a log, or a runbook. |
| DO3 | One job, one unit, one Label; a pipeline of steps is one wrapper script, not three units racing. |
| DO4 | Every always-on job writes a heartbeat; a job without a heartbeat is not installed, it is abandoned. |
| DO5 | Logs are capped (10 MB or daily, keep 7); an unbounded log file is a disk-full incident on a timer. |
| DO6 | No deterministic template strings addressed to the phone; events queue, an LLM composes, the budget binds. Position, order, and ticket events from the user's own systems are the stated exception. |
| DO7 | A unit change is verified by reload plus one observed healthy cycle in the logs, never by "it loaded". |
| DO8 | ELSE: a situation these rules do not cover gets stated in the runbook and taken to the user. |

## Checks

```
plutil -lint <plist>                      (mac units)
systemd-analyze verify <unit>             (ec2 units)
python3 $HOME/.claude/skills/writing-instructions/scripts/sweep.py <runbook.md>
```

All applicable commands MUST run as tool results at GATE DO-4/DO-6, outputs pasted. A lint failure blocks install; a missing linter on the target host is recorded in the runbook, never skipped silently.

## Delivery block

```delivery-block
DELIVERY daemon-ops
files:
  <unit path>  (<size> B)
  <runbook path>  (<size> B)
gates: <DO-1..DO-6 status, skips recorded>
checks:
  <lint output, first line>
  <load command output>
  <log tail line proving one healthy cycle>
  <sweep proof line on the runbook>
allows: <count> (<list or none>)
end-of-delivery
```
