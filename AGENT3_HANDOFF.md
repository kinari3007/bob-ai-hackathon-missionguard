# Agent 3 Handoff — MissionGuard Streamlit Dashboard

**Date:** 2026-09-14  
**Agent:** Agent 3 (Dashboard)  
**Status:** ✅ COMPLETE — 49/49 tests passing

---

## 1. What Was Built

A Streamlit dashboard (`src/dashboard/`) that consumes the Agent 2 FastAPI backend
over HTTP. It does **not** import any ML or risk-engine modules directly.

### Dashboard sections

| Section | What it shows |
|---|---|
| Sidebar | Backend health indicator (live), readiness filter, asset-type filter |
| KPI cards | Total assets · READY · WARNING · NOT READY · HIGH RISK |
| Fleet Readiness | Per-status counts, percentages, bar chart |
| Risk Distribution | LOW / MEDIUM / HIGH counts, percentages, bar chart |
| Priority Queue | Top-15 most urgent assets — ID, type, health score, risk, readiness, action |
| Asset Detail | Select any asset — health score, failure probability, risk level, readiness, priority rank, risk factors, recommended action, priority score gauge |
| Disclaimer | Prominent synthetic-data / not-for-military-use notice |

### API client (`src/dashboard/api_client.py`)

Thin `requests`-based wrapper. No ML logic. Raises typed exceptions so the
dashboard converts failures into user-friendly messages rather than tracebacks.

| Method | Endpoint |
|---|---|
| `health_check()` | `GET /health` |
| `get_assets()` | `GET /assets` |
| `get_asset_status(id)` | `GET /assets/{id}/status` |
| `get_asset_risk(id)` | `GET /assets/{id}/risk` |
| `get_asset_priority(id)` | `GET /assets/{id}/priority` |

Backend URL defaults to `http://localhost:8000` and is overridable via the
`MISSIONGUARD_API_URL` environment variable.

---

## 2. Files Created

| File | Purpose |
|---|---|
| `src/dashboard/__init__.py` | Package marker |
| `src/dashboard/api_client.py` | HTTP client — all backend communication |
| `src/dashboard/app.py` | Streamlit dashboard entry point |
| `tests/test_dashboard.py` | 15 unit tests for the API client (no live server needed) |
| `AGENT3_HANDOFF.md` | This file |

### Utility / diagnostic files (safe to delete after handoff)

`check_deps.py`, `check_deps2.py`, `deps_check.json`, `deps_check2.json`,
`diagnose.py`, `diagnose_out.json`, `fix_and_test.py`, `fix_run.bat`,
`count_tests.py`, `count_tests_out.txt`, `count_run.bat`,
`run_all_tests.py`, `run_suite.bat`, `probe.bat`, `probe_out.txt`,
`install_all.bat`, `diag.bat`, `test_results.json`

---

## 3. Files Modified

| File | Change |
|---|---|
| `requirements.txt` | Added `streamlit==1.45.1`, `requests==2.32.3`; corrected `httpx==0.28.1`; added pyarrow note |
| `README.md` | Full rewrite: architecture diagram, 4-step run instructions, dashboard table, API table |

### Files NOT touched (Agent 1 + 2 foundation intact)

`src/data/*`, `src/models/*`, `src/services/*`, `src/utils/*`,
`src/api/*`, `data/assets.csv`, all pre-existing tests.

---

## 4. How the Dashboard Communicates with FastAPI

```
Streamlit browser tab (localhost:8501)
    │
    │  Python in-process
    ▼
src/dashboard/app.py
    │  imports
    ▼
src/dashboard/api_client.MissionGuardClient
    │  requests.get() — HTTP
    ▼
FastAPI  localhost:8000
    │  Python function call
    ▼
Agent 1 ML / Risk Engine
```

`@st.cache_data(ttl=60)` caches the `/assets` bulk call for 60 seconds so
sidebar filter interactions and asset-selector changes don't hammer the API.
All single-asset endpoints (`/status`, `/risk`, `/priority`) are called
on demand when the user selects an asset in the detail view.

---

## 5. How to Run the Backend

```powershell
# Terminal 1 — FastAPI backend
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

Verify it's up: `http://localhost:8000/health` → `{"status":"ok",...}`  
Swagger docs: `http://localhost:8000/docs`

---

## 6. How to Run the Dashboard

```powershell
# Terminal 2 — Streamlit dashboard
.\.venv\Scripts\python.exe -m streamlit run src/dashboard/app.py
```

Dashboard: **http://localhost:8501**

If the backend is not running the dashboard shows a friendly error and a
copy-paste command to start it — it does not crash.

### Override backend URL

```powershell
$env:MISSIONGUARD_API_URL = "http://other-host:8000"
.\.venv\Scripts\python.exe -m streamlit run src/dashboard/app.py
```

---

## 7. Tests — Results

```
collected 49 items

tests\test_api.py           ...........   11 passed
tests\test_dashboard.py     ................  16 passed  (15 + 1 auto-collected)
tests\test_data_loader.py   .....          5 passed
tests\test_maintenance_priority.py  ........  8 passed
tests\test_risk_engine.py   .........      9 passed

====================== 49 passed, 1801 warnings in 1.46s ======================
```

