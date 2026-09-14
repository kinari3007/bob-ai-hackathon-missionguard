# MissionGuard AI — Quick Start Guide

**Status:** ✅ All 71 tests passing — Ready for submission
**Time to demo:** 5 minutes

---

## Instant Demo (3 Commands)

```powershell
# Terminal 1: Backend API
python -m uvicorn src.api.main:app --reload --port 8000

# Terminal 2: Dashboard (in a new terminal)
python -m streamlit run src/dashboard/app.py

# Terminal 3: MCP Server (optional, in a new terminal)
python run_mcp_server.py
```

**Then:**
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## First Time Setup (One-Time, 5 Minutes)

```powershell
# 1. Install all dependencies (no venv required)
pip install -r requirements.txt

# 2. Generate dataset
python -m src.data.generate_dataset

# 3. Verify everything works
python -m pytest -v
```

Expected: **71 tests passing**

---

## What's Implemented

### ✅ Agent 1 — ML / Risk Engine (22 tests)
- Synthetic fleet data (100 assets)
- Hybrid risk scoring (ML + domain)
- Explainable risk factors
- Mission readiness classification
- Maintenance priority ranking

### ✅ Agent 2 — FastAPI API (11 tests)
- 5 REST endpoints
- OpenAPI docs
- CORS support

### ✅ Agent 3 — Streamlit Dashboard (16 tests)
- Fleet overview with KPIs
- Maintenance priority queue
- Asset detail view
- Interactive charts

### ✅ Agent 4 — IBM Bob / MCP Integration (22 tests)
- MCP server with 5 tools
- IBM Bob ready
- Conversational AI interface

---

## Test MCP Integration

```powershell
# Run MCP tests
python -m pytest tests/test_mcp.py -v
```

---

## For Submission Team

**MUST DO (2 hours):**

1. Fill `submission.yaml` with team info
2. Record 3-5 min demo video
3. Take 3+ screenshots
4. Create presentation (5-10 slides)
5. Git push

**See:** `FINAL_PROJECT_AUDIT.md` for complete checklist

---

## Architecture

```
IBM Bob (conversational AI)
    ↓ MCP Protocol
MCP Server (5 tools) — Agent 4
    ↓ Python calls
ML/Risk Engine — Agent 1
    ↓ Data processing
Synthetic Dataset (100 assets)


Parallel:
FastAPI (REST API) — Agent 2
    ↓ HTTP
Streamlit Dashboard — Agent 3
```

---

## Key Files

| File | Purpose |
|---|---|
| `README.md` | Complete project documentation |
| `FINAL_PROJECT_AUDIT.md` | Full audit with submission checklist |
| `AGENT4_HANDOFF.md` | Agent 4 technical handoff |
| `docs/mcp-integration.md` | IBM Bob setup guide |
| `submission.yaml` | Hackathon submission metadata |

---

## Quick Questions

**"Does it work?"**
✅ Yes. 71/71 tests passing.

**"Is IBM Bob integrated?"**
✅ Yes. MCP server implemented and tested. Needs Bob IDE for live testing.

**"What's left to do?"**
📋 Documentation artifacts only: team info, video, screenshots, presentation.

**"How long to submit?"**
⏱️ 2 hours (no code changes needed).

**"What if something breaks?"**
📖 See troubleshooting in `AGENT4_HANDOFF.md` or `docs/mcp-integration.md`.

---

**All technical work complete. Ready for submission.**
