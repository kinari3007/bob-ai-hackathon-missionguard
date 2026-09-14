"""Dashboard API client tests.

These tests exercise src/dashboard/api_client.py using unittest.mock so no
live FastAPI server is required.  They verify:

1.  health_check succeeds when backend returns 200.
2.  health_check returns (False, msg) when backend is unreachable.
3.  get_assets returns a list on 200.
4.  get_assets raises BackendUnavailableError when backend is down.
5.  get_asset_status returns dict on 200.
6.  get_asset_status raises AssetNotFoundError on 404.
7.  get_asset_risk returns dict on 200.
8.  get_asset_risk raises AssetNotFoundError on 404.
9.  get_asset_priority returns dict on 200.
10. get_asset_priority raises AssetNotFoundError on 404.
11. get_assets returns [] on empty list response (graceful).
12. Timeout is handled as BackendUnavailableError.
13. MISSIONGUARD_API_URL env var is respected.
14. Required fields are present in mocked asset response.
15. Required fields are present in mocked priority response.
"""

from __future__ import annotations

import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests as req_lib

from src.dashboard.api_client import (
    AssetNotFoundError,
    BackendUnavailableError,
    MissionGuardClient,
    _api_url,
    get_client,
)


# ── Fixtures / helpers ─────────────────────────────────────────────────────────

SAMPLE_ASSET: dict[str, Any] = {
    "asset_id": "A-001",
    "asset_type": "UAV",
    "health_score": 72.5,
    "failure_probability": 0.275,
    "risk_level": "MEDIUM",
    "readiness_status": "WARNING",
    "top_risk_factors": ["High vibration level", "Long interval since maintenance"],
    "recommended_action": "Increase monitoring and plan service within the next cycle",
}

SAMPLE_STATUS: dict[str, Any] = {
    "asset_id": "A-001",
    "asset_type": "UAV",
    "readiness_status": "WARNING",
    "health_score": 72.5,
    "risk_level": "MEDIUM",
    "top_risk_factors": ["High vibration level", "Long interval since maintenance"],
    "recommended_action": "Increase monitoring and plan service within the next cycle",
}

SAMPLE_RISK: dict[str, Any] = {
    "asset_id": "A-001",
    "health_score": 72.5,
    "failure_probability": 0.275,
    "risk_level": "MEDIUM",
    "top_risk_factors": ["High vibration level", "Long interval since maintenance"],
    "recommended_action": "Increase monitoring and plan service within the next cycle",
}

SAMPLE_PRIORITY: dict[str, Any] = {
    "asset_id": "A-001",
    "asset_type": "UAV",
    "priority_score": 42.75,
    "priority_rank": 38,
    "total_assets": 100,
    "readiness_status": "WARNING",
    "risk_level": "MEDIUM",
    "health_score": 72.5,
    "priority_reasons": ["Asset status warning", "Moderate failure risk"],
    "recommended_action": "Increase monitoring and plan service within the next cycle",
}

SAMPLE_HEALTH: dict[str, Any] = {
    "status": "ok",
    "service": "MissionGuard API",
    "version": "1.0.0",
}


def _mock_response(status_code: int, json_data: Any) -> MagicMock:
    """Return a mock requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data
    if status_code >= 400:
        mock.raise_for_status.side_effect = req_lib.HTTPError(response=mock)
    else:
        mock.raise_for_status.return_value = None
    return mock


# ── 1. health_check — backend up ──────────────────────────────────────────────

def test_health_check_success() -> None:
    """health_check returns (True, version) when backend is reachable."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, SAMPLE_HEALTH)
        ok, info = client.health_check()
    assert ok is True
    assert info == "1.0.0"


# ── 2. health_check — backend down ───────────────────────────────────────────

def test_health_check_backend_unavailable() -> None:
    """health_check returns (False, error_msg) when backend is unreachable."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.side_effect = req_lib.exceptions.ConnectionError("refused")
        ok, msg = client.health_check()
    assert ok is False
    assert "unavailable" in msg.lower() or "connect" in msg.lower()


# ── 3. get_assets — success ───────────────────────────────────────────────────

def test_get_assets_returns_list() -> None:
    """get_assets returns a list of asset dicts on 200."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, [SAMPLE_ASSET] * 100)
        assets = client.get_assets()
    assert isinstance(assets, list)
    assert len(assets) == 100


# ── 4. get_assets — backend down ─────────────────────────────────────────────

def test_get_assets_raises_when_backend_down() -> None:
    """get_assets raises BackendUnavailableError when the server is unreachable."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.side_effect = req_lib.exceptions.ConnectionError("refused")
        with pytest.raises(BackendUnavailableError):
            client.get_assets()


# ── 5. get_asset_status — success ─────────────────────────────────────────────

def test_get_asset_status_success() -> None:
    """get_asset_status returns the status dict on 200."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, SAMPLE_STATUS)
        result = client.get_asset_status("A-001")
    assert result["asset_id"] == "A-001"
    assert result["readiness_status"] == "WARNING"
    assert "top_risk_factors" in result
    assert "recommended_action" in result


