import { useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar.jsx";
import ChatDock from "./components/ChatDock.jsx";
import { ToastProvider } from "./components/Toast.jsx";
import { DrawerProvider } from "./components/Drawer.jsx";
import CommandPalette from "./components/CommandPalette.jsx";
import Ticker from "./components/Ticker.jsx";
import Overview from "./views/Overview.jsx";
import Suppliers from "./views/Suppliers.jsx";
import ProductionPlan from "./views/ProductionPlan.jsx";
import DemandForecast from "./views/DemandForecast.jsx";
import InventoryHealth from "./views/InventoryHealth.jsx";
import Recommendations from "./views/Recommendations.jsx";
import WhatIf from "./views/WhatIf.jsx";
import AgentHub from "./views/AgentHub.jsx";

function usePins() {
  const [pins, setPins] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem("northline-pins") || "[]");
    } catch {
      return [];
    }
  });
  const save = (next) => {
    setPins(next);
    localStorage.setItem("northline-pins", JSON.stringify(next));
  };
  return {
    pins,
    pin: (a) => save([...pins, { ...a, pinnedAt: new Date().toISOString() }]),
    unpin: (i) => save(pins.filter((_, j) => j !== i)),
  };
}

function useTheme() {
  // Light is the client-facing default; the toggle persists per browser.
  // ?theme=dark|light overrides for demos and screenshots.
  const [theme, setTheme] = useState(() => {
    const fromUrl = new URLSearchParams(location.search).get("theme");
    return fromUrl || localStorage.getItem("northline-theme") || "light";
  });
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("northline-theme", theme);
  }, [theme]);
  return [theme, setTheme];
}

function TopBar({ kpis, theme, setTheme }) {
  return (
    <header className="flex items-center justify-between px-6 pt-4 pb-1">
      <div className="text-sm text-muted">
        {kpis
          ? `${kpis.skus_tracked} components tracked · ${kpis.critical} critical · ${kpis.warning} warning`
          : "loading"}
      </div>
      <div className="flex items-center gap-4 text-xs text-muted">
        {kpis && kpis.critical > 0 && (
          <span className="flex items-center gap-1.5 text-alert">
            <span className="anim-breathe inline-block h-1.5 w-1.5 rounded-full bg-alert" />
            Attention needed
          </span>
        )}
        <span>{kpis ? `as of ${kpis.as_of}` : ""}</span>
        <span className="hidden rounded border border-edge px-1.5 py-0.5 font-mono text-[10px] lg:inline">
          {navigator.platform?.includes("Mac") ? "\u2318" : "Ctrl+"}K
        </span>
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="rounded border border-edge px-2 py-1 hover:border-accent/60"
        >
          {theme === "dark" ? "Light" : "Dark"} mode
        </button>
      </div>
    </header>
  );
}

export default function App() {
  const { pins, pin, unpin } = usePins();
  const [theme, setTheme] = useTheme();
  const [kpis, setKpis] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/api/kpis")
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setKpis)
      .catch(() => setError("Could not reach the backend. Is uvicorn running on :8000?"));
  }, []);

  return (
    <BrowserRouter>
      <ToastProvider>
      <DrawerProvider>
      <CommandPalette theme={theme} setTheme={setTheme} />
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar kpis={kpis} theme={theme} setTheme={setTheme} />
          <Ticker />
          <main className="min-h-0 flex-1 overflow-y-auto px-6 py-5 pb-24">
            {error ? (
              <p className="text-sm text-muted">
                {error}{" "}
                <button className="underline" onClick={() => location.reload()}>
                  Retry
                </button>
              </p>
            ) : (
              <Routes>
                <Route path="/" element={<Overview kpis={kpis} />} />
                <Route path="/demand" element={<DemandForecast />} />
                <Route path="/inventory" element={<InventoryHealth />} />
                <Route path="/suppliers" element={<Suppliers />} />
                <Route path="/production" element={<ProductionPlan />} />
                <Route path="/recommendations" element={<Recommendations />} />
                <Route path="/whatif" element={<WhatIf />} />
                <Route
                  path="/agents"
                  element={<AgentHub pins={pins} pin={pin} unpin={unpin} />}
                />
              </Routes>
            )}
          </main>
        </div>
      </div>
      <ChatDock onPin={pin} />
      </DrawerProvider>
      </ToastProvider>
    </BrowserRouter>
  );
}
