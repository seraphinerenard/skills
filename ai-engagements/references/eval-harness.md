# The eval harness

Copy this file's code into the engagement repo as `eval_harness.py`, replace `system_under_test` with a call into the real system, and run it on every change. It is stdlib-only Python 3.10+, so it runs before the project has dependencies, and the LLM judge is mocked by default so the harness executes without an API key.

## Case format

Cases live in a JSONL file, one per line, frozen and versioned with the repo. Three kinds:

```json
{"id": "c01", "kind": "exact",  "input": "Route claim 4471: hail damage, $2,300, no injury", "expected": "auto-approve"}
{"id": "c02", "kind": "rubric", "input": "Summarize policy P-88 exclusions", "must_include": ["flood", "wear and tear"], "must_not_include": ["covered for flood"]}
{"id": "c03", "kind": "judge",  "input": "Explain why claim 5512 was denied", "rubric": "States the denial reason from the file, cites the policy clause, invents no figures"}
```

Sizing guidance: 20 cases proves feasibility, 100 tunes prompts and retrieval, 300+ gates regressions with enough resolution that a 2-point move is signal. Sample real inputs, include the ugly ones, and get the client to sign the expected outputs.

## The harness

```python
"""eval_harness.py — minimal engagement eval harness. Stdlib only, Python 3.10+.

Usage:
  python eval_harness.py cases.jsonl                 # run and print scorecard
  python eval_harness.py cases.jsonl --gate baseline.json   # fail if score drops
"""
import json
import re
import sys
from pathlib import Path


# --- 1. The system under test -------------------------------------------------
# Replace this with a call into the real pipeline (API call, function, CLI).
def system_under_test(case_input: str) -> str:
    raise NotImplementedError("wire this to the real system")


# --- 2. The LLM judge (MOCKED by default) --------------------------------------
# The mock scores by rubric-keyword overlap so the harness runs with no API key.
# For a real judge, call Claude with the rubric and answer and parse a PASS/FAIL —
# model choice and pricing per the claude-api skill. Keep the judge model FIXED
# for the life of the eval set; changing the judge changes the ruler.
def llm_judge(case_input: str, answer: str, rubric: str) -> bool:
    words = re.findall(r"[a-z]+", rubric.lower())
    keywords = [w for w in words if len(w) > 4]
    hits = sum(1 for w in keywords if w in re.findall(r"[a-z]+", answer.lower()))
    return hits >= max(1, len(keywords) // 3)


# --- 3. Scoring ----------------------------------------------------------------
def score_case(case: dict, answer: str) -> bool:
    if case["kind"] == "exact":
        return answer.strip().lower() == case["expected"].strip().lower()
    if case["kind"] == "rubric":
        text = answer.lower()
        wanted = all(k.lower() in text for k in case.get("must_include", []))
        banned = any(k.lower() in text for k in case.get("must_not_include", []))
        return wanted and not banned
    if case["kind"] == "judge":
        return llm_judge(case["input"], answer, case["rubric"])
    raise ValueError(f"unknown kind {case['kind']!r} in case {case['id']}")


def run(cases_path: str) -> dict:
    cases = [json.loads(l) for l in Path(cases_path).read_text().splitlines() if l.strip()]
    results, by_kind = [], {}
    for case in cases:
        try:
            answer = system_under_test(case["input"])
            passed = score_case(case, answer)
        except Exception as e:                      # a crash is a fail, never a skip
            answer, passed = f"<error: {e}>", False
        results.append({"id": case["id"], "kind": case["kind"], "pass": passed})
        agg = by_kind.setdefault(case["kind"], [0, 0])
        agg[0] += passed
        agg[1] += 1
    overall = sum(r["pass"] for r in results) / len(results)
    return {"overall": overall, "by_kind": by_kind, "results": results}


def print_scorecard(report: dict) -> None:
    print(f"\noverall: {report['overall']:.0%} ({sum(r['pass'] for r in report['results'])}"
          f"/{len(report['results'])})")
    for kind, (p, n) in sorted(report["by_kind"].items()):
        print(f"  {kind:<8} {p}/{n}")
    for r in report["results"]:
        if not r["pass"]:
            print(f"  FAIL {r['id']} ({r['kind']})")


if __name__ == "__main__":
    report = run(sys.argv[1])
    print_scorecard(report)
    if "--gate" in sys.argv:                        # regression gate
        baseline_path = sys.argv[sys.argv.index("--gate") + 1]
        baseline = json.loads(Path(baseline_path).read_text())["overall"]
        if report["overall"] < baseline - 0.02:     # 2-point tolerance
            print(f"REGRESSION: {report['overall']:.0%} < baseline {baseline:.0%}")
            sys.exit(1)
    Path("last_run.json").write_text(json.dumps(report, indent=2))
```

## Regression gating

Every change to the system — prompt edit, retrieval tweak, model swap, tool change — reruns the harness before it merges. The rule is mechanical:

1. After the first accepted run, copy `last_run.json` to `baseline.json` and commit both.
2. CI runs `python eval_harness.py cases.jsonl --gate baseline.json`; a score more than 2 points under baseline fails the build.
3. When a change raises the score, the new `last_run.json` becomes the new committed baseline in the same PR.
4. The eval set itself only grows; existing cases never get edited to make a failing system pass. A wrong case gets deleted with a note, never adjusted.

Two habits keep the numbers honest. Freeze the judge model and its prompt for the life of the eval set, because a new judge is a new ruler and every historical score stops being comparable. And report the client-facing number from this harness and nowhere else, so "how is it doing" always has one answer.
