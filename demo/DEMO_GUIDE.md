# MissionGuard AI — Demo Guide

> All data, metrics, and tool outputs on this page are real outputs from the validated system
> (Python 3.14, seed=42). Nothing is invented.

---

## Pre-Demo Checklist

Before presenting, have these three terminals ready:

```powershell
# Terminal 1 — FastAPI backend
python -m uvicorn src.api.main:app --port 8000

# Terminal 2 — Streamlit dashboard
python -m streamlit run src/dashboard/app.py

# Terminal 3 — (optional, for MCP demo)
python run_mcp_server.py
```

Confirm the backend is healthy:
```
GET http://localhost:8000/health
→ {"status": "ok", "service": "MissionGuard AI", "version": "1.0.0"}
```

---

## Demo Flow (10–15 minutes)

---

### Step 1 — Show the Fleet Overview

Open the Streamlit dashboard at **http://localhost:8501**.

**What to point to:**

The KPI cards at the top show the live fleet state (from seed=42 dataset):

| KPI | Value |
|---|---|
| Total Assets | 100 |
| READY | 38 |
| WARNING | 35 |
| NOT_READY | 27 |
| HIGH RISK | 27 |

**Talking point:** "MissionGuard scans the entire 100-asset fleet instantly. 27 assets are
NOT_READY right now — that's 27% of the fleet unavailable for a mission."

---

### Step 2 — Show High-Risk Assets

In the dashboard sidebar, set the **Readiness Filter** to `NOT_READY`.

The priority queue below updates immediately to show only the 27 non-ready assets, sorted by
urgency score.

**Top 5 highest-priority assets (actual data):**

| Rank | Asset ID | Priority Score | Risk Level | Readiness |
|---|---|---|---|---|
| 1 | A-017 | 100.0 | HIGH | NOT_READY |
| 2 | A-067 | 100.0 | HIGH | NOT_READY |
| 3 | A-079 | 100.0 | HIGH | NOT_READY |

**Talking point:** "Assets with a priority score of 100 are the most urgent — HIGH risk AND
NOT_READY. Maintenance should start here."

---

### Step 3 — Open One Asset Detail View

In the dashboard sidebar, type **A-042** in the Asset ID field.

**Actual output for A-042:**

| Field | Value |
|---|---|
| Asset Type | (shown in dashboard) |
| Health Score | 25.1 (on a scale of 0–100) |
| Failure Probability | 62.3% |
| Risk Level | HIGH |
| Readiness | NOT_READY |
| Priority Rank | (shown in dashboard) |

---

### Step 4 — Explain the Risk Factors

Still on the A-042 detail view, scroll to the **Risk Factors** section.

**Actual risk factors for A-042:**
1. High utilization intensity
2. Many days since last service
3. Elevated fuel consumption

**Recommended action:** Schedule inspection and preventive maintenance

**Talking point:** "Every score is explainable. We don't just say 'HIGH risk' — we tell the
maintainer exactly what is driving that risk and what to do about it. No black box."

---

### Step 5 — Show the Maintenance Priority Queue

Scroll to the **Maintenance Priority Queue** section (clear the readiness filter first to show
all assets). The top 15 assets are ranked by urgency.

**Talking point:** "The priority queue answers the hardest question in fleet maintenance:
*what should we do first?* The score is deterministic — it won't change unless the underlying
sensor data changes."

---

### Step 6 — Demonstrate the REST API

Switch to a browser and navigate to **http://localhost:8000/docs** to show the Swagger UI.

Demonstrate three live calls:

**Health check:**
```
GET /health
→ 200 {"status": "ok", "service": "MissionGuard AI", "version": "1.0.0"}
```

**Risk analysis for A-042:**
```
GET /assets/A-042/risk
→ 200
{
  "asset_id": "A-042",
  "health_score": 25.1,
  "failure_probability": 0.623,
  "risk_level": "HIGH",
  "top_risk_factors": [
    "High utilization intensity",
    "Many days since last service",
    "Elevated fuel consumption"
  ],
  "recommended_action": "Schedule inspection and preventive maintenance"
}
```

**Unknown asset (error handling):**
```
GET /assets/INVALID-999/status
→ 404 {"detail": "Asset INVALID-999 not found"}
```

**Talking point:** "The API is fully documented, returns structured JSON, and handles errors
cleanly. Any system — including IBM Bob — can call it."

---

### Step 7 — Demonstrate the MCP Tools

Open a Python REPL or show Terminal 3. Walk through the five MCP tools using the underlying
APIs directly (the MCP server wraps these exact same calls):

