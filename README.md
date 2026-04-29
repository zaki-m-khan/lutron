# Delivery Excellence Cell — MVP Prototype

Software prototype for **Option 3: Delivery Excellence Cell — Converting Operational Heroics into Systems**, the recommended growth path from the Lutron team report.

The DEC is a permanent, cross-functional team that intercepts delivery escalations in real time, finds root causes, and converts each one into a permanent systemic fix. This MVP demonstrates the **Year 2 predictive analytics layer** that team would actually use day-to-day.

The current build is a **two-process app**: a FastAPI backend that wraps the Python data + model layer, and a Vite + React + Tailwind frontend ("Northstar Ops · Delivery Excellence Cell") that renders the operational console.

## What it does

Three screens, all driven by the same scored synthetic dataset (15,000 orders across 24 months, 4 customer segments, 4 product lines, 4 plants, 3 distribution centers):

| Screen | Purpose |
|---|---|
| **Overview** | OTIF / On-Time / Lead Time / Variance KPIs vs Amazon and industry-best benchmarks, **filtered by the topbar date range** (Today / 7d / 30d / Quarter). 24-month OTIF trend with the 90/95/97.5% Lutron target bands. Top at-risk orders, worst-performing plants, open escalations. |
| **Risk Queue** | Every open order scored 0–100% for late-risk. Dense table, filterable, expandable rows with per-order feature contributions and timeline. **"Engage supplier" / "Reroute capacity" / etc. POSTs to the action endpoint** — the row disappears, the open count drops, the summary refreshes. **"Export CSV"** downloads the live scored queue. |
| **Root Causes** | Pareto of contributing factors (the headline auto-rewrites itself — "N factors explain 80% of late deliveries"), plant × product-line late-rate heatmap with worst/best/median callouts, monthly OTIF trend with seasonality annotations. |
| **Data preview** | Paginated raw view of `data/orders.csv` (15,000 rows, 16 columns). Filter by All / Open / Closed. The same frame the model trains on — useful for showing the audience that the dashboard isn't a mock-up. |

## Quick start

Two processes — one Python, one Node. From `delivery-excellence-cell/`:

```bash
# 1. backend
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000

# 2. frontend (in a second shell)
cd web
npm install
npm run dev   # → http://localhost:5173
```

First backend launch takes ~10 seconds: it generates the synthetic dataset (`data/orders.csv`), trains the risk model (`data/risk_model.pkl`), and caches both. Subsequent launches are instant.

`POST /api/regenerate` rebuilds both caches end-to-end live — useful during the demo.

The frontend ships with a "Demo build · synthetic data" badge so the audience knows what they're seeing.

## How it maps to Option 3

- **Rallying Point #3** ("Mechanisms to convert firefighting into systemic solutions") — every high-risk order gets a top driver and a recommended DEC action, turning prediction into intervention.
- **Year 1 of the case-report roadmap** — the Overview screen is the executive view of what the Cell owns.
- **Year 2 of the case-report roadmap** — the predictive risk model is the explicit "predictive analytics on the Year 1 data foundation" deliverable.
- **Year 3 connects forward** — the model's per-order predictions are the data substrate for the future Promise-Date and Tiered-SLA modules.

## Project layout

```
delivery-excellence-cell/
├── api/                            # FastAPI surface
│   ├── main.py                     # app, CORS, /api/* endpoints, lifespan bootstrap
│   └── shaping.py                  # builds the JSON shapes the React UI expects
├── src/                            # Domain modules (unchanged from MVP)
│   ├── data_generator.py           # Synthetic Lutron orders (deterministic seed)
│   ├── risk_model.py               # HistGradientBoostingClassifier + scoring
│   ├── kpis.py                     # OTIF / Fill Rate / Lead Time calculators
│   └── benchmarks.py               # Amazon / industry-best constants
├── web/                            # Vite + React + Tailwind frontend
│   ├── src/
│   │   ├── App.jsx                 # screen switcher + toast
│   │   ├── api.js                  # fetch helpers (one per endpoint)
│   │   ├── icons.jsx               # inline-SVG icon set
│   │   ├── charts.jsx              # Spark / OtifLine / HBar / Pareto / Heatmap / TrendLine / RiskBar / FeatureBars
│   │   ├── shell.jsx               # Sidebar, TopBar, Pill, Btn, Card primitives
│   │   ├── overview.jsx            # Overview screen
│   │   ├── risk_queue.jsx          # Risk Queue screen
│   │   └── root_causes.jsx         # Root Causes screen
│   ├── tailwind.config.js
│   └── vite.config.js              # proxies /api → http://localhost:8000
├── data/                           # Generated on first API boot
├── legacy_streamlit/               # Original Streamlit MVP, kept as a fallback demo
│   ├── app.py
│   └── pages/
└── requirements.txt
```

