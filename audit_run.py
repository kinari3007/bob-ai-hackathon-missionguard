"""Audit runner: pytest -v, ML smoke, API import, dashboard import. Writes audit_results.json."""
import json, subprocess, sys, os

root = r"C:\IBM Hackathone\bob-ai-hackathon-missionguard"
py = sys.executable
out = {}

# 1. pytest -v
proc = subprocess.run([py, "-m", "pytest", "-v", "--tb=short", "--no-header"],
                      capture_output=True, text=True, cwd=root)
out["pytest_returncode"] = proc.returncode
# Extract summary line
lines = (proc.stdout or "").splitlines()
summary = next((l for l in reversed(lines) if "passed" in l or "failed" in l or "error" in l), "no summary")
out["pytest_summary"] = summary
# Collect test names + status
test_lines = [l for l in lines if "PASSED" in l or "FAILED" in l or "ERROR" in l]
out["test_detail"] = test_lines
out["pytest_warnings"] = sum(1 for l in lines if "UserWarning" in l or "DeprecationWarning" in l)

# 2. ML engine smoke
proc2 = subprocess.run([py, "-c",
    "import sys; sys.path.insert(0,r'C:\\IBM Hackathone\\bob-ai-hackathon-missionguard'); "
    "from src import get_all_assets,get_asset_status,get_failure_risk,get_maintenance_priority; "
    "a=get_all_assets(); "
    "s=get_asset_status(a[0]['asset_id']); "
    "r=get_failure_risk(a[0]['asset_id']); "
    "p=get_maintenance_priority(a[0]['asset_id']); "
    "print(len(a), s['readiness_status'], r['risk_level'], p['priority_rank'])"],
    capture_output=True, text=True, cwd=root)
out["ml_smoke"] = proc2.stdout.strip() or proc2.stderr.strip()[:300]
out["ml_smoke_ok"] = proc2.returncode == 0

# 3. API import check
proc3 = subprocess.run([py, "-c",
    "import sys; sys.path.insert(0,r'C:\\IBM Hackathone\\bob-ai-hackathon-missionguard'); "
    "from src.api.main import app; "
    "print('FastAPI app:', app.title)"],
    capture_output=True, text=True, cwd=root)
out["api_import"] = proc3.stdout.strip() or proc3.stderr.strip()[:300]
out["api_import_ok"] = proc3.returncode == 0

# 4. Dashboard api_client import check
proc4 = subprocess.run([py, "-c",
    "import sys; sys.path.insert(0,r'C:\\IBM Hackathone\\bob-ai-hackathon-missionguard'); "
    "from src.dashboard.api_client import MissionGuardClient,BackendUnavailableError,AssetNotFoundError; "
    "c=MissionGuardClient(); print('client base_url:', c.base_url)"],
    capture_output=True, text=True, cwd=root)
out["dashboard_client_import"] = proc4.stdout.strip() or proc4.stderr.strip()[:300]
out["dashboard_client_ok"] = proc4.returncode == 0

# 5. Dataset check
proc5 = subprocess.run([py, "-c",
    "import sys; sys.path.insert(0,r'C:\\IBM Hackathone\\bob-ai-hackathon-missionguard'); "
    "import pandas as pd; "
    "df=pd.read_csv(r'C:\\IBM Hackathone\\bob-ai-hackathon-missionguard\\data\\assets.csv'); "
    "print(f'{len(df)} rows, cols: {list(df.columns)[:5]}')"],
    capture_output=True, text=True, cwd=root)
out["dataset_check"] = proc5.stdout.strip() or proc5.stderr.strip()[:300]
out["dataset_ok"] = proc5.returncode == 0

# 6. Check app.py for syntax
proc6 = subprocess.run([py, "-c",
    r"src=open(r'C:\IBM Hackathone\bob-ai-hackathon-missionguard\src\dashboard\app.py').read(); "
    r"compile(src,'app.py','exec'); print('app.py syntax OK')"],
    capture_output=True, text=True, cwd=root)
out["dashboard_app_syntax"] = proc6.stdout.strip() or proc6.stderr.strip()[:300]
out["dashboard_app_ok"] = proc6.returncode == 0

with open(os.path.join(root, "audit_results.json"), "w") as f:
    json.dump(out, f, indent=2)
print("audit_results.json written")
