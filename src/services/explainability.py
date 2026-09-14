"""Turn model contributions into human-readable risk factors."""

from __future__ import annotations

from src.models.risk_model import display_name, feature_contributions
from src.models.risk_model import FittedRiskModel
from src.utils.config import ThresholdConfig
import pandas as pd


def explain_asset(
    row: pd.Series,
    model: FittedRiskModel,
    thresholds: ThresholdConfig,
) -> list[str]:
    """Return the top positive drivers of failure risk for one asset."""
    ranked = feature_contributions(row, model)
    positive = [(name, score) for name, score in ranked if score > 0.05]

    if not positive:
        # Still report the least-favorable features so callers always get context.
        positive = list(ranked[: thresholds.top_factor_count])

    names: list[str] = []
    seen: set[str] = set()
    for feature, _score in positive:
        label = display_name(feature)
        if label in seen:
            continue
        seen.add(label)
        names.append(label)
        if len(names) >= thresholds.top_factor_count:
            break
    return names
