# MissionGuard AI — Quick Start Guide

**Team:** Team Sher
**Status:** ✅ All 71 tests passing (71 passed in 3.69s) — Ready for submission
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

Expected: **71 tests passing** (71 passed in 3.69s)
Non-fatal warnings: ~1901 sklearn feature-name warnings + 1 Starlette deprecation — all safe to ignore

---

## What's Implemented

### ✅ ML / Risk Engine (22 tests)
- Synthetic fleet data (100 assets)
- Hybrid risk scoring (ML + domain)
- Explainable risk factors
- Mission readiness classification
- Maintenance priority ranking

### ✅ FastAPI API (11 tests)
- 5 REST endpoints
- OpenAPI docs
- CORS support

### ✅ Streamlit Dashboard (16 tests)
- Fleet overview with KPIs
- Maintenance priority queue
- Asset detail view
- Interactive charts

### ✅ IBM Bob / MCP Integration (22 tests)
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

**REMAINING ACTIONS (before final submission):**

1. ✅ `submission.yaml` — team info filled (Team Sher)
2. ⚠️ Record 3–5 min demo video → add URL to `demo/demo-video-link.txt`
3. ⚠️ Add 3 screenshots to `demo/screenshots/` (dashboard, asset detail, IBM Bob+MCP)
4. ⚠️ Add presentation to `presentation/` as `MissionGuard-AI-Presentation.pdf` or `.pptx`
5. Git push → confirm GitHub Actions ✅ Validate Submission passes

**Note:** There is no live deployment. Project runs locally only.

**See:** `docs/setup-guide.md` for the full setup guide · `demo/DEMO_GUIDE.md` for demo script

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
| `submission.yaml` | Hackathon submission metadata |
| `docs/setup-guide.md` | Full setup and run guide |
| `docs/mcp-integration.md` | MCP tool reference |
| `docs/bob-mcp-integration.md` | IBM Bob step-by-step setup |
| `docs/architecture.md` | System architecture overview |

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
📖 See troubleshooting in `docs/mcp-integration.md` or `docs/bob-mcp-integration.md`.

---

**All technical work complete. Ready for submission.**
