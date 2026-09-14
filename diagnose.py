"""Diagnose environment issues and write findings to diagnose_out.json."""
import json, subprocess, sys, os

out = {}

# 1. Check pandas import with PYARROW_IGNORE_TIMEZONE workaround
os.environ["PANDAS_FUTURE_INFER_STRING"] = "0"
try:
    import pandas as pd
    out["pandas"] = pd.__version__
except Exception as e:
    out["pandas"] = f"FAILED: {e}"

# 2. Check numpy
try:
    import numpy as np
    out["numpy"] = np.__version__
except Exception as e:
    out["numpy"] = f"FAILED: {e}"

# 3. Find compatible httpx version
proc = subprocess.run(
    [sys.executable, "-m", "pip", "index", "versions", "httpx"],
    capture_output=True, text=True
)
out["httpx_versions_raw"] = proc.stdout[:500] if proc.stdout else proc.stderr[:500]

# 4. Try installing httpx without version pin
proc2 = subprocess.run(
    [sys.executable, "-m", "pip", "install", "httpx", "--quiet", "--dry-run"],
    capture_output=True, text=True
)
out["httpx_dryrun"] = proc2.stdout[:300] if proc2.stdout else proc2.stderr[:300]

# 5. Check if pyarrow is truly the blocker or if it's avoidable
try:
    import pyarrow
    out["pyarrow"] = pyarrow.__version__
except Exception as e:
    out["pyarrow"] = f"BLOCKED: {e}"

# 6. Check pandas WITHOUT pyarrow (set env var)
os.environ["PANDAS_FUTURE_INFER_STRING"] = "0"
proc3 = subprocess.run(
    [sys.executable, "-c",
     "import os; os.environ['MODIN_ENGINE']='python'; "
     "import pandas; print(pandas.__version__)"],
    capture_output=True, text=True
)
out["pandas_subprocess"] = proc3.stdout.strip() or proc3.stderr.strip()[:300]

with open("diagnose_out.json", "w") as f:
    json.dump(out, f, indent=2)
