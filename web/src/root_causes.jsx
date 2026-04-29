// Root Causes — Pareto, heatmap, monthly trend with annotations.
import React, { useEffect, useState, useMemo } from 'react';
import { I } from './icons.jsx';
import { Btn, Card } from './shell.jsx';
import { Pareto, Heatmap, TrendLine } from './charts.jsx';
import { getPareto, getHeatmap, getTrend } from './api.js';

function paretoHeadline(data) {
  if (!data || data.length === 0) return 'Loading factor analysis…';
  const total = data.reduce((s, d) => s + d.count, 0);
  if (total === 0) return 'No late deliveries in the selected window';
  let cum = 0;
  for (let i = 0; i < data.length; i++) {
    cum += data[i].count;
    if (cum / total >= 0.8) {
      const n = i + 1;
      return `${n} factor${n === 1 ? '' : 's'} explain 80% of late deliveries`;
    }
  }
  return `${data.length} factors explain late deliveries`;
}

function heatmapStats(hm) {
  if (!hm || !hm.m || hm.m.length === 0) {
    return { worst: null, best: null, median: null, count: 0 };
  }
  const cells = [];
  hm.m.forEach((row, i) => {
    row.forEach((v, j) => {
      cells.push({ v, plant: hm.y[i], product: hm.x[j] });
    });
  });
  const sorted = [...cells].sort((a, b) => a.v - b.v);
  const median = sorted[Math.floor(sorted.length / 2)];
  return {
    worst: sorted[sorted.length - 1],
    best: sorted[0],
    median,
    count: cells.length,
  };
}

export function RootCauses() {
  const [pareto, setPareto] = useState(null);
  const [heatmap, setHeatmap] = useState(null);
  const [trend, setTrend] = useState(null);

  useEffect(() => {
    getPareto().then(setPareto).catch(console.error);
    getHeatmap().then(setHeatmap).catch(console.error);
    getTrend().then(setTrend).catch(console.error);
  }, []);

  const headline = useMemo(() => paretoHeadline(pareto), [pareto]);
  const stats = useMemo(() => heatmapStats(heatmap), [heatmap]);

  return (
    <div className="px-5 py-4 space-y-4">
      <Card
        title={headline}
        action={
          <div className="flex items-center gap-3">
            <div className="text-2xs text-fg-faint flex items-center gap-3">
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-2 bg-accent rounded-sm" />
                Within 80%
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="w-2 h-2 bg-fg-ghost rounded-sm" />
                Tail
              </span>
              <span className="inline-flex items-center gap-1">
                <span className="w-3 h-[2px] bg-fg" />
                Cumulative
              </span>
            </div>
            <Btn kind="outline" size="xs">
              Last 90 days <I.ChevronDown size={10} />
            </Btn>
          </div>
        }
      >
        {pareto ? <Pareto data={pareto} /> : <div className="skeleton h-[260px] rounded" />}
      </Card>

      <Card
        title="Late-rate heatmap — Plant × Product Line"
        action={
          <div className="flex items-center gap-2 text-2xs text-fg-faint">
            <span>0%</span>
            <span
              className="inline-block w-32 h-2 rounded-sm"
              style={{ background: 'linear-gradient(90deg, #1A1D24 0%, #C9892D 50%, #E5484D 100%)' }}
            />
            <span>50%+</span>
          </div>
        }
      >
        {heatmap ? (
          <Heatmap x={heatmap.x} y={heatmap.y} m={heatmap.m} />
        ) : (
          <div className="skeleton h-[180px] rounded" />
        )}
        <div className="mt-3 pt-3 border-t border-ink-500 grid grid-cols-3 gap-3 text-xs">
          <div>
            <div className="text-2xs caps text-fg-faint">Worst cell</div>
            <div className="text-fg mt-0.5">
              {stats.worst ? (
                <>
                  {stats.worst.plant} × {stats.worst.product} —{' '}
                  <span className="tnum text-danger">{stats.worst.v}%</span> late
                </>
              ) : (
                '—'
              )}
            </div>
          </div>
          <div>
            <div className="text-2xs caps text-fg-faint">Best cell</div>
            <div className="text-fg mt-0.5">
              {stats.best ? (
                <>
                  {stats.best.plant} × {stats.best.product} —{' '}
                  <span className="tnum text-ok">{stats.best.v}%</span> late
                </>
              ) : (
                '—'
              )}
            </div>
          </div>
          <div>
            <div className="text-2xs caps text-fg-faint">Median</div>
            <div className="text-fg mt-0.5">
              {stats.median ? (
                <>
                  <span className="tnum">{stats.median.v}%</span> late across {stats.count} cells
                </>
              ) : (
                '—'
              )}
            </div>
          </div>
        </div>
      </Card>

      <Card
        title="Monthly OTIF trend — annotated"
        action={
          <Btn kind="outline" size="xs" icon={I.Calendar}>
            16 months
          </Btn>
        }
      >
        {trend ? <TrendLine data={trend} /> : <div className="skeleton h-[240px] rounded" />}
      </Card>
    </div>
  );
}
