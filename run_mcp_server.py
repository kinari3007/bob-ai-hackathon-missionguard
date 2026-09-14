"""
MissionGuard MCP Server Launcher

Starts the MissionGuard MCP server over stdio transport for IBM Bob integration.

Usage:
    python run_mcp_server.py

For IBM Bob configuration, add this to your Bob MCP config:
    {
        "mcpServers": {
            "missionguard-mcp": {
                "command": "python",
                "args": ["run_mcp_server.py"],
                "cwd": "/absolute/path/to/bob-ai-hackathon-missionguard"
            }
        }
    }
"""

import asyncio
import sys
from pathlib import Path

# Ensure the repository root is on sys.path so that `import src.*` resolves
# correctly.  Do NOT add the src/ subdirectory itself — that would shadow the
# installed `mcp` package with src/mcp/ and cause a circular import.
_repo_root = Path(__file__).resolve().parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from src.mcp.server import create_mcp_server


async def main() -> None:
    """Run the MCP server over stdio transport."""
    mcp = create_mcp_server()
    await mcp.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())
