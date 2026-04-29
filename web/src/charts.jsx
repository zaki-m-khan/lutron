// Inline SVG charts. Restrained: thin lines, no fills, tiny ticks.
import React from 'react';

export function Spark({ data, w = 100, h = 28, color = '#9AA0AB' }) {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data),
    max = Math.max(...data);
  const span = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * (w - 2) + 1;
    const y = h - 1 - ((v - min) / span) * (h - 2);
    return [x, y];
  });
  const d = pts.map((p, i) => (i === 0 ? `M${p[0]},${p[1]}` : `L${p[0]},${p[1]}`)).join(' ');
  return (
    <svg width={w} height={h} className="overflow-visible">
      <path d={d} fill="none" stroke={color} strokeWidth="1.25" />
      <circle cx={pts[pts.length - 1][0]} cy={pts[pts.length - 1][1]} r="1.8" fill={color} />
    </svg>
  );
}

export function OtifLine({ data, w = 1080, h = 240 }) {
  if (!data || !data.length) return null;
  const pad = { l: 40, r: 24, t: 18, b: 28 };
  const innerW = w - pad.l - pad.r;
  const innerH = h - pad.t - pad.b;
  const yMin = 50,
    yMax = 100;
  const x = (i) => pad.l + (i / (data.length - 1)) * innerW;
  const y = (v) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * innerH;

  const path = data.map((p, i) => (i === 0 ? `M${x(i)},${y(p.v)}` : `L${x(i)},${y(p.v)}`)).join(' ');

  const targets = [
    { v: 90, label: '90% target', color: '#363B45', dash: '3 3' },
    { v: 95, label: '95% target', color: '#363B45', dash: '3 3' },
    { v: 97.5, label: '97.5% target', color: '#363B45', dash: '3 3' },
    { v: 99, label: '99% benchmark', color: '#5B8DEF', dash: '2 4' },
  ];
  const yTicks = [50, 60, 70, 80, 90, 100];

  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      {yTicks.map((t) => (
        <g key={t}>
          <line x1={pad.l} x2={w - pad.r} y1={y(t)} y2={y(t)} stroke="#1A1D24" strokeWidth="1" />
          <text x={pad.l - 8} y={y(t) + 3} fontSize="10" textAnchor="end" fill="#646A75" className="tnum">
            {t}
          </text>
        </g>
      ))}
      {targets.map((t) => (
        <g key={t.v}>
          <line x1={pad.l} x2={w - pad.r} y1={y(t.v)} y2={y(t.v)} stroke={t.color} strokeWidth="1" strokeDasharray={t.dash} />
          <text x={w - pad.r} y={y(t.v) - 4} fontSize="10" textAnchor="end" fill={t.v === 99 ? '#5B8DEF' : '#646A75'}>
            {t.label}
          </text>
        </g>
      ))}
      {data.map((p, i) =>
        i % 3 === 0 ? (
          <text key={i} x={x(i)} y={h - 8} fontSize="10" textAnchor="middle" fill="#646A75" className="tnum">
            {p.m}
          </text>
        ) : null,
      )}
      <path d={path} fill="none" stroke="#C9892D" strokeWidth="1.5" />
      {data.map((p, i) => (
        <circle key={i} cx={x(i)} cy={y(p.v)} r="1.6" fill="#C9892D" />
      ))}
      <g transform={`translate(${x(data.length - 1) + 6},${y(data[data.length - 1].v) - 7})`}>
        <rect width="46" height="18" rx="3" fill="#1A1D24" stroke="#262A33" />
        <text x="23" y="12" fontSize="10" textAnchor="middle" fill="#E0A14A" className="tnum">
          {data[data.length - 1].v.toFixed(1)}%
        </text>
      </g>
    </svg>
  );
}

export function HBar({ data, max = 100 }) {
  if (!data || !data.length) return null;
  const rowH = 26;
  const labelW = 110;
  const w = 320;
  const barAreaW = w - labelW - 44;
  return (
    <svg width="100%" viewBox={`0 0 ${w} ${data.length * rowH}`}>
      {data.map((d, i) => {
        const v = d.otif;
        const bw = (v / max) * barAreaW;
        const color = v < 60 ? '#E5484D' : v < 75 ? '#FFB224' : '#46A758';
        return (
          <g key={d.plant} transform={`translate(0, ${i * rowH})`}>
            <text x="0" y={rowH / 2 + 4} fontSize="11" fill="#9AA0AB">
              {d.plant}
            </text>
            <rect x={labelW} y={rowH / 2 - 5} width={barAreaW} height="10" fill="#14171D" />
            <rect x={labelW} y={rowH / 2 - 5} width={bw} height="10" fill={color} />
            <text x={labelW + barAreaW + 8} y={rowH / 2 + 4} fontSize="11" fill="#E6E8EC" className="tnum">
              {v.toFixed(1)}%
            </text>
          </g>
        );
      })}
    </svg>
  );
}

