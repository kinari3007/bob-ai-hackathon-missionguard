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
| **mcp package** | Included in `requirements.txt` — `pip install "mcp[cli]>=2.0.0"` |
| **MissionGuard dependencies** | `pip install -r requirements.txt` (run from repo root) |
| **Dataset generated** | `python -m src.data.generate_dataset` |
| **Repo cloned** | `git clone` or extracted to a local directory |

Verify Python and mcp are installed from the repo root:

```powershell
python --version
python -c "import importlib.metadata; print(importlib.metadata.version('mcp'))"
```

Expected output: `Python 3.x.x` and `2.x.x` respectively.

Verify the MCP server starts cleanly (should return PASS):

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

This file is committed to the repository and is automatically read by IBM Bob when the
workspace is opened. It registers the `missionguard-mcp` server without requiring manual
configuration.

---

## 4. How the Configuration Works

`.bob/mcp.json` contains the following (already committed to the repo):

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

### Field reference

| Field | Purpose |
|---|---|
| `command` | `"python"` — uses the Python from your active environment / PATH |
| `args` | Path to the launcher script, relative to `cwd` |
| `cwd` | `"${workspaceFolder}"` — IBM Bob substitutes the actual workspace folder path |
| `alwaysAllow` | Empty: every tool call requires manual approval in the IBM Bob UI (recommended during demos) |
| `disabled` | `false` — server is active |

### Portability

The configuration uses `${workspaceFolder}` so it works on any machine without manual editing,
as long as the project folder is opened as a workspace in IBM Bob.

> **If IBM Bob on your machine does not expand `${workspaceFolder}`**, update `cwd` manually:
>
> 1. Find your Python executable: `python -c "import sys; print(sys.executable)"`
> 2. Find the absolute path to `run_mcp_server.py` in the cloned repo.
> 3. Update `.bob/mcp.json` accordingly:
>
> ```json
> {
>   "mcpServers": {
>     "missionguard-mcp": {
>       "command": "C:\\path\\to\\python.exe",
>       "args": ["C:\\path\\to\\bob-ai-hackathon-missionguard\\run_mcp_server.py"],
>       "cwd": "C:\\path\\to\\bob-ai-hackathon-missionguard",
>       "alwaysAllow": [],
>       "disabled": false
>     }
>   }
> }
> ```
>
> Do **not** commit machine-specific absolute paths — use `${workspaceFolder}` wherever possible.

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

---

## 8. Approve or Disable Individual Tools

IBM Bob requires explicit approval the first time each tool is called (because `alwaysAllow`
is empty). A confirmation dialog will appear with the tool name and arguments.

- **Approve once** — approves this single call.
- **Always allow** — adds the tool to `alwaysAllow` in `mcp.json` automatically.
- **Disable a tool** — click the toggle next to the tool name in the MCP panel.

Keeping manual approval enabled during the initial demonstration clearly shows each tool
being invoked by IBM Bob.

---

## 9. Example Bob Prompts

Paste any of these into the IBM Bob chat to exercise the MCP tools:

```
Show me the current fleet summary.
```
→ Calls `get_fleet_summary` — returns total assets, readiness/risk counts, top-10 priority queue.

```
Which assets have the highest failure risk?
```
→ Calls `list_assets` with `risk_filter="HIGH"`.

```
Is asset A-017 mission-ready?
```
→ Calls `get_asset_readiness` with `asset_id="A-017"`.

```
Why is asset A-042 at high risk?
```
→ Calls `get_asset_failure_risk` with `asset_id="A-042"` — returns explainable risk factors.

```
Which assets should receive maintenance first?
```
→ Calls `get_fleet_summary` (priority queue) or `list_assets` with `readiness_filter="NOT_READY"`.

```
List all non-mission-ready assets.
```
→ Calls `list_assets` with `readiness_filter="NOT_READY"`.

### Architecture note

IBM Bob is the **conversational interface** — it interprets natural language and decides
which MCP tool to call. The MissionGuard backend (`src/services/risk_engine.py`) performs
all structured risk analysis, readiness classification, and priority ranking. IBM Bob
receives the structured result from the MCP tool and presents it as a natural-language
response to the user.

---

## 10. Troubleshooting

### Server does not appear in the MCP panel

| Check | How |
|---|---|
| Workspace folder open? | File → Open Folder; empty window = no MCP |
| MCP toggle enabled? | MCP settings panel — "Use MCP Servers" must be ON |
| JSON valid? | Run `python -c "import json; json.load(open('.bob/mcp.json'))"` |
| Python on PATH? | Run `python --version` in a terminal |
| Dependencies installed? | Run `pip install -r requirements.txt` |
| Reload done? | Command Palette → Developer: Reload Window |

### Server appears but shows an error

| Symptom | Likely cause | Fix |
|---|---|---|
| `ModuleNotFoundError: src` | Wrong `cwd` | Open workspace folder correctly; or set `cwd` to the repo root |
| `ModuleNotFoundError: mcp` | mcp not installed | `pip install "mcp[cli]>=2.0.0"` |
| `No module named 'mcp.server'` | Old mcp version | Ensure `mcp>=2.0.0` is installed |
| Protocol framing errors | stdout contaminated with logs | Verify nothing prints to stdout at import time |
| Timeout on first call | ML model loading delay | Retry; the risk engine may take a moment on first load |

### Verify manually (STDIO test)

Run this from the repo root — it sends an `initialize` request and should return **PASS**:

```powershell
python test_server_start.py
```

### Check stderr for startup errors

Bob does not surface the server's stderr in the UI. Run the server manually to see startup errors:

```powershell
python run_mcp_server.py
```

Send a line of JSON to stdin:

```
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0.1"}}}
```

A valid response starts with `{"jsonrpc":"2.0","id":1,"result":{...}}`.

### STDIO protocol note

For STDIO MCP servers, **stdout is reserved for the MCP protocol**. Any logging must go to
**stderr**. If any import or startup code prints to stdout, the protocol frame will be
corrupted and Bob will report a parse error.

---

*MCP protocol version: 2024-11-05 · Server name: MissionGuard AI · Transport: stdio*
