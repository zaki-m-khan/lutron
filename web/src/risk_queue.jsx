// Risk Queue — filter rail, dense table, expandable rows, summary chip strip.
import React, { useEffect, useState } from 'react';
import { I } from './icons.jsx';
import { Btn, Card, Pill } from './shell.jsx';
import { RiskBar, FeatureBars } from './charts.jsx';
import { getRiskRows, getRiskSummary, actionOrder, riskRowsCsvUrl } from './api.js';

function FilterChip({ label, value, onRemove }) {
  return (
    <span className="inline-flex items-center gap-1 h-6 px-2 rounded-md border border-ink-500 bg-ink-700 text-xs">
      <span className="text-fg-faint">{label}</span>
      <span className="text-fg">{value}</span>
      <button onClick={onRemove} className="ml-0.5 text-fg-faint hover:text-fg kbd-ring rounded">
        <I.X size={10} />
      </button>
    </span>
  );
}

function ActionBtn({ action, onClick }) {
  const isPrimary = action.kind === 'engage';
  return (
    <button
      onClick={onClick}
      className={[
        'inline-flex items-center gap-1 h-6 px-2 rounded-md border text-xs kbd-ring transition-colors whitespace-nowrap',
        isPrimary
          ? 'border-accent/40 bg-accent-soft text-accent-hi hover:bg-accent/20'
          : 'border-ink-500 bg-ink-700 text-fg hover:bg-ink-600',
      ].join(' ')}
    >
      {action.label}
      <I.ChevronRight size={10} />
    </button>
  );
}

function ExpandedRow({ row, onAction }) {
  return (
    <tr className="row-expand">
      <td colSpan={9} className="bg-ink-800 border-t border-ink-500 p-0">
        <div className="grid grid-cols-12 gap-4 p-4">
          <div className="col-span-5">
            <div className="text-2xs caps text-fg-faint mb-2">Why this is at risk</div>
            <FeatureBars data={row.contribution} />
          </div>

          <div className="col-span-5">
            <div className="text-2xs caps text-fg-faint mb-2">Order timeline</div>
            <ol className="relative pl-3">
              <span className="absolute left-1 top-1 bottom-1 w-px bg-ink-500" />
              {[
                { t: 'Order', l: 'Order placed', state: 'done' },
                { t: 'BoM', l: 'BoM released to plant', state: 'done' },
                { t: 'Risk', l: 'Lateness predicted by model', state: 'risk' },
                { t: row.promised, l: 'Promised ship date', state: 'pending' },
                { t: '+5d', l: 'Customer required date', state: 'pending' },
              ].map((s, i) => (
                <li key={i} className="relative mb-2 last:mb-0">
                  <span
                    className={[
                      'absolute -left-[7px] top-1 w-2 h-2 rounded-full',
                      s.state === 'done'
                        ? 'bg-ok'
                        : s.state === 'risk'
                        ? 'bg-danger ring-2 ring-[#2A1417]'
                        : 'bg-ink-400',
                    ].join(' ')}
                  />
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-fg">{s.l}</span>
                    <span className="text-xs tnum text-fg-faint">{s.t}</span>
                  </div>
                </li>
              ))}
            </ol>
          </div>

          <div className="col-span-2">
            <div className="text-2xs caps text-fg-faint mb-2">Actions</div>
            <div className="space-y-2">
              <Btn kind="primary" size="md" className="w-full justify-center" onClick={() => onAction(row.id)}>
                <I.Check size={12} /> Mark as actioned
              </Btn>
              <Btn kind="secondary" size="md" className="w-full justify-center">
                Reassign owner
              </Btn>
              <Btn kind="ghost" size="md" className="w-full justify-center">
                Open full record <I.ArrowUpRight size={11} />
              </Btn>
            </div>
          </div>
        </div>
      </td>
    </tr>
  );
}

