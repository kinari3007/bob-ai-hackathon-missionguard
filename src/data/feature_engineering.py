"""Derived features used by the hybrid risk model."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd

from src.data.generate_dataset import REF_DATE

MODEL_FEATURE_COLUMNS: tuple[str, ...] = (
    "engine_temperature",
    "vibration_level",
    "operating_hours",
    "component_age",
    "hours_since_service",
    "maintenance_age",
    "fuel_consumption",
    "service_count",
    "days_since_service",
    "expected_service_gap",
    "temp_vibration_stress",
    "utilization_intensity",
    "fuel_per_hour",
)


def engineer_features(frame: pd.DataFrame, reference_date: date | None = None) -> pd.DataFrame:
    """Add derived columns that encode maintenance pressure and stress."""
    ref = reference_date or REF_DATE
    out = frame.copy()

    service_dates = pd.to_datetime(out["last_service_date"], errors="coerce")
    ref_ts = pd.Timestamp(ref)
    days = (ref_ts - service_dates).dt.days.astype(float)
    days = days.clip(lower=0.0).fillna(days.median() if days.notna().any() else 30.0)
    out["days_since_service"] = days

    expected_from_usage = out["operating_hours"] / out["service_count"].clip(lower=1)
    out["expected_service_gap"] = out["hours_since_service"] / expected_from_usage.replace(0, np.nan)
    out["expected_service_gap"] = out["expected_service_gap"].replace([np.inf, -np.inf], np.nan)
    out["expected_service_gap"] = out["expected_service_gap"].fillna(1.0)

    temp_norm = (out["engine_temperature"] - out["engine_temperature"].median()) / (
        out["engine_temperature"].std(ddof=0) + 1e-6
    )
    vib_norm = (out["vibration_level"] - out["vibration_level"].median()) / (
        out["vibration_level"].std(ddof=0) + 1e-6
    )
    out["temp_vibration_stress"] = temp_norm.clip(-4, 4) + vib_norm.clip(-4, 4)

    age_days = (out["component_age"] * 30.0).clip(lower=1.0)
    out["utilization_intensity"] = out["operating_hours"] / age_days
    out["fuel_per_hour"] = out["fuel_consumption"] / out["operating_hours"].clip(lower=1.0)
    return out


def model_feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """Select the numeric matrix consumed by the classifier."""
    missing = [col for col in MODEL_FEATURE_COLUMNS if col not in frame.columns]
    if missing:
        raise ValueError("Feature frame missing columns: " + ", ".join(missing))
    return frame.loc[:, list(MODEL_FEATURE_COLUMNS)].astype(float)
