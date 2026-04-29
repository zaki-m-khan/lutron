// Data preview — paginated raw orders table for the demo.
import React, { useEffect, useState } from 'react';
import { I } from './icons.jsx';
import { Btn, Card, Pill } from './shell.jsx';
import { getOrders } from './api.js';

const FILTERS = [
  { key: 'all', label: 'All' },
  { key: 'open', label: 'Open' },
  { key: 'closed', label: 'Closed' },
];

function formatCell(col, v) {
  if (v == null) return <span className="text-fg-ghost">—</span>;
  if (typeof v === 'boolean') {
    return v ? (
      <span className="text-ok tnum">true</span>
    ) : (
      <span className="text-fg-faint tnum">false</span>
    );
  }
  if (col === 'order_id') return <span className="font-mono text-fg">{v}</span>;
  if (col === 'order_date' || col === 'promised_date') {
    return <span className="tnum text-fg-muted">{v}</span>;
  }
  if (typeof v === 'number') return <span className="tnum text-fg">{v}</span>;
  return <span className="text-fg">{String(v)}</span>;
}

const COL_LABELS = {
  order_id: 'Order ID',
  order_date: 'Order date',
  customer_segment: 'Segment',
  product_line: 'Product line',
  plant: 'Plant',
  distribution_center: 'DC',
  quantity: 'Qty',
  unit_price: 'Unit $',
  config_complexity: 'Complexity',
  supplier_risk_flag: 'Supplier risk',
  promised_lead_days: 'Promised days',
  promised_date: 'Promised',
  actual_lead_days: 'Actual days',
  is_open: 'Open?',
  is_late: 'Late?',
  on_time: 'On-time?',
  otif: 'OTIF?',
};

export function DataPreview() {
  const [data, setData] = useState(null);
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState('all');
  const pageSize = 25;

  useEffect(() => {
    setData(null);
    getOrders({ page, pageSize, filter })
      .then(setData)
      .catch(console.error);
  }, [page, filter]);

  const totalPages = data ? Math.max(1, Math.ceil(data.total / pageSize)) : 1;

  return (
    <div className="px-5 py-4 space-y-3">
      <div className="flex items-center gap-2 flex-wrap">
        <div className="text-xs text-fg-faint">Filter</div>
        <div className="flex items-center bg-ink-800 border border-ink-500 rounded-md p-0.5">
          {FILTERS.map((f) => (
            <button
              key={f.key}
              onClick={() => {
                setFilter(f.key);
                setPage(1);
              }}
              className={[
                'px-2.5 h-6 text-xs rounded kbd-ring',
                filter === f.key ? 'bg-ink-600 text-fg' : 'text-fg-muted hover:text-fg',
              ].join(' ')}
            >
              {f.label}
            </button>
          ))}
        </div>
        <span className="h-4 w-px bg-ink-500 mx-1" />
        <Pill tone="neutral" className="!h-6 !px-2">
          <span className="tnum text-fg">{data ? data.total.toLocaleString() : '…'}</span>{' '}
          <span className="text-fg-faint">orders</span>
        </Pill>
        <Pill tone="accent" className="!h-6 !px-2">
          {data ? data.columns.length : '…'} columns
        </Pill>
        <div className="ml-auto text-2xs text-fg-faint">
          Raw rows from <span className="font-mono text-fg-muted">data/orders.csv</span> — the same
          frame the model trains on.
        </div>
      </div>

      <Card pad={false}>
        <div className="overflow-x-auto scroll-thin">
          <table className="w-full text-xs">
            <thead className="bg-ink-800 sticky top-0 z-10">
              <tr className="text-2xs caps text-fg-faint">
                {data &&
                  data.columns.map((c) => (
                    <th key={c} className="text-left font-normal py-2 px-3 whitespace-nowrap">
                      {COL_LABELS[c] || c}
                    </th>
                  ))}
                {!data && (
                  <th className="text-left font-normal py-2 px-3">Loading…</th>
                )}
              </tr>
            </thead>
            <tbody>
              {data &&
                data.rows.map((row, i) => (
                  <tr
                    key={row.order_id + i}
                    className={[
                      'border-t border-ink-500',
                      i % 2 === 1 ? 'bg-ink-700' : 'bg-ink-700/60',
                      'hover:bg-ink-600/60',
                    ].join(' ')}
                  >
                    {data.columns.map((c) => (
                      <td key={c} className="py-1.5 px-3 whitespace-nowrap">
                        {formatCell(c, row[c])}
                      </td>
                    ))}
                  </tr>
                ))}
              {!data &&
                Array.from({ length: 8 }).map((_, i) => (
                  <tr key={i} className="border-t border-ink-500">
                    <td colSpan={20} className="p-2">
                      <div className="skeleton h-5 rounded" />
                    </td>
                  </tr>
                ))}
            </tbody>
          </table>
        </div>
        {data && data.rows.length > 0 && (
          <div className="flex items-center justify-between px-3 h-9 border-t border-ink-500 bg-ink-800 text-xs text-fg-muted">
            <div>
              Showing{' '}
              <span className="text-fg tnum">
                {(page - 1) * pageSize + 1}–{(page - 1) * pageSize + data.rows.length}
              </span>{' '}
              of <span className="text-fg tnum">{data.total.toLocaleString()}</span>
            </div>
            <div className="flex items-center gap-2">
              <Btn kind="outline" size="xs" onClick={() => setPage(Math.max(1, page - 1))} disabled={page <= 1}>
                Prev
              </Btn>
              <span className="tnum">
                Page {page} / {totalPages}
              </span>
              <Btn
                kind="outline"
                size="xs"
                onClick={() => setPage(Math.min(totalPages, page + 1))}
                disabled={page >= totalPages}
              >
                Next
              </Btn>
            </div>
          </div>
        )}
      </Card>
    </div>
  );
}
