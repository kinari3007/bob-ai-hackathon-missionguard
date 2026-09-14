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
- **Agent-2 API:** `get_all_assets`, `get_asset_status`, `get_failure_risk`

## Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python |
| **Frameworks** | pandas, NumPy, scikit-learn, pytest |
| **IBM Technologies** | Not wired in this phase (reserved for later agents) |
| **Databases** | Local CSV |
| **Other** | joblib (optional model snapshot) |

## Repository Structure

```
├── src/                  # Risk engine package
├── tests/                # pytest suite
├── data/assets.csv       # Synthetic fleet
├── docs/                 # Including docs/risk-engine.md
├── demo/                 # Demo artifacts (later)
├── presentation/         # Slide deck (later)
└── submission.yaml       # Hackathon metadata (fill before submit)
```

## How to Run

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m src.data.generate_dataset
python -m src
python -m pytest
```

Details: [`docs/setup-guide.md`](docs/setup-guide.md) and [`docs/risk-engine.md`](docs/risk-engine.md).

## Demo

| Artifact | Link |
|---|---|
| Demo Video | Not recorded yet — see `demo/demo-video-link.txt` |
| Live Demo | Not deployed — run locally |
| Screenshots | Later (dashboard agent) |
| Presentation | Later |

## Known Limitations

- Synthetic data only; no real platform telemetry
- No IBM Bob, MCP, HTTP API, or UI in this phase
- Logistic regression + heuristic blend, not deep learning
- Labels are generated, not observed failures

## What We're Most Proud Of

A small, tested, explainable scoring pipeline that another agent can call as plain Python without re-implementing the model.
