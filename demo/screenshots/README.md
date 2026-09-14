# MissionGuard AI Screenshots

**Instructions:** Add at least 3 screenshots to this directory.

## Required Screenshots (Minimum 3)

1. **dashboard-main-view.png** — Dashboard with KPI cards, fleet overview, risk distribution
2. **priority-queue.png** — Maintenance priority queue showing top 15 assets
3. **asset-detail.png** — Asset detail view with risk factors and recommended action

## Optional Screenshots (Nice to Have)

4. **api-docs.png** — FastAPI Swagger documentation at http://localhost:8000/docs
5. **bob-conversation.png** — IBM Bob asking about fleet health (if Bob is installed)
6. **mcp-inspector.png** — MCP Inspector showing registered tools
7. **architecture-diagram.png** — Architecture overview from README

## How to Take Screenshots

### Dashboard (http://localhost:8501)

1. Start FastAPI backend:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn src.api.main:app --reload --port 8000
   ```

2. Start Streamlit dashboard:
   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run src/dashboard/app.py
   ```

3. Navigate to http://localhost:8501

4. Take screenshots:
   - Main view: Full page with KPI cards, charts
   - Priority queue: Scroll to "Maintenance Priority Queue" section
   - Asset detail: Use dropdown to select an asset (e.g., A-001), show detail panel

### API Docs (http://localhost:8000/docs)

1. Ensure backend is running
2. Open http://localhost:8000/docs in browser
3. Take screenshot showing all 5 endpoints

### IBM Bob (Optional)

1. Configure Bob per `docs/mcp-integration.md`
2. Ask Bob: "Give me a fleet overview"
3. Take screenshot of Bob's response

## File Naming Convention

Use descriptive kebab-case names:
- `dashboard-main-view.png`
- `maintenance-priority-queue.png`
- `asset-detail-a001.png`
- `fastapi-swagger-docs.png`
- `ibm-bob-fleet-query.png`

## Image Requirements

- Format: PNG or JPG
- Resolution: At least 1280x720 (HD)
- Quality: High (not compressed/blurry)
- Content: Clear, readable text
- No sensitive information

---

**Current status:** Placeholder README — Add actual screenshots before submission
