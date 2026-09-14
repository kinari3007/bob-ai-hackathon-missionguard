"""
Fix the pyarrow DLL block, pin httpx correctly, then run the full test suite.
Writes test_results.json.
"""
import json, subprocess, sys, os

root = r"C:\IBM Hackathone\bob-ai-hackathon-missionguard"
py   = sys.executable
out  = {"steps": {}, "pytest": {}, "status": "unknown"}

def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=root, **kw)

# ── Step 1: uninstall pyarrow (its DLL is policy-blocked) ─────────────────────
proc = run([py, "-m", "pip", "uninstall", "pyarrow", "-y", "--quiet"])
out["steps"]["uninstall_pyarrow"] = "ok" if proc.returncode == 0 else proc.stderr[:200]

# ── Step 2: verify pandas now imports cleanly ──────────────────────────────────
proc = run([py, "-c", "import pandas; print(pandas.__version__)"])
out["steps"]["pandas_import"] = proc.stdout.strip() or f"FAIL: {proc.stderr.strip()[:200]}"

# ── Step 3: install fastapi + uvicorn ──────────────────────────────────────────
for pkg in ["fastapi==0.115.12", "uvicorn[standard]==0.34.2"]:
    proc = run([py, "-m", "pip", "install", pkg, "--quiet"])
    out["steps"][f"install_{pkg}"] = "ok" if proc.returncode == 0 else proc.stderr[:200]

# ── Step 4: install httpx (latest available = 0.28.1) ─────────────────────────
proc = run([py, "-m", "pip", "install", "httpx==0.28.1", "--quiet"])
out["steps"]["install_httpx"] = "ok" if proc.returncode == 0 else proc.stderr[:200]

# ── Step 5: run full pytest suite ─────────────────────────────────────────────
proc = run([py, "-m", "pytest", "--tb=short", "-q"])
out["pytest"]["returncode"] = proc.returncode
out["pytest"]["stdout"]     = proc.stdout[-6000:] if proc.stdout else ""
out["pytest"]["stderr"]     = proc.stderr[-2000:] if proc.stderr else ""
out["status"] = "PASSED" if proc.returncode == 0 else "FAILED"

with open(root + r"\test_results.json", "w") as f:
    json.dump(out, f, indent=2)
