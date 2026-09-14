# Solution Overview

> **Disclaimer:** All asset data is entirely synthetic and fictional.
> Risk scores are model estimates, not observed failure rates.

---

## What We Built

MissionGuard AI is a local decision-support system that analyzes a synthetic fleet of 100 assets,
scores each one for failure risk and mission readiness, ranks maintenance priorities, explains
every decision in plain language, and exposes all of this through three interfaces:

- A **REST API** (FastAPI) for structured programmatic access
- An **interactive dashboard** (Streamlit) for visual fleet oversight
- A **conversational AI interface** via IBM Bob and the Model Context Protocol (MCP)

---

## How It Works

### 1 — Data Layer

`src/data/generate_dataset.py` creates `data/assets.csv` — 100 synthetic fleet assets with
correlated sensor-like fields (engine temperature, vibration, operating hours, maintenance
history, etc.) generated from a fixed seed (42) so results are fully reproducible.

### 2 — Risk Engine (`src/services/`, `src/models/`, `src/data/`)

The core analysis pipeline:

1. Load and validate the CSV (`src/data/data_loader.py`)
2. Impute missing values and coerce types (`src/data/preprocessing.py`)
3. Engineer maintenance-gap, stress, and utilization features (`src/data/feature_engineering.py`)
4. Fit a logistic regression on a synthetic failure label; blend with a domain median/IQR score (`src/models/risk_model.py`)
5. Map failure probability + health score onto `LOW`/`MEDIUM`/`HIGH` risk and `READY`/`WARNING`/`NOT_READY` readiness (`src/services/readiness.py`)
6. Identify the largest positive model contributions and translate them into human-readable phrases (`src/services/explainability.py`)

The output for every asset: health score (0–100), failure probability (0–1), risk level, readiness status, up to 3 top risk factors, and a recommended action.

### 3 — REST API (`src/api/main.py`)

A FastAPI application that wraps the risk engine functions as HTTP endpoints. It does not
reimplement any scoring logic — it calls the same Python functions directly. Swagger docs
are available at `http://localhost:8000/docs`.

### 4 — Streamlit Dashboard (`src/dashboard/app.py`)

An interactive dashboard that connects to the FastAPI backend and presents:

- KPI cards (total assets, READY / WARNING / NOT_READY / HIGH-RISK counts)
- Fleet readiness and risk distribution charts
- Maintenance priority queue (top 15 assets ranked by urgency)
- Per-asset detail view with health score, failure probability, risk factors, and recommended action

### 5 — MCP Server & IBM Bob Integration (`src/mcp/server.py`)

Five MCP tools wrap the risk engine Python functions and expose them to IBM Bob:

| Tool | Purpose |
|---|---|
| `list_assets` | List fleet assets with optional readiness / risk / type filtering |
| `get_asset_readiness` | Mission-readiness status and evidence for a specific asset |
| `get_asset_failure_risk` | Failure probability, risk factors, and recommended action |
| `get_asset_maintenance` | Priority score, fleet rank, and priority reasons |
| `get_fleet_summary` | Fleet-wide counts, percentages, and top-10 priority queue |

IBM Bob reads `.bob/mcp.json`, spawns the MCP server process (`run_mcp_server.py`), and
routes natural-language questions to the appropriate tool. The MissionGuard backend performs
all structured analysis; IBM Bob provides the conversational interface that presents results
to the user.

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Synthetic correlated data, not uniform random | Prototype looks like a real fleet; model can learn meaningful structure |
| Logistic regression + domain score blend | Explainable MVP; avoids brittle single-threshold rules |
| Thresholds in `config.py` | Readiness and risk rules stay tunable without touching ML code |
| Thin wrapper layers | Each layer (API, MCP) calls the layer below without reimplementing logic |
| stdio MCP transport | Works without a running HTTP server; IBM Bob spawns and manages the process |

---

## IBM Technologies Used

- **Model Context Protocol (MCP)** — standardized interface between IBM Bob and the MissionGuard backend
- **IBM Bob** — conversational AI interface used to query the MissionGuard MCP tools

The MissionGuard risk engine is built on open-source Python libraries (scikit-learn, pandas,
FastAPI, Streamlit). Watson credentials are not required for the local demo.

---

## What Is Implemented (Verified)

| Component | Status |
|---|---|
| Risk engine (data → model → scores → explainability) | ✅ Implemented and tested |
| FastAPI REST API (5 endpoints) | ✅ Implemented and tested |
| Streamlit dashboard (KPIs, charts, priority queue, detail view) | ✅ Implemented and tested |
| MCP server (5 tools, stdio transport) | ✅ Implemented and tested |
| IBM Bob MCP integration | ✅ Demonstrated locally |
| 71 automated tests across all layers | ✅ All passing (71 passed in 3.69s) |

---

## What Is Not Implemented

- Real military or operational telemetry (all data is synthetic)
- Deep learning or neural networks (logistic regression + heuristic blend by design)
- Observed failure rates (labels are synthetically generated)
- Public deployment (local demo only)
- Authentication / authorization (not required for the prototype)
- watsonx.ai model inference (credentials reserved, not integrated in this version)

---

## Architecture Reference

See [`docs/architecture.md`](architecture.md) for the full component diagram and data flow.
