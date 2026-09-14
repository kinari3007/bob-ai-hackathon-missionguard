"""MissionGuard API client.

Thin HTTP wrapper around the Agent 2 FastAPI backend.
All risk logic lives in the backend — this module only issues HTTP requests
and returns plain Python dicts/lists.

Usage::

    from src.dashboard.api_client import MissionGuardClient

    client = MissionGuardClient()               # uses MISSIONGUARD_API_URL env var
    assets  = client.get_assets()              # list[dict]
    status  = client.get_asset_status("A-001") # dict | None
    risk    = client.get_asset_risk("A-001")   # dict | None
    priority = client.get_asset_priority("A-001") # dict | None
    ok, msg = client.health_check()            # (bool, str)
"""

from __future__ import annotations

import os
from typing import Any

import requests

# ── Configuration ────────────────────────────────────────────────────────────

DEFAULT_API_URL = "http://localhost:8000"
_REQUEST_TIMEOUT = 10  # seconds


def _api_url() -> str:
    """Return the backend base URL, honouring MISSIONGUARD_API_URL env var."""
    return os.environ.get("MISSIONGUARD_API_URL", DEFAULT_API_URL).rstrip("/")


# ── Errors ───────────────────────────────────────────────────────────────────

class BackendUnavailableError(Exception):
    """Raised when the MissionGuard API cannot be reached."""


class AssetNotFoundError(Exception):
    """Raised when the API returns 404 for an asset ID."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(f"Asset not found: {asset_id!r}")


# ── Client ───────────────────────────────────────────────────────────────────

class MissionGuardClient:
    """HTTP client for the MissionGuard FastAPI backend.

    All methods return plain Python objects (list or dict).
    Callers do *not* need to handle requests exceptions — the client converts
    connectivity failures into :class:`BackendUnavailableError` and 404s into
    :class:`AssetNotFoundError`.
    """

    def __init__(self, base_url: str | None = None, timeout: float = _REQUEST_TIMEOUT) -> None:
        self.base_url = (base_url or _api_url()).rstrip("/")
        self.timeout = timeout

    # ── private helpers ──────────────────────────────────────────────────────

    def _get(self, path: str) -> Any:
        """Issue a GET request; raise descriptive errors on failure."""
        url = f"{self.base_url}{path}"
        try:
            response = requests.get(url, timeout=self.timeout)
        except requests.exceptions.ConnectionError as exc:
            raise BackendUnavailableError(
                f"Cannot connect to MissionGuard backend at {self.base_url}. "
                "Start the FastAPI server on port 8000."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise BackendUnavailableError(
                f"Request to {url} timed out after {self.timeout}s."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise BackendUnavailableError(f"HTTP request failed: {exc}") from exc

        if response.status_code == 404:
            # Parse asset_id from path like /assets/A-001/status
            parts = path.strip("/").split("/")
            asset_id = parts[1] if len(parts) >= 2 else path
            raise AssetNotFoundError(asset_id)

        response.raise_for_status()
        return response.json()

    # ── public API ───────────────────────────────────────────────────────────

    def health_check(self) -> tuple[bool, str]:
        """Return ``(True, version_str)`` if backend is up, else ``(False, error_msg)``."""
        try:
            data = self._get("/health")
            version = data.get("version", "unknown")
            return True, version
        except BackendUnavailableError as exc:
            return False, str(exc)
        except Exception as exc:  # unexpected
            return False, f"Unexpected error: {exc}"

    def get_assets(self) -> list[dict[str, Any]]:
        """Return all assets with risk scores and readiness status.

        Returns an empty list on any error rather than raising, so the
        dashboard can display a friendly message instead of crashing.
        """
        try:
            result = self._get("/assets")
            return result if isinstance(result, list) else []
        except BackendUnavailableError:
            raise
        except Exception:
            return []

    def get_asset_status(self, asset_id: str) -> dict[str, Any]:
        """Return readiness status record for *asset_id*.

        Raises :class:`AssetNotFoundError` for unknown IDs.
        Raises :class:`BackendUnavailableError` if the backend is down.
        """
        return self._get(f"/assets/{asset_id}/status")

    def get_asset_risk(self, asset_id: str) -> dict[str, Any]:
        """Return failure risk analysis for *asset_id*."""
        return self._get(f"/assets/{asset_id}/risk")

    def get_asset_priority(self, asset_id: str) -> dict[str, Any]:
        """Return maintenance priority record for *asset_id*."""
        return self._get(f"/assets/{asset_id}/priority")


# ── Module-level convenience singleton ───────────────────────────────────────
# Streamlit re-imports modules on each run; the singleton is only alive for
# the current script execution so there is no state-bleed between sessions.

_default_client: MissionGuardClient | None = None


def get_client(base_url: str | None = None) -> MissionGuardClient:
    """Return (and lazily create) a module-level client instance."""
    global _default_client
    if _default_client is None or base_url is not None:
        _default_client = MissionGuardClient(base_url=base_url)
    return _default_client
