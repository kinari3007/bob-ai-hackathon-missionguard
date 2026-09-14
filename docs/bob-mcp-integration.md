# MissionGuard — IBM Bob MCP Integration Guide

This guide covers every step required to connect the MissionGuard MCP server to IBM Bob,
from prerequisites through live tool verification.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Open the Project in IBM Bob](#2-open-the-project-in-ibm-bob)
3. [Configuration File Location](#3-configuration-file-location)
4. [How the Configuration Works](#4-how-the-configuration-works)
5. [Enable MCP Servers in IBM Bob](#5-enable-mcp-servers-in-ibm-bob)
6. [Reload IBM Bob](#6-reload-ibm-bob)
7. [Confirm the Server Appears](#7-confirm-the-server-appears)
8. [Approve or Disable Individual Tools](#8-approve-or-disable-individual-tools)
9. [Example Bob Prompts](#9-example-bob-prompts)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Prerequisites

| Requirement | Detail |
|---|---|
| **IBM Bob** | Installed and working; workspace folder support required |
| **Python 3.11+** | `python --version` must return 3.11 or higher |
| **mcp package** | `pip install "mcp[cli]>=2.0.0"` |
| **MissionGuard dependencies** | `pip install -r requirements.txt` (run from repo root) |
| **Repo cloned** | `git clone` or extracted to a local directory |

Verify Python and mcp are installed from the repo root:

```powershell
python --version
python -c "import importlib.metadata; print(importlib.metadata.version('mcp'))"
```

Expected output: `Python 3.x.x` and `2.x.x` respectively.

Verify the server starts cleanly (should return PASS):

```powershell
python test_server_start.py
```

---

## 2. Open the Project in IBM Bob

1. Launch IBM Bob.
2. Go to **File → Open Folder**.
3. Navigate to the cloned `bob-ai-hackathon-missionguard` directory and click **Open**.

> **Important:** IBM Bob's MCP servers only activate when a workspace folder is open.
> They do **not** connect in an empty window.

---

## 3. Configuration File Location

The workspace-scoped MCP configuration lives at:

```
<repo-root>/.bob/mcp.json
```

This file is automatically read by IBM Bob when the workspace is opened. It overrides
any global MCP settings for servers with the same name.

---

## 4. How the Configuration Works

`.bob/mcp.json` contains a single server entry:

```json
{
  "mcpServers": {
    "missionguard-mcp": {
      "command": "C:\\Users\\Preneel\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe",
      "args": [
        "C:\\Users\\Preneel\\OneDrive\\Desktop\\Himay\\bob-ai-hackathon-missionguard\\run_mcp_server.py"
      ],
      "cwd": "C:\\Users\\Preneel\\OneDrive\\Desktop\\Himay\\bob-ai-hackathon-missionguard",
      "alwaysAllow": [],
      "disabled": false
    }
  }
}
```

### Field reference

| Field | Purpose |
|---|---|
| `command` | Absolute path to the Python executable — **must be updated on each machine** |
| `args` | Absolute path to the launcher script — **must be updated on each machine** |
| `cwd` | Repo root — required so `import src.*` resolves correctly |
| `alwaysAllow` | Empty: every tool call requires manual approval (recommended) |
| `disabled` | `false` — server is active |

### ⚠️ Porting to another machine

IBM Bob does **not** expand `${workspaceFolder}` in `mcp.json`. When moving this project
to a different machine or user account, update the three absolute paths:

1. `command` → output of `python -c "import sys; print(sys.executable)"`
2. `args[0]` → full path to `run_mcp_server.py` in the cloned repo
3. `cwd` → full path to the repo root

---

## 5. Enable MCP Servers in IBM Bob

1. Open the **Command Palette** (`Ctrl+Shift+P` / `Cmd+Shift+P`).
2. Type **"MCP"** and select **"MCP: Open MCP Settings"** (or open the MCP panel from the
   activity bar if your version shows it there).
3. Ensure **"Use MCP Servers"** (or equivalent toggle) is **ON**.
4. IBM Bob hot-reloads `.bob/mcp.json` on save — no manual restart is needed after
   saving the file for the first time.

---

## 6. Reload IBM Bob

If the server does not appear automatically after saving `.bob/mcp.json`:

- **Command Palette → "Developer: Reload Window"** — fastest option.
- Or fully restart IBM Bob (close and reopen).

After reload, Bob spawns the Python process in the background. The server typically
registers within 2–5 seconds.

---

## 7. Confirm the Server Appears

1. Open the MCP panel / settings view.
2. Look for **missionguard-mcp** in the list of connected servers.
3. Expand it — you should see all **five tools** listed:

| Tool name | Description |
|---|---|
| `list_assets` | List fleet assets with optional readiness / risk / type filters |
| `get_asset_readiness` | Mission-readiness status and evidence for a specific asset |
| `get_asset_failure_risk` | Failure probability, risk factors, and recommended action |
| `get_asset_maintenance` | Maintenance priority score, rank, and reasons for a specific asset |
| `get_fleet_summary` | High-level fleet health summary and top-10 priority queue |

> **Note on tool names:** The task specification mentioned `get_maintenance_priority`, but
> the MCP tool is registered as **`get_asset_maintenance`** — this is the name Bob will display.

---

## 8. Approve or Disable Individual Tools

IBM Bob requires explicit approval the first time each tool is called (because `alwaysAllow`
is empty). A confirmation dialog will appear with the tool name and arguments.

- **Approve once** — approves this single call.
- **Always allow** — adds the tool to `alwaysAllow` in `mcp.json` automatically.
- **Disable a tool** — click the toggle next to the tool name in the MCP panel, or add its
  name to `disabledTools` in `.bob/mcp.json`.

Keep manual approval enabled during the initial demonstration to clearly show each tool
being invoked.

---

## 9. Example Bob Prompts

Paste any of these into the Bob chat to exercise the MCP tools:

```
Show me the current fleet summary.
```
→ Calls `get_fleet_summary` — returns total assets, readiness/risk counts, top-10 priority queue.

```
Which assets have the highest failure risk?
```
→ Calls `list_assets` with `risk_filter="HIGH"`.

```
Show me the readiness status of asset ASSET-001.
```
→ Calls `get_asset_readiness` with `asset_id="ASSET-001"`.

```
Which assets should receive maintenance first?
```
→ Calls `get_fleet_summary` (priority queue) or `list_assets` with `readiness_filter="NOT_READY"`.

```
Explain why asset ASSET-001 has a high failure risk.
```
→ Calls `get_asset_failure_risk` with `asset_id="ASSET-001"` — returns explainable risk factors.

```
List all non-mission-ready assets and explain the reasons.
```
→ Calls `list_assets` with `readiness_filter="NOT_READY"`, then Bob may follow up with
`get_asset_failure_risk` for each returned asset.

---

## 10. Troubleshooting

### Server does not appear in the MCP panel

| Check | How |
|---|---|
| Workspace folder open? | File → Open Folder; empty window = no MCP |
| MCP toggle enabled? | MCP settings panel — "Use MCP Servers" must be ON |
| JSON valid? | Run `python -c "import json; json.load(open('.bob/mcp.json'))"` |
| Python path correct? | Run `"C:\path\to\python.exe" --version` in a terminal |
| Script path correct? | Confirm `run_mcp_server.py` exists at the path in `args` |
| Reload done? | Command Palette → Developer: Reload Window |

### Server appears but shows an error

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: src` | Wrong `cwd` | Set `cwd` to the repo root |
| `ModuleNotFoundError: mcp` | mcp not installed for this Python | `python -m pip install "mcp[cli]>=2.0.0"` |
| `No module named 'mcp.server.fastmcp'` | Using wrong `mcp` version | Ensure `mcp>=2.0.0` is installed |
| Protocol framing errors | stdout contaminated with logs | Verify nothing prints to stdout at import time |
| Timeout on first call | ML model loading delay | Retry; the risk engine may take a moment on first load |

### Verify manually (STDIO test)

Run this from the repo root — it sends an `initialize` request and should return **PASS**:

```powershell
python test_server_start.py
```

### Check stderr for startup errors

Bob does not surface the server's stderr in the UI. Run the server manually to see any
startup errors:

```powershell
python run_mcp_server.py
```
Send a line of JSON to stdin, e.g.:
```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}
```
A valid response starts with `{"jsonrpc":"2.0","id":1,"result":{...}}`.

### STDIO protocol note

For STDIO MCP servers, **stdout is reserved for the MCP protocol**. Any normal logging
must go to **stderr**. If any import or startup code prints to stdout, the protocol frame
will be corrupted and Bob will report a parse error. Check `run_mcp_server.py` and all
imports for stray `print()` calls.

---

*Last updated: Phase 5 integration — IBM Bob MCP server configured and validated.*
