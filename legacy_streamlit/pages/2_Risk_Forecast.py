"""Delivery Risk Forecast — open orders ranked by predicted late-risk."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from src.risk_model import per_order_contributions
from src.theme import (
    COLORS,
    alert,
    apply_plotly_theme,
    inject_theme,
    kpi_card,
    kpi_grid,
    order_tile,
    pill,
    tile_grid,
)

st.set_page_config(page_title="Delivery Risk Forecast", page_icon="🎯", layout="wide")
inject_theme()

if "scored_open" not in st.session_state:
    st.warning("Open the **Delivery Excellence Cell** landing page first to bootstrap data.")
    st.stop()

scored: pd.DataFrame = st.session_state["scored_open"].copy()

# --- Sidebar filters ---
with st.sidebar:
    st.header("Filters")
    segments = sorted(scored["customer_segment"].unique())
    plants = sorted(scored["plant"].unique())
    products = sorted(scored["product_line"].unique())

    sel_segments = st.multiselect("Customer segment", segments, default=segments)
    sel_plants = st.multiselect("Plant", plants, default=plants)
    sel_products = st.multiselect("Product line", products, default=products)
    min_risk = st.slider("Min risk score", 0, 100, 0, step=5) / 100.0

mask = (
    scored["customer_segment"].isin(sel_segments)
    & scored["plant"].isin(sel_plants)
    & scored["product_line"].isin(sel_products)
    & (scored["risk_score"] >= min_risk)
)
view = scored[mask].sort_values("risk_score", ascending=False)

# --- Page header ---
st.markdown(pill("Module · Delivery Risk Forecast"), unsafe_allow_html=True)
st.markdown(
    "<h1 style='margin-top:0;'>Today's triage queue</h1>"
    "<div style='color:#94A3B8; font-size:1.05rem; max-width:820px; margin-bottom:1.4rem;'>"
    "Every open order in the network, scored 0-100% for late-risk by a "
    "gradient-boosted model. The DEC works the queue top-down: highest risk "
    "first, with a recommended action attached to each order."
    "</div>",
    unsafe_allow_html=True,
)

# --- Alert banner ---
critical = int((view["risk_score"] >= 0.7).sum())
high_risk = int((view["risk_score"] >= 0.5).sum())
rev_at_risk = float(view.loc[view["risk_score"] >= 0.5, "revenue_usd"].sum())

if critical > 0:
    st.markdown(
        alert(
            "🚨",
            f"{critical} critical order{'s' if critical != 1 else ''} need DEC action today",
            f"Predicted ≥ 70% chance of late delivery. ${rev_at_risk/1_000_000:.2f}M total revenue exposed across all high-risk orders.",
        ),
        unsafe_allow_html=True,
    )

# --- KPI summary ---
total_open = int(view.shape[0])
mean_risk = float(view["risk_score"].mean()) if total_open else 0.0
cards = [
    kpi_card(
        "Open orders",
        f"{total_open:,}",
        "After filters",
        status="gold",
    ),
    kpi_card(
        "Critical (≥70%)",
        f"{critical:,}",
        "Top-priority DEC action",
        status="red" if critical else "green",
    ),
    kpi_card(
        "High-risk (≥50%)",
        f"{high_risk:,}",
        "Watch list",
        status="amber" if high_risk else "green",
    ),
    kpi_card(
        "Revenue at risk",
        f"${rev_at_risk/1_000_000:.2f}M",
        "Sum of $ across high-risk orders",
        status="amber",
    ),
]
st.markdown(kpi_grid(cards), unsafe_allow_html=True)

# --- Triage queue: top urgent orders as tile grid ---
st.markdown(
    "<div style='margin-top:1.6rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Top of queue</span>"
    "<h3 style='margin:0;'>Top 12 most urgent orders</h3>"
    "<div style='color:#94A3B8; font-size:0.92rem;'>"
    "Each tile shows risk %, the order's particulars, and the DEC's recommended next step."
    "</div></div>",
    unsafe_allow_html=True,
)

if total_open == 0:
    st.info("No orders match the current filters.")
else:
    top12 = view.head(12)
    tiles = [
        order_tile(
            order_id=row["order_id"],
            risk_pct=float(row["risk_score"]),
            product=str(row["product_line"]),
            plant=str(row["plant"]),
            qty=int(row["quantity"]),
            promised=str(pd.Timestamp(row["promised_date"]).date()),
            action=str(row["suggested_action"]),
        )
        for _, row in top12.iterrows()
    ]
    st.markdown(tile_grid(tiles), unsafe_allow_html=True)

# --- Drill-down ---
st.markdown(
    "<div style='margin-top:1.8rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Inspect</span>"
    "<h3 style='margin:0;'>Drill into a single order</h3>"
    "</div>",
    unsafe_allow_html=True,
)
if total_open > 0:
    order_id = st.selectbox(
        "Select an order to inspect",
        view["order_id"].tolist()[:200],
        index=0,
        label_visibility="collapsed",
    )
    row = view[view["order_id"] == order_id].iloc[0]

    d1, d2 = st.columns([2, 3])
    with d1:
        st.markdown(
            f"""
