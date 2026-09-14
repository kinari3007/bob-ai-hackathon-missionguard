# Source Code — MissionGuard AI

This directory contains the complete Python source code for all four components
of MissionGuard AI. All code is importable from the repository root
(`pytest.ini` sets `pythonpath = .`).

---

## Directory Structure

```
src/
├── __init__.py              ← Public API: get_all_assets, get_asset_status,
│                              get_failure_risk, get_maintenance_priority
├── __main__.py              ← python -m src  (prints fleet summary)
│
├── data/
│   ├── generate_dataset.py  ← Synthetic CSV writer (seed=42, 100 assets)
│   ├── data_loader.py       ← Load and validate assets.csv
│   ├── preprocessing.py     ← Impute missing values, coerce types, parse dates
│   └── feature_engineering.py ← Compute maintenance-gap, stress, utilization features
│
├── models/
│   └── risk_model.py        ← Hybrid risk model (logistic regression + domain blend)
│
├── services/
│   ├── risk_engine.py       ← Main API: get_all_assets / get_asset_status /
│   │                           get_failure_risk / get_maintenance_priority
│   ├── readiness.py         ← READY / WARNING / NOT_READY classification
│   └── explainability.py    ← Translates model contributions → risk factor phrases
│
├── api/
│   └── main.py              ← FastAPI REST API (5 endpoints, wraps risk engine)
│
├── dashboard/
│   ├── app.py               ← Streamlit dashboard (fleet overview, priority queue,
│   │                           asset detail view)
│   └── api_client.py        ← HTTP client for FastAPI backend
│
├── mcp/
│   └── server.py            ← MCP server (5 tools for IBM Bob integration)
│
└── utils/
    ├── config.py             ← Paths, thresholds, random seed (AppConfig, ThresholdConfig)
    └── exceptions.py         ← AssetNotFoundError and other project exceptions
```

---

## Public Python API

Import from `src` directly (or from `src.services.risk_engine`):

```python
from src import get_all_assets, get_asset_status, get_failure_risk, get_maintenance_priority

# All 100 assets with risk, readiness, and explainability
assets = get_all_assets()

# Single asset — readiness status
status = get_asset_status("A-017")

# Single asset — failure risk
risk = get_failure_risk("A-042")

# Single asset — maintenance priority
priority = get_maintenance_priority("A-001")
```

Unknown asset IDs raise `src.utils.exceptions.AssetNotFoundError`.

---

## Component Responsibilities

| Directory | Responsibility |
|---|---|
| `src/data/` | Data generation, loading, preprocessing, feature engineering |
| `src/models/` | Risk model training and inference (logistic regression + domain blend) |
| `src/services/` | High-level API wrapping models + readiness + explainability |
| `src/api/` | FastAPI REST API — thin HTTP wrapper around `src/services/` |
| `src/dashboard/` | Streamlit UI — connects to FastAPI backend via `api_client.py` |
| `src/mcp/` | MCP server — 5 tools exposing `src/services/` to IBM Bob |
| `src/utils/` | Shared configuration, thresholds, and custom exceptions |

---

## Running from Source

```powershell
# Print fleet summary (generates dataset if missing)
python -m src

# Generate dataset only
python -m src.data.generate_dataset

# Start FastAPI backend
python -m uvicorn src.api.main:app --reload --port 8000

# Start Streamlit dashboard
python -m streamlit run src/dashboard/app.py

# Start MCP server (for IBM Bob)
python run_mcp_server.py
```

---

## Environment Variables

Copy `src/.env.example` to `.env` at the repo root.
No credentials are required for local development — the system uses a synthetic CSV
and does not connect to any external service by default.

See `docs/setup-guide.md` for the full setup and run guide.
See `docs/architecture.md` for the full component diagram.