All 1801 warnings are non-critical:
- ~1800 × sklearn `UserWarning: X does not have valid feature names` (Agent 1, known)
- 1 × starlette `DeprecationWarning` about `anyio.abc.BlockingPortal` alias

No test failures. No errors.

---

## 8. Known Issues

### pyarrow DLL blocked by Windows Application Control

`pyarrow` was pulled as a transitive dependency of pandas/streamlit and its
compiled DLL is blocked by the machine's Application Control policy.

**Fix applied:** `pyarrow` was uninstalled. pandas works correctly without it.

**If you reinstall requirements on a new machine:** run
`.venv\Scripts\pip.exe uninstall pyarrow -y` after `pip install -r requirements.txt`
if you see `ImportError: DLL load failed while importing _compute`.

Alternatively, add `--no-deps` flag when installing pandas and install its
actual required dependencies manually, or use a machine without App Control.

### httpx version mismatch

`httpx==0.28.2` specified by Agent 2 does not exist on PyPI. Fixed to `0.28.1`
in `requirements.txt`. Functionally identical for test usage.

### sklearn feature-name warnings

~1800 `UserWarning: X does not have valid feature names` from scikit-learn.
Inherited from Agent 1. Non-critical — all tests pass. Suppress in CI with
`-W ignore::UserWarning` if desired.

### Streamlit cache and the risk engine

The ML model is re-fitted on every fresh import of the `src` package (by
design — see Agent 1). `@st.cache_data(ttl=60)` prevents the dashboard from
calling `/assets` on every widget interaction, but the first load will trigger
a full model fit in the backend. This is expected and acceptable for the demo.

---

## 9. What Agent 4 Should NOT Change

### Entire Agent 1 foundation (read-only)
`src/data/`, `src/models/`, `src/services/`, `src/utils/`, `data/assets.csv`

### Entire Agent 2 API layer (read-only unless adding endpoints)
`src/api/main.py`, `src/api/__init__.py`

### Agent 3 dashboard (should not need changes for IBM Bob integration)
`src/dashboard/api_client.py`, `src/dashboard/app.py`

Agent 4 should add IBM Bob / MCP in a **new** module (e.g. `src/mcp/`) that
calls the same FastAPI endpoints or the same Python APIs directly. It must not
rewrite or duplicate risk scoring.

---

## 10. What Remains for IBM Bob / MCP Integration (Agent 4)

The clean attachment points are:

### Option A — MCP wraps the REST API (recommended)
```
IBM Bob (watsonx) ──→ MCP Server ──→ GET http://localhost:8000/assets
                                  ──→ GET http://localhost:8000/assets/{id}/status
                                  ──→ GET http://localhost:8000/assets/{id}/risk
                                  ──→ GET http://localhost:8000/assets/{id}/priority
```

Agent 4 creates `src/mcp/server.py` (or similar) that exposes MCP tools backed
by the FastAPI endpoints. The dashboard and API layer remain unchanged.

### Option B — MCP wraps Python APIs directly
```python
from src import get_all_assets, get_asset_status, get_failure_risk, get_maintenance_priority
```

Import directly without HTTP overhead. Suitable if Bob and the risk engine run
in the same process.

### Suggested MCP tool definitions for Agent 4

| Tool name | Maps to | Description |
|---|---|---|
| `list_assets` | `GET /assets` | Get all assets with risk scores |
| `get_asset_status` | `GET /assets/{id}/status` | Readiness for one asset |
| `get_asset_risk` | `GET /assets/{id}/risk` | Failure risk for one asset |
| `get_asset_priority` | `GET /assets/{id}/priority` | Maintenance priority for one asset |
| `get_fleet_summary` | Computed from `/assets` | High-level fleet health summary |

### Conversation patterns Bob should support

- "Which assets are not mission-ready?" → `list_assets()`, filter `readiness_status == NOT_READY`
- "Why is asset A-042 at risk?" → `get_asset_risk("A-042")`, return `top_risk_factors`
- "What should we service first?" → `list_assets()`, sort by `failure_probability` desc
- "What is the health score of A-017?" → `get_asset_status("A-017")`, return `health_score`

### Environment variables already reserved (`.env.example`)

```
WATSONX_API_KEY=
WATSONX_PROJECT_ID=
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

---

## Architecture Summary

```
data/assets.csv  (synthetic — 100 assets, seed=42)
       ↓
src/data/ + src/models/ + src/services/   [Agent 1 — ML/Risk Engine]
       ↓  Python function calls
src/api/main.py  FastAPI                  [Agent 2 — REST API]
       ↓  HTTP GET requests (requests lib)
src/dashboard/api_client.py + app.py      [Agent 3 — Streamlit Dashboard]
       ↓
[Agent 4 — IBM Bob / MCP — TODO]
```

Each layer is tested independently. No layer reimplements the logic of any
other layer. Agent 4 inherits a clean, layered, 49-test-covered codebase.
