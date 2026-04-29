// Sidebar + topbar shell. Original branding (no real logos).
import React from 'react';
import { I } from './icons.jsx';

function DECMark({ size = 22 }) {
  return (
    <div className="flex items-center gap-2">
      <svg width={size} height={size} viewBox="0 0 24 24" aria-hidden="true">
        <rect x="2" y="2" width="20" height="20" rx="4" fill="#1A1D24" stroke="#363B45" />
        <path d="M7 12h10M12 7v10" stroke="#C9892D" strokeWidth="1.6" strokeLinecap="round" />
        <circle cx="12" cy="12" r="2.4" fill="#C9892D" />
      </svg>
      <div className="leading-tight">
        <div className="text-[13px] font-semibold tracking-tight text-fg">Northstar Ops</div>
        <div className="text-2xs caps text-fg-faint">Delivery Excellence Cell</div>
      </div>
    </div>
  );
}

function NavItem({ icon: Ic, label, badge, selected, onClick }) {
  return (
    <button
      onClick={onClick}
      className={[
        'group relative w-full flex items-center gap-2 px-2 py-1.5 rounded-md text-base text-left',
        'kbd-ring transition-colors',
        selected ? 'bg-ink-700 text-fg' : 'text-fg-muted hover:bg-ink-700/60 hover:text-fg',
      ].join(' ')}
    >
      {selected && <span className="absolute left-[-8px] top-1.5 bottom-1.5 w-[2px] bg-accent rounded-r" />}
      <Ic size={15} className={selected ? 'text-fg' : 'text-fg-muted group-hover:text-fg'} />
      <span className="flex-1 truncate">{label}</span>
      {badge != null && (
        <span
          className={[
            'tnum text-2xs px-1.5 py-0.5 rounded',
            selected ? 'bg-ink-600 text-fg' : 'bg-ink-700 text-fg-muted',
          ].join(' ')}
        >
          {badge}
        </span>
      )}
    </button>
  );
}

function NavGroup({ title, children }) {
  return (
    <div className="mt-4">
      <div className="px-2 mb-1 text-2xs caps text-fg-faint">{title}</div>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
}

export function Sidebar({ screen, setScreen, openCount, escCount }) {
  return (
    <aside className="w-[220px] shrink-0 border-r border-ink-500 bg-ink-900 flex flex-col">
      <div className="h-[48px] px-3 flex items-center border-b border-ink-500">
        <DECMark />
      </div>

      <nav className="flex-1 p-2 overflow-y-auto scroll-thin">
        <div className="space-y-0.5">
          <NavItem icon={I.Home} label="Overview" selected={screen === 'overview'} onClick={() => setScreen('overview')} />
          <NavItem
            icon={I.Activity}
            label="Risk Queue"
            badge={openCount != null ? openCount : '…'}
            selected={screen === 'risk'}
            onClick={() => setScreen('risk')}
          />
          <NavItem icon={I.Layers} label="Root Causes" selected={screen === 'root'} onClick={() => setScreen('root')} />
          <NavItem
            icon={I.Flag}
            label="Escalations"
            badge={escCount != null ? escCount : '…'}
            selected={screen === 'esc'}
            onClick={() => setScreen('esc')}
          />
          <NavItem icon={I.Box} label="Data" selected={screen === 'data'} onClick={() => setScreen('data')} />
        </div>

        <NavGroup title="Workspaces">
          <NavItem icon={I.Factory} label="Plants" onClick={() => setScreen('overview')} />
          <NavItem icon={I.Truck} label="Suppliers" onClick={() => setScreen('overview')} />
          <NavItem icon={I.Box} label="SKUs" onClick={() => setScreen('overview')} />
        </NavGroup>

        <NavGroup title="System">
          <NavItem icon={I.Sparkles} label="Models" onClick={() => setScreen('overview')} />
          <NavItem icon={I.Settings} label="Settings" selected={screen === 'settings'} onClick={() => setScreen('settings')} />
        </NavGroup>
      </nav>

      <div className="p-2 border-t border-ink-500">
        <button className="w-full flex items-center gap-2 px-2 py-1.5 rounded-md hover:bg-ink-700 kbd-ring">
          <div className="w-6 h-6 rounded-full bg-ink-600 border border-ink-400 grid place-items-center text-2xs font-semibold text-fg">
            KD
          </div>
          <div className="flex-1 text-left leading-tight">
            <div className="text-xs font-medium text-fg">K. Dalbey</div>
            <div className="text-2xs text-fg-faint truncate">Coopersburg Ops</div>
          </div>
          <I.ChevronDown size={12} className="text-fg-faint" />
        </button>
      </div>
    </aside>
  );
}

export function TopBar({ screen, range, setRange }) {
  const titles = {
    overview: { crumb: 'Operations', title: 'Overview' },
    risk: { crumb: 'Operations', title: 'Risk Queue' },
    root: { crumb: 'Analysis', title: 'Root Causes' },
    esc: { crumb: 'Operations', title: 'Escalations' },
    data: { crumb: 'System', title: 'Data preview' },
    settings: { crumb: 'System', title: 'Settings' },
  };
  const t = titles[screen] || titles.overview;
  const ranges = ['Today', '7d', '30d', 'Quarter'];

  return (
    <div className="h-[48px] shrink-0 border-b border-ink-500 bg-ink-900 flex items-center px-4 gap-3">
      <div className="flex items-center gap-1.5 min-w-0">
        <button className="p-1 -ml-1 rounded text-fg-faint hover:text-fg hover:bg-ink-700 kbd-ring">
          <I.PanelLeft size={14} />
        </button>
        <span className="text-xs text-fg-muted">{t.crumb}</span>
        <I.ChevronRight size={12} className="text-fg-ghost" />
        <span className="text-base font-medium text-fg">{t.title}</span>
        <span className="ml-3 inline-flex items-center gap-1 h-5 px-1.5 rounded text-2xs border border-accent/30 bg-accent-soft text-accent-hi">
          <span className="w-1 h-1 rounded-full bg-accent-hi" />
          Demo build · synthetic data
        </span>
      </div>

      <div className="flex-1 flex justify-center px-6">
        <div className="w-full max-w-[520px] relative">
          <I.Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-fg-faint" />
          <input
            type="text"
            placeholder="Search orders, plants, suppliers…"
            className="w-full bg-ink-800 border border-ink-500 rounded-md pl-8 pr-16 h-7 text-sm text-fg placeholder:text-fg-faint kbd-ring focus:border-ink-400"
          />
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1 text-fg-faint">
            <kbd className="px-1 h-4 inline-flex items-center text-2xs font-mono border border-ink-500 rounded bg-ink-900">⌘</kbd>
            <kbd className="px-1 h-4 inline-flex items-center text-2xs font-mono border border-ink-500 rounded bg-ink-900">K</kbd>
          </div>
        </div>
      </div>

      <div className="flex items-center gap-2">
        <div className="flex items-center bg-ink-800 border border-ink-500 rounded-md p-0.5">
          {ranges.map((r) => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={[
                'px-2.5 h-6 text-xs rounded kbd-ring tnum',
                range === r ? 'bg-ink-600 text-fg' : 'text-fg-muted hover:text-fg',
              ].join(' ')}
            >
              {r}
            </button>
          ))}
        </div>

        <button className="relative w-7 h-7 grid place-items-center rounded-md border border-ink-500 bg-ink-800 text-fg-muted hover:text-fg hover:bg-ink-700 kbd-ring">
          <I.Bell size={14} />
          <span className="absolute top-1 right-1 w-1.5 h-1.5 rounded-full bg-danger ring-2 ring-ink-800" />
        </button>

        <button className="w-7 h-7 grid place-items-center rounded-full bg-ink-600 border border-ink-400 text-2xs font-semibold text-fg kbd-ring">
          KD
        </button>
      </div>
    </div>
  );
}

