"""Maintenance priority calculation and ranking tests."""

from __future__ import annotations

import pytest

from src.services.risk_engine import get_maintenance_priority


def test_maintenance_priority_structure(engine) -> None:
    """Verify priority response has required fields."""
    asset_id = engine.get_all_assets()[0]["asset_id"]
    priority = engine.get_maintenance_priority(asset_id)
    
    assert "asset_id" in priority
    assert "priority_score" in priority
    assert "priority_rank" in priority
    assert "total_assets" in priority
    assert "priority_reasons" in priority
    assert "recommended_action" in priority
    assert priority["asset_id"] == asset_id


def test_priority_score_range(engine) -> None:
    """Priority scores should be between 0 and 100."""
    for asset in engine.get_all_assets():
        priority = engine.get_maintenance_priority(asset["asset_id"])
        score = float(priority["priority_score"])
        assert 0.0 <= score <= 100.0, f"Score {score} out of range for {asset['asset_id']}"


def test_high_risk_assets_have_higher_priority(engine) -> None:
    """Assets with HIGH risk should have higher priority than LOW risk."""
    high_risk = [a for a in engine.get_all_assets() if a["risk_level"] == "HIGH"]
    low_risk = [a for a in engine.get_all_assets() if a["risk_level"] == "LOW"]
    
    if high_risk and low_risk:
        high_priorities = [
            engine.get_maintenance_priority(a["asset_id"])["priority_score"]
            for a in high_risk
        ]
        low_priorities = [
            engine.get_maintenance_priority(a["asset_id"])["priority_score"]
            for a in low_risk
        ]
        
        avg_high = sum(high_priorities) / len(high_priorities)
        avg_low = sum(low_priorities) / len(low_priorities)
        assert avg_high > avg_low, "High-risk assets should have higher average priority"


def test_not_ready_assets_prioritized(engine) -> None:
    """NOT_READY assets should generally have higher priority than READY."""
    not_ready = [a for a in engine.get_all_assets() if a["readiness_status"] == "NOT_READY"]
    ready = [a for a in engine.get_all_assets() if a["readiness_status"] == "READY"]
    
    if not_ready and ready:
        not_ready_priorities = [
            engine.get_maintenance_priority(a["asset_id"])["priority_score"]
            for a in not_ready
        ]
        ready_priorities = [
            engine.get_maintenance_priority(a["asset_id"])["priority_score"]
            for a in ready
        ]
        
        avg_not_ready = sum(not_ready_priorities) / len(not_ready_priorities)
        avg_ready = sum(ready_priorities) / len(ready_priorities)
        assert avg_not_ready > avg_ready, "NOT_READY assets should have higher average priority"


def test_priority_ranking_is_consistent(engine) -> None:
    """Rankings should be consistent and span 1 to N."""
    all_assets = engine.get_all_assets()
    rankings = [
        engine.get_maintenance_priority(a["asset_id"])["priority_rank"]
        for a in all_assets
    ]
    
    # All ranks should be unique
    assert len(rankings) == len(set(rankings)), "Rankings should be unique"
    
    # Ranks should span from 1 to total_assets
    assert min(rankings) == 1
    assert max(rankings) == len(all_assets)
    assert sorted(rankings) == list(range(1, len(all_assets) + 1))


def test_priority_reasons_are_meaningful(engine) -> None:
    """Priority reasons should be non-empty and informative."""
    for asset in engine.get_all_assets():
        priority = engine.get_maintenance_priority(asset["asset_id"])
        reasons = priority["priority_reasons"]
        
        assert isinstance(reasons, list)
        assert len(reasons) > 0, f"Asset {asset['asset_id']} should have priority reasons"
        
        for reason in reasons:
            assert isinstance(reason, str)
            assert reason.strip(), "Reasons should not be empty strings"


def test_top_priority_asset_is_most_urgent(engine) -> None:
    """The rank-1 asset should have the highest priority score."""
    all_assets = engine.get_all_assets()
    priorities = [
        engine.get_maintenance_priority(a["asset_id"])
        for a in all_assets
    ]
    
    top_priority = next(p for p in priorities if p["priority_rank"] == 1)
    max_score = max(p["priority_score"] for p in priorities)
    
    assert top_priority["priority_score"] == max_score


def test_module_level_api(engine) -> None:
    """Module-level get_maintenance_priority function should work."""
    asset_id = engine.get_all_assets()[0]["asset_id"]
    priority = get_maintenance_priority(asset_id)
    
    assert priority["asset_id"] == asset_id
    assert "priority_score" in priority
    assert "priority_rank" in priority
