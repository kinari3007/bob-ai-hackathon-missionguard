# MissionGuard AI — IBM Bob / MCP Integration Guide

## Overview

MissionGuard AI exposes its fleet intelligence capabilities through the Model Context Protocol (MCP), enabling IBM Bob and other MCP-compatible AI agents to interact with the risk engine conversationally.

## What is MCP?

The [Model Context Protocol](https://modelcontextprotocol.io/) is a standardized interface that allows AI applications to access tools, resources, and data from external systems. Think of it as an API designed specifically for LLM interactions.

## Architecture

```
IBM Bob / watsonx AI Agent
         ↓  MCP Protocol (stdio or HTTP)
MissionGuard MCP Server  (src/mcp/server.py)
         ↓  Python function calls
Agent 1 ML/Risk Engine  (src/services/risk_engine.py)
         ↓  Data processing
Agent 1 Data & Models  (data/assets.csv + ML models)
```

The MCP layer is a **thin wrapper** that exposes Agent 1 APIs as MCP tools. It does **not** reimplement any risk scoring or ML logic.

## Available MCP Tools

The MissionGuard MCP server exposes 5 tools:

### 1. `list_assets`

**Purpose:** List fleet assets with filtering

**Parameters:**
- `readiness_filter` (optional): Filter by readiness status (`READY`, `WARNING`, `NOT_READY`)
- `risk_filter` (optional): Filter by risk level (`LOW`, `MEDIUM`, `HIGH`)
- `asset_type_filter` (optional): Filter by asset type (e.g., `UAV`, `Ground Vehicle`)

**Returns:** Array of assets with risk scores and readiness information

**Example queries:**
- "Which assets are not mission-ready?"
- "Show all high-risk assets"
- "List all UAVs"

### 2. `get_asset_readiness`

**Purpose:** Get mission-readiness status for a specific asset

**Parameters:**
- `asset_id` (required): Asset identifier (e.g., `A-001`)

**Returns:** Readiness status, health score, risk factors, recommended action

**Example queries:**
- "What is the readiness status of A-042?"
- "Is asset A-017 mission-ready?"

### 3. `get_asset_failure_risk`

**Purpose:** Get failure risk analysis for a specific asset

**Parameters:**
- `asset_id` (required): Asset identifier

**Returns:** Failure probability, risk level, explainable risk factors, recommended action

**Example queries:**
- "Why is asset A-042 at risk?"
- "What are the risk factors for A-017?"
- "Explain the risk level of A-089"

### 4. `get_asset_maintenance`

**Purpose:** Get maintenance priority for a specific asset

**Parameters:**
- `asset_id` (required): Asset identifier

**Returns:** Priority score (0-100), fleet-wide rank, priority reasons, recommended action

**Example queries:**
- "What is the maintenance priority of A-042?"
- "Should we service A-017 soon?"

### 5. `get_fleet_summary`

**Purpose:** Get high-level fleet health overview

**Parameters:** None

**Returns:** Fleet statistics, readiness/risk distributions, top 10 priority assets

**Example queries:**
- "Give me a fleet overview"
- "What's the overall fleet health?"
- "Which assets need service first?"

## Running the MCP Server

### Prerequisites

1. Python 3.11+ (tested with Python 3.14 on Windows)
2. All dependencies installed:
   ```powershell
   pip install -r requirements.txt
   ```

3. Dataset generated:
   ```powershell
   python -m src.data.generate_dataset
   ```

### Standalone Server (stdio)

For local testing with the [MCP Inspector](https://github.com/modelcontextprotocol/inspector):

```powershell
# Option 1: Using mcp dev command
python -m mcp dev src/mcp/server.py

# Option 2: Direct invocation (recommended)
python run_mcp_server.py
```

This starts the server over stdio transport, ready to accept MCP client connections.

### HTTP Server (for remote access)

For deployment or remote IBM Bob instances:

```powershell
python -m mcp run src/mcp/server.py --transport streamable-http --port 8100
```

The server will be available at `http://localhost:8100/mcp`.

## IBM Bob Configuration

### Local Server (stdio)

The workspace-scoped configuration is already committed at `.bob/mcp.json`. For reference,
the structure is:

```json
{
  "mcpServers": {
    "missionguard": {
      "command": "python",
      "args": ["run_mcp_server.py"],
      "cwd": "/absolute/path/to/bob-ai-hackathon-missionguard",
      "env": {
        "MISSIONGUARD_RANDOM_SEED": "42"
      }
    }
  }
}
```

Replace `cwd` with the actual path to your MissionGuard repository.

### Remote Server (HTTP)

If the MCP server is deployed remotely:

```json
{
  "mcpServers": {
    "missionguard": {
      "url": "http://your-server:8100/mcp"
    }
  }
}
```

## Watsonx Integration

The MissionGuard MCP server is designed to work with IBM watsonx through Bob. The environment variables are reserved for watsonx credentials:

```bash
# .env file
WATSONX_API_KEY=your_api_key_here
WATSONX_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**Note:** The current implementation uses synthetic local data. Watsonx credentials are optional for local development and only needed if integrating with watsonx.ai models.

## Testing the Integration

### Unit Tests

Run the MCP test suite:

```powershell
python -m pytest tests/test_mcp.py -v
```

Expected: **22 tests passing**

### Manual Validation

1. Start the MCP server:
   ```powershell
   python -m mcp dev src/mcp/server.py
   ```

2. Open the MCP Inspector in your browser (launched automatically)

3. Test each tool:
   - `list_assets`: Call with no parameters → should return 100 assets
   - `get_asset_readiness`: Call with `asset_id="A-001"` → should return readiness data
   - `get_asset_failure_risk`: Call with `asset_id="A-001"` → should return risk analysis
   - `get_asset_maintenance`: Call with `asset_id="A-001"` → should return priority
   - `get_fleet_summary`: Call with no parameters → should return fleet overview

### IBM Bob Testing

Once configured in Bob:

1. Open IBM Bob
2. Start a conversation
3. Ask: "What is the fleet status?"
4. Bob should call `get_fleet_summary` and report the results
5. Ask: "Why is asset A-042 at risk?"
6. Bob should call `get_asset_failure_risk` for A-042

## Conversation Examples

### Example 1: Fleet Overview

**User:** "Give me a fleet health overview"

**Bob (via MissionGuard MCP):**
- Calls `get_fleet_summary`
- Reports: "The fleet has 100 assets. 38 are READY, 35 are in WARNING status, and 27 are NOT_READY. 27 assets are HIGH risk. The top priority is A-001 with a score of 93.26."

### Example 2: Asset Investigation

**User:** "Why is asset A-042 at risk?"

**Bob:**
- Calls `get_asset_failure_risk("A-042")`
- Reports: "Asset A-042 has a HIGH risk level with 84.7% failure probability. Risk factors: High vibration level, Long interval since maintenance, High engine temperature. Recommended action: Ground the asset and inspect rotating components."

### Example 3: Maintenance Planning

**User:** "Which assets need service first?"

**Bob:**
- Calls `list_assets(readiness_filter="NOT_READY")`
- Or calls `get_fleet_summary` and reports top priority queue
- Lists assets sorted by priority score with recommendations

## Architecture Rules

### What the MCP Layer Does

✅ Exposes Agent 1 APIs as MCP tools
✅ Validates input parameters
✅ Handles exceptions gracefully
✅ Provides clear tool descriptions for Bob
✅ Returns structured data

### What the MCP Layer Does NOT Do

❌ Reimplement risk scoring
❌ Duplicate ML logic
❌ Modify Agent 1 APIs
❌ Change data processing
❌ Access the database directly

## Security Considerations

- The MCP server runs locally or within your trusted network
- No credentials are required for local synthetic data
- For watsonx integration, use environment variables, never hardcode API keys
- The `.env` file is in `.gitignore` to prevent credential leaks

## Troubleshooting

### "Module mcp not found"

Install the MCP SDK:
```powershell
pip install "mcp[cli]>=2.0.0"
```

### "Asset not found" errors

Ensure the dataset is generated:
```powershell
python -m src.data.generate_dataset
```

### sklearn warnings

~1901 sklearn warnings about feature names are expected and safe to ignore. They do not affect functionality.

### Bob cannot connect

1. Verify the MCP server is running:
   ```powershell
   python run_mcp_server.py
   ```

2. Check Bob's MCP config points to the correct path/URL

3. Verify no firewall is blocking the connection (for HTTP transport)

## Deployment

For production or demo deployment:

1. **Local Demo:** Use stdio transport (simplest)
2. **Remote Demo:** Use HTTP transport, deploy behind a reverse proxy
3. **Cloud Deployment:** Consider containerization (Docker) with HTTP transport

Example Dockerfile (optional):
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "mcp", "run", "src/mcp/server.py", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8100"]
```

## Known Limitations

- **Synthetic data only:** No real military telemetry
- **Local model:** Logistic regression + domain heuristics, not deep learning
- **No persistence:** All state is in-memory per request
- **Single-threaded:** Suitable for demo, not high-concurrency production

## Current Status

- ✅ MCP server implemented and tested (22/22 tests passing)
- ✅ IBM Bob MCP integration demonstrated locally
- ⏭️ watsonx.ai model integration (credentials reserved, not required for local demo)
- ⏭️ Authentication (not required for prototype)
- ⏭️ Caching (not required for demo scale)

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [IBM Bob Documentation](https://bob.ibm.com/docs/)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)

---

**Status:** ✅ MCP Integration Complete
**Tests:** 22/22 passing
**Ready for:** IBM Bob configuration and testing
