"""Check which packages are installed — include submodule check."""
import json, importlib, subprocess, sys

pkgs = {}
# Try direct import approach
for pkg, mod in [("fastapi","fastapi"), ("uvicorn","uvicorn"), ("httpx","httpx"), ("streamlit","streamlit"), ("requests","requests")]:
    try:
        m = importlib.import_module(mod)
        pkgs[pkg] = getattr(m, "__version__", "installed")
    except ImportError:
        pkgs[pkg] = "MISSING"

# Also get pip list
result = subprocess.run([sys.executable, "-m", "pip", "list", "--format=json"], capture_output=True, text=True)
if result.returncode == 0:
    pip_list = {p["name"].lower(): p["version"] for p in json.loads(result.stdout)}
    pkgs["_pip_fastapi"] = pip_list.get("fastapi", "not in pip list")
    pkgs["_pip_uvicorn"] = pip_list.get("uvicorn", "not in pip list")
    pkgs["_pip_httpx"] = pip_list.get("httpx", "not in pip list")

with open("deps_check2.json", "w") as f:
    json.dump(pkgs, f, indent=2)
