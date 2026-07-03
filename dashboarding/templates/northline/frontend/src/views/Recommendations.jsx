import { useState } from "react";
import { Panel, LoadingBlock } from "../components/ui.jsx";
import BusMark from "../components/BusMark.jsx";
import { ToolStep } from "../components/ChatPanel.jsx";
import { readSse } from "../lib/sse.js";

/* Split the analyst's numbered list into cards once the stream completes.
   Anchored on the priority tag so stray preamble or missing newlines cannot
   break the split. */
function parseRecommendations(text) {
  const items = text
    .split(/(?=\d+\.\s*\[(?:CRITICAL|NORMAL)\])/i)
    .filter((s) => /^\d+\.\s*\[(?:CRITICAL|NORMAL)\]/i.test(s.trim()));
  return items.map((raw) => {
    const critical = /\[CRITICAL\]/i.test(raw);
    const body = raw.replace(/^\d+\.\s*/, "").replace(/\[(CRITICAL|NORMAL)\]\s*/i, "").trim();
    const [action, ...rest] = body.split("\n");
    return { critical, action: action.trim(), why: rest.join(" ").trim() };
  });
}

export default function Recommendations() {
  const [text, setText] = useState("");
  const [steps, setSteps] = useState([]);
  const [state, setState] = useState("idle"); // idle | running | done | error

  async function generate() {
    setText("");
    setSteps([]);
    setState("running");
    try {
      let acc = "";
      await readSse("/api/recommendations", {}, (ev) => {
        if (ev.type === "delta") {
          acc += ev.text;
          setText(acc);
        } else if (ev.type === "tool") setSteps((s) => [...s, ev]);
        else if (ev.type === "error") {
          acc = acc || ev.message;
          setText(acc);
        }
      });
      setState("done");
    } catch (e) {
      setText(`The analyst is unavailable: ${e.message}`);
      setState("error");
    }
  }

  const cards = state === "done" ? parseRecommendations(text) : [];
  const tail = state === "done" ? text.split("\n").filter((l) => l.trim() && !/^\d+\./.test(l.trim()) && !cards.some((c) => l.includes(c.action))).slice(-1)[0] : null;

  return (
    <div className="stagger space-y-4">
      <section className="flex items-end justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">
            The analyst turns the inventory position into a priced order list
          </h1>
          <p className="mt-0.5 text-xs text-muted">
            Generated live from the same tools the chat uses; every call is shown below the list.
          </p>
        </div>
        <button
          onClick={generate}
          disabled={state === "running"}
          className="btn-primary px-4 py-2 text-sm disabled:opacity-40"
        >
          {state === "running" ? "Working" : state === "idle" ? "Generate recommendations" : "Regenerate"}
        </button>
      </section>

      {state === "idle" && (
        <Panel>
          <div className="py-8 text-center">
            <BusMark size={92} />
            <p className="mt-3 text-sm text-muted">
              No recommendations yet. Generate them to get a prioritized order plan with
              quantities, suppliers, and the exposure each order removes.
            </p>
          </div>
        </Panel>
      )}

      {state === "running" && (
        <>
          {steps.map((s, i) => <ToolStep key={i} step={s} />)}
          {text ? (
            <Panel><p className="whitespace-pre-wrap text-sm text-ink/90">{text}</p></Panel>
          ) : (
            <LoadingBlock h="h-24" />
          )}
        </>
      )}

      {(state === "done" || state === "error") && (
        <>
          {cards.length > 0 ? (
            <div className="space-y-2">
              {cards.map((c, i) => (
                <div
                  key={i}
                  className={`rounded-md border border-edge border-l-2 bg-panel px-4 py-3 ${
                    c.critical ? "border-l-alert" : "border-l-muted"
                  }`}
                >
                  <div className="flex items-baseline gap-2">
                    <span className={`text-[10px] font-semibold uppercase tracking-wider ${c.critical ? "text-alert" : "text-muted"}`}>
                      {c.critical ? "Critical" : "Normal"}
                    </span>
                    <h3 className="text-sm font-medium">{c.action}</h3>
                  </div>
                  {c.why && <p className="mt-1 text-[13px] leading-relaxed text-ink/85">{c.why}</p>}
                </div>
              ))}
              {tail && <p className="px-1 text-sm text-muted">{tail}</p>}
            </div>
          ) : (
            <Panel><p className="whitespace-pre-wrap text-sm text-ink/90">{text}</p></Panel>
          )}
          {steps.length > 0 && (
            <details className="text-sm">
              <summary className="cursor-pointer text-xs text-muted">
                Show working ({steps.length} tool {steps.length === 1 ? "call" : "calls"})
              </summary>
              {steps.map((s, i) => <ToolStep key={i} step={s} />)}
            </details>
          )}
        </>
      )}
    </div>
  );
}
