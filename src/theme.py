"""Lutron-flavored visual theme: CSS injection + reusable card helpers.

Streamlit's built-in components are functional but generic. This module
overlays a dark-navy + warm-gold executive-dashboard look and provides a
small set of HTML helpers (status cards, hero, alert banners, order tiles)
that the pages call instead of plain `st.metric`, etc.
"""

from __future__ import annotations

import streamlit as st

# Lutron-inspired palette ----------------------------------------------------
COLORS = {
    "bg": "#0B1220",
    "surface": "#162033",
    "surface_2": "#1E2B45",
    "border": "#2A3A5C",
    "gold": "#D4A574",
    "gold_bright": "#F4C77A",
    "text": "#F1F5F9",
    "muted": "#94A3B8",
    "red": "#EF4444",
    "amber": "#F59E0B",
    "green": "#10B981",
    "blue": "#60A5FA",
}

# Plotly template default for every chart in the app.
PLOTLY_TEMPLATE = "plotly_dark"
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=COLORS["text"], family="Inter, system-ui, sans-serif"),
    colorway=[
        COLORS["gold"],
        COLORS["blue"],
        COLORS["green"],
        COLORS["amber"],
        COLORS["red"],
        "#A78BFA",
    ],
    margin=dict(l=10, r=10, t=30, b=10),
)


def apply_plotly_theme(fig):
    """Apply our Lutron palette to any plotly figure in one call."""
    fig.update_layout(template=PLOTLY_TEMPLATE, **PLOTLY_LAYOUT)
    return fig


