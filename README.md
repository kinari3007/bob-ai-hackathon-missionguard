# MissionGuard AI — Mission Readiness & Predictive Maintenance Copilot

Prototype decision-support system for IBM BoB AI Innovation Hackathon 2026, problem **D1**.
All telemetry is **synthetic**. This is not operationally validated military software.

> **Disclaimer:** Data is entirely synthetic and fictional. Risk probabilities are model estimates,
> not observed failure rates. Do not use for real military operations.

## Team

| Field | Value |
|---|---|
| **Team Name** | To be completed before submission |
| **Track** | AI |
| **Team Lead** | To be completed before submission |
| **Members** | To be completed before submission |

## Problem Statement

Maintainers need a fast way to see which assets are not mission-ready, why they are at risk,
and what to service first. Spreadsheets of sensor-like fields do not produce ranked, explainable actions.

## Solution

MissionGuard scores a fictional fleet CSV with a hybrid, interpretable risk engine: pandas
preprocessing, logistic regression, a domain blend, readiness labels (`READY` / `WARNING` /
`NOT_READY`), and human-readable risk factors — exposed through a FastAPI backend and a
Streamlit dashboard.

## Key Features

- **Synthetic fleet:** 100 reproducible assets in `data/assets.csv`
- **Hybrid risk scores:** health score, failure probability, LOW / MEDIUM / HIGH
- **Readiness layer:** evidence-based READY / WARNING / NOT_READY classification
- **Explainability:** top contributing risk factors and a recommended action per asset
- **Maintenance priority:** deterministic priority score and fleet-wide ranking
- **REST API:** FastAPI backend with auto-generated OpenAPI / Swagger docs
- **Streamlit dashboard:** interactive fleet overview, priority queue, and per-asset detail view

## Architecture

```
Synthetic Dataset (data/assets.csv)
         ↓
Agent 1 — ML / Risk Engine  (src/data/, src/models/, src/services/)
         ↓  Python calls
Agent 2 — FastAPI REST API  (src/api/)     http://localhost:8000
         ↓  HTTP requests
Agent 3 — Streamlit Dashboard (src/dashboard/)  http://localhost:8501
         ↓
[Agent 4 — IBM Bob / MCP — next phase]
```

## Tech Stack

| Layer | Technologies |
|---|---|
| **Languages** | Python 3.13.15 |
| **ML / Data** | pandas 3.0.5, NumPy 2.5.3, scikit-learn 1.9.1, joblib 1.6.0 |
| **API** | FastAPI 0.115.12, uvicorn 0.34.2 |
| **Dashboard** | Streamlit 1.45.1, requests 2.32.3 |
| **Testing** | pytest 9.1.1, httpx 0.28.2, unittest.mock |
| **IBM Technologies** | Reserved for Agent 4 (IBM Bob / watsonx) |
| **Data store** | Local CSV — no external database |

## Repository Structure

```
├── src/
│   ├── api/              # FastAPI REST API          (Agent 2)
│   ├── dashboard/        # Streamlit dashboard       (Agent 3)
│   ├── data/             # Data loading & generation (Agent 1)
│   ├── models/           # ML risk model             (Agent 1)
│   ├── services/         # Risk engine & business logic (Agent 1)
│   └── utils/            # Config, exceptions        (Agent 1)
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py          # Agent 1
│   ├── test_risk_engine.py          # Agent 1
│   ├── test_maintenance_priority.py # Agent 1
│   ├── test_api.py                  # Agent 2
│   └── test_dashboard.py           # Agent 3
├── data/assets.csv       # Synthetic fleet dataset (100 assets)
├── docs/                 # Technical documentation
├── AGENT1_HANDOFF.md
├── AGENT2_HANDOFF.md
├── AGENT3_HANDOFF.md
└── submission.yaml
```

## How to Run

### 1 — Install all dependencies

```powershell
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### 2 — Generate dataset (first time only)

```powershell
.\.venv\Scripts\python.exe -m src.data.generate_dataset
```

### 3 — Start the FastAPI backend (Terminal 1)

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
```

Backend available at: **http://localhost:8000**
API docs (Swagger): **http://localhost:8000/docs**

### 4 — Start the Streamlit dashboard (Terminal 2)

```powershell
.\.venv\Scripts\python.exe -m streamlit run src/dashboard/app.py
```

Dashboard available at: **http://localhost:8501**

### 5 — Run the full test suite

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Expected: **53 tests passing** (23 Agent 1 + 11 Agent 2 + 4 Agent 2 extras + 15 Agent 3)

### Optional — run the ML engine directly (no API needed)

```powershell
.\.venv\Scripts\python.exe -m src
```

## Dashboard Overview

The Streamlit dashboard answers three questions at a glance:

| Question | Where to look |
|---|---|
| Which assets are mission-ready? | KPI cards + Fleet Readiness Overview |
| Which need service first? | Maintenance Priority Queue (top 15) |
| Why is this asset risky? | Asset Detail View → risk factors + action |

### Dashboard sections

| Section | Description |
|---|---|
| **KPI cards** | Total assets, READY, WARNING, NOT READY, HIGH RISK counts |
| **Fleet Readiness** | Bar chart + per-status counts and percentages |
| **Risk Distribution** | Bar chart + LOW / MEDIUM / HIGH counts |
| **Priority Queue** | Top 15 assets sorted by urgency — ID, type, health, risk, action |
| **Asset Detail** | Select any asset — health score, failure probability, risk factors, priority rank, recommended action |
| **Sidebar** | Backend health indicator, readiness filter, asset-type filter |

### Configuration

Override the default backend URL with an environment variable:

```powershell
$env:MISSIONGUARD_API_URL = "http://my-server:8000"
.\.venv\Scripts\python.exe -m streamlit run src/dashboard/app.py
```

## API Endpoints (Agent 2)

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Backend health check |
| GET | `/assets` | All 100 assets with risk scores |
| GET | `/assets/{id}/status` | Readiness status for one asset |
| GET | `/assets/{id}/risk` | Failure risk analysis for one asset |
| GET | `/assets/{id}/priority` | Maintenance priority for one asset |

Unknown asset IDs return HTTP 404 with a JSON error body.

## Demo

| Artifact | Link |
|---|---|
| Demo Video | Not recorded yet — see `demo/demo-video-link.txt` |
| Live Demo | Run locally (see How to Run above) |
| Screenshots | `demo/screenshots/` |
| Presentation | `presentation/` |

## Known Limitations

- Synthetic data only — no real platform telemetry
- IBM Bob / MCP not wired in yet (Agent 4)
- Logistic regression + heuristic blend, not deep learning
- Labels are generated, not observed failures
- ~900 sklearn feature-name warnings (informational, not errors — safe to ignore)
- Dashboard requires the FastAPI backend to be running separately

## What We're Most Proud Of

- **Clean layering:** each agent builds on the previous without rewriting it
- **Explainability:** every risk score is backed by human-readable factor phrases
- **53 automated tests** covering data, ML, API, and dashboard client layers
- **Graceful failure handling:** dashboard shows a friendly message when the API is offline
