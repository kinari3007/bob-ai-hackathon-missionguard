"""Quick MCP validation script"""
import asyncio
from src.mcp.server import create_mcp_server

async def main():
    mcp = create_mcp_server()
    tools = await mcp.list_tools()

    print(f"✓ MCP Server: {mcp.name}")
    print(f"✓ Tools registered: {len(tools)}")
    print("\nTools:")
    for tool in tools:
        desc = tool.description[:80] + "..." if len(tool.description) > 80 else tool.description
        print(f"  • {tool.name}")
        print(f"    {desc}")

    print("\n✓ MCP layer validated successfully!")

if __name__ == "__main__":
    asyncio.run(main())
