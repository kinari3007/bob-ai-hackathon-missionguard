"""Hybrid interpretable risk model (logistic regression + domain score)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from src.data.feature_engineering import MODEL_FEATURE_COLUMNS, model_feature_matrix
from src.utils.config import FEATURE_DISPLAY_NAMES, TARGET_COLUMN, ThresholdConfig


@dataclass
class FittedRiskModel:
    """In-memory fitted model plus the scaler used at training time."""

    scaler: StandardScaler
    classifier: LogisticRegression
    feature_names: tuple[str, ...]
    domain_medians: dict[str, float]
    domain_iqr: dict[str, float]


DOMAIN_WEIGHTS: dict[str, float] = {
    "engine_temperature": 0.16,
    "vibration_level": 0.18,
    "operating_hours": 0.12,
    "component_age": 0.12,
    "hours_since_service": 0.16,
    "maintenance_age": 0.10,
    "fuel_consumption": 0.08,
    "expected_service_gap": 0.08,
}


def _robust_scale(value: float, median: float, iqr: float) -> float:
    scale = iqr if iqr > 1e-6 else 1.0
    return float(np.clip((value - median) / scale, -3.0, 3.0))


def domain_failure_probability(row: pd.Series, model: FittedRiskModel) -> float:
    """Heuristic 0–1 risk from how far drivers sit above fleet medians."""
    score = 0.0
    weight_sum = 0.0
    for name, weight in DOMAIN_WEIGHTS.items():
        if name not in row:
            continue
        z = _robust_scale(float(row[name]), model.domain_medians[name], model.domain_iqr[name])
        # service_count is inverted elsewhere; remaining drivers increase risk when high.
        score += weight * max(0.0, z)
        weight_sum += weight
    if "service_count" in row:
        z_svc = _robust_scale(
            float(row["service_count"]),
            model.domain_medians.get("service_count", float(row["service_count"])),
            model.domain_iqr.get("service_count", 1.0),
        )
        score += 0.08 * max(0.0, -z_svc)
        weight_sum += 0.08
    if weight_sum <= 0:
        return 0.5
    # Map a typical 0–1.5 weighted score onto a probability.
    return float(np.clip(0.12 + 0.38 * (score / weight_sum * 2.0), 0.02, 0.98))


def fit_risk_model(featured: pd.DataFrame, random_seed: int = 42) -> FittedRiskModel:
    """Train a logistic classifier on engineered features and a synthetic label."""
    features = model_feature_matrix(featured)
    scaler = StandardScaler()
    scaled = scaler.fit_transform(features)

    if TARGET_COLUMN in featured.columns and featured[TARGET_COLUMN].nunique() > 1:
        y = featured[TARGET_COLUMN].astype(int).to_numpy()
    else:
        # Fallback label: upper quartile of a simple stress sum.
        stress = features[["engine_temperature", "vibration_level", "hours_since_service"]].rank().mean(axis=1)
        y = (stress >= stress.quantile(0.7)).astype(int).to_numpy()

    classifier = LogisticRegression(
        random_state=random_seed,
        max_iter=500,
        class_weight="balanced",
        solver="lbfgs",
    )
    classifier.fit(scaled, y)

    medians: dict[str, float] = {}
    iqrs: dict[str, float] = {}
    for column in list(DOMAIN_WEIGHTS) + ["service_count"]:
        if column not in featured.columns:
            continue
        series = featured[column].astype(float)
        medians[column] = float(series.median())
        q75 = float(series.quantile(0.75))
        q25 = float(series.quantile(0.25))
        iqrs[column] = max(q75 - q25, 1e-6)

    return FittedRiskModel(
        scaler=scaler,
        classifier=classifier,
        feature_names=tuple(MODEL_FEATURE_COLUMNS),
        domain_medians=medians,
        domain_iqr=iqrs,
    )


def ml_failure_probability(featured: pd.DataFrame, model: FittedRiskModel) -> np.ndarray:
    features = featured.loc[:, list(model.feature_names)].astype(float)
    scaled = model.scaler.transform(features)
    proba = model.classifier.predict_proba(scaled)
    # Column 1 is the failure class if classes_ is [0, 1].
    classes = list(model.classifier.classes_)
    if 1 in classes:
        return proba[:, classes.index(1)]
    return np.zeros(len(featured), dtype=float)


def blended_failure_probability(
    featured: pd.DataFrame,
    model: FittedRiskModel,
    thresholds: ThresholdConfig,
) -> np.ndarray:
    ml_p = ml_failure_probability(featured, model)
    domain_p = np.array(
        [domain_failure_probability(row, model) for _, row in featured.iterrows()],
        dtype=float,
    )
    w = thresholds.ml_blend_weight
    blended = w * ml_p + (1.0 - w) * domain_p
    return np.clip(blended, 0.01, 0.99)


def feature_contributions(row: pd.Series, model: FittedRiskModel) -> list[tuple[str, float]]:
    """Return (feature, contribution) pairs; positive values raise failure odds."""
    values = np.array([float(row[name]) for name in model.feature_names], dtype=float).reshape(1, -1)
    scaled = model.scaler.transform(values)[0]
    coef = model.classifier.coef_[0]
    contrib = coef * scaled
    ranked = sorted(
        zip(model.feature_names, contrib.tolist()),
        key=lambda item: item[1],
        reverse=True,
    )
    return ranked


def display_name(feature: str) -> str:
    return FEATURE_DISPLAY_NAMES.get(feature, feature.replace("_", " "))
