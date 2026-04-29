"""Root Cause Patterns — Pareto story of what's driving lateness."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from src.risk_model import FEATURE_LABELS
from src.theme import (
    COLORS,
    apply_plotly_theme,
    inject_theme,
    pill,
    section,
)

st.set_page_config(page_title="Root Cause Patterns", page_icon="🔍", layout="wide")
inject_theme()

if "orders" not in st.session_state:
    st.warning("Open the **Delivery Excellence Cell** landing page first to bootstrap data.")
    st.stop()

orders: pd.DataFrame = st.session_state["orders"]
model = st.session_state["model"]

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    segments = sorted(orders["customer_segment"].unique())
    plants = sorted(orders["plant"].unique())
    sel_segments = st.multiselect("Customer segment", segments, default=segments)
    sel_plants = st.multiselect("Plant", plants, default=plants)
    min_d, max_d = orders["order_date"].min().date(), orders["order_date"].max().date()
    date_range = st.date_input("Order date range", (min_d, max_d), min_value=min_d, max_value=max_d)

closed = orders[orders["is_open"] == False]  # noqa: E712
mask = closed["customer_segment"].isin(sel_segments) & closed["plant"].isin(sel_plants)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
    mask = mask & (closed["order_date"] >= start) & (closed["order_date"] <= end)
df = closed[mask].copy()
df["is_late_f"] = pd.to_numeric(df["is_late"], errors="coerce")

if df.empty:
    st.info("No orders match the current filters.")
    st.stop()

# --- Compute Pareto on positive-importance features ---
imp = model.feature_importance.copy()
imp["feature"] = imp["feature"].map(FEATURE_LABELS).fillna(imp["feature"])
imp = imp[imp["importance"] > 0].sort_values("importance", ascending=False).reset_index(drop=True)
total_imp = imp["importance"].sum()
imp["share"] = imp["importance"] / total_imp * 100
imp["cumulative"] = imp["share"].cumsum()
top_n_for_80 = int((imp["cumulative"] <= 80).sum()) + 1
top_n_for_80 = min(top_n_for_80, len(imp))

# --- Page header & headline insight ---
st.markdown(pill("Module · Root Cause Patterns"), unsafe_allow_html=True)

leading_drivers = imp.head(top_n_for_80)["feature"].tolist()
drivers_text = ", ".join(leading_drivers[:-1]) + (
    f" and {leading_drivers[-1]}" if len(leading_drivers) > 1 else leading_drivers[0]
)

st.markdown(
    f"""
<div class="lut-hero">
  <div class="lut-hero-eyebrow">The 80/20 of late deliveries</div>
  <div class="lut-hero-title">{top_n_for_80} factors explain 80% of why we're late.</div>
  <div class="lut-hero-sub">
    A Pareto view of the model's permutation importance. The DEC's compounding
    fixes should target these drivers first — every systemic fix on this short
    list moves the OTIF needle on the Executive Scorecard.
    <br><br>
    <b style='color:{COLORS["gold"]};'>Top drivers:</b> {drivers_text}.
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# --- Pareto chart (the hero chart) ---
fig_pareto = make_subplots(specs=[[{"secondary_y": True}]])
fig_pareto.add_trace(
    go.Bar(
        x=imp["feature"],
        y=imp["share"],
        name="Share of importance",
        marker=dict(
            color=imp["share"],
            colorscale=[(0, COLORS["surface_2"]), (1, COLORS["gold_bright"])],
        ),
        text=imp["share"].round(1).astype(str) + "%",
        textposition="outside",
    ),
    secondary_y=False,
)
fig_pareto.add_trace(
    go.Scatter(
        x=imp["feature"],
        y=imp["cumulative"],
        mode="lines+markers",
        name="Cumulative %",
        line=dict(color=COLORS["amber"], width=3),
        marker=dict(size=8),
    ),
    secondary_y=True,
)
fig_pareto.add_hline(
    y=80,
    line_dash="dot",
    line_color=COLORS["green"],
    annotation_text="80% line",
    annotation_position="right",
    annotation_font_color=COLORS["green"],
    secondary_y=True,
)
fig_pareto.update_yaxes(title="Share of importance (%)", range=[0, max(50, imp["share"].max() * 1.2)], secondary_y=False)
fig_pareto.update_yaxes(title="Cumulative %", range=[0, 105], secondary_y=True)
fig_pareto.update_layout(
    height=440,
    showlegend=False,
    title="Driver Pareto — what shapes late delivery",
)
apply_plotly_theme(fig_pareto)
st.plotly_chart(fig_pareto, use_container_width=True)

