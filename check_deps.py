"""Check which packages are installed."""
import json, importlib

pkgs = {
    "fastapi": None,
    "uvicorn": None,
    "httpx": None,
    "streamlit": None,
    "requests": None,
}
for pkg in list(pkgs):
    try:
        m = importlib.import_module(pkg)
        pkgs[pkg] = getattr(m, "__version__", "installed")
    except ImportError:
        pkgs[pkg] = "MISSING"

with open("deps_check.json", "w") as f:
    json.dump(pkgs, f, indent=2)
