"""Late-delivery risk model for open orders.

Trains a HistGradientBoostingClassifier on closed orders, exports per-order
risk scores for open orders, and surfaces feature importances for the Root
Cause page. Cached to disk so the Streamlit app starts instantly on rerun.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.inspection import permutation_importance
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

MODEL_PATH = Path(__file__).resolve().parent.parent / "data" / "risk_model.pkl"

CATEGORICAL_FEATURES = [
    "customer_segment",
    "product_line",
    "plant",
    "distribution_center",
]
NUMERIC_FEATURES = [
    "quantity",
    "config_complexity",
    "supplier_risk_flag",
    "promised_lead_days",
    "order_month",
]
FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Friendlier labels for display.
FEATURE_LABELS = {
    "customer_segment": "Customer Segment",
    "product_line": "Product Line",
    "plant": "Plant",
    "distribution_center": "Distribution Center",
    "quantity": "Order Quantity",
    "config_complexity": "Configuration Complexity",
    "supplier_risk_flag": "Supplier Risk Flag",
    "promised_lead_days": "Promised Lead Time",
    "order_month": "Order Month (seasonality)",
}

# Suggested action for the highest-contributing feature.
ACTION_BY_FEATURE = {
    "supplier_risk_flag": "Engage supplier — escalate component readiness",
    "config_complexity": "Expedite engineering review for configuration",
    "plant": "Reroute capacity / coordinate with plant ops",
    "quantity": "Flag as large-order — schedule capacity buffer",
    "product_line": "Apply product-line specific playbook",
    "customer_segment": "Loop in segment account team for status update",
    "distribution_center": "Coordinate with DC for staging priority",
    "promised_lead_days": "Reset customer expectation on promise date",
    "order_month": "Apply seasonal-surge mitigations",
}


@dataclass
class TrainedModel:
    pipeline: Pipeline
    auc: float
    feature_importance: pd.DataFrame  # columns: feature, importance


def _build_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["order_month"] = out["order_date"].dt.month
    return out[FEATURES]


def _build_pipeline() -> Pipeline:
    pre = ColumnTransformer(
        transformers=[
            (
                "cat",
                OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1),
                CATEGORICAL_FEATURES,
            ),
            ("num", "passthrough", NUMERIC_FEATURES),
        ]
    )
    return Pipeline(
        steps=[
            ("pre", pre),
            (
                "clf",
                HistGradientBoostingClassifier(
                    max_depth=6,
                    learning_rate=0.08,
                    max_iter=300,
                    random_state=42,
                ),
            ),
        ]
    )


def train(df: pd.DataFrame) -> TrainedModel:
    closed = df[df["is_open"] == False].copy()  # noqa: E712
    X = _build_features(closed)
    y = closed["is_late"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    pipe = _build_pipeline()
    pipe.fit(X_train, y_train)
    auc = roc_auc_score(y_test, pipe.predict_proba(X_test)[:, 1])

    # Permutation importance on a sample for speed.
    sample = X_test.sample(min(2000, len(X_test)), random_state=0)
    sample_y = y_test.loc[sample.index]
    perm = permutation_importance(
        pipe, sample, sample_y, n_repeats=5, random_state=0, n_jobs=1
    )
    importance_df = (
        pd.DataFrame({"feature": FEATURES, "importance": perm.importances_mean})
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    return TrainedModel(pipeline=pipe, auc=float(auc), feature_importance=importance_df)


def save(model: TrainedModel, path: Path = MODEL_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load(path: Path = MODEL_PATH) -> TrainedModel:
    return joblib.load(path)


def ensure_model(df: pd.DataFrame, force: bool = False) -> TrainedModel:
    if not force and MODEL_PATH.exists():
        try:
            return load()
        except Exception:
            pass
    model = train(df)
    save(model)
    return model


def score_open_orders(df: pd.DataFrame, model: TrainedModel) -> pd.DataFrame:
    open_df = df[df["is_open"] == True].copy()  # noqa: E712
    if open_df.empty:
        open_df["risk_score"] = []
        open_df["top_driver"] = []
        open_df["suggested_action"] = []
        return open_df

    X = _build_features(open_df)
    proba = model.pipeline.predict_proba(X)[:, 1]
    open_df["risk_score"] = proba

    # Rule-based "top driver" — heuristic rather than per-row SHAP, but maps
    # cleanly to the DEC's playbook actions and is fast enough to compute live.
    drivers = []
    for _, row in open_df.iterrows():
        candidates = []
        if row["supplier_risk_flag"] == 1:
            candidates.append(("supplier_risk_flag", 0.9))
        if row["config_complexity"] >= 7:
            candidates.append(("config_complexity", 0.8))
        if row["plant"] == "Mexico":
            candidates.append(("plant", 0.7))
        if row["quantity"] > 500:
            candidates.append(("quantity", 0.65))
        if row["product_line"] in ("Configured Shades", "Bespoke Controls"):
            candidates.append(("product_line", 0.55))
        if row["customer_segment"] == "Hospitality":
            candidates.append(("customer_segment", 0.45))
        if not candidates:
            candidates.append(("promised_lead_days", 0.3))
        drivers.append(max(candidates, key=lambda c: c[1])[0])
    open_df["top_driver"] = drivers
    open_df["top_driver_label"] = open_df["top_driver"].map(FEATURE_LABELS)
    open_df["suggested_action"] = open_df["top_driver"].map(ACTION_BY_FEATURE)
    return open_df


def per_order_contributions(row: pd.Series) -> pd.DataFrame:
    """Lightweight per-order driver breakdown for the drill-down expander.

    Not a full SHAP analysis — just the same rule-based scoring expressed
    as a small frame for charting.
    """
    items = [
        ("Supplier risk flag", 0.9 if row["supplier_risk_flag"] == 1 else 0.05),
        ("Configuration complexity", row["config_complexity"] / 10 * 0.8),
        ("Plant: " + str(row["plant"]), 0.7 if row["plant"] == "Mexico" else 0.2),
        (
            "Order size",
            min(row["quantity"] / 1000, 1.0) * 0.65,
        ),
        (
            "Product line: " + str(row["product_line"]),
            0.6
            if row["product_line"] in ("Configured Shades", "Bespoke Controls")
            else 0.15,
        ),
        (
            "Segment: " + str(row["customer_segment"]),
            0.45 if row["customer_segment"] == "Hospitality" else 0.15,
        ),
    ]
    return (
        pd.DataFrame(items, columns=["factor", "contribution"])
        .sort_values("contribution", ascending=True)
        .reset_index(drop=True)
    )
