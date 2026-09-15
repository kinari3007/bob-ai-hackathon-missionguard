# MissionGuard AI — Setup Guide

> **Local demo only.** There is no public deployment. All components run on your local machine.

---

## Prerequisites

| Requirement | Version | How to verify |
|---|---|---|
| Python | 3.11 or later (tested with 3.14 on Windows) | `python --version` |
| pip | any recent version | `pip --version` |
| Git | any | `git --version` |

No IBM Cloud account, Docker, or external services are required for the local demo.

---

## 1 — Clone the Repository

```powershell
git clone https://github.com/[your-org]/bob-ai-hackathon-missionguard.git
cd bob-ai-hackathon-missionguard
```

---

## 2 — Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs all dependencies for every layer: ML/data, FastAPI, Streamlit, and MCP.

> **Virtual environment (recommended):**
> ```powershell
> python -m venv .venv
> .\.venv\Scripts\Activate.ps1   # PowerShell
> # or
> .venv\Scripts\activate          # Command Prompt
> pip install -r requirements.txt
> ```

---

## 3 — Generate the Synthetic Dataset (first time only)

```powershell
python -m src.data.generate_dataset
```

Creates `data/assets.csv` with 100 reproducible synthetic assets (seed=42).
Safe to re-run — it will not change results because the seed is fixed.

---

## 4 — Run the Application

The full stack uses three terminals. Start them in order.

### Terminal 1 — FastAPI Backend

```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```

Verify it is running:

```
GET http://localhost:8000/health
→ {"status": "ok", "service": "MissionGuard API", "version": "1.0.0"}
```

| URL | Description |
|---|---|
| http://localhost:8000/health | Health check |
| http://localhost:8000/assets | All 100 assets |
| http://localhost:8000/docs | Swagger UI (interactive API docs) |
| http://localhost:8000/redoc | ReDoc |

### Terminal 2 — Streamlit Dashboard

```powershell
python -m streamlit run src/dashboard/app.py
```

Dashboard available at **http://localhost:8501**.

The dashboard connects to the FastAPI backend at `http://localhost:8000` by default.
Override with the `MISSIONGUARD_API_URL` environment variable if your backend is on a different port:

```powershell
# PowerShell
$env:MISSIONGUARD_API_URL = "http://localhost:8000"
python -m streamlit run src/dashboard/app.py
```

### Terminal 3 — MCP Server (for IBM Bob integration)

```powershell
python run_mcp_server.py
```

