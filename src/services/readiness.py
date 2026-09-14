"""Map health/risk evidence onto mission-readiness labels."""

from __future__ import annotations

from src.utils.config import ThresholdConfig


VALID_RISK_LEVELS = ("LOW", "MEDIUM", "HIGH")
VALID_READINESS = ("READY", "WARNING", "NOT_READY")


def classify_risk_level(failure_probability: float, health_score: float, thresholds: ThresholdConfig) -> str:
    """Derive LOW/MEDIUM/HIGH from probability and health, using config cut-offs."""
    if failure_probability >= thresholds.high_risk_probability or health_score <= thresholds.not_ready_health_score:
        return "HIGH"
    if failure_probability >= thresholds.medium_risk_probability or health_score <= thresholds.warning_health_score:
        return "MEDIUM"
    return "LOW"


def classify_readiness(risk_level: str, health_score: float, thresholds: ThresholdConfig) -> str:
    """Derive READY/WARNING/NOT_READY from risk evidence, not from asset IDs."""
    if risk_level == "HIGH" or health_score < thresholds.not_ready_health_score:
        return "NOT_READY"
    if risk_level == "MEDIUM" or health_score < thresholds.warning_health_score:
        return "WARNING"
    return "READY"


def recommend_action(readiness_status: str, top_risk_factors: list[str]) -> str:
    """Pick a maintenance action from readiness plus the leading factor."""
    lead = top_risk_factors[0].lower() if top_risk_factors else ""

    if readiness_status == "NOT_READY":
        if "vibration" in lead:
            return "Ground the asset and inspect rotating components before the next mission"
        if "temperature" in lead:
            return "Schedule inspection and cooling-system / engine diagnostics"
        if "maintenance" in lead or "service" in lead:
            return "Schedule inspection and preventive maintenance"
        return "Schedule inspection and preventive maintenance"

    if readiness_status == "WARNING":
        if "operating hours" in lead:
            return "Plan service within the next cycle and reduce peak utilization"
        return "Increase monitoring and plan service within the next cycle"

    return "Continue routine maintenance schedule"
