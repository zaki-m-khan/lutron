"""Delivery Excellence Cell — landing page."""

from __future__ import annotations

import streamlit as st

from src.benchmarks import AMAZON_OTD_PCT
from src.data_generator import ensure_data, DATA_PATH
from src.kpis import otif_rate
from src.risk_model import ensure_model, score_open_orders, MODEL_PATH
from src.theme import (
    alert,
    feature_card,
    feature_grid,
    hero,
    inject_theme,
    kpi_card,
    kpi_grid,
    pill,
)

st.set_page_config(
    page_title="Delivery Excellence Cell — Lutron",
    page_icon="📦",
    layout="wide",
)
inject_theme()


@st.cache_data(show_spinner="Loading orders…")
def _load_orders():
    return ensure_data()


@st.cache_resource(show_spinner="Training risk model…")
def _load_model(_orders):
    return ensure_model(_orders)


@st.cache_data(show_spinner="Scoring open orders…")
def _score(_orders, _model_auc):
    model = _load_model(_orders)
    return score_open_orders(_orders, model)


orders = _load_orders()
model = _load_model(orders)
scored = _score(orders, model.auc)

st.session_state["orders"] = orders
st.session_state["model"] = model
st.session_state["scored_open"] = scored

# ---------------------------------------------------------------------------
# Hero — the gap headline
# ---------------------------------------------------------------------------
otif_now = otif_rate(orders)
gap = AMAZON_OTD_PCT - otif_now

st.markdown(pill("Lutron · Delivery as a Delighter"), unsafe_allow_html=True)
st.markdown(
    hero(
        eyebrow="Option 3 · MVP Prototype",
        title="Delivery Excellence Cell",
        subtitle=(
            "Lutron's products are world-class. Its delivery experience isn't. "
            "The Delivery Excellence Cell converts daily firefighting into "
            "permanent systemic fixes — every escalation makes the company "
            "permanently better instead of just &ldquo;getting through the day.&rdquo;"
        ),
        big_stat=f"{otif_now:.0f}%",
        vs_label="Lutron OTIF today &nbsp;·&nbsp; vs &nbsp;·&nbsp; Amazon",
        bench_stat=f"{AMAZON_OTD_PCT:.0f}%",
        gap_pct=otif_now,
    ),
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# At-a-glance KPIs
# ---------------------------------------------------------------------------
high_risk = int((scored["risk_score"] >= 0.5).sum())
revenue_at_risk = float(scored.loc[scored["risk_score"] >= 0.5, "revenue_usd"].sum())

cards = [
    kpi_card(
        "Orders in dataset",
        f"{len(orders):,}",
        "24 months of synthetic Lutron-flavored history",
        status="gold",
    ),
    kpi_card(
        "Open orders being scored",
        f"{int(orders['is_open'].sum()):,}",
        "In-flight orders evaluated by the risk model",
        status="gold",
    ),
    kpi_card(
        "High-risk open orders",
        f"{high_risk:,}",
        "Predicted ≥ 50% chance of late delivery",
        status="red" if high_risk > 100 else "amber",
        status_label="Needs DEC action" if high_risk else "Clear",
    ),
    kpi_card(
        "Revenue at risk",
        f"${revenue_at_risk/1_000_000:.2f}M",
        "Sum of $ value across high-risk open orders",
        status="amber" if revenue_at_risk < 5_000_000 else "red",
    ),
]
st.markdown(kpi_grid(cards), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Feature cards — three pages
# ---------------------------------------------------------------------------
st.markdown(
    "<div style='margin-top:1.5rem; color:#94A3B8; font-size:0.95rem;'>"
    "Use the sidebar to open each module — or read the headlines below."
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    feature_grid(
        [
            feature_card(
                "📊",
                "Executive Scorecard",
                "Are we improving? OTIF, On-Time, and Lead-Time variance vs the "
                "Lutron 90 / 95 / 97.5% targets and Amazon's 99% on-time benchmark.",
            ),
            feature_card(
                "🎯",
                "Delivery Risk Forecast",
                "Which orders need the DEC's attention today? Every open order "
                "scored 0–100% by a gradient-boosted model, with a top driver "
                "and a recommended action per order.",
            ),
            feature_card(
                "🔍",
                "Root Cause Patterns",
                "What's actually making us late? A Pareto view of the few drivers "
                "that explain most of the lateness — the targets for the DEC's "
                "compounding systemic fixes.",
            ),
        ]
    ),
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Behind-the-prototype + controls
# ---------------------------------------------------------------------------
st.markdown("<div style='height:1.4rem;'></div>", unsafe_allow_html=True)

with st.expander("⚙️ Behind the prototype"):
    st.markdown(
        f"""
- **Dataset:** `{DATA_PATH.name}` — 15,000 synthetic orders over 24 months, deterministic seed.
- **Model:** scikit-learn `HistGradientBoostingClassifier` · ROC-AUC **{model.auc:.3f}** on a 20% held-out sample.
- **Patterns baked in** (so the model has signal to find): configured / bespoke products run ~3× later than stock; Q4 surge ~1.5×; Mexico plant ramp window mid-2024 (~1.6× variance); concentrated supplier-risk flag (+25% late prob); large orders (qty > 500) ~2× more variable; Hospitality skews bespoke.
- **Out of scope for this MVP:** ERP integration, escalation log, multi-user auth, Promise-Date / Tiered-SLA modules. Those are Year 1 / Year 3 items in the case-report roadmap.
"""
    )

c_left, c_right = st.columns([1, 3])
with c_left:
    if st.button("🔄 Regenerate data + retrain model", type="secondary"):
        DATA_PATH.unlink(missing_ok=True)
        MODEL_PATH.unlink(missing_ok=True)
        st.cache_data.clear()
        st.cache_resource.clear()
        st.rerun()
with c_right:
    st.caption(
        "Useful during a live demo — fully rebuilds the dataset and the model "
        "from scratch. Takes about 10 seconds."
    )
