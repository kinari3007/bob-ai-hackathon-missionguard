"""Risk scoring, readiness, explainability, and API-contract tests."""

from __future__ import annotations

import pytest

from src.services.readiness import VALID_READINESS, VALID_RISK_LEVELS
from src.utils.exceptions import AssetNotFoundError


def test_risk_scores_generated_for_every_asset(engine) -> None:
    assets = engine.get_all_assets()
    assert len(assets) == 100
    for asset in assets:
        assert "health_score" in asset
        assert 0.0 <= float(asset["health_score"]) <= 100.0
        assert asset["recommended_action"]


def test_failure_probability_range(engine) -> None:
    for asset in engine.get_all_assets():
        prob = float(asset["failure_probability"])
        assert 0.0 <= prob <= 1.0


def test_risk_level_validity(engine) -> None:
    for asset in engine.get_all_assets():
        assert asset["risk_level"] in VALID_RISK_LEVELS


def test_readiness_status_validity(engine) -> None:
    for asset in engine.get_all_assets():
        assert asset["readiness_status"] in VALID_READINESS


def test_readiness_follows_risk_evidence(engine) -> None:
    for asset in engine.get_all_assets():
        if asset["risk_level"] == "HIGH":
            assert asset["readiness_status"] == "NOT_READY"
        if asset["readiness_status"] == "READY":
            assert asset["risk_level"] == "LOW"


def test_explainability_output(engine) -> None:
    high = [a for a in engine.get_all_assets() if a["risk_level"] == "HIGH"]
    assert high, "synthetic fleet should include at least one HIGH-risk asset"
    sample = engine.get_failure_risk(high[0]["asset_id"])
    assert isinstance(sample["top_risk_factors"], list)
    assert 1 <= len(sample["top_risk_factors"]) <= 3
    for factor in sample["top_risk_factors"]:
        assert isinstance(factor, str)
        assert factor.strip()


def test_api_get_asset_status(engine) -> None:
    asset_id = engine.get_all_assets()[0]["asset_id"]
    status = engine.get_asset_status(asset_id)
    assert status["asset_id"] == asset_id
    assert status["readiness_status"] in VALID_READINESS
    assert "recommended_action" in status


def test_unknown_asset_handling(engine) -> None:
    with pytest.raises(AssetNotFoundError, match="UNKNOWN-999"):
        engine.get_asset_status("UNKNOWN-999")
    with pytest.raises(AssetNotFoundError):
        engine.get_failure_risk("MISSING")


def test_summary_counts_match_records(engine) -> None:
    stats = engine.summary()
    assets = engine.get_all_assets()
    assert stats["total_assets"] == len(assets)
    assert stats["READY"] + stats["WARNING"] + stats["NOT_READY"] == len(assets)
    assert stats["HIGH"] == sum(1 for a in assets if a["risk_level"] == "HIGH")
