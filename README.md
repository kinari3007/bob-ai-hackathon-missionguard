# MissionGuard AI — Mission Readiness & Predictive Maintenance Copilot

Prototype decision-support system for **IBM BoB AI Innovation Hackathon 2026**, problem **D1**.

> **Disclaimer:** All telemetry data is entirely synthetic and fictional. Risk probabilities are
> model estimates, not observed failure rates. Do not use for real military operations.

---

## Team

| Field | Value |
|---|---|
| **Team Name** | To be completed before submission |
| **Track** | AI |
| **Team Lead** | To be completed before submission |
| **Members** | To be completed before submission |

---

## Problem Statement

Military asset maintainers lack fast, explainable insight into which platforms are mission-ready,
why specific assets are at risk, and which maintenance tasks should happen first. Spreadsheets of
sensor readings do not produce ranked, actionable decisions.

---

## Solution

MissionGuard AI is a decision-support system that analyzes a synthetic fleet using a hybrid
risk engine (logistic regression + domain heuristics), classifies mission readiness, ranks
maintenance priorities, explains every score in plain language, and exposes everything through
a REST API, an interactive dashboard, and a conversational AI interface via IBM Bob / MCP.

---

## Key Features

| Feature | Description |
|---|---|
| **Hybrid risk scores** | Health score (0–100), failure probability (0–1), LOW/MEDIUM/HIGH classification |
| **Mission readiness** | Evidence-based READY / WARNING / NOT_READY per asset |
| **Explainability** | Up to 3 human-readable risk factors and a recommended action per asset |
| **Maintenance priority** | Deterministic priority score (0–100) and fleet-wide rank (1–100) |
| **REST API** | FastAPI with auto-generated OpenAPI / Swagger docs |
| **Streamlit dashboard** | Fleet overview, KPIs, priority queue, per-asset detail view |
| **MCP / IBM Bob** | 5 conversational AI tools for natural-language fleet queries |

---

## Architecture

```
data/assets.csv  (100 synthetic assets, seed=42)
        │
        ▼
Agent 1 — ML / Risk Engine   src/data/ + src/models/ + src/services/
        │  Python function calls
        ▼
Agent 2 — FastAPI REST API   src/api/main.py         → http://localhost:8000
        │  HTTP requests
        ▼
Agent 3 — Streamlit Dashboard  src/dashboard/app.py  → http://localhost:8501

Agent 4 — MCP Server   src/mcp/server.py  ←→  IBM Bob / watsonx (stdio or HTTP)
        │  calls Agent 1 APIs directly (no duplication)
        ▼
IBM Bob AI Agent  (conversational interface — requires separate IBM Bob installation)
```

Each agent layer calls the previous one without reimplementing its logic.

---

## Repository Structure

```
├── src/
│   ├── api/              # FastAPI REST API               (Agent 2)
│   │   └── main.py
│   ├── dashboard/        # Streamlit dashboard            (Agent 3)
│   │   ├── app.py
│   │   └── api_client.py
│   ├── mcp/              # MCP server for IBM Bob         (Agent 4)
│   │   └── server.py
│   ├── data/             # Data loading & generation      (Agent 1)
│   ├── models/           # ML risk model                  (Agent 1)
│   ├── services/         # Risk engine, readiness, explainability (Agent 1)
│   └── utils/            # Config, exceptions
├── tests/
│   ├── conftest.py
│   ├── test_data_loader.py          # 5 tests  — Agent 1
│   ├── test_risk_engine.py          # 9 tests  — Agent 1
│   ├── test_maintenance_priority.py # 8 tests  — Agent 1
│   ├── test_api.py                  # 11 tests — Agent 2
│   ├── test_dashboard.py            # 16 tests — Agent 3
│   └── test_mcp.py                  # 22 tests — Agent 4
├── data/assets.csv        # Synthetic fleet dataset (100 assets)
├── docs/
│   ├── architecture.md
│   ├── mcp-integration.md # IBM Bob setup guide
│   ├── risk-engine.md
│   └── setup-guide.md
├── run_mcp_server.py      # MCP server launcher (stdio transport)
├── requirements.txt
├── pytest.ini
└── submission.yaml
```

---

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.14 (3.11+ supported) |
| ML / Data | pandas, NumPy, scikit-learn, joblib | 3.0.5, 2.5.3, 1.9.1, 1.6.0 |
| API | FastAPI, uvicorn | 0.141+, 0.53+ |
| Dashboard | Streamlit, requests | 1.63+, 2.34+ |
| Testing | pytest, pytest-asyncio, httpx | 9.1.1, 1.4.0, 0.28.1 |
| MCP | mcp[cli] | 2.2+ |
| Data store | Local CSV | — |

---

## Installation

### Prerequisites

- Python 3.11 or later (tested with Python 3.14 on Windows)
- pip

### Install dependencies

