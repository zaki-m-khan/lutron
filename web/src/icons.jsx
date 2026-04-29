// Lucide-styled inline SVG icons. Stroke 1.6px to match dense UI.
import React from 'react';

const Icon = ({ d, size = 14, stroke = 1.6, className = '', children }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={stroke}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    aria-hidden="true"
  >
    {d ? <path d={d} /> : children}
  </svg>
);

export const I = {
  Home: (p) => (
    <Icon {...p}>
      <path d="M3 11l9-8 9 8" />
      <path d="M5 10v10h14V10" />
    </Icon>
  ),
  Activity: (p) => <Icon {...p} d="M3 12h4l3-8 4 16 3-8h4" />,
  Layers: (p) => (
    <Icon {...p}>
      <path d="M12 3l9 5-9 5-9-5 9-5z" />
      <path d="M3 13l9 5 9-5" />
      <path d="M3 17l9 5 9-5" />
    </Icon>
  ),
  Flag: (p) => (
    <Icon {...p}>
      <path d="M5 22V4" />
      <path d="M5 4h12l-2 4 2 4H5" />
    </Icon>
  ),
  Settings: (p) => (
    <Icon {...p}>
      <circle cx="12" cy="12" r="3" />
      <path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3h0a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8v0a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z" />
    </Icon>
  ),
  Search: (p) => (
    <Icon {...p}>
      <circle cx="11" cy="11" r="7" />
      <path d="M21 21l-4.3-4.3" />
    </Icon>
  ),
  Bell: (p) => (
    <Icon {...p}>
      <path d="M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8" />
      <path d="M10.3 21a2 2 0 0 0 3.4 0" />
    </Icon>
  ),
  ChevronDown: (p) => <Icon {...p} d="M6 9l6 6 6-6" />,
  ChevronRight: (p) => <Icon {...p} d="M9 6l6 6-6 6" />,
  ChevronUp: (p) => <Icon {...p} d="M6 15l6-6 6 6" />,
  ArrowUpRight: (p) => (
    <Icon {...p}>
      <path d="M7 17 17 7" />
      <path d="M8 7h9v9" />
    </Icon>
  ),
  ArrowUp: (p) => <Icon {...p} d="M12 19V5M5 12l7-7 7 7" />,
  ArrowDown: (p) => <Icon {...p} d="M12 5v14M5 12l7 7 7-7" />,
  X: (p) => <Icon {...p} d="M18 6 6 18M6 6l12 12" />,
  Plus: (p) => <Icon {...p} d="M12 5v14M5 12h14" />,
  Filter: (p) => <Icon {...p} d="M3 5h18l-7 9v6l-4-2v-4z" />,
  Check: (p) => <Icon {...p} d="M20 6 9 17l-5-5" />,
  Inbox: (p) => (
    <Icon {...p}>
      <path d="M22 12h-6l-2 3h-4l-2-3H2" />
      <path d="M5.5 5h13L22 12v6a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-6z" />
    </Icon>
  ),
  Triangle: (p) => <Icon {...p} d="M12 4l9 16H3z" />,
  Dot: (p) => (
    <Icon {...p}>
      <circle cx="12" cy="12" r="3" fill="currentColor" stroke="none" />
    </Icon>
  ),
  Calendar: (p) => (
    <Icon {...p}>
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M16 3v4M8 3v4M3 11h18" />
    </Icon>
  ),
  Command: (p) => <Icon {...p} d="M9 3a3 3 0 1 1-3 3v12a3 3 0 1 1 3-3h6a3 3 0 1 1-3 3V6a3 3 0 1 1 3 3z" />,
  CornerDownLeft: (p) => <Icon {...p} d="M9 10l-5 5 5 5M20 4v7a4 4 0 0 1-4 4H4" />,
  PanelLeft: (p) => (
    <Icon {...p}>
      <rect x="3" y="4" width="18" height="16" rx="2" />
      <path d="M9 4v16" />
    </Icon>
  ),
  Sparkles: (p) => (
    <Icon
      {...p}
      d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6zM19 14l.7 2 2 .7-2 .7-.7 2-.7-2-2-.7 2-.7zM5 16l.5 1.5L7 18l-1.5.5L5 20l-.5-1.5L3 18l1.5-.5z"
    />
  ),
  Clock: (p) => (
    <Icon {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 7v5l3 2" />
    </Icon>
  ),
  Truck: (p) => (
    <Icon {...p}>
      <path d="M3 7h11v9H3z" />
      <path d="M14 10h4l3 3v3h-7" />
      <circle cx="7" cy="18" r="2" />
      <circle cx="17" cy="18" r="2" />
    </Icon>
  ),
  Factory: (p) => <Icon {...p} d="M3 21V10l5 3V10l5 3V8l8 4v9z M7 21v-4 M11 21v-4 M15 21v-4 M19 21v-4" />,
  AlertCircle: (p) => (
    <Icon {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5M12 16.5v.01" />
    </Icon>
  ),
  CheckCircle: (p) => (
    <Icon {...p}>
      <circle cx="12" cy="12" r="9" />
      <path d="M8 12.5l3 3 5-6" />
    </Icon>
  ),
  Box: (p) => (
    <Icon {...p}>
      <path d="M3 7l9-4 9 4-9 4-9-4z" />
      <path d="M3 7v10l9 4 9-4V7" />
      <path d="M12 11v10" />
    </Icon>
  ),
};

export default I;