export function Pill({ tone = 'neutral', children, dot, className = '' }) {
  const tones = {
    neutral: 'bg-ink-700 text-fg-muted border-ink-500',
    accent: 'bg-accent-soft text-accent-hi border-accent/30',
    danger: 'bg-[#2A1417] text-danger border-danger/30',
    warn: 'bg-[#2A2014] text-warn border-warn/30',
    ok: 'bg-[#142A1B] text-ok border-ok/30',
    info: 'bg-[#142036] text-info border-info/30',
  };
  return (
    <span className={`inline-flex items-center gap-1 px-1.5 h-5 rounded text-2xs border ${tones[tone]} ${className}`}>
      {dot && <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'currentColor' }} />}
      {children}
    </span>
  );
}

export function Btn({ kind = 'ghost', size = 'sm', children, onClick, disabled, className = '', icon: Ic }) {
  const kinds = {
    primary: 'bg-accent text-[#0F0A03] hover:bg-accent-hi border border-accent',
    secondary: 'bg-ink-700 text-fg hover:bg-ink-600 border border-ink-400',
    ghost: 'bg-transparent text-fg-muted hover:text-fg hover:bg-ink-700 border border-transparent',
    outline: 'bg-ink-800 text-fg-muted hover:text-fg hover:bg-ink-700 border border-ink-500',
    danger: 'bg-transparent text-danger hover:bg-[#2A1417] border border-danger/30',
  };
  const sizes = {
    xs: 'h-5 px-1.5 text-2xs',
    sm: 'h-6 px-2  text-xs',
    md: 'h-7 px-2.5 text-sm',
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`inline-flex items-center gap-1.5 rounded-md kbd-ring transition-colors disabled:opacity-50 ${kinds[kind]} ${sizes[size]} ${className}`}
    >
      {Ic && <Ic size={size === 'xs' ? 11 : 12} />}
      {children}
    </button>
  );
}

export function Card({ title, action, children, className = '', pad = true }) {
  return (
    <section className={`bg-ink-700 border border-ink-500 rounded-md ${className}`}>
      {(title || action) && (
        <header className="h-9 px-3 flex items-center justify-between border-b border-ink-500">
          <div className="text-xs font-medium text-fg">{title}</div>
          <div className="flex items-center gap-2">{action}</div>
        </header>
      )}
      <div className={pad ? 'p-3' : ''}>{children}</div>
    </section>
  );
}
