"""Synthetic Lutron-flavored order dataset.

Generates ~15,000 orders over 24 months with patterns that mirror Lutron's
real-world pain points (configured products run late, supplier risk concentrates
in certain plants, Q4 surges, Mexico ramp variance, etc.) so the downstream
risk model has signal to learn.
"""

from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
N_ORDERS = 15_000
START_DATE = pd.Timestamp("2024-01-01")
END_DATE = pd.Timestamp("2025-12-31")

CUSTOMER_SEGMENTS = ["Luxury Dealer", "Big Box Retailer", "Commercial PM", "Hospitality"]
SEGMENT_WEIGHTS = [0.30, 0.25, 0.30, 0.15]

PRODUCT_LINES = ["Stock Shades", "Configured Shades", "Lighting Controls", "Bespoke Controls"]
PRODUCT_WEIGHTS = [0.35, 0.30, 0.20, 0.15]

PLANTS = ["Coopersburg PA", "Ireland", "Mexico", "China"]
PLANT_WEIGHTS = [0.45, 0.20, 0.20, 0.15]

DCS = ["Coopersburg DC", "Reno DC", "Florida DC"]
DC_WEIGHTS = [0.50, 0.25, 0.25]

# Per-product baseline late probabilities (before plant/segment/season modifiers).
PRODUCT_LATE_BASE = {
    "Stock Shades": 0.05,
    "Configured Shades": 0.18,
    "Lighting Controls": 0.10,
    "Bespoke Controls": 0.28,
}

# Plant variance adders.
PLANT_LATE_BASE = {
    "Coopersburg PA": 0.02,
    "Ireland": 0.04,
    "Mexico": 0.08,   # ramp issues
    "China": 0.06,
}

SEGMENT_BIAS = {
    "Luxury Dealer": 0.02,
    "Big Box Retailer": -0.02,
    "Commercial PM": 0.03,
    "Hospitality": 0.07,
}

# Promised lead times by product line (days).
PROMISED_LEAD_BY_PRODUCT = {
    "Stock Shades": (5, 1.5),
    "Configured Shades": (15, 4),
    "Lighting Controls": (10, 3),
    "Bespoke Controls": (28, 7),
}

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "orders.csv"


def _seasonality_multiplier(month: int) -> float:
    """Q4 holiday surge lifts late rates."""
    if month in (10, 11, 12):
        return 1.5
    if month in (6, 7):
        return 1.15
    return 1.0


def _mexico_ramp_multiplier(plant: str, order_date: pd.Timestamp) -> float:
    """Mexico plant ramp pain in months 6-10 of dataset (mid-2024)."""
    if plant != "Mexico":
        return 1.0
    if pd.Timestamp("2024-06-01") <= order_date <= pd.Timestamp("2024-10-31"):
        return 1.6
    return 1.0


