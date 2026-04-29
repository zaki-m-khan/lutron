"""Executive Scorecard — KPIs vs Amazon and industry-best benchmarks."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from src.benchmarks import (
    AMAZON_OTD_PCT,
    INDUSTRY_BEST_FILL_RATE,
    LUTRON_OTIF_GOAL,
    LUTRON_TARGET_FILL_RATES,
    LUTRON_LEAD_TIME_GOAL_DAYS,
)
from src.kpis import (
    avg_lead_time,
    breakdown_by,
    lead_time_std,
    monthly_otif,
    on_time_rate,
    otif_rate,
    quarterly_delta,
)
from src.theme import (
    COLORS,
    apply_plotly_theme,
    hero,
    inject_theme,
    kpi_card,
    kpi_grid,
    kpi_status_for,
    pill,
)

st.set_page_config(page_title="Executive Scorecard", page_icon="📊", layout="wide")
inject_theme()

if "orders" not in st.session_state:
    st.warning("Open the **Delivery Excellence Cell** landing page first to bootstrap data.")
    st.stop()

orders: pd.DataFrame = st.session_state["orders"]

# --- Sidebar filter ---
with st.sidebar:
    st.header("Filters")
    min_d, max_d = orders["order_date"].min().date(), orders["order_date"].max().date()
    date_range = st.date_input("Order date range", (min_d, max_d), min_value=min_d, max_value=max_d)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        df = orders[(orders["order_date"] >= start) & (orders["order_date"] <= end)]
    else:
        df = orders

# --- Hero ---
otif_now, otif_delta = quarterly_delta(df, otif_rate)
gap_to_amazon = AMAZON_OTD_PCT - otif_now
gap_to_lutron_goal = LUTRON_OTIF_GOAL - otif_now

st.markdown(pill("Module · Executive Scorecard"), unsafe_allow_html=True)
st.markdown(
    hero(
        eyebrow="OTIF gap to industry leaders",
        title=f"We're {gap_to_amazon:.0f} points behind Amazon and {gap_to_lutron_goal:.0f} short of our own 97.5% goal.",
        subtitle=(
            "The DEC's job is to close this gap by converting recurring escalations "
            "into permanent process, software, and supplier fixes — every fix "
            "compounds the next quarter's number."
        ),
        big_stat=f"{otif_now:.0f}%",
        vs_label="Lutron OTIF this quarter &nbsp;·&nbsp; vs &nbsp;·&nbsp; Amazon",
        bench_stat=f"{AMAZON_OTD_PCT:.0f}%",
        gap_pct=otif_now,
    ),
    unsafe_allow_html=True,
)

# --- Status-colored KPI cards ---
ot_now, ot_delta = quarterly_delta(df, on_time_rate)
lead_now, lead_delta = quarterly_delta(df, avg_lead_time)
std_now, std_delta = quarterly_delta(df, lead_time_std)

otif_status, otif_label = kpi_status_for(otif_now, LUTRON_OTIF_GOAL, higher_is_better=True)
ot_status, ot_label = kpi_status_for(ot_now, 95.0, higher_is_better=True)
lead_status, lead_label = kpi_status_for(lead_now, 10.0, higher_is_better=False)
std_status, std_label = kpi_status_for(std_now, 5.0, higher_is_better=False)


def fmt_delta(d: float, suffix: str = "") -> str:
    arrow = "▲" if d >= 0 else "▼"
    color = "#10B981" if d >= 0 else "#EF4444"
    return f"<span style='color:{color}; font-weight:600;'>{arrow} {abs(d):.1f}{suffix}</span> vs prior quarter"


cards = [
    kpi_card(
        "OTIF (On Time, In Full)",
        f"{otif_now:.1f}%",
        fmt_delta(otif_delta, "%"),
        status=otif_status,
        status_label=otif_label,
    ),
    kpi_card(
        "On-Time Rate",
        f"{ot_now:.1f}%",
        fmt_delta(ot_delta, "%"),
        status=ot_status,
        status_label=ot_label,
    ),
    kpi_card(
        "Avg Lead Time",
        f"{lead_now:.1f} d",
        fmt_delta(-lead_delta, " d"),  # invert so green = improving
        status=lead_status,
        status_label=lead_label,
    ),
    kpi_card(
        "Lead Time Std Dev",
        f"{std_now:.1f} d",
        fmt_delta(-std_delta, " d"),
        status=std_status,
        status_label=std_label,
    ),
]
st.markdown(kpi_grid(cards), unsafe_allow_html=True)

# --- Trend chart ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Trend</span>"
    f"<h3 style='margin:0;'>OTIF month-over-month vs targets</h3>"
    "</div>",
    unsafe_allow_html=True,
)
trend = monthly_otif(df)

fig = go.Figure()
fig.add_trace(
    go.Scatter(
        x=trend["month"],
        y=trend["otif_pct"],
        mode="lines+markers",
        name="Lutron OTIF",
        line=dict(width=3, color=COLORS["gold_bright"]),
        marker=dict(size=8, color=COLORS["gold_bright"]),
        fill="tozeroy",
        fillcolor="rgba(212,165,116,0.10)",
    )
)
for goal in LUTRON_TARGET_FILL_RATES:
    fig.add_hline(
        y=goal,
        line_dash="dot",
        line_color=COLORS["amber"],
        annotation_text=f"Target {goal}%",
        annotation_position="right",
        annotation_font_color=COLORS["amber"],
    )
fig.add_hline(
    y=AMAZON_OTD_PCT,
    line_dash="dash",
    line_color=COLORS["green"],
    annotation_text=f"Amazon ≈{AMAZON_OTD_PCT}%",
    annotation_position="right",
    annotation_font_color=COLORS["green"],
)
fig.add_hline(
    y=INDUSTRY_BEST_FILL_RATE,
    line_dash="dash",
    line_color=COLORS["blue"],
    annotation_text=f"Industry best {INDUSTRY_BEST_FILL_RATE}%",
    annotation_position="left",
    annotation_font_color=COLORS["blue"],
)
fig.update_layout(
    yaxis=dict(title="OTIF %", range=[0, 102]),
    xaxis_title=None,
    height=420,
    showlegend=False,
)
apply_plotly_theme(fig)
st.plotly_chart(fig, use_container_width=True)

# --- Two-column breakdown row ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Breakdowns</span>"
    f"<h3 style='margin:0;'>Where the pain is concentrated</h3>"
    "</div>",
    unsafe_allow_html=True,
)
b1, b2 = st.columns(2)

with b1:
    seg = breakdown_by(df, "customer_segment")
    fig_seg = px.bar(
        seg,
        x="otif_pct",
        y="customer_segment",
        orientation="h",
        text=seg["otif_pct"].round(1).astype(str) + "%",
        labels={"otif_pct": "OTIF %", "customer_segment": ""},
        title="OTIF by customer segment",
        color="otif_pct",
        color_continuous_scale=[(0, COLORS["red"]), (0.5, COLORS["amber"]), (1, COLORS["green"])],
        range_color=[40, 80],
    )
    fig_seg.update_traces(textposition="outside")
    fig_seg.update_layout(height=320, coloraxis_showscale=False)
    apply_plotly_theme(fig_seg)
    st.plotly_chart(fig_seg, use_container_width=True)

with b2:
    plant = breakdown_by(df, "plant")
    fig_plant = px.bar(
        plant,
        x="otif_pct",
        y="plant",
        orientation="h",
        text=plant["otif_pct"].round(1).astype(str) + "%",
        labels={"otif_pct": "OTIF %", "plant": ""},
        title="OTIF by plant",
        color="otif_pct",
        color_continuous_scale=[(0, COLORS["red"]), (0.5, COLORS["amber"]), (1, COLORS["green"])],
        range_color=[40, 80],
    )
    fig_plant.update_traces(textposition="outside")
    fig_plant.update_layout(height=320, coloraxis_showscale=False)
    apply_plotly_theme(fig_plant)
    st.plotly_chart(fig_plant, use_container_width=True)

# --- Lead time distribution ---
st.markdown(
    "<div style='margin-top:1.4rem; margin-bottom:0.6rem;'>"
    f"<span class='lut-pill'>Distribution</span>"
    f"<h3 style='margin:0;'>Variance is the real enemy</h3>"
    "</div>",
    unsafe_allow_html=True,
)
closed = df[df["is_open"] == False]  # noqa: E712
fig_lt = px.histogram(
    closed,
    x="actual_lead_days",
    nbins=40,
    labels={"actual_lead_days": "Actual lead time (days)"},
    color_discrete_sequence=[COLORS["gold"]],
)
fig_lt.add_vline(
    x=LUTRON_LEAD_TIME_GOAL_DAYS,
    line_dash="dot",
    line_color=COLORS["amber"],
    annotation_text=f"Stretch goal {LUTRON_LEAD_TIME_GOAL_DAYS:.0f} d",
    annotation_font_color=COLORS["amber"],
)
fig_lt.update_layout(height=320, bargap=0.05)
apply_plotly_theme(fig_lt)
st.plotly_chart(fig_lt, use_container_width=True)
st.caption(
    "Lutron is a B2B configured-product manufacturer, so absolute lead times will run "
    "longer than Amazon's 2-day median. **The killer metric is variance** — and that's "
    "exactly where the DEC's compounding fixes deliver the most customer trust."
)