```powershell
# From the repository root
pip install -r requirements.txt
```

> **Note:** `requirements.txt` pins exact versions. If you are on Python 3.14, pip will
> automatically select compatible wheels (e.g. pandas 3.0.5 instead of 2.2.3).

### Environment variables (optional)

Copy `src/.env.example` to `.env`. No credentials are required for local development —
the system uses a local synthetic CSV file and does not connect to any external service by default.

```
# src/.env.example — optional overrides
MISSIONGUARD_RANDOM_SEED=42

# Reserved for IBM Bob / watsonx — not used locally
# WATSONX_API_KEY=your_api_key_here
# WATSONX_PROJECT_ID=your_project_id_here
# WATSONX_URL=https://us-south.ml.cloud.ibm.com
# MISSIONGUARD_API_URL=http://localhost:8000
```

---

## How to Run

### 1 — Generate the dataset (first time only)

```powershell
python -m src.data.generate_dataset
```

Creates `data/assets.csv` with 100 reproducible synthetic assets (seed=42). Safe to re-run.

### 2 — Start the FastAPI backend (Terminal 1)

```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```

| URL | Description |
|---|---|
| http://localhost:8000/health | Health check |
| http://localhost:8000/assets | All 100 assets |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/redoc | ReDoc |

### 3 — Start the Streamlit dashboard (Terminal 2)

```powershell
python -m streamlit run src/dashboard/app.py
```

Dashboard available at **http://localhost:8501**

The dashboard connects to the FastAPI backend at `http://localhost:8000` by default.
Override with the `MISSIONGUARD_API_URL` environment variable:

```powershell
# PowerShell
$env:MISSIONGUARD_API_URL = "http://my-server:8000"
python -m streamlit run src/dashboard/app.py
```

### 4 — Run the MCP server for IBM Bob (Terminal 3)

```powershell
python run_mcp_server.py
```

The server runs over stdio and is ready for IBM Bob to connect. See
[docs/mcp-integration.md](docs/mcp-integration.md) for IBM Bob configuration details.

### 5 — Run the test suite

```powershell
python -m pytest -v
```

Expected result: **71 tests passing** (verified on Python 3.14 / pytest 9.1.1).

### 6 — (Optional) Run the risk engine directly

```powershell
python -m src
```

Generates the dataset if missing, scores all assets, and prints a summary to the console.

---

## REST API Endpoints

| Method | Path | Status codes | Description |
|---|---|---|---|
| GET | `/health` | 200 | Service health check |
| GET | `/assets` | 200 | All 100 assets with risk and readiness |
| GET | `/assets/{id}/status` | 200, 404 | Readiness status for one asset |
| GET | `/assets/{id}/risk` | 200, 404 | Failure risk analysis for one asset |
| GET | `/assets/{id}/priority` | 200, 404 | Maintenance priority for one asset |

All 404 responses return `{"detail": "Asset {id} not found"}`.

### Example requests

```bash
# Health check
curl http://localhost:8000/health

# All assets
curl http://localhost:8000/assets

# One asset — readiness
curl http://localhost:8000/assets/A-001/status

# One asset — risk analysis
curl http://localhost:8000/assets/A-042/risk

# One asset — maintenance priority
curl http://localhost:8000/assets/A-017/priority
```

### Example response — `/assets/A-001/risk`

```json
{
  "asset_id": "A-001",
  "health_score": 25.1,
  "failure_probability": 0.7488,
  "risk_level": "HIGH",
  "top_risk_factors": [
    "High utilization intensity",
    "High operating hours",
    "Elevated fuel consumption"
  ],
  "recommended_action": "Schedule inspection and preventive maintenance"
}
```

---

## Dashboard Overview

The dashboard answers three questions at a glance:

| Question | Where to look |
|---|---|
| Which assets are mission-ready? | KPI cards + Fleet Readiness bar |
| Which need service first? | Maintenance Priority Queue (top 15) |
| Why is this asset risky? | Asset Detail → risk factors + action |

| Section | Description |
|---|---|
| **KPI cards** | Total assets, READY count, WARNING count, NOT_READY count, HIGH RISK count |
| **Fleet Readiness** | Bar chart + counts and percentages by status |
| **Risk Distribution** | Bar chart + LOW / MEDIUM / HIGH counts |
| **Priority Queue** | Top 15 assets sorted by urgency |
| **Asset Detail** | Health score, failure probability, risk factors, priority rank, recommended action |
| **Sidebar** | Backend status, readiness filter, asset-type filter |

---

## MCP Tools (IBM Bob Integration)

The MCP server exposes 5 tools. The server connects directly to the Agent 1 risk engine —
it does not duplicate any scoring logic.

