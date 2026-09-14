# MissionGuard AI Screenshots

> **Status:** Screenshots will be added before submission.

---

## Required Screenshots (Minimum 3)

Add at least 3 screenshots to this directory before submission.

| # | Filename (suggested) | Content |
|---|---|---|
| 1 | `01-dashboard-fleet-overview.png` | Dashboard main view with KPI cards (Total Assets=100, READY=38, WARNING=35, NOT_READY=27, HIGH RISK=27), fleet readiness chart, and risk distribution chart |
| 2 | `02-risky-asset-detail.png` | Asset detail panel for a HIGH-risk asset (e.g., A-042) showing health score, failure probability, risk factors, and recommended action |
| 3 | `03-ibm-bob-mcp-interaction.png` | IBM Bob chat window showing a conversational query (e.g., "Why is asset A-042 high risk?") and the MCP tool response |

---

## How to Take Screenshots

### Screenshot 1 — Dashboard Fleet Overview

1. Start the FastAPI backend:
   ```powershell
   python -m uvicorn src.api.main:app --reload --port 8000
   ```

2. Start the Streamlit dashboard:
   ```powershell
   python -m streamlit run src/dashboard/app.py
   ```

3. Open **http://localhost:8501** in a browser.

4. Capture the full page showing:
   - KPI cards at the top (100 total, 38 READY, 35 WARNING, 27 NOT_READY, 27 HIGH RISK)
   - Fleet readiness bar/chart
   - Risk distribution chart
   - Maintenance priority queue (top 15 assets)

### Screenshot 2 — Risky Asset Detail

1. With the dashboard running at **http://localhost:8501**:
   - Use the asset dropdown or filter to select a HIGH-risk asset (e.g., A-042)
   - Scroll to the asset detail panel

2. Capture the detail panel showing:
   - Health score and failure probability
   - Risk level (HIGH) and readiness status (NOT_READY)
   - Top 3 risk factors
   - Recommended action

### Screenshot 3 — IBM Bob + MCP Interaction

1. Open the MissionGuard project in IBM Bob (File → Open Folder).
2. Ensure the `missionguard-mcp` server is connected (visible in the MCP panel).
3. In the IBM Bob chat, ask: "Why is asset A-042 at high risk?" or "Give me a fleet overview."
4. When Bob calls the MCP tool (a confirmation dialog may appear), approve the call.
5. Capture the IBM Bob chat window showing:
   - The user prompt
   - The MCP tool call (tool name + parameters visible in IBM Bob UI)
   - Bob's natural-language response with the risk analysis

---

## Image Requirements

- **Format:** PNG or JPG
- **Resolution:** At least 1280×720 (HD or higher preferred)
- **Quality:** Clear, readable text — avoid heavy compression
- **Content:** No sensitive personal information visible in the screenshot

---

## File Naming Convention

Use descriptive, sequential names:
- `01-dashboard-fleet-overview.png`
- `02-risky-asset-detail.png`
- `03-ibm-bob-mcp-interaction.png`

Optional additional screenshots:
- `04-api-swagger-docs.png` — FastAPI Swagger UI at http://localhost:8000/docs
- `05-maintenance-priority-queue.png` — Priority queue close-up