function EmptyState() {
  return (
    <div className="py-16 grid place-items-center">
      <div className="w-10 h-10 rounded-full border border-ink-400 grid place-items-center text-fg-muted mb-3">
        <I.CheckCircle size={18} />
      </div>
      <div className="text-md font-medium text-fg">No high-risk orders</div>
      <div className="text-xs text-fg-muted mt-1 max-w-[320px] text-center">
        Every open order is currently within tolerance for the selected risk threshold.
      </div>
    </div>
  );
}

export function RiskQueue({ onToast, onActioned }) {
  const [expanded, setExpanded] = useState(null);
  const [rows, setRows] = useState(null);
  const [total, setTotal] = useState(0);
  const [summary, setSummary] = useState(null);
  const [page, setPage] = useState(1);
  const [reloadTick, setReloadTick] = useState(0);
  const pageSize = 18;
  const [filters, setFilters] = useState([
    { key: 'risk', label: 'Risk', value: '≥ 50', threshold: 0.5 },
  ]);

  useEffect(() => {
    const minRisk = filters.find((f) => f.key === 'risk')?.threshold ?? 0;
    getRiskRows({ page, pageSize, minRisk }).then((d) => {
      setRows(d.rows);
      setTotal(d.total);
    });
    getRiskSummary().then(setSummary);
  }, [page, filters, reloadTick]);

  const handleAction = async (id) => {
    try {
      await actionOrder(id);
      setExpanded(null);
      onToast(`Order ${id} marked as actioned`);
      setReloadTick((t) => t + 1);
      if (onActioned) onActioned();
    } catch (e) {
      onToast(`Failed: ${e.message}`);
    }
  };

  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  return (
    <div className="px-5 py-4 space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <Btn kind="outline" size="sm" icon={I.Filter}>
          Filters
        </Btn>
        <span className="h-4 w-px bg-ink-500 mx-1" />
        {filters.map((f) => (
          <FilterChip
            key={f.key}
            label={f.label}
            value={f.value}
            onRemove={() => setFilters(filters.filter((x) => x.key !== f.key))}
          />
        ))}
        <button className="h-6 px-2 rounded-md border border-dashed border-ink-500 text-xs text-fg-faint hover:text-fg hover:border-ink-400 inline-flex items-center gap-1">
          <I.Plus size={10} /> Add filter
        </button>

        <div className="ml-auto flex items-center gap-2">
          <Btn kind="outline" size="sm">
            Group: Plant <I.ChevronDown size={11} />
          </Btn>
          <Btn kind="outline" size="sm">
            Sort: Risk ↓
          </Btn>
          <a
            href={riskRowsCsvUrl()}
            download="risk_rows.csv"
            className="inline-flex items-center gap-1.5 h-6 px-2 text-xs rounded-md kbd-ring bg-ink-800 text-fg-muted hover:text-fg hover:bg-ink-700 border border-ink-500"
          >
            <I.ArrowUpRight size={12} /> Export CSV
          </a>
        </div>
      </div>

      <div className="flex items-center gap-1.5 flex-wrap text-xs">
        <span className="text-fg-faint">Showing</span>
        <Pill tone="neutral" className="!h-6 !px-2">
          <span className="tnum text-fg">{summary ? summary.open : '…'}</span> <span className="text-fg-faint">open</span>
        </Pill>
        <span className="text-fg-faint">·</span>
        <Pill tone="danger" className="!h-6 !px-2" dot>
          <span className="tnum">{summary ? summary.critical : '…'}</span> critical
        </Pill>
        <Pill tone="warn" className="!h-6 !px-2" dot>
          <span className="tnum">{summary ? summary.high : '…'}</span> high-risk
        </Pill>
        <span className="text-fg-faint">·</span>
        <Pill tone="accent" className="!h-6 !px-2">
          <span className="tnum">{summary ? summary.dollarsAtRisk : '…'}</span> at risk
        </Pill>
      </div>

      <div className="bg-ink-700 border border-ink-500 rounded-md overflow-hidden">
        {rows && rows.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="overflow-x-auto scroll-thin">
            <table className="w-full text-sm">
              <thead className="bg-ink-800 sticky top-0 z-10">
                <tr className="text-2xs caps text-fg-faint">
                  <th className="text-left font-normal py-2 px-3 w-[120px]">Risk</th>
                  <th className="text-left font-normal py-2 px-3 w-[110px]">Order ID</th>
                  <th className="text-left font-normal py-2 px-3">Product</th>
                  <th className="text-left font-normal py-2 px-3 w-[220px]">Plant → DC</th>
                  <th className="text-right font-normal py-2 px-3 w-[64px]">Qty</th>
                  <th className="text-left font-normal py-2 px-3 w-[88px]">Promised</th>
                  <th className="text-left font-normal py-2 px-3 w-[170px]">Top driver</th>
                  <th className="text-left font-normal py-2 px-3 w-[170px]">Action</th>
                  <th className="w-7"></th>
                </tr>
              </thead>
              <tbody>
                {(rows || []).map((row, i) => {
                  const isOpen = expanded === row.id;
                  return (
                    <React.Fragment key={row.id + i}>
                      <tr
                        onClick={() => setExpanded(isOpen ? null : row.id)}
                        className={[
                          'border-t border-ink-500 cursor-pointer group',
                          i % 2 === 1 ? 'bg-ink-700' : 'bg-ink-700/60',
                          'hover:bg-ink-600/60',
                          isOpen ? '!bg-ink-600/80' : '',
                        ].join(' ')}
                      >
                        <td className="py-2 px-3">
                          <RiskBar value={row.risk} />
                        </td>
                        <td className="py-2 px-3 font-mono text-xs">
                          <a className="text-fg hover:text-accent-hi" href="#">
                            {row.id}
                          </a>
                        </td>
                        <td className="py-2 px-3 text-fg truncate max-w-[220px]">{row.product}</td>
                        <td className="py-2 px-3 text-fg-muted">
                          <span className="text-fg">{row.plant}</span>
                          <span className="text-fg-ghost mx-1">→</span>
                          <span>{row.dc}</span>
                        </td>
                        <td className="py-2 px-3 text-right tnum text-fg">{row.qty.toLocaleString()}</td>
                        <td className="py-2 px-3 tnum text-fg-muted">{row.promised}</td>
                        <td className="py-2 px-3">
                          <Pill tone="neutral">{row.driver}</Pill>
                        </td>
                        <td className="py-2 px-3" onClick={(e) => e.stopPropagation()}>
                          <ActionBtn action={row.action} onClick={() => handleAction(row.id)} />
                        </td>
                        <td className="py-2 pr-3 text-right">
                          <I.ChevronRight
                            size={12}
                            className={`text-fg-faint transition-transform ${isOpen ? 'rotate-90 text-fg' : 'group-hover:text-fg'}`}
                          />
                        </td>
                      </tr>
                      {isOpen && (
                        <ExpandedRow row={row} onAction={handleAction} />
                      )}
                    </React.Fragment>
                  );
                })}
                {!rows &&
                  Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i} className="border-t border-ink-500">
                      <td colSpan={9} className="p-2">
                        <div className="skeleton h-6 rounded" />
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        )}

        {rows && rows.length > 0 && (
          <div className="flex items-center justify-between px-3 h-9 border-t border-ink-500 bg-ink-800 text-xs text-fg-muted">
            <div>
              Showing{' '}
              <span className="text-fg tnum">
                {(page - 1) * pageSize + 1}–{(page - 1) * pageSize + rows.length}
              </span>{' '}
              of <span className="text-fg tnum">{total}</span>
            </div>
            <div className="flex items-center gap-2">
              <Btn kind="outline" size="xs" onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1}>
                Prev
              </Btn>
              <span className="tnum">
                Page {page} / {totalPages}
              </span>
              <Btn kind="outline" size="xs" onClick={() => setPage(Math.min(totalPages, page + 1))} disabled={page >= totalPages}>
                Next
              </Btn>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
