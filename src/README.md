# Source Code

Phase 1 lives entirely under `src/` as a Python package importable from the repo root (`pytest.ini` sets `pythonpath = .`).

```
src/
  __main__.py              ← python -m src  (fleet summary)
  data/
    generate_dataset.py    ← synthetic CSV writer
    data_loader.py
    preprocessing.py
    feature_engineering.py
  models/
    risk_model.py          ← logistic + domain blend
  services/
    risk_engine.py         ← get_all_assets / get_asset_status / get_failure_risk
    readiness.py
    explainability.py
  utils/
    config.py              ← paths, seed, thresholds
    exceptions.py
```

See `docs/risk-engine.md` for dataset fields, scoring, and how to run tests.

Do not put IBM Bob or MCP code in this tree until that phase; keep `.env` out of git.
