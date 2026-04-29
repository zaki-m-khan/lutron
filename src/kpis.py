"""KPI calculators for the Executive Scorecard.

All functions operate on the full orders DataFrame. They ignore open orders
(no actual delivery yet) and coerce nullable booleans to floats so means
work cleanly.
"""

from __future__ import annotations

import pandas as pd


def _closed(df: pd.DataFrame) -> pd.DataFrame:
    return df[df["is_open"] == False].copy()  # noqa: E712


def _as_float(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def otif_rate(df: pd.DataFrame) -> float:
    closed = _closed(df)
    if closed.empty:
        return 0.0
    return float(_as_float(closed["otif"]).mean()) * 100


def fill_rate(df: pd.DataFrame) -> float:
    """Fill rate = on_time AND in_full at the order level (a.k.a. OTIF).

    Lutron's own one-pager calls out the goal of evolving 'Fill Rate -> OTIF',
    so we treat them as the same headline metric here.
    """
    return otif_rate(df)


def on_time_rate(df: pd.DataFrame) -> float:
    closed = _closed(df)
    if closed.empty:
        return 0.0
    return float(_as_float(closed["on_time"]).mean()) * 100


def avg_lead_time(df: pd.DataFrame) -> float:
    closed = _closed(df)
    if closed.empty:
        return 0.0
    return float(closed["actual_lead_days"].mean())


def lead_time_std(df: pd.DataFrame) -> float:
    closed = _closed(df)
    if closed.empty:
        return 0.0
    return float(closed["actual_lead_days"].std())


def monthly_otif(df: pd.DataFrame) -> pd.DataFrame:
    closed = _closed(df).copy()
    closed["month"] = closed["order_date"].dt.to_period("M").dt.to_timestamp()
    grp = closed.groupby("month").agg(
        otif_pct=("otif", lambda s: _as_float(s).mean() * 100),
        orders=("order_id", "count"),
    )
    return grp.reset_index()


def breakdown_by(df: pd.DataFrame, column: str) -> pd.DataFrame:
    closed = _closed(df)
    grp = closed.groupby(column).agg(
        otif_pct=("otif", lambda s: _as_float(s).mean() * 100),
        on_time_pct=("on_time", lambda s: _as_float(s).mean() * 100),
        avg_lead_days=("actual_lead_days", "mean"),
        orders=("order_id", "count"),
    )
    return grp.reset_index().sort_values("otif_pct")


def revenue_at_risk(df: pd.DataFrame, risk_threshold: float = 0.5) -> float:
    """Sum of revenue for open orders predicted late above the threshold."""
    if "risk_score" not in df.columns:
        return 0.0
    open_orders = df[df["is_open"] == True]  # noqa: E712
    flagged = open_orders[open_orders["risk_score"] >= risk_threshold]
    return float(flagged["revenue_usd"].sum())


def quarterly_delta(df: pd.DataFrame, metric_fn) -> tuple[float, float]:
    """Return (current_quarter_value, delta_vs_prior_quarter)."""
    closed = _closed(df).copy()
    if closed.empty:
        return 0.0, 0.0
    closed["quarter"] = closed["order_date"].dt.to_period("Q")
    quarters = sorted(closed["quarter"].unique())
    if len(quarters) < 2:
        return float(metric_fn(closed)), 0.0
    cur = closed[closed["quarter"] == quarters[-1]]
    prev = closed[closed["quarter"] == quarters[-2]]
    cur_val = float(metric_fn(cur))
    prev_val = float(metric_fn(prev))
    return cur_val, cur_val - prev_val