## API surface

| Endpoint | What the React UI gets |
|---|---|
| `GET /api/health` | `{status, orders, model_auc, open_orders, actioned}` |
| `GET /api/kpis?range=today\|7d\|30d\|quarter` | OTIF / On-Time / Lead Time / Variance for the requested window, with delta vs the prior equal-length window |
| `GET /api/otif-history` | 24 months of OTIF |
| `GET /api/top-at-risk?limit=N` | Top-N open orders by risk score (excludes actioned) |
| `GET /api/worst-plants` | Plants ranked by OTIF |
| `GET /api/risk-summary` | `{open, critical, high, dollarsAtRisk}` (excludes actioned) |
| `GET /api/risk-rows?page=&pageSize=&minRisk=` | Paginated risk-scored open orders + per-row feature contributions |
| `GET /api/risk-rows.csv` | All scored open orders as CSV download |
| `POST /api/orders/{id}/action` | Mark an order actioned — disappears from queue + counts |
| `POST /api/orders/reset-actions` | Clear the actioned set (run between demos) |
| `GET /api/orders?page=&pageSize=&filter=all\|open\|closed` | Raw orders rows for the Data preview screen |
| `GET /api/pareto` | Feature importance × total late orders (top 7 + "Other") |
| `GET /api/heatmap` | Plant × Product Line late-rate matrix |
| `GET /api/trend` | 16 months OTIF with seasonality annotations |
| `GET /api/escalations` | Static stub (Year 1 module not yet wired) |
| `POST /api/regenerate` | Rebuilds dataset + retrains model, refreshes server cache, clears actioned |

## Deployment

The repo splits cleanly into two deployables:

**Frontend → Vercel.** `vercel.json` is preconfigured. When connecting the repo on Vercel, set the **Root Directory** to `delivery-excellence-cell`. Vercel will run `cd web && npm install && npm run build` and serve `web/dist`. Set the `VITE_API_BASE` environment variable on Vercel to your backend URL (e.g. `https://dec-api.onrender.com`).

**Backend → Render / Railway / Fly.io.** The FastAPI app (`pandas` + `scikit-learn`) is too large for Vercel's serverless function size limit, so host it as a long-lived process elsewhere. Render free tier works:

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- Root directory: `delivery-excellence-cell`
- Add a CORS origin for your Vercel domain in `api/main.py` (currently allows `localhost:5173` only).

For local-only demos none of this is needed — the two-process quickstart above is self-contained.

## Streamlit fallback

The original Streamlit MVP is preserved in `legacy_streamlit/` and still runs:

```bash
streamlit run legacy_streamlit/app.py
```

Use it if the demo machine can't run two processes.

## What's intentionally out of scope (next iterations)

- Escalation log / systemic-fix tracker (Year 1 in the roadmap; the Overview shows static stubs in the meantime)
- ERP / real-data integration
- Multi-user auth and role-based views
- Promise-Date and Tiered-SLA modules (Years 3+)
- Workspace navigation (Plants / Suppliers / SKUs / Models) — wired into the sidebar for design fidelity, but click-through is a placeholder

## Demo script

1. Open `http://localhost:5173`. Frame the DEC concept and point out the "Demo build · synthetic data" badge.
2. **Overview** — OTIF (~55%) vs the 99% Amazon benchmark and the 90/95/97.5% Lutron target bands. Mexico plant is visibly the worst performer.
3. **Risk Queue** — 907 open orders, $3.99M at risk. Click a high-risk Bespoke Controls row; walk through its feature contributions, the timeline, and the suggested DEC action. Click "Mark as actioned" to fire the toast.
4. **Root Causes** — read the auto-generated headline ("N factors explain 80%"). Mexico × Bespoke is the hottest heatmap cell. Pair the trend's Q4 surge / Mexico ramp annotations with where the DEC's compounding fixes pay off.
5. `curl -X POST http://localhost:8000/api/regenerate` to prove the pipeline rebuilds end-to-end live.
