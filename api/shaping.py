"""JSON shapers — turn the pandas-heavy outputs of src/ into the exact
shapes the React UI expects.

Each function returns plain-Python primitives ready for FastAPI to serialize.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.benchmarks import (
    AMAZON_OTD_PCT,
    LUTRON_LEAD_TIME_GOAL_DAYS,
    LUTRON_OTIF_GOAL,
)
from src.kpis import (
    avg_lead_time,
    breakdown_by,
    lead_time_std,
    monthly_otif,
    on_time_rate,
    otif_rate,
    quarterly_delta,
    revenue_at_risk,
)
from src.risk_model import (
    ACTION_BY_FEATURE,
    FEATURE_LABELS,
    per_order_contributions,
)


# --- Action kind mapping (design expects: engage/reroute/expedite/split/rebook) ---
ACTION_KIND_BY_FEATURE = {
    "supplier_risk_flag": "engage",
    "config_complexity": "expedite",
    "plant": "reroute",
    "quantity": "split",
    "product_line": "expedite",
    "customer_segment": "engage",
    "distribution_center": "reroute",
    "promised_lead_days": "rebook",
    "order_month": "reroute",
}


def _fmt_month(ts: pd.Timestamp) -> str:
    """`2024-05-01` -> `May 24`."""
    return pd.Timestamp(ts).strftime("%b %y")


def _closed(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["is_open"] == False].copy()  # noqa: E712


_RANGE_DAYS = {"today": 1, "7d": 7, "30d": 30, "quarter": 90}


def filter_by_range(df: pd.DataFrame, range_key: str | None) -> pd.DataFrame:
    """Filter orders to those whose promised_date falls in the last N days
    relative to the dataset's max promised_date.

    Default (None or 'all') returns the full frame. promised_date is the right
    column for KPI windows: "OTIF for orders due to deliver in the last 7 days"
    is more meaningful than orders *placed* in that window (most of which are
    still open).
    """
    if not range_key or range_key == "all":
        return df
    days = _RANGE_DAYS.get(range_key.lower())
    if days is None:
        return df
    if df.empty or "promised_date" not in df.columns:
        return df
    end = df["promised_date"].max()
    start = end - pd.Timedelta(days=days)
    return df[df["promised_date"] > start].copy()


# ------------------------------------------------------------------------- KPIs

def _monthly_metric(df: pd.DataFrame, col: str, agg: str = "mean", scale: float = 1.0) -> list[float]:
    """Monthly aggregate of a numeric column on closed orders, last 13 months."""
    closed = _closed(df).copy()
    closed["month"] = closed["order_date"].dt.to_period("M").dt.to_timestamp()
    s = pd.to_numeric(closed[col], errors="coerce")
    closed["_v"] = s
    grp = closed.groupby("month")["_v"].agg(agg).dropna()
    tail = grp.tail(13).tolist()
    return [round(float(v) * scale, 2) for v in tail]


def _ranged_delta(orders: pd.DataFrame, fn, range_key: str | None) -> tuple[float, float]:
    """If range_key is set, compute fn(current_window) and delta vs the
    immediately-prior window of the same length. Otherwise fall back to the
    quarterly delta used elsewhere in the app."""
    if not range_key or range_key == "all" or range_key.lower() == "quarter":
        return quarterly_delta(orders, fn)
    days = _RANGE_DAYS.get(range_key.lower())
    if days is None or orders.empty or "promised_date" not in orders.columns:
        return quarterly_delta(orders, fn)
    closed_subset = _closed(orders)
    if closed_subset.empty:
        return 0.0, 0.0
    end = closed_subset["promised_date"].max()
    cur_start = end - pd.Timedelta(days=days)
    prev_start = cur_start - pd.Timedelta(days=days)
    cur = orders[orders["promised_date"] > cur_start]
    prev = orders[(orders["promised_date"] > prev_start) & (orders["promised_date"] <= cur_start)]
    def _safe(df):
        if df.empty:
            return 0.0
        v = float(fn(df))
        return 0.0 if pd.isna(v) else v
    cur_v = _safe(cur)
    prev_v = _safe(prev)
    return cur_v, cur_v - prev_v


def kpis(orders: pd.DataFrame, range_key: str | None = None) -> dict[str, Any]:
    otif_now, otif_d = _ranged_delta(orders, otif_rate, range_key)
    ot_now, ot_d = _ranged_delta(orders, on_time_rate, range_key)
    lt_now, lt_d = _ranged_delta(orders, avg_lead_time, range_key)
    sd_now, sd_d = _ranged_delta(orders, lead_time_std, range_key)

    return {
        "otif": {
            "label": "OTIF",
            "value": round(otif_now, 1),
            "unit": "%",
            "delta": round(otif_d, 1),
            "target": LUTRON_OTIF_GOAL,
            "spark": _monthly_metric(orders, "otif", "mean", scale=100.0),
        },
        "onTime": {
            "label": "On-Time",
            "value": round(ot_now, 1),
            "unit": "%",
            "delta": round(ot_d, 1),
            "target": AMAZON_OTD_PCT,
            "spark": _monthly_metric(orders, "on_time", "mean", scale=100.0),
        },
        "leadTime": {
            "label": "Lead Time",
            "value": round(lt_now, 1),
            "unit": "d",
            "delta": round(lt_d, 1),
            "target": LUTRON_LEAD_TIME_GOAL_DAYS,
            "spark": _monthly_metric(orders, "actual_lead_days", "mean"),
            "inverse": True,
        },
        "variance": {
            "label": "Variance",
            "value": round(sd_now, 1),
            "unit": "d",
            "delta": round(sd_d, 1),
            "target": 5.0,
            "spark": _monthly_metric(orders, "actual_lead_days", "std"),
            "inverse": True,
        },
    }


# ------------------------------------------------------------- OTIF history (24m)

def otif_history(orders: pd.DataFrame) -> list[dict[str, Any]]:
    df = monthly_otif(orders).tail(24)
    return [{"m": _fmt_month(row["month"]), "v": round(float(row["otif_pct"]), 1)} for _, row in df.iterrows()]


# ----------------------------------------------------------- Top at-risk orders

def top_at_risk(scored: pd.DataFrame, limit: int = 5) -> list[dict[str, Any]]:
    if scored.empty:
        return []
    top = scored.sort_values("risk_score", ascending=False).head(limit)
    return [
        {
            "id": str(row["order_id"]),
            "product": str(row["product_line"]),
            "plant": str(row["plant"]),
            "risk": int(round(float(row["risk_score"]) * 100)),
            "qty": int(row["quantity"]),
        }
        for _, row in top.iterrows()
    ]


# ----------------------------------------------------------- Worst plants (4)

def worst_plants(orders: pd.DataFrame) -> list[dict[str, Any]]:
    grp = breakdown_by(orders, "plant").sort_values("otif_pct").head(4)
    return [{"plant": str(row["plant"]), "otif": round(float(row["otif_pct"]), 1)} for _, row in grp.iterrows()]


# ---------------------------------------------------------------- Risk summary

def risk_summary(scored: pd.DataFrame) -> dict[str, Any]:
    if scored.empty:
        return {"open": 0, "critical": 0, "high": 0, "dollarsAtRisk": "$0.00M"}
    risk = scored["risk_score"]
    revenue = revenue_at_risk(scored, 0.5)
    return {
        "open": int(scored.shape[0]),
        "critical": int((risk >= 0.7).sum()),
        "high": int((risk >= 0.5).sum()),
        "dollarsAtRisk": f"${revenue / 1_000_000:.2f}M",
    }


# ----------------------------------------------------------------- Risk rows

def _row_to_dict(row: pd.Series) -> dict[str, Any]:
    contrib_df = per_order_contributions(row).sort_values("contribution", ascending=False)
    contribution = [
        {"name": str(r["factor"]), "v": round(float(r["contribution"]), 3)}
        for _, r in contrib_df.iterrows()
    ]
    promised = pd.Timestamp(row["promised_date"])
    driver = str(row["top_driver"])
    action_kind = ACTION_KIND_BY_FEATURE.get(driver, "engage")
    action_label = ACTION_BY_FEATURE.get(driver, "Engage supplier — escalate component readiness")
    # Trim long action labels to fit the table cell.
    short_action = {
        "engage": "Engage supplier",
        "reroute": "Reroute capacity",
        "expedite": "Expedite review",
        "split": "Split shipment",
        "rebook": "Rebook freight",
    }.get(action_kind, action_label)
    return {
        "id": str(row["order_id"]),
        "product": str(row["product_line"]),
        "plant": str(row["plant"]),
        "dc": str(row["distribution_center"]),
        "qty": int(row["quantity"]),
        "promised": promised.strftime("%b %d"),
        "promisedISO": promised.strftime("%Y-%m-%d"),
        "driver": str(FEATURE_LABELS.get(driver, driver)),
        "risk": int(round(float(row["risk_score"]) * 100)),
        "action": {"kind": action_kind, "label": short_action},
        "contribution": contribution,
    }


def risk_rows(scored: pd.DataFrame, page: int = 1, page_size: int = 18,
              min_risk: float = 0.0) -> dict[str, Any]:
    if scored.empty:
        return {"rows": [], "total": 0}
    df = scored[scored["risk_score"] >= min_risk].sort_values("risk_score", ascending=False)
    total = int(df.shape[0])
    start = max(0, (page - 1) * page_size)
    page_df = df.iloc[start : start + page_size]
    return {"rows": [_row_to_dict(r) for _, r in page_df.iterrows()], "total": total}


# ------------------------------------------------------------------- Pareto

def pareto(orders: pd.DataFrame, model) -> list[dict[str, Any]]:
    imp = model.feature_importance.copy()
    imp = imp[imp["importance"] > 0].sort_values("importance", ascending=False).reset_index(drop=True)
    if imp.empty:
        return []
    total_imp = float(imp["importance"].sum())
    closed = _closed(orders)
    total_late = int(pd.to_numeric(closed["is_late"], errors="coerce").sum())
    out: list[dict[str, Any]] = []
    for _, row in imp.iterrows():
        share = float(row["importance"]) / total_imp
        out.append({
            "factor": str(FEATURE_LABELS.get(row["feature"], row["feature"])),
            "count": int(round(share * total_late)),
        })
    # Keep top 7 + tail bucketed as "Other".
    if len(out) > 8:
        head = out[:7]
        tail_count = sum(o["count"] for o in out[7:])
        head.append({"factor": "Other", "count": tail_count})
        out = head
    return out


# ------------------------------------------------------------------ Heatmap

def heatmap(orders: pd.DataFrame) -> dict[str, Any]:
    closed = _closed(orders).copy()
    closed["is_late_f"] = pd.to_numeric(closed["is_late"], errors="coerce")
    pivot = closed.pivot_table(
        index="plant",
        columns="product_line",
        values="is_late_f",
        aggfunc="mean",
    ) * 100.0
    pivot = pivot.round(0).fillna(0)
    y = [str(p) for p in pivot.index.tolist()]
    x = [str(c) for c in pivot.columns.tolist()]
    m = [[int(v) for v in row] for row in pivot.values.tolist()]
    return {"x": x, "y": y, "m": m}


# --------------------------------------------------------------------- Trend

_ANNOTATIONS = {
    "Jun 24": "Mexico ramp window opens",
    "Oct 24": "Q4 surge begins",
    "Oct 25": "Q4 surge begins",
}


def trend(orders: pd.DataFrame) -> list[dict[str, Any]]:
    df = monthly_otif(orders).tail(16)
    out: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        m = _fmt_month(row["month"])
        item: dict[str, Any] = {"m": m, "v": round(float(row["otif_pct"]), 1)}
        if m in _ANNOTATIONS:
            item["note"] = _ANNOTATIONS[m]
        out.append(item)
    return out


# ----------------------------------------------------------------- Escalations

# Static stub — Year 1 module not yet wired to a real backend.
ESCALATIONS_STUB = [
    {"id": "ESC-0142", "title": "Component shortage — DC motor 24V (Mexico)",
     "status": "Investigating", "owner": "M. Vasquez", "age": "2d"},
    {"id": "ESC-0139", "title": "Inbound delay — fabric SKU FB-9123 from Italy",
     "status": "Action Pending", "owner": "K. Dalbey", "age": "3d"},
    {"id": "ESC-0136", "title": "QA hold — keypad faceplates lot Q-882",
     "status": "Investigating", "owner": "R. Kowalski", "age": "5d"},
    {"id": "ESC-0128", "title": "Capacity reroute — Coopersburg line 4",
     "status": "Fix Deployed", "owner": "L. Chen", "age": "8d"},
]


def escalations() -> list[dict[str, Any]]:
    return ESCALATIONS_STUB


# ----------------------------------------------------------- Orders preview tab

_PREVIEW_COLUMNS = [
    "order_id", "order_date", "customer_segment", "product_line",
    "plant", "distribution_center", "quantity", "unit_price",
    "config_complexity", "supplier_risk_flag", "promised_lead_days",
    "promised_date", "actual_lead_days", "is_open", "is_late", "on_time", "otif",
]


def orders_preview(orders: pd.DataFrame, page: int = 1, page_size: int = 25,
                   filter_kind: str = "all") -> dict[str, Any]:
    df = orders
    if filter_kind == "open":
        df = df[df["is_open"] == True]  # noqa: E712
    elif filter_kind == "closed":
        df = df[df["is_open"] == False]  # noqa: E712
    df = df.sort_values("order_date", ascending=False)
    total = int(df.shape[0])
    start = max(0, (page - 1) * page_size)
    page_df = df.iloc[start : start + page_size]
    cols = [c for c in _PREVIEW_COLUMNS if c in page_df.columns]
    rows: list[dict[str, Any]] = []
    for _, row in page_df.iterrows():
        item: dict[str, Any] = {}
        for c in cols:
            v = row[c]
            if pd.isna(v):
                item[c] = None
            elif isinstance(v, pd.Timestamp):
                item[c] = v.strftime("%Y-%m-%d")
            elif isinstance(v, (np.integer,)):
                item[c] = int(v)
            elif isinstance(v, (np.floating,)):
                item[c] = round(float(v), 3)
            elif isinstance(v, (bool, np.bool_)):
                item[c] = bool(v)
            else:
                item[c] = str(v)
        rows.append(item)
    return {"columns": cols, "rows": rows, "total": total}


# -------------------------------------------------------- Risk-rows CSV export

def risk_rows_csv(scored: pd.DataFrame) -> str:
    """All scored open orders as CSV, sorted by risk descending."""
    if scored.empty:
        return "order_id,product,plant,dc,qty,promised,risk,driver,action\n"
    df = scored.sort_values("risk_score", ascending=False)
    rows = []
    for _, r in df.iterrows():
        driver = str(r["top_driver"])
        action_kind = ACTION_KIND_BY_FEATURE.get(driver, "engage")
        action_label = {
            "engage": "Engage supplier", "reroute": "Reroute capacity",
            "expedite": "Expedite review", "split": "Split shipment",
            "rebook": "Rebook freight",
        }.get(action_kind, "Engage supplier")
        rows.append({
            "order_id": str(r["order_id"]),
            "product": str(r["product_line"]),
            "plant": str(r["plant"]),
            "dc": str(r["distribution_center"]),
            "qty": int(r["quantity"]),
            "promised": pd.Timestamp(r["promised_date"]).strftime("%Y-%m-%d"),
            "risk": int(round(float(r["risk_score"]) * 100)),
            "driver": str(FEATURE_LABELS.get(driver, driver)),
            "action": action_label,
        })
    out = pd.DataFrame(rows).to_csv(index=False)
    return out
