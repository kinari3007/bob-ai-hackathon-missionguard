"""Install missing deps then run the full pytest suite; write results to JSON."""
import json
import subprocess
import sys

root = r"C:\IBM Hackathone\bob-ai-hackathon-missionguard"
py   = sys.executable   # venv python

results = {"install": {}, "pytest": {}, "status": "unknown"}

# ── 1. Install outstanding packages ──────────────────────────────────────────
pkgs = [
    "fastapi==0.115.12",
    "uvicorn[standard]==0.34.2",
    "httpx==0.28.2",
    "requests==2.32.3",
]

for pkg in pkgs:
    proc = subprocess.run(
        [py, "-m", "pip", "install", pkg, "--quiet"],
        capture_output=True, text=True, cwd=root,
    )
    results["install"][pkg] = "ok" if proc.returncode == 0 else proc.stderr.strip()[:200]

# ── 2. Run pytest ──────────────────────────────────────────────────────────────
proc = subprocess.run(
    [py, "-m", "pytest", "--tb=short", "-q"],
    capture_output=True, text=True, cwd=root,
)
results["pytest"]["returncode"] = proc.returncode
results["pytest"]["stdout"]     = proc.stdout[-4000:] if proc.stdout else ""
results["pytest"]["stderr"]     = proc.stderr[-2000:] if proc.stderr else ""
results["status"] = "PASSED" if proc.returncode == 0 else "FAILED"

with open(root + r"\test_results.json", "w") as f:
    json.dump(results, f, indent=2)