| Tool | Parameters | Description |
|---|---|---|
| `list_assets` | `readiness_filter`, `risk_filter`, `asset_type_filter` (all optional) | List fleet assets with optional filtering |
| `get_asset_readiness` | `asset_id` (required) | Mission-readiness status and evidence |
| `get_asset_failure_risk` | `asset_id` (required) | Failure probability, risk level, risk factors |
| `get_asset_maintenance` | `asset_id` (required) | Priority score, fleet rank, priority reasons |
| `get_fleet_summary` | none | Fleet-wide counts, percentages, top 10 priority assets |

### Example conversational queries

```
"Which assets are not mission-ready?"
→ list_assets(readiness_filter="NOT_READY")  → 27 assets

"Show all high-risk UAVs"
→ list_assets(risk_filter="HIGH", asset_type_filter="UAV")

"Is asset A-017 mission-ready?"
→ get_asset_readiness("A-017")

"Why is asset A-042 at risk?"
→ get_asset_failure_risk("A-042")
→ HIGH risk, failure_probability=0.623
→ factors: High utilization intensity, Many days since last service, Elevated fuel consumption

"Which asset should we service first?"
→ get_fleet_summary() → top priority: A-017 (score=100, rank=1)

"Give me a fleet health overview"
→ get_fleet_summary()
→ 100 assets: 38 READY (38%), 35 WARNING (35%), 27 NOT_READY (27%)
→ 38 LOW risk, 35 MEDIUM risk, 27 HIGH risk
```

### IBM Bob configuration

Add to your IBM Bob MCP configuration file:

```json
{
  "mcpServers": {
    "missionguard": {
      "command": "python",
      "args": ["run_mcp_server.py"],
      "cwd": "/absolute/path/to/bob-ai-hackathon-missionguard"
    }
  }
}
```

Replace `cwd` with the actual absolute path on your machine.
See [docs/mcp-integration.md](docs/mcp-integration.md) for full IBM Bob setup, HTTP transport,
and watsonx configuration.

---

## Fleet Statistics (verified from live system)

These numbers come from the validated system with seed=42:

| Metric | Value |
|---|---|
| Total assets | 100 |
| READY | 38 (38%) |
| WARNING | 35 (35%) |
| NOT_READY | 27 (27%) |
| LOW risk | 38 |
| MEDIUM risk | 35 |
| HIGH risk | 27 |
| Highest priority asset | A-017 (score 100, rank 1) |

---

## Known Limitations

- **Synthetic data only** — no real platform telemetry
- **Logistic regression + heuristic blend** — not deep learning
- **Labels are generated**, not observed failure rates
- **~1900 sklearn feature-name warnings** — informational, not errors; safe to ignore
- **Dashboard requires the FastAPI backend** to be running separately
- **IBM Bob live connection** requires a separate IBM Bob installation and configuration
- **No authentication** — suitable for demo, not production deployment
- **No persistence** — model is re-fit from the CSV on each cold start (fast: <1 second)

---

## IBM Bob Integration — What Is and Isn't Implemented

### Implemented locally (verified)

- MCP server (`src/mcp/server.py`) with all 5 tools
- stdio transport via `run_mcp_server.py`
- Full test suite for all MCP tool logic (22 tests passing)
- IBM Bob JSON configuration snippet (in `docs/mcp-integration.md`)

### Requires IBM Bob configuration

- Installing IBM Bob on your machine
- Adding MissionGuard to Bob's MCP server list
- Testing the natural-language conversation flow end-to-end

### Requires credentials or deployment setup

- `WATSONX_API_KEY`, `WATSONX_PROJECT_ID`, `WATSONX_URL` for watsonx.ai integration
- A deployed server for remote/HTTP MCP transport
- No fake credentials are in this repository; environment variables are documented in `src/.env.example`

---

## Security & Data Disclaimer

- No real credentials, API keys, or secrets are committed to this repository
- `src/.env.example` documents variable names only — never actual values
- `.env` is listed in `.gitignore`
- All asset data is entirely synthetic and randomly generated
- This system is not validated for any operational or safety-critical use

---

## What We're Most Proud Of

- **Clean layering:** each agent builds strictly on the previous one, no logic duplication
- **Explainability by design:** every risk score is backed by human-readable factor phrases
- **71 automated tests** covering data, ML, API, dashboard client, and MCP layers
- **IBM Bob–ready MCP integration** with clear separation between what works locally and what needs Bob configuration
- **Graceful degradation:** dashboard shows a clear message when the API is offline rather than crashing

---

## Documentation

| Document | Contents |
|---|---|
| [docs/architecture.md](docs/architecture.md) | System design and data flow |
| [docs/mcp-integration.md](docs/mcp-integration.md) | IBM Bob setup, MCP tools, watsonx config |
| [docs/risk-engine.md](docs/risk-engine.md) | Risk scoring algorithm and thresholds |
| [docs/setup-guide.md](docs/setup-guide.md) | Detailed installation and troubleshooting |
| [QUICKSTART.md](QUICKSTART.md) | Fast-start commands |
