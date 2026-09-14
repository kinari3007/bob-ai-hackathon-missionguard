# Setup Guide

> Risk-engine phase. No IBM Cloud keys, containers, or frontend are required yet.

## Prerequisites

- [ ] Python 3.11+ (developed with Python 3.14 on Windows)
- [ ] PowerShell (or Command Prompt) with permission to create `.venv` in the repo

## Environment Variables

This phase does not require secrets. Optional overrides can be copied from `src/.env.example` later when IBM services are wired. For local scoring you can skip `.env`.

## Installation

```powershell
# 1. Clone the repository
git clone <your-fork-url>
cd bob-ai-hackathon-missionguard

# 2. Create and activate a virtual environment (do not install globally)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip

# 3. Install this phase's dependencies
python -m pip install -r requirements.txt
```

Command Prompt activation, if you are not using PowerShell:

```bat
.venv\Scripts\activate
```

## Running the Application

```powershell
# Generate the synthetic fleet CSV (safe to re-run; seed is fixed)
python -m src.data.generate_dataset

# Score the fleet and print READY / WARNING / NOT_READY counts
python -m src
```

You should see total asset count, readiness counts, HIGH-risk count, average health score, and one example high-risk record.

## Running Tests

```powershell
python -m pytest
```

Always run pytest with the virtual environment interpreter:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

## Quick Demo

```powershell
python -m src
```

Then, in a Python REPL with the venv active:

```python
from src.services.risk_engine import get_failure_risk, get_asset_status
print(get_asset_status("A-001"))
print(get_failure_risk("A-001"))
```

## Troubleshooting

| Issue | Solution |
|---|---|
| `ModuleNotFoundError: pandas` | Activate `.venv` and `pip install -r requirements.txt` |
| `pytest` not found | Use `.\.venv\Scripts\python.exe -m pytest` |
| Dataset missing | `python -m src.data.generate_dataset` |
| Execution policy blocks `Activate.ps1` | Use `.\.venv\Scripts\python.exe` directly instead of activating |
| Scores look different after editing thresholds | Thresholds live in `src/utils/config.py`; re-run `python -m src` |
