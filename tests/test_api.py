"""FastAPI endpoint tests for MissionGuard backend."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    """Test GET /health returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "MissionGuard API"
    assert "version" in data


def test_list_assets_endpoint() -> None:
    """Test GET /assets returns all 100 assets."""
    response = client.get("/assets")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 100
    
    # Verify structure of first asset
    asset = data[0]
    assert "asset_id" in asset
    assert "asset_type" in asset
    assert "health_score" in asset
    assert "failure_probability" in asset
    assert "risk_level" in asset
    assert "readiness_status" in asset
    assert "top_risk_factors" in asset
    assert "recommended_action" in asset


def test_asset_status_valid_id() -> None:
    """Test GET /assets/{id}/status returns correct structure for valid asset."""
    response = client.get("/assets/A-001/status")
    assert response.status_code == 200
    data = response.json()
    
    assert data["asset_id"] == "A-001"
    assert "asset_type" in data
    assert "readiness_status" in data
    assert data["readiness_status"] in ["READY", "WARNING", "NOT_READY"]
    assert "health_score" in data
    assert 0.0 <= data["health_score"] <= 100.0
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "top_risk_factors" in data
    assert isinstance(data["top_risk_factors"], list)
    assert "recommended_action" in data


def test_asset_risk_valid_id() -> None:
    """Test GET /assets/{id}/risk returns correct structure for valid asset."""
    response = client.get("/assets/A-050/risk")
    assert response.status_code == 200
    data = response.json()
    
    assert data["asset_id"] == "A-050"
    assert "health_score" in data
    assert 0.0 <= data["health_score"] <= 100.0
    assert "failure_probability" in data
    assert 0.0 <= data["failure_probability"] <= 1.0
    assert "risk_level" in data
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
    assert "top_risk_factors" in data
    assert isinstance(data["top_risk_factors"], list)
    assert len(data["top_risk_factors"]) > 0
    assert "recommended_action" in data


def test_asset_priority_valid_id() -> None:
    """Test GET /assets/{id}/priority returns correct structure for valid asset."""
    response = client.get("/assets/A-100/priority")
    assert response.status_code == 200
    data = response.json()
    
    assert data["asset_id"] == "A-100"
    assert "asset_type" in data
    assert "priority_score" in data
    assert 0.0 <= data["priority_score"] <= 100.0
    assert "priority_rank" in data
    assert 1 <= data["priority_rank"] <= 100
    assert "total_assets" in data
    assert data["total_assets"] == 100
    assert "readiness_status" in data
    assert "risk_level" in data
    assert "health_score" in data
    assert "priority_reasons" in data
    assert isinstance(data["priority_reasons"], list)
    assert len(data["priority_reasons"]) > 0
    assert "recommended_action" in data


def test_asset_status_unknown_id_returns_404() -> None:
    """Test GET /assets/{unknown_id}/status returns 404."""
    response = client.get("/assets/UNKNOWN-999/status")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "UNKNOWN-999" in data["detail"]


def test_asset_risk_unknown_id_returns_404() -> None:
    """Test GET /assets/{unknown_id}/risk returns 404."""
    response = client.get("/assets/INVALID/risk")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "INVALID" in data["detail"]


def test_asset_priority_unknown_id_returns_404() -> None:
    """Test GET /assets/{unknown_id}/priority returns 404."""
    response = client.get("/assets/DOES-NOT-EXIST/priority")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "DOES-NOT-EXIST" in data["detail"]


def test_api_returns_real_ml_data() -> None:
    """Verify API returns data from ML engine, not mock data."""
    # Get multiple assets and verify they have different scores
    assets = client.get("/assets").json()
    health_scores = [a["health_score"] for a in assets]
    
    # Should have variety of scores
    assert len(set(health_scores)) > 10, "Health scores should vary across fleet"
    
    # Should have all risk levels represented
    risk_levels = {a["risk_level"] for a in assets}
    assert "LOW" in risk_levels
    assert "MEDIUM" in risk_levels
    assert "HIGH" in risk_levels
    
    # Should have all readiness statuses represented
    readiness = {a["readiness_status"] for a in assets}
    assert "READY" in readiness
    assert "WARNING" in readiness
    assert "NOT_READY" in readiness


def test_priority_ranking_is_consistent() -> None:
    """Verify priority rankings are deterministic and sensible."""
    # Get priorities for multiple assets
    priorities = [
        client.get(f"/assets/A-{i:03d}/priority").json()
        for i in range(1, 11)
    ]
    
    # All should return 200
    assert all("priority_rank" in p for p in priorities)
    
    # Ranks should be unique
    ranks = [p["priority_rank"] for p in priorities]
    assert len(ranks) == len(set(ranks))
    
    # Ranks should be in valid range
    assert all(1 <= r <= 100 for r in ranks)


def test_docs_endpoint_accessible() -> None:
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    openapi_spec = response.json()
    assert "openapi" in openapi_spec
    assert "paths" in openapi_spec
    assert "/assets" in openapi_spec["paths"]
    assert "/health" in openapi_spec["paths"]