export function RiskBar({ value, w = 64 }) {
  const color = value >= 85 ? '#E5484D' : value >= 70 ? '#FFB224' : '#9AA0AB';
  return (
    <div className="flex items-center gap-2">
      <div className="h-1.5 rounded-sm overflow-hidden bg-ink-600" style={{ width: w }}>
        <div className="h-full" style={{ width: `${value}%`, background: color }} />
      </div>
      <span className="text-fg-muted tnum text-xs w-7 text-right">{value}</span>
    </div>
  );
}

export function FeatureBars({ data }) {
  if (!data || !data.length) return null;
  const max = Math.max(...data.map((d) => d.v));
  return (
    <div className="space-y-1.5">
      {data.map((d) => (
        <div key={d.name} className="grid grid-cols-[160px_1fr_36px] items-center gap-2">
          <div className="text-xs text-fg-muted truncate">{d.name}</div>
          <div className="h-1.5 bg-ink-600 rounded-sm overflow-hidden">
            <div className="h-full bg-accent" style={{ width: `${(d.v / max) * 100}%` }} />
          </div>
          <div className="text-xs tnum text-fg-muted text-right">{(d.v * 100).toFixed(0)}%</div>
        </div>
      ))}
    </div>
  );
}

export function Pareto({ data, w = 1080, h = 260 }) {
  if (!data || !data.length) return null;
  const pad = { l: 36, r: 56, t: 18, b: 50 };
  const innerW = w - pad.l - pad.r;
  const innerH = h - pad.t - pad.b;

  const total = data.reduce((s, d) => s + d.count, 0) || 1;
  const cum = [];
  let acc = 0;
  for (const d of data) {
    acc += d.count;
    cum.push(acc / total);
  }

  const maxCount = data[0].count || 1;
  const barW = (innerW / data.length) * 0.62;
  const step = innerW / data.length;
  const xCenter = (i) => pad.l + step * i + step / 2;
  const yBar = (c) => pad.t + (1 - c / maxCount) * innerH;
  const yCum = (p) => pad.t + (1 - p) * innerH;

  const cumPath = cum.map((p, i) => (i === 0 ? `M${xCenter(i)},${yCum(p)}` : `L${xCenter(i)},${yCum(p)}`)).join(' ');

  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`}>
      {[0, 0.25, 0.5, 0.75, 1].map((p) => (
        <g key={p}>
          <line x1={pad.l} x2={w - pad.r} y1={yCum(p)} y2={yCum(p)} stroke="#1A1D24" />
          <text x={pad.l - 6} y={yCum(p) + 3} fontSize="10" textAnchor="end" fill="#646A75" className="tnum">
            {Math.round(p * maxCount)}
          </text>
          <text x={w - pad.r + 6} y={yCum(p) + 3} fontSize="10" fill="#646A75" className="tnum">
            {Math.round(p * 100)}%
          </text>
        </g>
      ))}
      <line x1={pad.l} x2={w - pad.r} y1={yCum(0.8)} y2={yCum(0.8)} stroke="#C9892D" strokeWidth="1" strokeDasharray="3 3" />
      <text x={w - pad.r - 4} y={yCum(0.8) - 4} fontSize="10" textAnchor="end" fill="#E0A14A">
        80% threshold
      </text>
      {data.map((d, i) => {
        const xx = xCenter(i) - barW / 2;
        const yy = yBar(d.count);
        const isAbove80 = cum[i] <= 0.8;
        return (
          <g key={d.factor}>
            <rect x={xx} y={yy} width={barW} height={pad.t + innerH - yy} fill={isAbove80 ? '#C9892D' : '#363B45'} />
            <text x={xCenter(i)} y={h - 28} fontSize="10" textAnchor="middle" fill="#9AA0AB">
              <tspan>{d.factor.length > 14 ? d.factor.slice(0, 13) + '…' : d.factor}</tspan>
            </text>
            <text x={xCenter(i)} y={h - 14} fontSize="10" textAnchor="middle" fill="#646A75" className="tnum">
              {d.count}
            </text>
          </g>
        );
      })}
      <path d={cumPath} fill="none" stroke="#E6E8EC" strokeWidth="1.25" />
      {cum.map((p, i) => (
        <circle key={i} cx={xCenter(i)} cy={yCum(p)} r="2" fill="#E6E8EC" />
      ))}
    </svg>
  );
}

export function Heatmap({ x, y, m }) {
  if (!x || !y || !m) return null;
  function color(v) {
    const t = Math.min(1, v / 50);
    if (t < 0.5) {
      const k = t / 0.5;
      const r = Math.round(0x1a + (0xc9 - 0x1a) * k);
      const g = Math.round(0x1d + (0x89 - 0x1d) * k);
      const b = Math.round(0x24 + (0x2d - 0x24) * k);
      return `rgb(${r},${g},${b})`;
    } else {
      const k = (t - 0.5) / 0.5;
      const r = Math.round(0xc9 + (0xe5 - 0xc9) * k);
      const g = Math.round(0x89 + (0x48 - 0x89) * k);
      const b = Math.round(0x2d + (0x4d - 0x2d) * k);
      return `rgb(${r},${g},${b})`;
    }
  }

  return (
    <div className="overflow-x-auto scroll-thin">
      <div className="grid" style={{ gridTemplateColumns: `140px repeat(${x.length}, minmax(96px, 1fr))` }}>
        <div></div>
        {x.map((c) => (
          <div key={c} className="text-2xs caps text-fg-faint pb-2 px-2">
            {c}
          </div>
        ))}
        {y.map((row, ri) => (
          <React.Fragment key={row}>
            <div className="text-xs text-fg-muted py-2 pr-2 border-t border-ink-500">{row}</div>
            {x.map((_, ci) => {
              const v = m[ri][ci];
              const bg = color(v);
              const fg = v > 25 ? '#0F1115' : '#E6E8EC';
              return (
                <div
                  key={ci}
                  className="border-t border-l border-ink-500 px-2 py-3 text-sm tnum hover:outline hover:outline-1 hover:outline-fg-muted"
                  style={{ background: bg, color: fg }}
                  title={`${row} · ${x[ci]} — ${v}% late`}
                >
                  {v}%
                </div>
              );
            })}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
}

export function TrendLine({ data, w = 1080, h = 200 }) {
  if (!data || !data.length) return null;
  const pad = { l: 40, r: 24, t: 30, b: 30 };
  const innerW = w - pad.l - pad.r;
  const innerH = h - pad.t - pad.b;
  const values = data.map((d) => d.v);
  const yMin = Math.min(...values) - 1;
  const yMax = Math.max(...values) + 1;

  const x = (i) => pad.l + (i / (data.length - 1)) * innerW;
  const y = (v) => pad.t + (1 - (v - yMin) / (yMax - yMin)) * innerH;
  const path = data.map((p, i) => (i === 0 ? `M${x(i)},${y(p.v)}` : `L${x(i)},${y(p.v)}`)).join(' ');

  const yTicks = [yMin, (yMin + yMax) / 2, yMax].map((v) => Math.round(v));

  return (
    <svg width="100%" viewBox={`0 0 ${w} ${h}`} className="overflow-visible">
      {yTicks.map((t) => (
        <g key={t}>
          <line x1={pad.l} x2={w - pad.r} y1={y(t)} y2={y(t)} stroke="#1A1D24" />
          <text x={pad.l - 6} y={y(t) + 3} fontSize="10" textAnchor="end" fill="#646A75" className="tnum">
            {t}
          </text>
        </g>
      ))}
      {data.map((p, i) =>
        i % 2 === 0 ? (
          <text key={i} x={x(i)} y={h - 10} fontSize="10" textAnchor="middle" fill="#646A75">
            {p.m}
          </text>
        ) : null,
      )}
      {data.map((p, i) =>
        p.note ? (
          <g key={'a' + i}>
            <line x1={x(i)} x2={x(i)} y1={pad.t - 8} y2={y(p.v) - 4} stroke="#363B45" strokeDasharray="2 3" />
            <circle cx={x(i)} cy={y(p.v)} r="3" fill="#0F1115" stroke="#C9892D" strokeWidth="1.5" />
            <g transform={`translate(${x(i)},${pad.t - 14})`}>
              <rect x="-78" y="-12" width="156" height="14" rx="2" fill="#1A1D24" stroke="#262A33" />
              <text x="0" y="-2" fontSize="10" textAnchor="middle" fill="#E0A14A">
                {p.note}
              </text>
            </g>
          </g>
        ) : null,
      )}
      <path d={path} fill="none" stroke="#C9892D" strokeWidth="1.5" />
      {data.map((p, i) => (
        <circle key={'p' + i} cx={x(i)} cy={y(p.v)} r="1.6" fill="#C9892D" />
      ))}
    </svg>
  );
}
