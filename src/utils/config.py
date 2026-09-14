"""Project-wide configuration for the MissionGuard risk engine.

Thresholds live here so readiness and risk labels are not scattered as magic
numbers. Paths are resolved from the repository root, never from the CWD alone.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def project_root() -> Path:
    """Return the repository root (parent of ``src/``)."""
    return Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class ThresholdConfig:
    """Configurable cut-offs for risk level and mission readiness."""

    high_risk_probability: float = 0.65
    medium_risk_probability: float = 0.35
    not_ready_health_score: float = 40.0
    warning_health_score: float = 65.0
    ml_blend_weight: float = 0.70
    top_factor_count: int = 3


@dataclass(frozen=True)
class AppConfig:
    """Runtime configuration for data loading and modelling."""

    random_seed: int = 42
    n_assets: int = 100
    data_path: Path = field(default_factory=lambda: project_root() / "data" / "assets.csv")
    model_path: Path = field(default_factory=lambda: project_root() / "models" / "risk_model.joblib")
    thresholds: ThresholdConfig = field(default_factory=ThresholdConfig)


REQUIRED_COLUMNS: tuple[str, ...] = (
    "asset_id",
    "asset_type",
    "engine_temperature",
    "vibration_level",
    "operating_hours",
    "component_age",
    "hours_since_service",
    "maintenance_age",
    "fuel_consumption",
    "service_count",
    "last_service_date",
)

NUMERIC_COLUMNS: tuple[str, ...] = (
    "engine_temperature",
    "vibration_level",
    "operating_hours",
    "component_age",
    "hours_since_service",
    "maintenance_age",
    "fuel_consumption",
    "service_count",
)

CATEGORICAL_COLUMNS: tuple[str, ...] = ("asset_type",)

# Internal training label written by the synthetic generator. Not required at
# inference time if a fitted model is already present.
TARGET_COLUMN = "failure_label"

FEATURE_DISPLAY_NAMES: dict[str, str] = {
    "engine_temperature": "High engine temperature",
    "vibration_level": "High vibration level",
    "operating_hours": "High operating hours",
    "component_age": "Elevated component age",
    "hours_since_service": "Long interval since maintenance",
    "maintenance_age": "Stale major-maintenance cycle",
    "fuel_consumption": "Elevated fuel consumption",
    "service_count": "Sparse service history for usage",
    "days_since_service": "Many days since last service",
    "expected_service_gap": "Service interval longer than expected",
    "temp_vibration_stress": "Combined temperature and vibration stress",
    "utilization_intensity": "High utilization intensity",
    "fuel_per_hour": "Inefficient fuel burn rate",
}

DEFAULT_CONFIG = AppConfig()
