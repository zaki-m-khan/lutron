// Fetch helpers — dev: vite proxies /api → :8000. Prod: VITE_API_BASE points to deployed backend.
const API_BASE = (import.meta.env.VITE_API_BASE || '').replace(/\/$/, '');
const url = (path) => `${API_BASE}${path}`;

async function get(path) {
  const res = await fetch(url(path));
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

async function post(path, body) {
  const res = await fetch(url(path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) throw new Error(`${path} → ${res.status}`);
  return res.json();
}

const RANGE_API = { Today: 'today', '7d': '7d', '30d': '30d', Quarter: 'quarter' };
export const rangeToApi = (label) => RANGE_API[label] ?? 'quarter';

export const getHealth = () => get('/api/health');
export const getKpis = (range) => get(`/api/kpis${range ? `?range=${rangeToApi(range)}` : ''}`);
export const getOtifHistory = () => get('/api/otif-history');
export const getTopAtRisk = (limit = 5) => get(`/api/top-at-risk?limit=${limit}`);
export const getWorstPlants = () => get('/api/worst-plants');
export const getRiskSummary = () => get('/api/risk-summary');
export const getRiskRows = ({ page = 1, pageSize = 18, minRisk = 0 } = {}) =>
  get(`/api/risk-rows?page=${page}&pageSize=${pageSize}&minRisk=${minRisk}`);
export const getPareto = () => get('/api/pareto');
export const getHeatmap = () => get('/api/heatmap');
export const getTrend = () => get('/api/trend');
export const getEscalations = () => get('/api/escalations');
export const getOrders = ({ page = 1, pageSize = 25, filter = 'all' } = {}) =>
  get(`/api/orders?page=${page}&pageSize=${pageSize}&filter=${filter}`);

export const actionOrder = (id) => post(`/api/orders/${encodeURIComponent(id)}/action`);
export const resetActions = () => post('/api/orders/reset-actions');
export const regenerate = () => post('/api/regenerate');

export const riskRowsCsvUrl = () => url('/api/risk-rows.csv');
