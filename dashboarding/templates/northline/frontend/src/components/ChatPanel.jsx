import { useRef, useState } from "react";
import { readSse } from "../lib/sse.js";

export function ToolStep({ step }) {
  return (
    <details className="my-1 rounded border border-edge bg-bg px-2 py-1">
      <summary className="cursor-pointer text-[11px] text-muted">
        {step.name} — {step.summary}
      </summary>
      <pre className="mt-1 overflow-x-auto text-[11px] text-muted">
        {JSON.stringify(step.input, null, 2)}
      </pre>
    </details>
  );
}

/* The analyst conversation: streaming transcript, visible tool steps, pin action.
   Used small in the corner dock and full-size in the Agent Hub. */
export default function ChatPanel({ onPin, suggestions = [], placeholder = "Ask a question" }) {
  const [items, setItems] = useState([]); // {role, text, steps}
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const scrollRef = useRef(null);

  async function send(text) {
    const question = (text ?? input).trim();
    if (!question || busy) return;
    setInput("");
    setBusy(true);

    const history = items
      .filter((m) => m.text)
      .map((m) => ({ role: m.role, content: m.text }));
    setItems((cur) => [
      ...cur,
      { role: "user", text: question },
      { role: "assistant", text: "", steps: [] },
    ]);

    const update = (fn) =>
      setItems((cur) => {
        const copy = [...cur];
        copy[copy.length - 1] = fn({ ...copy[copy.length - 1] });
        return copy;
      });

    try {
      await readSse(
        "/api/chat",
        { messages: [...history, { role: "user", content: question }] },
        (ev) => {
          if (ev.type === "delta") update((m) => ({ ...m, text: m.text + ev.text }));
          else if (ev.type === "tool") update((m) => ({ ...m, steps: [...m.steps, ev] }));
          else if (ev.type === "error") update((m) => ({ ...m, text: m.text || ev.message }));
          scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
        },
      );
    } catch (e) {
      update((m) => ({ ...m, text: m.text || `The analyst is unavailable: ${e.message}` }));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="flex h-full min-h-0 flex-col">
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2">
        {items.length === 0 && (
          <div className="py-4">
            <p className="text-sm text-muted">
              Ask about demand, stock cover, suppliers, or what to order.
            </p>
            {suggestions.length > 0 && (
              <div className="mt-3 flex flex-wrap gap-2">
                {suggestions.map((s) => (
                  <button
                    key={s}
                    onClick={() => send(s)}
                    className="rounded border border-edge px-2 py-1 text-left text-xs text-ink/80 hover:border-accent/60"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}
        {items.map((m, i) => (
          <div key={i} className="mb-3">
            {m.role === "user" ? (
              <p className="rounded bg-ink/[0.06] px-2 py-1.5 text-sm">{m.text}</p>
            ) : (
              <div>
                {m.steps?.map((s, j) => <ToolStep key={j} step={s} />)}
                {m.text ? (
                  <p className="whitespace-pre-wrap text-sm text-ink/90">{m.text}</p>
                ) : (
                  busy && i === items.length - 1 && <p className="text-xs text-muted">thinking</p>
                )}
                {m.text && !busy && onPin && (
                  <button
                    className="mt-1 text-xs text-accent hover:underline"
                    onClick={() =>
                      onPin({ question: items[i - 1]?.text ?? "", answer: m.text, steps: m.steps })
                    }
                  >
                    Pin as panel
                  </button>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      <form
        className="flex gap-2 border-t border-edge p-2"
        onSubmit={(e) => {
          e.preventDefault();
          send();
        }}
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={busy ? "answering" : placeholder}
          disabled={busy}
          className="flex-1 rounded border border-edge bg-bg px-2 py-1.5 text-sm outline-none focus:border-accent/60"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="rounded border border-edge px-3 py-1.5 text-sm disabled:opacity-40"
        >
          Send
        </button>
      </form>
    </div>
  );
}