def inject_theme() -> None:
    """Inject custom CSS. Call this near the top of every page."""
    st.markdown(
        f"""
<style>
  /* App background */
  .stApp {{
    background:
      radial-gradient(circle at 0% 0%, rgba(212,165,116,0.06) 0%, transparent 40%),
      radial-gradient(circle at 100% 0%, rgba(96,165,250,0.05) 0%, transparent 40%),
      {COLORS['bg']};
  }}

  /* Tighten default block padding so hero sections feel intentional */
  .block-container {{ padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1280px; }}

  /* Sidebar */
  section[data-testid="stSidebar"] {{
    background: {COLORS['surface']};
    border-right: 1px solid {COLORS['border']};
  }}

  /* Headings */
  h1, h2, h3, h4 {{
    color: {COLORS['text']};
    font-weight: 700;
    letter-spacing: -0.01em;
  }}
  h1 {{ font-size: 2.4rem !important; }}

  /* Custom card primitives ------------------------------------------------- */
  .lut-hero {{
    background: linear-gradient(135deg, {COLORS['surface']} 0%, {COLORS['surface_2']} 100%);
    border: 1px solid {COLORS['border']};
    border-radius: 16px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.8rem;
    position: relative;
    overflow: hidden;
  }}
  .lut-hero::before {{
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 90% 0%, rgba(212,165,116,0.18), transparent 50%);
    pointer-events: none;
  }}
  .lut-hero-eyebrow {{
    color: {COLORS['gold']};
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.16em;
    font-weight: 600;
    margin-bottom: 0.6rem;
  }}
  .lut-hero-title {{
    color: {COLORS['text']};
    font-size: 2.2rem;
    line-height: 1.15;
    font-weight: 800;
    margin-bottom: 0.8rem;
  }}
  .lut-hero-stat {{
    display: flex;
    align-items: baseline;
    gap: 1.1rem;
    margin-top: 1.2rem;
    flex-wrap: wrap;
  }}
  .lut-hero-stat-big {{
    font-size: 4.4rem;
    font-weight: 800;
    color: {COLORS['gold_bright']};
    line-height: 1;
  }}
  .lut-hero-stat-vs {{
    color: {COLORS['muted']};
    font-size: 1.05rem;
  }}
  .lut-hero-stat-bench {{
    font-size: 2rem;
    color: {COLORS['text']};
    font-weight: 700;
  }}
  .lut-hero-sub {{
    color: {COLORS['muted']};
    font-size: 1.02rem;
    line-height: 1.55;
    max-width: 820px;
  }}
  .lut-gap-bar {{
    margin-top: 1.4rem;
    height: 14px;
    border-radius: 10px;
    background: {COLORS['surface_2']};
    overflow: hidden;
    position: relative;
  }}
  .lut-gap-bar-fill {{
    height: 100%;
    background: linear-gradient(90deg, {COLORS['red']}, {COLORS['amber']}, {COLORS['gold']});
    border-radius: 10px;
  }}

  /* KPI cards */
  .lut-kpi-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 1rem;
    margin-bottom: 1.4rem;
  }}
  .lut-kpi {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-left: 4px solid {COLORS['muted']};
    border-radius: 12px;
    padding: 1.2rem 1.3rem;
  }}
  .lut-kpi.green {{ border-left-color: {COLORS['green']}; }}
  .lut-kpi.amber {{ border-left-color: {COLORS['amber']}; }}
  .lut-kpi.red   {{ border-left-color: {COLORS['red']}; }}
  .lut-kpi.gold  {{ border-left-color: {COLORS['gold']}; }}
  .lut-kpi-label {{
    color: {COLORS['muted']};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
    margin-bottom: 0.5rem;
  }}
  .lut-kpi-value {{
    color: {COLORS['text']};
    font-size: 2rem;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 0.25rem;
  }}
  .lut-kpi-sub {{
    color: {COLORS['muted']};
    font-size: 0.85rem;
  }}
  .lut-kpi-status {{
    display: inline-block;
    margin-top: 0.45rem;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 999px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }}
  .lut-kpi-status.green {{ background: rgba(16,185,129,0.15); color: {COLORS['green']}; }}
  .lut-kpi-status.amber {{ background: rgba(245,158,11,0.15); color: {COLORS['amber']}; }}
  .lut-kpi-status.red   {{ background: rgba(239,68,68,0.15); color: {COLORS['red']}; }}
  .lut-kpi-status.gold  {{ background: rgba(212,165,116,0.15); color: {COLORS['gold']}; }}

  /* Section card wrapper */
  .lut-section {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.2rem;
  }}
  .lut-section-title {{
    color: {COLORS['gold']};
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-weight: 700;
    margin-bottom: 0.4rem;
  }}
  .lut-section-headline {{
    color: {COLORS['text']};
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 0.4rem;
  }}

  /* Alert banner */
  .lut-alert {{
    background: linear-gradient(135deg, rgba(239,68,68,0.18), rgba(245,158,11,0.10));
    border: 1px solid rgba(239,68,68,0.4);
    border-radius: 14px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 1rem;
  }}
  .lut-alert-icon {{
    font-size: 1.8rem;
  }}
  .lut-alert-headline {{
    color: {COLORS['text']};
    font-size: 1.15rem;
    font-weight: 700;
  }}
  .lut-alert-sub {{
    color: {COLORS['muted']};
    font-size: 0.92rem;
  }}

  /* Order tile (for risk forecast triage queue) */
  .lut-tile-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }}
  .lut-tile {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    position: relative;
    overflow: hidden;
  }}
  .lut-tile.critical {{ border-color: rgba(239,68,68,0.5); box-shadow: 0 0 0 1px rgba(239,68,68,0.25); }}
  .lut-tile.high     {{ border-color: rgba(245,158,11,0.45); }}
  .lut-tile.medium   {{ border-color: rgba(96,165,250,0.30); }}
  .lut-tile-id {{
    color: {COLORS['gold']};
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.06em;
  }}
  .lut-tile-risk {{
    float: right;
    font-size: 1.5rem;
    font-weight: 800;
    color: {COLORS['gold_bright']};
  }}
  .lut-tile.critical .lut-tile-risk {{ color: {COLORS['red']}; }}
  .lut-tile.high .lut-tile-risk     {{ color: {COLORS['amber']}; }}
  .lut-tile-meta {{
    color: {COLORS['text']};
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0.4rem 0 0.2rem 0;
  }}
  .lut-tile-meta-sub {{
    color: {COLORS['muted']};
    font-size: 0.82rem;
    margin-bottom: 0.7rem;
  }}
  .lut-tile-action {{
    background: rgba(212,165,116,0.12);
    border-left: 3px solid {COLORS['gold']};
    color: {COLORS['text']};
    padding: 0.5rem 0.7rem;
    font-size: 0.85rem;
    border-radius: 6px;
    line-height: 1.35;
  }}

  /* Feature cards on landing */
  .lut-feature-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1rem;
    margin-top: 1.6rem;
  }}
  .lut-feature {{
    background: {COLORS['surface']};
    border: 1px solid {COLORS['border']};
    border-radius: 14px;
    padding: 1.4rem 1.5rem;
    transition: transform 0.18s ease, border-color 0.18s ease;
  }}
  .lut-feature:hover {{
    transform: translateY(-2px);
    border-color: {COLORS['gold']};
  }}
  .lut-feature-icon {{ font-size: 2rem; margin-bottom: 0.6rem; }}
  .lut-feature-title {{ color: {COLORS['gold']}; font-weight: 700; margin-bottom: 0.4rem; }}
  .lut-feature-body {{ color: {COLORS['muted']}; font-size: 0.92rem; line-height: 1.5; }}

  /* Tagline pill */
  .lut-pill {{
    display: inline-block;
    background: rgba(212,165,116,0.12);
    color: {COLORS['gold']};
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 0.8rem;
  }}

  /* Streamlit dataframe tweaks */
  .stDataFrame {{ border-radius: 10px; }}

  /* Hide default streamlit footer */
  footer {{ visibility: hidden; }}
</style>
""",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# HTML helper functions
# ---------------------------------------------------------------------------

def hero(eyebrow: str, title: str, subtitle: str, big_stat: str, vs_label: str, bench_stat: str, gap_pct: float) -> str:
    """Render the landing-page hero with a gap visualization."""
    fill_pct = max(0.0, min(100.0, gap_pct))
    return f"""
<div class="lut-hero">
  <div class="lut-hero-eyebrow">{eyebrow}</div>
  <div class="lut-hero-title">{title}</div>
  <div class="lut-hero-sub">{subtitle}</div>
  <div class="lut-hero-stat">
    <span class="lut-hero-stat-big">{big_stat}</span>
    <span class="lut-hero-stat-vs">{vs_label}</span>
    <span class="lut-hero-stat-bench">{bench_stat}</span>
  </div>
  <div class="lut-gap-bar">
    <div class="lut-gap-bar-fill" style="width:{fill_pct}%;"></div>
  </div>
</div>
"""


def kpi_card(label: str, value: str, sub: str, status: str = "gold", status_label: str | None = None) -> str:
    """Status-colored KPI card. status ∈ {green, amber, red, gold}."""
    badge = (
        f'<div class="lut-kpi-status {status}">{status_label}</div>'
        if status_label
        else ""
    )
    return f"""
<div class="lut-kpi {status}">
  <div class="lut-kpi-label">{label}</div>
  <div class="lut-kpi-value">{value}</div>
  <div class="lut-kpi-sub">{sub}</div>
  {badge}
</div>
"""


def kpi_grid(cards: list[str]) -> str:
    return f'<div class="lut-kpi-grid">{"".join(cards)}</div>'


def section(title: str, headline: str, body_html: str = "") -> str:
    return f"""
<div class="lut-section">
  <div class="lut-section-title">{title}</div>
  <div class="lut-section-headline">{headline}</div>
  {body_html}
</div>
"""


def alert(icon: str, headline: str, sub: str) -> str:
    return f"""
<div class="lut-alert">
  <div class="lut-alert-icon">{icon}</div>
  <div>
    <div class="lut-alert-headline">{headline}</div>
    <div class="lut-alert-sub">{sub}</div>
  </div>
</div>
"""


def order_tile(
    order_id: str,
    risk_pct: float,
    product: str,
    plant: str,
    qty: int,
    promised: str,
    action: str,
) -> str:
    if risk_pct >= 0.7:
        klass = "critical"
    elif risk_pct >= 0.5:
        klass = "high"
    else:
        klass = "medium"
    return f"""
<div class="lut-tile {klass}">
  <span class="lut-tile-risk">{risk_pct*100:.0f}%</span>
  <div class="lut-tile-id">{order_id}</div>
  <div class="lut-tile-meta">{product}</div>
  <div class="lut-tile-meta-sub">{plant} · qty {qty:,} · promised {promised}</div>
  <div class="lut-tile-action">{action}</div>
</div>
"""


def tile_grid(tiles: list[str]) -> str:
    return f'<div class="lut-tile-grid">{"".join(tiles)}</div>'


def feature_card(icon: str, title: str, body: str) -> str:
    return f"""
<div class="lut-feature">
  <div class="lut-feature-icon">{icon}</div>
  <div class="lut-feature-title">{title}</div>
  <div class="lut-feature-body">{body}</div>
</div>
"""


def feature_grid(cards: list[str]) -> str:
    return f'<div class="lut-feature-grid">{"".join(cards)}</div>'


def pill(text: str) -> str:
    return f'<span class="lut-pill">{text}</span>'


def kpi_status_for(value: float, target: float, higher_is_better: bool = True) -> tuple[str, str]:
    """Decide (color_class, status_label) for a KPI vs its target."""
    if higher_is_better:
        ratio = value / target if target else 0
        if ratio >= 1.0:
            return "green", "On target"
        if ratio >= 0.85:
            return "amber", "Below target"
        return "red", "Critical"
    else:
        if value <= target:
            return "green", "On target"
        if value <= target * 1.3:
            return "amber", "Above target"
        return "red", "Critical"
