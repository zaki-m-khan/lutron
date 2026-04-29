// Overview screen — KPI tiles, OTIF chart, 3 column widgets.
import React, { useEffect, useState } from 'react';
import { I } from './icons.jsx';
import { Btn, Card, Pill } from './shell.jsx';
import { Spark, OtifLine, HBar, RiskBar } from './charts.jsx';
import { getKpis, getOtifHistory, getTopAtRisk, getWorstPlants, getEscalations } from './api.js';

function KPITile({ k, loading }) {
  if (loading || !k) {
    return (
      <div className="bg-ink-700 border border-ink-500 rounded-md p-3">
        <div className="skeleton h-2.5 w-12 rounded" />
        <div className="skeleton h-7 w-20 mt-3 rounded" />
        <div className="flex items-end justify-between mt-3">
          <div className="skeleton h-6 w-24 rounded" />
          <div className="skeleton h-3 w-12 rounded" />
        </div>
      </div>
    );
  }
  const positive = k.inverse ? k.delta < 0 : k.delta > 0;
  const deltaColor = positive ? 'text-ok' : 'text-danger';
  const Arrow = k.delta > 0 ? I.ArrowUp : I.ArrowDown;
  const value = typeof k.value === 'number' ? (k.unit === '%' ? k.value.toFixed(1) : k.value) : k.value;
  return (
    <div className="bg-ink-700 border border-ink-500 rounded-md p-3 hover:border-ink-400 transition-colors">
      <div className="flex items-center justify-between">
        <div className="text-2xs caps text-fg-faint">{k.label}</div>
        <div className="text-2xs text-fg-faint tnum">
          target {k.target}
          {k.unit}
        </div>
      </div>
      <div className="mt-2 flex items-baseline gap-1.5">
        <div className="text-[28px] font-semibold tracking-tight tnum text-fg leading-none">{value}</div>
        <div className="text-base text-fg-muted">{k.unit}</div>
      </div>
      <div className="mt-2.5 flex items-end justify-between">
        <Spark data={k.spark} w={120} h={28} color="#9AA0AB" />
        <div className={`inline-flex items-center gap-0.5 text-xs tnum ${deltaColor}`}>
          <Arrow size={11} />
          {Math.abs(k.delta).toFixed(1)}
          {k.unit === '%' ? 'pp' : k.unit}
        </div>
      </div>
    </div>
  );
}

function AtRiskRow({ row, onAction }) {
  return (
    <div className="grid grid-cols-[100px_1fr_120px_110px_44px] items-center gap-3 px-3 py-2 border-t border-ink-500 hover:bg-ink-600/40 group cursor-pointer">
      <div className="font-mono text-xs text-fg">{row.id}</div>
      <div className="text-xs text-fg truncate">{row.product}</div>
      <div className="text-xs text-fg-muted truncate">{row.plant}</div>
      <RiskBar value={row.risk} />
      <div className="text-right">
        <button
          onClick={onAction}
          className="text-xs text-fg-muted group-hover:text-accent-hi inline-flex items-center gap-0.5 kbd-ring"
        >
          Open <I.ArrowUpRight size={10} />
        </button>
      </div>
    </div>
  );
}

function EscalationRow({ e }) {
  const tone = e.status === 'Investigating' ? 'warn' : e.status === 'Action Pending' ? 'danger' : 'ok';
  return (
    <div className="px-3 py-2 border-t border-ink-500 hover:bg-ink-600/40">
      <div className="flex items-center justify-between gap-2">
        <span className="font-mono text-2xs text-fg-muted">{e.id}</span>
        <Pill tone={tone} dot>
          {e.status}
        </Pill>
      </div>
      <div className="text-xs text-fg mt-1 truncate">{e.title}</div>
      <div className="mt-1 flex items-center justify-between text-2xs text-fg-faint">
        <span>{e.owner}</span>
        <span className="tnum">{e.age} open</span>
      </div>
    </div>
  );
}

export function Overview({ onToast, range }) {
  const [kpis, setKpis] = useState(null);
  const [history, setHistory] = useState(null);
  const [topRisk, setTopRisk] = useState(null);
  const [worstPlants, setWorstPlants] = useState(null);
  const [escalations, setEscalations] = useState(null);

  useEffect(() => {
    setKpis(null);
    getKpis(range).then(setKpis).catch(console.error);
  }, [range]);

  useEffect(() => {
    getOtifHistory().then(setHistory).catch(console.error);
    getTopAtRisk(5).then(setTopRisk).catch(console.error);
    getWorstPlants().then(setWorstPlants).catch(console.error);
    getEscalations().then(setEscalations).catch(console.error);
  }, []);

  return (
    <div className="px-5 py-4 space-y-4">
      <div className="grid grid-cols-4 gap-3">
        {(kpis ? [kpis.otif, kpis.onTime, kpis.leadTime, kpis.variance] : [null, null, null, null]).map((k, i) => (
          <KPITile key={i} k={k} loading={!k} />
        ))}
      </div>

      <Card
        title="OTIF — last 24 months"
        action={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-3 text-2xs text-fg-faint">
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-[2px] bg-accent" />
                OTIF
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-[2px] bg-fg-ghost" />
                Targets
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-[2px] bg-info" />
                99% benchmark
              </span>
            </div>
            <Btn kind="outline" size="xs" icon={I.ArrowUpRight}>
              Export
            </Btn>
          </div>
        }
      >
        {history ? <OtifLine data={history} /> : <div className="skeleton h-[240px] rounded" />}
      </Card>

      <div className="grid grid-cols-12 gap-3">
        <Card
          className="col-span-5"
          title="Top at-risk orders right now"
          action={
            <Btn kind="ghost" size="xs">
              View all <I.ChevronRight size={11} />
            </Btn>
          }
          pad={false}
        >
          <div className="grid grid-cols-[100px_1fr_120px_110px_44px] items-center gap-3 px-3 h-7 text-2xs caps text-fg-faint">
            <div>Order</div>
            <div>Product</div>
            <div>Plant</div>
            <div>Risk</div>
            <div className="text-right">—</div>
          </div>
          {(topRisk || []).map((r) => (
            <AtRiskRow key={r.id} row={r} onAction={() => onToast(`Opened ${r.id}`)} />
          ))}
          {!topRisk && <div className="skeleton h-32 m-3 rounded" />}
        </Card>

        <Card
          className="col-span-4"
          title="Worst-performing plants this week"
          action={<Pill tone="neutral">vs target 95%</Pill>}
        >
          {worstPlants ? <HBar data={worstPlants} /> : <div className="skeleton h-24 rounded" />}
          <div className="flex items-center gap-3 mt-3 pt-3 border-t border-ink-500 text-2xs text-fg-faint">
            <span className="inline-flex items-center gap-1">
              <span className="w-2 h-2 rounded-sm bg-danger" />
              &lt; 60%
            </span>
            <span className="inline-flex items-center gap-1">
              <span className="w-2 h-2 rounded-sm bg-warn" />
              60–75%
            </span>
            <span className="inline-flex items-center gap-1">
              <span className="w-2 h-2 rounded-sm bg-ok" />
              &gt; 75%
            </span>
          </div>
        </Card>

        <Card
          className="col-span-3"
          title="Open escalations"
          action={<Pill tone="accent">{escalations ? escalations.length : '…'}</Pill>}
          pad={false}
        >
          {(escalations || []).map((e) => (
            <EscalationRow key={e.id} e={e} />
          ))}
          {!escalations && <div className="skeleton h-32 m-3 rounded" />}
        </Card>
      </div>
    </div>
  );
}