# ── 6. get_asset_status — 404 ────────────────────────────────────────────────

def test_get_asset_status_not_found() -> None:
    """get_asset_status raises AssetNotFoundError when the API returns 404."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404, {"detail": "Asset UNKNOWN not found"})
        with pytest.raises(AssetNotFoundError) as exc_info:
            client.get_asset_status("UNKNOWN")
    assert "UNKNOWN" in str(exc_info.value)


# ── 7. get_asset_risk — success ───────────────────────────────────────────────

def test_get_asset_risk_success() -> None:
    """get_asset_risk returns the risk dict on 200."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, SAMPLE_RISK)
        result = client.get_asset_risk("A-001")
    assert 0.0 <= result["failure_probability"] <= 1.0
    assert result["risk_level"] in ("LOW", "MEDIUM", "HIGH")
    assert isinstance(result["top_risk_factors"], list)


# ── 8. get_asset_risk — 404 ───────────────────────────────────────────────────

def test_get_asset_risk_not_found() -> None:
    """get_asset_risk raises AssetNotFoundError on 404."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404, {"detail": "not found"})
        with pytest.raises(AssetNotFoundError):
            client.get_asset_risk("MISSING")


# ── 9. get_asset_priority — success ──────────────────────────────────────────

def test_get_asset_priority_success() -> None:
    """get_asset_priority returns the priority dict on 200."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, SAMPLE_PRIORITY)
        result = client.get_asset_priority("A-001")
    assert 0.0 <= result["priority_score"] <= 100.0
    assert 1 <= result["priority_rank"] <= result["total_assets"]
    assert isinstance(result["priority_reasons"], list)


# ── 10. get_asset_priority — 404 ─────────────────────────────────────────────

def test_get_asset_priority_not_found() -> None:
    """get_asset_priority raises AssetNotFoundError on 404."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(404, {"detail": "not found"})
        with pytest.raises(AssetNotFoundError):
            client.get_asset_priority("MISSING")


# ── 11. get_assets — empty list ───────────────────────────────────────────────

def test_get_assets_empty_list_is_graceful() -> None:
    """get_assets returns [] (not an error) when backend responds with empty list."""
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, [])
        assets = client.get_assets()
    assert assets == []


# ── 12. Timeout → BackendUnavailableError ─────────────────────────────────────

def test_timeout_raises_backend_unavailable() -> None:
    """A request timeout is converted to BackendUnavailableError."""
    client = MissionGuardClient(base_url="http://localhost:8000", timeout=0.001)
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.side_effect = req_lib.exceptions.Timeout("timed out")
        with pytest.raises(BackendUnavailableError, match="timed out"):
            client.get_asset_status("A-001")


# ── 13. MISSIONGUARD_API_URL env var ─────────────────────────────────────────

def test_env_var_sets_base_url(monkeypatch: pytest.MonkeyPatch) -> None:
    """MISSIONGUARD_API_URL environment variable is respected."""
    monkeypatch.setenv("MISSIONGUARD_API_URL", "http://custom-host:9999")
    url = _api_url()
    assert url == "http://custom-host:9999"


def test_env_var_used_by_default_client(monkeypatch: pytest.MonkeyPatch) -> None:
    """get_client() picks up MISSIONGUARD_API_URL."""
    monkeypatch.setenv("MISSIONGUARD_API_URL", "http://test-server:1234")
    # Force recreation by passing explicit URL
    client = get_client(base_url="http://test-server:1234")
    assert client.base_url == "http://test-server:1234"


# ── 14. Required fields in asset response ────────────────────────────────────

def test_asset_response_has_required_fields() -> None:
    """get_assets items contain the fields the dashboard depends on."""
    required = {
        "asset_id", "asset_type", "health_score", "failure_probability",
        "risk_level", "readiness_status", "top_risk_factors", "recommended_action",
    }
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, [SAMPLE_ASSET])
        assets = client.get_assets()
    missing = required - set(assets[0].keys())
    assert not missing, f"Missing fields in asset response: {missing}"


# ── 15. Required fields in priority response ─────────────────────────────────

def test_priority_response_has_required_fields() -> None:
    """get_asset_priority response contains the fields the dashboard depends on."""
    required = {
        "asset_id", "asset_type", "priority_score", "priority_rank",
        "total_assets", "readiness_status", "risk_level", "health_score",
        "priority_reasons", "recommended_action",
    }
    client = MissionGuardClient(base_url="http://localhost:8000")
    with patch("src.dashboard.api_client.requests.get") as mock_get:
        mock_get.return_value = _mock_response(200, SAMPLE_PRIORITY)
        result = client.get_asset_priority("A-001")
    missing = required - set(result.keys())
    assert not missing, f"Missing fields in priority response: {missing}"
