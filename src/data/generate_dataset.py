"""Reproducible synthetic fleet dataset for the MissionGuard prototype.

All values are fictional. They are generated from domain-inspired relationships
plus noise so a downstream model can learn risk without a trivial rule.
"""

from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src.utils.config import DEFAULT_CONFIG, AppConfig

REF_DATE = date(2026, 9, 14)

# Typical operating envelopes by fictional asset class (not real military specs).
TYPE_PROFILES: dict[str, dict[str, float]] = {
    "UAV": {
        "engine_temperature": 82.0,
        "vibration_level": 1.8,
        "operating_hours": 420.0,
        "component_age": 16.0,
        "fuel_consumption": 12.5,
        "hours_per_day": 3.5,
    },
    "Ground Vehicle": {
        "engine_temperature": 94.0,
        "vibration_level": 3.4,
        "operating_hours": 1400.0,
        "component_age": 36.0,
        "fuel_consumption": 38.0,
        "hours_per_day": 6.0,
    },
    "Generator": {
        "engine_temperature": 88.0,
        "vibration_level": 1.6,
        "operating_hours": 2100.0,
        "component_age": 48.0,
        "fuel_consumption": 22.0,
        "hours_per_day": 10.0,
    },
    "Communications Relay": {
        "engine_temperature": 54.0,
        "vibration_level": 0.6,
        "operating_hours": 780.0,
        "component_age": 24.0,
        "fuel_consumption": 4.5,
        "hours_per_day": 18.0,
    },
    "Rotary Wing": {
        "engine_temperature": 108.0,
        "vibration_level": 4.2,
        "operating_hours": 900.0,
        "component_age": 28.0,
        "fuel_consumption": 72.0,
        "hours_per_day": 2.8,
    },
}

TYPE_NAMES = tuple(TYPE_PROFILES.keys())
TYPE_WEIGHTS = (0.24, 0.26, 0.18, 0.16, 0.16)

# Mixture of latent stress regimes: healthy / warning / high-risk.
REGIME_WEIGHTS = (0.40, 0.35, 0.25)
REGIME_OFFSETS = {
    0: {  # healthy
        "temp": -7.0,
        "vib": -0.45,
        "hours": 0.78,
        "age": 0.80,
        "service_delay": 0.45,
        "fuel": 0.88,
        "services_factor": 1.25,
    },
    1: {  # warning
        "temp": 4.5,
        "vib": 0.35,
        "hours": 1.05,
        "age": 1.10,
        "service_delay": 1.05,
        "fuel": 1.08,
        "services_factor": 0.95,
    },
    2: {  # high-risk
        "temp": 16.0,
        "vib": 1.35,
        "hours": 1.45,
        "age": 1.40,
        "service_delay": 2.10,
        "fuel": 1.32,
        "services_factor": 0.55,
    },
}


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -20.0, 20.0)))