<div class="lut-section">
  <div class="lut-section-title">Order detail</div>
  <div class="lut-section-headline">{order_id}</div>
  <div style='color:#94A3B8; font-size:0.95rem; line-height:1.7;'>
    <b style='color:#F1F5F9;'>Segment:</b> {row['customer_segment']}<br>
    <b style='color:#F1F5F9;'>Product:</b> {row['product_line']}<br>
    <b style='color:#F1F5F9;'>Plant → DC:</b> {row['plant']} → {row['distribution_center']}<br>
    <b style='color:#F1F5F9;'>Quantity:</b> {row['quantity']:,}<br>
    <b style='color:#F1F5F9;'>Promised date:</b> {pd.Timestamp(row['promised_date']).date()}<br>
    <b style='color:#F1F5F9;'>Revenue:</b> ${row['revenue_usd']:,.0f}
  </div>
  <div style='margin-top:1rem; font-size:2.4rem; font-weight:800; color:{COLORS["gold_bright"]};'>
    {row['risk_score']*100:.0f}% <span style='font-size:0.9rem; color:#94A3B8; font-weight:500;'>late-risk</span>
  </div>
  <div class='lut-tile-action' style='margin-top:0.6rem;'>
    <b>DEC Action:</b> {row['suggested_action']}
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

    with d2:
        contrib = per_order_contributions(row)
        fig = px.bar(
            contrib,
            x="contribution",
            y="factor",
            orientation="h",
            labels={"contribution": "Contribution to risk score", "factor": ""},
            title="What's driving this order's risk",
            color="contribution",
            color_continuous_scale=[(0, COLORS["blue"]), (1, COLORS["red"])],
        )
        fig.update_layout(height=380, coloraxis_showscale=False)
        apply_plotly_theme(fig)
        st.plotly_chart(fig, use_container_width=True)

# --- Full table ---
with st.expander(f"📋 Full risk-ranked list ({total_open:,} orders)"):
    display = view[
        [
            "order_id",
            "customer_segment",
            "product_line",
            "plant",
            "distribution_center",
            "quantity",
            "promised_date",
            "revenue_usd",
            "risk_score",
            "top_driver_label",
            "suggested_action",
        ]
    ].rename(
        columns={
            "order_id": "Order",
            "customer_segment": "Segment",
            "product_line": "Product",
            "plant": "Plant",
            "distribution_center": "DC",
            "quantity": "Qty",
            "promised_date": "Promised",
            "revenue_usd": "Revenue ($)",
            "risk_score": "Risk",
            "top_driver_label": "Top Driver",
            "suggested_action": "DEC Action",
        }
    )
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Risk": st.column_config.ProgressColumn("Risk", format="%.0f%%", min_value=0, max_value=1),
            "Revenue ($)": st.column_config.NumberColumn(format="$%.0f"),
            "Promised": st.column_config.DateColumn(format="YYYY-MM-DD"),
        },
        height=420,
    )

# --- Risk distribution ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Distribution</span>"
    "<h3 style='margin:0;'>How risk is spread across the open-order book</h3>"
    "</div>",
    unsafe_allow_html=True,
)
fig_dist = px.histogram(
    view,
    x="risk_score",
    nbins=30,
    labels={"risk_score": "Predicted late-risk"},
    color_discrete_sequence=[COLORS["gold"]],
)
fig_dist.update_layout(height=300, bargap=0.05)
fig_dist.update_xaxes(tickformat=".0%")
apply_plotly_theme(fig_dist)
st.plotly_chart(fig_dist, use_container_width=True)