```python
from src import get_all_assets, get_asset_status, get_failure_risk, get_maintenance_priority

# Tool 1: list_assets — all assets
assets = get_all_assets()
print(len(assets))           # 100
print(assets[0].keys())      # ['asset_id', 'asset_type', 'health_score', ...]

# Tool 1: list_assets — filtered
not_ready = [a for a in assets if a["readiness_status"] == "NOT_READY"]
print(len(not_ready))        # 27

# Tool 2: get_asset_readiness
status = get_asset_status("A-017")
print(status["readiness_status"])   # NOT_READY
print(status["health_score"])       # (actual value)

# Tool 3: get_asset_failure_risk
risk = get_failure_risk("A-042")
print(risk["failure_probability"])  # 0.623
print(risk["top_risk_factors"])     # ['High utilization intensity', ...]

# Tool 4: get_asset_maintenance
priority = get_maintenance_priority("A-017")
print(priority["priority_rank"])    # 1
print(priority["priority_score"])   # 100.0

# Tool 5: get_fleet_summary (computed by MCP server)
# READY=38, WARNING=35, NOT_READY=27
# LOW=38, MEDIUM=35, HIGH=27
# Top priority: A-017 (score=100, rank=1)
```

**Talking point:** "IBM Bob calls these same functions through MCP. The MCP layer is a thin
wrapper — no risk logic is duplicated."

---

### Step 8 — Show Conversational AI Questions

Demonstrate how IBM Bob would answer these questions using MCP (show the tool mapping):

---

**Q: "Which assets are mission-ready?"**

```
Bob calls: list_assets(readiness_filter="READY")
Result: 38 assets with readiness_status=READY
Bob says: "38 assets are currently mission-ready (38% of the fleet)."
```

---

**Q: "Which assets have the highest failure risk?"**

```
Bob calls: list_assets(risk_filter="HIGH")
Result: 27 assets with risk_level=HIGH
Bob says: "27 assets are HIGH risk. Top priority is A-017 with a score of 100."
```

---

**Q: "Why is asset A-042 high risk?"**

```
Bob calls: get_asset_failure_risk("A-042")
Result:
  failure_probability: 0.623
  risk_level: HIGH
  top_risk_factors: ["High utilization intensity",
                     "Many days since last service",
                     "Elevated fuel consumption"]
  recommended_action: "Schedule inspection and preventive maintenance"

Bob says: "Asset A-042 is HIGH risk with a 62.3% failure probability.
           The main factors are high utilization intensity, overdue
           maintenance, and elevated fuel consumption. Recommended
           action: schedule inspection and preventive maintenance."
```

---

**Q: "Which maintenance tasks should happen first?"**

```
Bob calls: get_fleet_summary()
Result: top_priority_assets[0] = A-017 (score=100, rank=1, NOT_READY, HIGH)

Bob says: "The highest priority asset is A-017 (score 100/100, ranked #1),
           followed by A-067 and A-079, all NOT_READY and HIGH risk."
```

---

**Q: "Summarize fleet readiness."**

```
Bob calls: get_fleet_summary()
Result:
  total_assets: 100
  readiness: READY=38 (38%), WARNING=35 (35%), NOT_READY=27 (27%)
  risk:       LOW=38 (38%), MEDIUM=35 (35%), HIGH=27 (27%)

Bob says: "Fleet summary: 100 assets total. 38 are mission-ready,
           35 are in warning status, and 27 are not ready for deployment.
           27 assets are at HIGH failure risk. Top maintenance focus:
           27 NOT_READY assets, 27 HIGH-risk assets."
```

---

## Test Results (actual, not fabricated)

```
Platform: Python 3.14.7 / Windows
Test runner: pytest 9.1.1
Run command: python -m pytest tests/ -v

tests/test_api.py                  11 passed
tests/test_dashboard.py            16 passed
tests/test_data_loader.py           5 passed
tests/test_maintenance_priority.py  8 passed
tests/test_mcp.py                  22 passed
tests/test_risk_engine.py           9 passed
────────────────────────────────────────────
TOTAL                              71 passed   in 16.30s
```

Warnings (non-fatal):
- ~1900 sklearn `UserWarning` about feature names — benign, no effect on scores
- 1 starlette `DeprecationWarning` about `anyio.abc.BlockingPortal` — benign

---

## Remaining Steps for Submission

| Item | Status | Required action |
|---|---|---|
| Team info in `submission.yaml` | ⚠️ Empty | Fill in team name, lead, members, email |
| Demo video | ⚠️ Not recorded | Record and add URL to `demo/demo-video-link.txt` |
| Screenshots | ⚠️ Empty | Add to `demo/screenshots/` |
| Presentation slides | ⚠️ Empty | Add to `presentation/` |
| IBM Bob live test | ⚠️ Requires Bob | Install IBM Bob, add MCP config, test conversation |
| `submission.yaml` language version | ⚠️ Says Python 3.13 | Update to Python 3.14 |
