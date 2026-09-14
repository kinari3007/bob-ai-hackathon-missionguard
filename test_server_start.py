"""
Test that the MCP server starts and responds to a JSON-RPC 'initialize'
request over stdio, exactly as IBM Bob would call it.

All output is ASCII-only to avoid Windows cp1252 encoding issues.
"""
import asyncio
import json
import sys
from pathlib import Path

PYTHON = sys.executable
REPO_ROOT = Path(__file__).resolve().parent
SERVER_SCRIPT = REPO_ROOT / "run_mcp_server.py"

# Minimal MCP initialize request (JSON-RPC 2.0)
INIT_REQUEST = json.dumps({
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "test-client", "version": "0.1"}
    }
}) + "\n"


async def test():
    print(f"Python:        {PYTHON}")
    print(f"Server script: {SERVER_SCRIPT}")
    print(f"Script exists: {SERVER_SCRIPT.exists()}")
    print(f"CWD:           {REPO_ROOT}")

    proc = await asyncio.create_subprocess_exec(
        PYTHON,
        str(SERVER_SCRIPT),
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=str(REPO_ROOT),
    )
    print(f"Server PID:    {proc.pid} -- started")

    try:
        # Send initialize
        proc.stdin.write(INIT_REQUEST.encode())
        await proc.stdin.drain()
        print(f"Sent:          {INIT_REQUEST.strip()}")

        # Wait for first response line
        try:
            raw = await asyncio.wait_for(proc.stdout.readline(), timeout=15.0)
            line = raw.decode("utf-8", errors="replace").strip()
            print(f"Response raw:  {line}")

            if not line:
                print("RESULT: FAIL -- no output from server")
                return

            try:
                resp = json.loads(line)
                if "result" in resp:
                    result = resp["result"]
                    si = result.get("serverInfo", {})
                    caps = result.get("capabilities", {})
                    print(f"RESULT: PASS")
                    print(f"  protocolVersion: {result.get('protocolVersion')}")
                    print(f"  serverInfo.name: {si.get('name')}")
                    print(f"  serverInfo.version: {si.get('version')}")
                    print(f"  capabilities keys: {list(caps.keys())}")
                elif "error" in resp:
                    print(f"RESULT: JSON-RPC error -- {resp['error']}")
                else:
                    print(f"RESULT: unexpected response structure")
            except json.JSONDecodeError as e:
                print(f"RESULT: FAIL -- response is not valid JSON: {e}")
                print(f"  raw was: {repr(line)}")

        except asyncio.TimeoutError:
            print("RESULT: FAIL -- no response within 15s")

    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        try:
            proc.kill()
        except Exception:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=3.0)
        except Exception:
            pass

        # Drain stderr for diagnostics
        try:
            err = await asyncio.wait_for(proc.stderr.read(8192), timeout=2.0)
            if err:
                print(f"\n-- Server stderr --\n{err.decode('utf-8', errors='replace')}")
        except Exception:
            pass

        print("Server process terminated.")


asyncio.run(test())
