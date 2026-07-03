import { useState } from "react";
import ChatPanel from "./ChatPanel.jsx";

export default function ChatDock({ onPin }) {
  const [open, setOpen] = useState(false);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="btn-primary fixed bottom-5 right-5 rounded-full px-4 py-2 text-sm"
      >
        Ask the analyst
      </button>
    );
  }

  return (
    <div className="fixed bottom-5 right-5 z-20 flex h-[70vh] w-[400px] flex-col rounded-md border border-edge bg-panel shadow-lg">
      <div className="flex items-center justify-between border-b border-edge px-3 py-2">
        <span className="text-sm font-medium">Coachworks analyst</span>
        <button className="text-xs text-muted hover:text-ink" onClick={() => setOpen(false)}>
          Close
        </button>
      </div>
      <ChatPanel onPin={onPin} />
    </div>
  );
}