The server runs over stdio transport and is ready for IBM Bob to connect.
See [IBM Bob Setup](#6--ibm-bob-setup) below for configuration details.

---

## 5 — Run the Test Suite

```powershell
python -m pytest -v
```

Expected result: **71 tests passing**.

```
tests/test_data_loader.py            5 passed
tests/test_risk_engine.py            9 passed
tests/test_maintenance_priority.py   8 passed
tests/test_api.py                   11 passed
tests/test_dashboard.py             16 passed
tests/test_mcp.py                   22 passed
──────────────────────────────────────────────
71 passed in ~3.69s
```

Non-fatal warnings you may see (safe to ignore):
- ~1901 sklearn `UserWarning` about feature names — informational only, no effect on scores
- 1 Starlette/AnyIO `DeprecationWarning` — benign

To run only the MCP tests:

```powershell
python -m pytest tests/test_mcp.py -v
```

To verify the MCP server starts and responds to IBM Bob's initialization handshake:

```powershell
python test_server_start.py
```

Expected: `RESULT: PASS`

---

## 6 — IBM Bob Setup

IBM Bob reads `.bob/mcp.json` when the workspace folder is open.
This file is already committed to the repository and registers the `missionguard-mcp` server.

### Step 1 — Open the project folder in IBM Bob

1. Launch IBM Bob.
2. **File → Open Folder** → navigate to the cloned `bob-ai-hackathon-missionguard` directory → click **Open**.

> IBM Bob's MCP servers only activate when a workspace folder is open.

### Step 2 — Verify the MCP configuration

The file `.bob/mcp.json` contains:

```json
{
  "mcpServers": {
    "missionguard-mcp": {
      "command": "python",
      "args": ["run_mcp_server.py"],
      "cwd": "${workspaceFolder}",
      "alwaysAllow": [],
      "disabled": false
    }
  }
}
```

`${workspaceFolder}` is substituted with the actual repo path by IBM Bob. No manual path editing is needed as long as the workspace folder is opened correctly.

> **If IBM Bob does not expand `${workspaceFolder}`** on your installation, replace it with the
> absolute path to the repository root:
> ```json
> "cwd": "C:\\path\\to\\bob-ai-hackathon-missionguard"
> ```
> Find the correct Python executable with: `python -c "import sys; print(sys.executable)"`

### Step 3 — Enable MCP servers

1. Open the **Command Palette** (`Ctrl+Shift+P`).
2. Type `MCP` and select **MCP: Open MCP Settings** (or the equivalent in your Bob version).
3. Ensure **"Use MCP Servers"** is **ON**.

### Step 4 — Reload IBM Bob

After saving `.bob/mcp.json` for the first time (or after any change):

- **Command Palette → Developer: Reload Window**

### Step 5 — Confirm the server appears

Open the MCP panel and look for **missionguard-mcp**. Expand it — you should see five tools:
`list_assets`, `get_asset_readiness`, `get_asset_failure_risk`, `get_asset_maintenance`, `get_fleet_summary`.

### Example Bob Prompts

```
"Show me the current fleet summary."
"Which assets have the highest failure risk?"
"Is asset A-017 mission-ready?"
"Why is asset A-042 high risk?"
"Which assets should receive maintenance first?"
```

IBM Bob routes each prompt to the appropriate MCP tool. The MissionGuard backend performs
all structured risk analysis; IBM Bob formats and presents the results conversationally.

---

## 7 — Environment Variables (Optional)

Copy `src/.env.example` to `.env` at the repo root:

```powershell
copy src\.env.example .env
```

No credentials are required for the local demo. The `.env` file is gitignored.

```
# Optional overrides
MISSIONGUARD_RANDOM_SEED=42

# Reserved for future watsonx.ai integration — not required locally
# WATSONX_API_KEY=your_api_key_here
# WATSONX_PROJECT_ID=your_project_id_here
# WATSONX_URL=https://us-south.ml.cloud.ibm.com
# MISSIONGUARD_API_URL=http://localhost:8000
```

---

## 8 — Optional: Run the Risk Engine Directly

```powershell
python -m src
```

Generates the dataset if missing, scores all 100 assets, and prints a summary to the console.

Python REPL example:

```python
from src.services.risk_engine import get_all_assets, get_asset_status, get_failure_risk, get_maintenance_priority

print(get_asset_status("A-017"))
print(get_failure_risk("A-042"))
print(get_maintenance_priority("A-001"))
```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: pandas` | Activate `.venv` and run `pip install -r requirements.txt` |
| `ModuleNotFoundError: mcp` | Run `pip install "mcp[cli]>=2.0.0"` |
| `ModuleNotFoundError: src` | Run commands from the **repository root** (where `src/` folder is) |
| Dataset missing | `python -m src.data.generate_dataset` |
| Dashboard shows "API offline" | Start the FastAPI backend first (`python -m uvicorn src.api.main:app --port 8000`) |
| `pytest` not found | Use `python -m pytest` instead of bare `pytest` |
| Execution policy blocks `Activate.ps1` | Use `python -m uvicorn ...` directly without activating the venv |
| MCP server not found in Bob | Check workspace folder is open; reload window (`Ctrl+Shift+P → Developer: Reload Window`) |
| Bob cannot connect to MCP | Run `python test_server_start.py` — should return `RESULT: PASS` |
| sklearn feature-name warnings | ~1901 warnings are expected and non-fatal — scores are not affected |