# --- Heatmap & timeline side-by-side ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Where & When</span>"
    "<h3 style='margin:0;'>Hot spots and seasonality</h3>"
    "</div>",
    unsafe_allow_html=True,
)
c1, c2 = st.columns([5, 6])

with c1:
    pivot = (
        df.groupby(["plant", "product_line"])["is_late_f"]
        .mean()
        .unstack("product_line")
        * 100
    )
    fig_heat = px.imshow(
        pivot,
        text_auto=".1f",
        color_continuous_scale=[(0, COLORS["green"]), (0.5, COLORS["amber"]), (1, COLORS["red"])],
        labels=dict(color="Late %"),
        aspect="auto",
        title="Late rate by plant × product line",
    )
    fig_heat.update_layout(height=380)
    apply_plotly_theme(fig_heat)
    st.plotly_chart(fig_heat, use_container_width=True)

with c2:
    monthly = df.copy()
    monthly["month"] = monthly["order_date"].dt.to_period("M").dt.to_timestamp()
    ts = (
        monthly.groupby("month")
        .agg(late_pct=("is_late_f", lambda s: s.mean() * 100), orders=("order_id", "count"))
        .reset_index()
    )
    fig_ts = px.line(
        ts,
        x="month",
        y="late_pct",
        markers=True,
        labels={"month": "Month", "late_pct": "Late %"},
        title="Monthly late rate with seasonality",
    )
    fig_ts.update_traces(line_color=COLORS["gold_bright"], marker_color=COLORS["gold_bright"])
    fig_ts.add_vrect(
        x0="2024-06-01",
        x1="2024-10-31",
        fillcolor=COLORS["amber"],
        opacity=0.10,
        line_width=0,
        annotation_text="Mexico ramp",
        annotation_position="top left",
        annotation_font_color=COLORS["amber"],
    )
    fig_ts.add_vrect(
        x0="2024-10-01",
        x1="2024-12-31",
        fillcolor=COLORS["red"],
        opacity=0.08,
        line_width=0,
        annotation_text="Q4 surge",
        annotation_position="top right",
        annotation_font_color=COLORS["red"],
    )
    fig_ts.add_vrect(
        x0="2025-10-01",
        x1="2025-12-31",
        fillcolor=COLORS["red"],
        opacity=0.08,
        line_width=0,
    )
    fig_ts.update_layout(height=380)
    apply_plotly_theme(fig_ts)
    st.plotly_chart(fig_ts, use_container_width=True)

st.caption(
    f"**Mexico × Configured / Bespoke is the hottest cell.** That's where the DEC's "
    "first systemic-fix initiative pays back fastest — the kind of compounding "
    "improvement Rallying Point #3 was written to enable."
)

# --- Segment view ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Segments</span>"
    "<h3 style='margin:0;'>Which customers feel it most</h3>"
    "</div>",
    unsafe_allow_html=True,
)
seg = (
    df.groupby("customer_segment")
    .agg(late_pct=("is_late_f", lambda s: s.mean() * 100), orders=("order_id", "count"))
    .reset_index()
    .sort_values("late_pct", ascending=False)
)
fig_seg = px.bar(
    seg,
    x="customer_segment",
    y="late_pct",
    text=seg["late_pct"].round(1).astype(str) + "%",
    labels={"customer_segment": "Customer segment", "late_pct": "Late %"},
    color="late_pct",
    color_continuous_scale=[(0, COLORS["green"]), (0.5, COLORS["amber"]), (1, COLORS["red"])],
    range_color=[20, 50],
)
fig_seg.update_traces(textposition="outside")
fig_seg.update_layout(height=320, coloraxis_showscale=False, showlegend=False)
apply_plotly_theme(fig_seg)
st.plotly_chart(fig_seg, use_container_width=True)
st.caption(
    "Hospitality and Commercial PM segments — the ones with the most configured "
    "and bespoke orders — carry the most lateness. The DEC's playbook should "
    "weight fixes for those segments highest."
)
