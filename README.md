# MissionGuard AI — Mission Readiness & Predictive Maintenance Copilot

Prototype decision-support core for IBM BoB AI Innovation Hackathon 2026, problem **D1**. All telemetry is **synthetic**. This is not operationally validated military software.

## Team

| Field | Value |
|---|---|
| **Team Name** | To be completed before submission |
| **Track** | AI |
| **Team Lead** | To be completed before submission |
| **Members** | To be completed before submission |

## Problem Statement

Maintainers need a fast way to see which assets are not mission-ready, why they are at risk, and what to service first. Spreadsheets of sensor-like fields do not by themselves produce ranked, explainable actions.

## Solution

MissionGuard scores a fictional fleet CSV with a hybrid, interpretable risk engine: pandas preprocessing, logistic regression, a domain blend, readiness labels (`READY` / `WARNING` / `NOT_READY`), and human-readable risk factors. Later phases will add IBM Bob / MCP and a UI on top of the Python API already exposed here.

## Key Features

- **Synthetic fleet:** ~100 reproducible assets in `data/assets.csv`
- **Hybrid risk scores:** health, failure probability, LOW/MEDIUM/HIGH
- **Readiness layer:** evidence-based READY / WARNING / NOT_READY
- **Explainability:** top contributing factors and a recommended action per asset
- **Maintenance priority:** deterministic ranking for service scheduling
- **REST API:** FastAPI backend with OpenAPI docs (Agent 2)
- **Python APIs:** `get_all_assets`, `get_asset_status`, `get_failure_risk`, `get_maintenance_priority`

## Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python 3.13.15 |
| **ML/Data** | pandas, NumPy, scikit-learn |
| **API** | FastAPI, uvicorn |
| **Testing** | pytest, httpx |
| **IBM Technologies** | Not wired yet (reserved for later agents) |
| **Databases** | Local CSV |
| **Other** | joblib (model persistence) |

## Repository Structure

```
├── src/
│   ├── api/              # FastAPI REST API (Agent 2)
│   ├── data/             # Data loading and generation (Agent 1)
│   ├── models/           # ML risk model (Agent 1)
│   ├── services/         # Risk engine and business logic (Agent 1)
│   └── utils/            # Configuration and utilities (Agent 1)
├── tests/                # pytest suite (Agent 1 & 2)
├── data/assets.csv       # Synthetic fleet dataset
├── docs/                 # Technical documentation
├── demo/                 # Demo artifacts (later)
├── presentation/         # Slide deck (later)
├── AGENT1_HANDOFF.md     # Foundation layer handoff
├── AGENT2_HANDOFF.md     # API layer handoff
└── submission.yaml       # Hackathon metadata
```

## How to Run

### ML Foundation (Agent 1)

```powershell
# Setup virtual environment (if not already done)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
python -m pip install -r requirements.txt

# Generate synthetic dataset
python -m src.data.generate_dataset

# Run risk engine
python -m src

# Run tests
python -m pytest -v
```

### REST API (Agent 2)

```powershell
# Install API dependencies (if not already done)
.\.venv\Scripts\python.exe install_api_dependencies.py

# Start API server
.\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload

# Access API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/assets
curl http://localhost:8000/assets/A-001/status
```

Details: [`docs/setup-guide.md`](docs/setup-guide.md), [`docs/risk-engine.md`](docs/risk-engine.md), [`AGENT1_HANDOFF.md`](AGENT1_HANDOFF.md), and [`AGENT2_HANDOFF.md`](AGENT2_HANDOFF.md).

## Demo

| Artifact | Link |
|---|---|
| Demo Video | Not recorded yet — see `demo/demo-video-link.txt` |
| Live Demo | Not deployed — run locally |
| Screenshots | Later (dashboard agent) |
| Presentation | Later |

## Known Limitations

- Synthetic data only; no real platform telemetry
- No IBM Bob, MCP, or dashboard UI in current phase
- Logistic regression + heuristic blend, not deep learning
- Labels are generated, not observed failures
- ~900 sklearn feature-name warnings (informational, not errors)

## What We're Most Proud Of

- **Agent 1:** Small, tested, explainable ML scoring pipeline that produces deterministic, reproducible risk assessments
- **Agent 2:** Clean REST API layer that wraps the foundation without reimplementing logic
- **Architecture:** Clear separation of concerns (data → ML → API → future UI)
- **Testability:** 38 tests covering foundation and API layers
