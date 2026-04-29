"""FastAPI surface for the Delivery Excellence Cell demo.

Bootstraps the synthetic dataset and trained risk model on startup, then
exposes the JSON shapes the React UI consumes verbatim.

Run: uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from src.data_generator import DATA_PATH, ensure_data
from src.risk_model import MODEL_PATH, ensure_model, score_open_orders

from api import shaping


state: dict = {}


def _bootstrap() -> None:
    orders = ensure_data()
    model = ensure_model(orders)
    scored = score_open_orders(orders, model)
    state["orders"] = orders
    state["model"] = model
    state["scored"] = scored
    state.setdefault("actioned", set())


@asynccontextmanager
async def lifespan(app: FastAPI):
    _bootstrap()
    yield
    state.clear()


app = FastAPI(title="Delivery Excellence Cell API", lifespan=lifespan)

_default_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]
_extra_origins = [o.strip() for o in os.environ.get("CORS_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_default_origins + _extra_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


def _orders():
    if "orders" not in state:
        raise HTTPException(503, "Backend not bootstrapped yet")
    return state["orders"]


def _model():
    return state["model"]


def _scored_active():
    """scored open orders with actioned IDs filtered out."""
    scored = state["scored"]
    actioned: set = state.get("actioned", set())
    if not actioned:
        return scored
    return scored[~scored["order_id"].astype(str).isin(actioned)]


# --------------------------------------------------------------------- routes


@app.get("/api/health")
def health() -> dict:
    return {
        "status": "ok",
        "orders": int(state.get("orders", []).shape[0]) if "orders" in state else 0,
        "model_auc": round(float(state["model"].auc), 3) if "model" in state else None,
        "open_orders": int(_scored_active().shape[0]) if "scored" in state else 0,
        "actioned": len(state.get("actioned", set())),
    }


@app.get("/api/kpis")
def kpis(range: str | None = Query(None)):
    return shaping.kpis(_orders(), range_key=range)


@app.get("/api/otif-history")
def otif_history():
    return shaping.otif_history(_orders())


@app.get("/api/top-at-risk")
def top_at_risk(limit: int = Query(5, ge=1, le=50)):
    return shaping.top_at_risk(_scored_active(), limit=limit)


@app.get("/api/worst-plants")
def worst_plants():
    return shaping.worst_plants(_orders())


@app.get("/api/risk-summary")
def risk_summary():
    return shaping.risk_summary(_scored_active())


@app.get("/api/risk-rows")
def risk_rows(
    page: int = Query(1, ge=1),
    pageSize: int = Query(18, ge=1, le=200),
    minRisk: float = Query(0.0, ge=0.0, le=1.0),
):
    return shaping.risk_rows(_scored_active(), page=page, page_size=pageSize, min_risk=minRisk)


@app.get("/api/risk-rows.csv")
def risk_rows_csv():
    csv = shaping.risk_rows_csv(_scored_active())
    return Response(
        content=csv,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="risk_rows.csv"'},
    )


@app.post("/api/orders/{order_id}/action")
def action_order(order_id: str):
    scored = state["scored"]
    if order_id not in scored["order_id"].astype(str).values:
        raise HTTPException(404, f"Order {order_id} is not in the open queue")
    actioned: set = state.setdefault("actioned", set())
    actioned.add(order_id)
    return {
        "ok": True,
        "order_id": order_id,
        "actioned_total": len(actioned),
        "remaining_open": int(_scored_active().shape[0]),
    }


@app.post("/api/orders/reset-actions")
def reset_actions():
    """Clear the actioned set — useful between demos."""
    n = len(state.get("actioned", set()))
    state["actioned"] = set()
    return {"ok": True, "cleared": n}


@app.get("/api/orders")
def orders_preview(
    page: int = Query(1, ge=1),
    pageSize: int = Query(25, ge=1, le=200),
    filter: str = Query("all", pattern="^(all|open|closed)$"),
):
    return shaping.orders_preview(_orders(), page=page, page_size=pageSize, filter_kind=filter)


@app.get("/api/pareto")
def pareto():
    return shaping.pareto(_orders(), _model())


@app.get("/api/heatmap")
def heatmap():
    return shaping.heatmap(_orders())


@app.get("/api/trend")
def trend():
    return shaping.trend(_orders())


@app.get("/api/escalations")
def escalations():
    return shaping.escalations()


@app.post("/api/regenerate")
def regenerate():
    """Mirror of the Streamlit 'Regenerate data + retrain' button."""
    DATA_PATH.unlink(missing_ok=True)
    MODEL_PATH.unlink(missing_ok=True)
    state["actioned"] = set()
    _bootstrap()
    return {
        "ok": True,
        "orders": int(state["orders"].shape[0]),
        "model_auc": round(float(state["model"].auc), 3),
    }
