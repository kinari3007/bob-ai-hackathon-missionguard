# MissionGuard AI — Demo

> **Deployment:** This is a local demo project. There is no public deployment.
> Judges run the project locally using `docs/setup-guide.md`.

---

## Demo Contents

| File / Directory | Description |
|---|---|
| `demo-video-link.txt` | ⚠️ Video URL — to be provided before submission |
| `live-demo-url.txt` | NOT DEPLOYED — project runs locally |
| `screenshots/` | Screenshots of the running application (to be added) |
| `DEMO_GUIDE.md` | Detailed demo script with actual data values and talking points |

---

## Intended Demo Flow

The planned demonstration sequence:

1. **Dashboard** — open `http://localhost:8501`, show fleet overview KPI cards (100 assets, 38 READY, 35 WARNING, 27 NOT_READY)
2. **Select a risky asset** — filter to NOT_READY assets; navigate to the highest-priority asset in the priority queue
3. **View risk factors** — open the asset detail panel, show health score, failure probability, and the three top risk factors
4. **Ask IBM Bob** — in IBM Bob, ask "Why is this asset at high risk?" or "What is the maintenance priority for A-017?"
5. **Bob calls MCP** — IBM Bob routes the question to the appropriate MCP tool (`get_asset_failure_risk` or `get_asset_maintenance`)
6. **Retrieve result** — the MissionGuard backend returns structured risk data via the MCP tool
7. **Bob explains** — IBM Bob formats the result as a natural-language response, showing the risk factors and recommended action

> This is the intended/planned demo flow. The specific asset IDs and exact wording may vary during the live demo.

---

## Running Locally

See `docs/setup-guide.md` for the full setup guide. Quick start:

```powershell
# Terminal 1 — Backend API
python -m uvicorn src.api.main:app --reload --port 8000

# Terminal 2 — Dashboard
python -m streamlit run src/dashboard/app.py

# Terminal 3 — MCP Server (for IBM Bob)
python run_mcp_server.py
```

- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

---

## Screenshots

Three screenshots will be added to `demo/screenshots/` before submission:

1. Dashboard / fleet overview with KPI cards
2. Risky asset detail with risk factors
3. IBM Bob + MCP interaction

See `demo/screenshots/README.md` for naming conventions and requirements.

---

## Video

The demo video URL will be added to `demo/demo-video-link.txt` before submission.

**Planned video content (3–5 minutes):**

1. Introduction — project name, team, problem statement
2. Dashboard walkthrough — fleet overview, priority queue, asset detail
3. Risk factor explanation — explainability in action
4. IBM Bob + MCP demonstration — conversational fleet query
5. Conclusion — test suite passing, architectural highlights

---

## Test Results

```
71 passed in 3.69s
(1901 non-fatal warnings — sklearn feature names + Starlette deprecation)
```

See `demo/DEMO_GUIDE.md` for the full test output breakdown and actual data values.
