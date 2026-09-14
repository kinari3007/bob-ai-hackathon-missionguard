"""
MissionGuard MCP Server Launcher

Starts the MissionGuard MCP server over stdio transport for IBM Bob integration.

Usage:
    python run_mcp_server.py

For IBM Bob configuration, add this to your Bob MCP config:
    {
        "missionguard": {
            "command": "python",
            "args": ["run_mcp_server.py"],
            "cwd": "/path/to/bob-ai-hackathon-missionguard"
        }
    }
"""

import asyncio
import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.mcp.server import create_mcp_server
from mcp.server.stdio import stdio_server


async def main():
    """Run the MCP server over stdio transport."""
    async with stdio_server() as (read_stream, write_stream):
        mcp = create_mcp_server()
        await mcp.run(
            read_stream,
            write_stream,
            mcp.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
