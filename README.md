# Delivery Excellence Cell — Year 2 Predictive Analytics Prototype

A working software artifact accompanying the team's Lutron case-report recommendation of **Option 3: Delivery Excellence Cell**. The Cell is proposed as a permanent cross-functional unit whose mandate is to convert delivery escalations into permanent systemic fixes. This prototype implements the **Year 2 deliverable** of that proposal: the predictive analytics layer that the Cell would use day-to-day to surface at-risk orders, attribute root causes, and direct structural-fix priorities.

The point of the artifact is to demonstrate that the Year 2 scope is technically straightforward on commodity tooling, and that the per-order risk score it produces is the direct data input for the Year 3 customer-facing modules (Promise Date, Tiered SLAs).

## Substance

**Dataset.** 15,000 synthetic orders across 24 months, deterministic seed. The generator (`src/data_generator.py`) encodes the patterns identified in the case report's diagnosis: Configured and Bespoke product lines run later than Stock (28% vs. 5% baseline), the Mexico plant has elevated late-rate during its mid-2024 ramp window, supplier risk concentrates in Mexico and Bespoke Controls, Q4 carries a 1.5× seasonality multiplier, and large/complex orders slip more often. The most recent ~8% of orders are flagged open (no realized delivery yet) and serve as the model's prediction targets.

**Model.** A `HistGradientBoostingClassifier` (scikit-learn) trained on closed orders, predicting `is_late` from nine features: customer segment, product line, plant, distribution center, quantity, configuration complexity, supplier risk flag, promised lead days, and order month. 80/20 stratified train/test split. **Held-out test AUC ≈ 0.74** — meaningfully above chance, demonstrating the architecture works on Lutron-shaped data. Global feature ranking is computed via permutation importance and feeds the Pareto chart on the Root Causes screen.

**Per-order attribution.** Each open order receives a top-driver assignment that maps onto a recommended DEC action ("engage supplier," "reroute capacity," "expedite engineering review," etc.). The current implementation is a rule-based heuristic that prioritizes the same factors the model treats as most predictive; production deployment would substitute TreeSHAP for true per-row attribution.

**Architecture.** Two-process application. FastAPI backend (`api/`) wraps the Python data and model layer and exposes a JSON API. Vite + React + Tailwind frontend (`web/`) renders the operator console. Backend bootstrap generates the dataset and trains the model on first launch (~10 seconds), then caches both to disk; subsequent launches are instant.

## Operator console

Four screens, all driven by live API responses against the scored dataset:

| Screen | What it shows |
|---|---|
| **Overview** | OTIF, On-Time, Lead Time, and Variance KPIs against Amazon and industry-best benchmarks, filterable by date window. Twenty-four-month OTIF trend overlaid with the 90/95/97.5% Lutron target bands from the case-report roadmap. Top at-risk open orders, worst-performing plants, escalations stub. |
| **Risk Queue** | All open orders scored 0–100% for late-risk. Filterable, paginated, with expandable rows that surface per-order driver contributions, an order timeline, and the recommended DEC action. Marking an order actioned posts to the backend; it disappears from the queue and the open count, summary chips, and dollars-at-risk all refresh in real time. CSV export pulls the live scored queue. |
| **Root Causes** | Pareto of contributing factors with auto-generated headline ("N factors explain 80% of late deliveries," computed live from permutation importances). Plant × product-line late-rate heatmap with worst/best/median annotations. Sixteen-month OTIF trend annotated at the seasonality inflection points. |
| **Data preview** | Paginated raw view of the 15,000-row training frame, filterable by open/closed status. Demonstrates that the dashboard reads from the same data the model trains on rather than from hardcoded fixtures. |

## How to run it

Two processes, from `delivery-excellence-cell/`:

```bash
# Backend
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000

# Frontend (separate shell)
cd web
npm install
npm run dev    # http://localhost:5173
```

`POST /api/regenerate` rebuilds the dataset and retrains the model end-to-end; useful for demonstrating that the pipeline is live rather than scripted.

## Project layout

```
delivery-excellence-cell/
├── api/                      FastAPI surface (main.py, shaping.py)
├── src/                      Domain modules
│   ├── data_generator.py     Synthetic Lutron orders (deterministic seed)
│   ├── risk_model.py         Gradient-boosted classifier + scoring
│   ├── kpis.py               OTIF / Fill Rate / Lead Time calculators
│   └── benchmarks.py         Amazon / industry-best constants
├── web/                      Vite + React + Tailwind frontend
├── data/                     Generated on first API boot (gitignored)
├── legacy_streamlit/         Earlier Streamlit MVP, retained as fallback
└── requirements.txt
```

## Mapping to the case-report roadmap

- **Year 1 (data foundation).** The Overview screen is the executive view of what the Cell would own once it has live OMS/ERP data. The synthetic generator is the placeholder for that integration.
- **Year 2 (predictive analytics).** Implemented here. The Risk Queue and Root Causes screens are the Cell's working surfaces; the gradient-boosted model and per-order attribution are the analytical core.
- **Year 3 (customer-facing modules).** The per-order risk score produced here is the direct data input required by the Promise Date and Tiered SLA modules proposed as later phases. Building it now is what makes the staged sequencing argument operationally credible.

## Deliberately out of scope

- ERP / OMS integration. The Year 1 deliverable; not built here. The synthetic generator is its placeholder.
- Per-row TreeSHAP attribution. Rule-based heuristic substitutes; a ten-line swap.
- The Cell's escalation log / systemic-fix tracker (Year 1 module). The Overview shows a static stub.
- Promise-Date and Tiered-SLA modules. Year 3.
- Authentication, role-based views, and multi-user state.