def generate_orders(
    n: int = N_ORDERS,
    start: pd.Timestamp = START_DATE,
    end: pd.Timestamp = END_DATE,
    seed: int = SEED,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    order_dates = pd.to_datetime(
        rng.integers(
            low=start.value // 10**9,
            high=end.value // 10**9,
            size=n,
        ),
        unit="s",
    ).normalize()
    order_dates = pd.DatetimeIndex(sorted(order_dates))

    segments = rng.choice(CUSTOMER_SEGMENTS, size=n, p=SEGMENT_WEIGHTS)
    products = rng.choice(PRODUCT_LINES, size=n, p=PRODUCT_WEIGHTS)
    # Hospitality skews bespoke.
    hosp_mask = segments == "Hospitality"
    rebespoke = rng.random(hosp_mask.sum()) < 0.45
    products[hosp_mask] = np.where(rebespoke, "Bespoke Controls", products[hosp_mask])

    plants = rng.choice(PLANTS, size=n, p=PLANT_WEIGHTS)
    dcs = rng.choice(DCS, size=n, p=DC_WEIGHTS)

    # Quantities — log-normal, capped.
    quantities = np.clip(
        np.round(rng.lognormal(mean=2.5, sigma=1.1, size=n)).astype(int),
        1,
        2000,
    )

    # Configuration complexity 0-10, higher for configured/bespoke.
    base_complexity = rng.integers(0, 4, size=n)
    config_bonus = np.where(
        np.isin(products, ["Configured Shades", "Bespoke Controls"]),
        rng.integers(3, 8, size=n),
        0,
    )
    complexity = np.clip(base_complexity + config_bonus, 0, 10)

    # Supplier risk flag — concentrated in Mexico + Bespoke Controls.
    supplier_risk = (
        ((plants == "Mexico") & (rng.random(n) < 0.35))
        | ((products == "Bespoke Controls") & (rng.random(n) < 0.25))
        | (rng.random(n) < 0.05)
    ).astype(int)

    # Promised lead time.
    promised_lead = np.zeros(n)
    for prod, (mu, sigma) in PROMISED_LEAD_BY_PRODUCT.items():
        mask = products == prod
        promised_lead[mask] = np.clip(
            rng.normal(mu, sigma, size=mask.sum()), 1, None
        )
    promised_lead = np.round(promised_lead).astype(int)

    promised_dates = order_dates + pd.to_timedelta(promised_lead, unit="D")

    # Build per-row late probability.
    late_prob = np.zeros(n)
    for i in range(n):
        p = (
            PRODUCT_LATE_BASE[products[i]]
            + PLANT_LATE_BASE[plants[i]]
            + SEGMENT_BIAS[segments[i]]
        )
        # Complexity bumps it.
        p += 0.012 * complexity[i]
        # Supplier risk.
        if supplier_risk[i]:
            p += 0.25
        # Big orders.
        if quantities[i] > 500:
            p += 0.08
        # Seasonality.
        p *= _seasonality_multiplier(order_dates[i].month)
        # Mexico ramp window.
        p *= _mexico_ramp_multiplier(plants[i], order_dates[i])
        late_prob[i] = np.clip(p, 0.01, 0.92)

    is_late = rng.random(n) < late_prob

    # Slip days when late: gamma-ish; small early-shipments when on-time.
    slip = np.where(
        is_late,
        np.round(rng.gamma(shape=2.0, scale=4.0, size=n)).astype(int) + 1,
        -np.round(rng.gamma(shape=1.0, scale=1.2, size=n)).astype(int),
    )
    delivered_dates = promised_dates + pd.to_timedelta(slip, unit="D")
    shipped_dates = delivered_dates - pd.to_timedelta(
        rng.integers(1, 4, size=n), unit="D"
    )

    # In-full: bigger / more complex orders more likely partial.
    short_prob = np.clip(
        0.02 + 0.01 * complexity + (quantities > 500) * 0.06 + supplier_risk * 0.05,
        0,
        0.5,
    )
    in_full = rng.random(n) > short_prob

    on_time = ~is_late
    otif = on_time & in_full

    # Mark the most recent ~8% as still-open (no actual delivery yet).
    cutoff = pd.Timestamp("2025-11-15")
    is_open = order_dates >= cutoff
    delivered_dates = pd.Series(delivered_dates).where(~is_open, pd.NaT)
    shipped_dates = pd.Series(shipped_dates).where(~is_open, pd.NaT)
    on_time = pd.Series(on_time).where(~is_open, other=pd.NA)
    in_full = pd.Series(in_full).where(~is_open, other=pd.NA)
    otif = pd.Series(otif).where(~is_open, other=pd.NA)
    is_late_out = pd.Series(is_late).where(~is_open, other=pd.NA)

    # Approximate revenue per order — different price points by line.
    price_map = {
        "Stock Shades": 180,
        "Configured Shades": 420,
        "Lighting Controls": 260,
        "Bespoke Controls": 950,
    }
    unit_price = np.array([price_map[p] for p in products])
    revenue_usd = (unit_price * quantities * (0.85 + 0.3 * rng.random(n))).round(2)

    df = pd.DataFrame(
        {
            "order_id": [f"LUT-{100000 + i}" for i in range(n)],
            "order_date": order_dates,
            "promised_date": promised_dates,
            "shipped_date": shipped_dates,
            "delivered_date": delivered_dates,
            "customer_segment": segments,
            "product_line": products,
            "plant": plants,
            "distribution_center": dcs,
            "quantity": quantities,
            "config_complexity": complexity,
            "supplier_risk_flag": supplier_risk,
            "promised_lead_days": promised_lead,
            "actual_lead_days": (delivered_dates - order_dates).dt.days,
            "slip_days": slip,
            "is_late": is_late_out,
            "on_time": on_time,
            "in_full": in_full,
            "otif": otif,
            "is_open": is_open,
            "revenue_usd": revenue_usd,
        }
    )
    df = df.sort_values("order_date").reset_index(drop=True)
    return df


def ensure_data(force: bool = False) -> pd.DataFrame:
    """Load orders.csv, generating it if missing or `force=True`."""
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    if force or not DATA_PATH.exists():
        df = generate_orders()
        df.to_csv(DATA_PATH, index=False)
        return df
    return pd.read_csv(
        DATA_PATH,
        parse_dates=["order_date", "promised_date", "shipped_date", "delivered_date"],
    )


if __name__ == "__main__":
    df = ensure_data(force=True)
    closed = df[~df["is_open"]]
    print(f"Generated {len(df):,} orders -> {DATA_PATH}")
    print(f"Open orders: {df['is_open'].sum():,}")
    print(f"Closed orders late rate: {closed['is_late'].astype(float).mean():.1%}")
    print(f"Closed orders OTIF rate: {closed['otif'].astype(float).mean():.1%}")
