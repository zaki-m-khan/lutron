// App entry — sidebar/topbar/screen switcher + toast. No demo-state panel.
import React, { useEffect, useState } from 'react';
import { I } from './icons.jsx';
import { Sidebar, TopBar } from './shell.jsx';
import { Overview } from './overview.jsx';
import { RiskQueue } from './risk_queue.jsx';
import { RootCauses } from './root_causes.jsx';
import { DataPreview } from './data_preview.jsx';
import { getRiskSummary, getEscalations } from './api.js';

function Toast({ msg, onClose }) {
  useEffect(() => {
    if (!msg) return;
    const t = setTimeout(onClose, 3200);
    return () => clearTimeout(t);
  }, [msg, onClose]);
  if (!msg) return null;
  return (
    <div className="fixed bottom-4 right-4 z-50 toast-in">
      <div className="flex items-center gap-2 bg-ink-700 border border-ink-400 rounded-md px-3 h-9 shadow-lg">
        <div className="w-5 h-5 rounded-full bg-ok/20 grid place-items-center">
          <I.Check size={12} className="text-ok" />
        </div>
        <span className="text-sm text-fg">{msg}</span>
        <button onClick={onClose} className="ml-2 text-fg-faint hover:text-fg kbd-ring rounded">
          <I.X size={11} />
        </button>
      </div>
    </div>
  );
}

function PlaceholderScreen({ title }) {
  return (
    <div className="px-5 py-12 grid place-items-center text-center">
      <div className="text-md text-fg">{title}</div>
      <div className="text-xs text-fg-muted mt-1 max-w-[420px]">
        Reserved for a later milestone — wired into navigation only. The current build covers Overview,
        Risk Queue, and Root Causes.
      </div>
    </div>
  );
}

export default function App() {
  const [screen, setScreen] = useState('overview');
  const [range, setRange] = useState('Quarter');
  const [toast, setToast] = useState(null);
  const [openCount, setOpenCount] = useState(null);
  const [escCount, setEscCount] = useState(null);

  const refreshOpenCount = () => {
    getRiskSummary()
      .then((s) => setOpenCount(s.open))
      .catch(console.error);
  };

  useEffect(() => {
    refreshOpenCount();
    getEscalations()
      .then((e) => setEscCount(e.length))
      .catch(console.error);
  }, []);

  const showToast = (msg) => setToast(msg);

  return (
    <div className="h-screen flex flex-col bg-ink-900 text-fg overflow-hidden">
      <div className="flex flex-1 min-h-0">
        <Sidebar screen={screen} setScreen={setScreen} openCount={openCount} escCount={escCount} />
        <div className="flex-1 flex flex-col min-w-0">
          <TopBar screen={screen} range={range} setRange={setRange} />
          <main className="flex-1 overflow-y-auto scroll-thin" data-screen-label={screen}>
            {screen === 'overview' && <Overview onToast={showToast} range={range} />}
            {screen === 'risk' && <RiskQueue onToast={showToast} onActioned={refreshOpenCount} />}
            {screen === 'root' && <RootCauses />}
            {screen === 'data' && <DataPreview />}
            {screen === 'esc' && <PlaceholderScreen title="Escalations" />}
            {screen === 'settings' && <PlaceholderScreen title="Settings" />}
          </main>
        </div>
      </div>
      <Toast msg={toast} onClose={() => setToast(null)} />
    </div>
  );
}