def generate_assets_dataframe(
    n_assets: int | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    """Build a synthetic asset table with correlated, noisy risk drivers."""
    cfg = DEFAULT_CONFIG
    n_assets = n_assets if n_assets is not None else cfg.n_assets
    seed = seed if seed is not None else cfg.random_seed
    rng = np.random.default_rng(seed)

    asset_types = rng.choice(TYPE_NAMES, size=n_assets, p=TYPE_WEIGHTS)
    regimes = rng.choice([0, 1, 2], size=n_assets, p=REGIME_WEIGHTS)

    rows: list[dict[str, object]] = []
    latent_scores: list[float] = []

    for i in range(n_assets):
        asset_type = str(asset_types[i])
        regime = int(regimes[i])
        profile = TYPE_PROFILES[asset_type]
        off = REGIME_OFFSETS[regime]

        # Independent noise so regime is not a perfect lookup table.
        temp = (
            profile["engine_temperature"]
            + off["temp"]
            + rng.normal(0.0, 4.5)
        )
        vib = max(
            0.05,
            profile["vibration_level"] + off["vib"] + rng.normal(0.0, 0.35),
        )
        component_age = max(
            3.0,
            profile["component_age"] * off["age"] * rng.lognormal(0.0, 0.18),
        )
        operating_hours = max(
            40.0,
            profile["operating_hours"] * off["hours"] * rng.lognormal(0.0, 0.22),
        )

        hours_per_day = max(0.4, profile["hours_per_day"] * rng.lognormal(0.0, 0.15))
        calendar_days = max(30.0, (component_age * 30.0) * rng.uniform(0.85, 1.15))
        # Keep hours loosely consistent with age and utilization.
        operating_hours = max(40.0, 0.55 * operating_hours + 0.45 * hours_per_day * calendar_days)

        expected_interval_hours = max(40.0, 180.0 * rng.lognormal(0.0, 0.12))
        expected_services = max(1.0, operating_hours / expected_interval_hours)
        service_count = max(
            0,
            int(round(expected_services * off["services_factor"] + rng.normal(0.0, 1.1))),
        )

        days_since_service = max(
            1.0,
            (18.0 + 22.0 * off["service_delay"]) * rng.lognormal(0.0, 0.35),
        )
        if regime == 2 and rng.random() < 0.15:
            # Occasional recently serviced but still stressed asset (not a pure rule).
            days_since_service = float(rng.integers(4, 18))
        if regime == 0 and rng.random() < 0.12:
            # Occasional overdue healthy-looking asset.
            days_since_service = float(rng.integers(50, 95))

        hours_since_service = max(2.0, days_since_service * hours_per_day * rng.uniform(0.75, 1.25))
        maintenance_age = max(
            1.0,
            (component_age * 0.35 * off["service_delay"]) + rng.normal(0.0, 2.5),
        )

        fuel = max(
            0.8,
            profile["fuel_consumption"]
            * off["fuel"]
            * (1.0 + 0.08 * (temp - profile["engine_temperature"]) / 10.0)
            * (1.0 + 0.04 * max(0.0, vib - profile["vibration_level"]))
            * rng.lognormal(0.0, 0.10),
        )

        last_service = REF_DATE - timedelta(days=int(round(days_since_service)))

        # Latent failure tendency: weighted drivers + residual noise.
        temp_z = (temp - profile["engine_temperature"]) / 8.0
        vib_z = (vib - profile["vibration_level"]) / 0.7
        hours_z = (operating_hours / max(profile["operating_hours"], 1.0)) - 1.0
        age_z = (component_age / max(profile["component_age"], 1.0)) - 1.0
        svc_z = (hours_since_service / 80.0) - 0.6
        maint_z = (maintenance_age / 12.0) - 0.5
        fuel_z = (fuel / max(profile["fuel_consumption"], 1.0)) - 1.0
        sparse_z = (expected_services - service_count) / 3.0

        latent = (
            0.22 * temp_z
            + 0.24 * vib_z
            + 0.14 * hours_z
            + 0.14 * age_z
            + 0.18 * svc_z
            + 0.12 * maint_z
            + 0.10 * fuel_z
            + 0.16 * sparse_z
            + rng.normal(0.0, 0.45)
        )
        latent_scores.append(float(latent))

        rows.append(
            {
                "asset_id": f"A-{i + 1:03d}",
                "asset_type": asset_type,
                "engine_temperature": round(float(temp), 2),
                "vibration_level": round(float(vib), 3),
                "operating_hours": round(float(operating_hours), 1),
                "component_age": round(float(component_age), 1),
                "hours_since_service": round(float(hours_since_service), 1),
                "maintenance_age": round(float(maintenance_age), 1),
                "fuel_consumption": round(float(fuel), 2),
                "service_count": int(service_count),
                "last_service_date": last_service.isoformat(),
            }
        )

    frame = pd.DataFrame(rows)
    latent_arr = np.asarray(latent_scores, dtype=float)
    # Center latent scores so labels are mixed rather than all-positive.
    latent_arr = (latent_arr - np.median(latent_arr)) / (np.std(latent_arr) + 1e-6)
    failure_p = _sigmoid(1.15 * latent_arr - 0.35)
    labels = (rng.uniform(0.0, 1.0, size=n_assets) < failure_p).astype(int)
    frame["failure_label"] = labels
    return frame


def save_dataset(path: Path | None = None, config: AppConfig | None = None) -> Path:
    """Generate the synthetic CSV and return the written path."""
    config = config or DEFAULT_CONFIG
    path = Path(path) if path is not None else config.data_path
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_assets_dataframe(n_assets=config.n_assets, seed=config.random_seed)
    frame.to_csv(path, index=False)
    return path


def main() -> None:
    path = save_dataset()
    frame = pd.read_csv(path)
    print(f"Wrote {len(frame)} assets to {path}")
    print(frame["asset_type"].value_counts().to_string())
    print("failure_label counts:")
    print(frame["failure_label"].value_counts().to_string())


if __name__ == "__main__":
    main()
