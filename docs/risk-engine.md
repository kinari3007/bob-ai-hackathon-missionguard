# MissionGuard Risk Engine (Phase 1)

Developer notes for the synthetic-data risk core. This phase does **not** include IBM Bob, MCP, a dashboard, or any real operational feed.

Prototype disclaimer: scores are computed from **fictional** fleet data. They are not military-validated.

## Dataset structure

File: `data/assets.csv` (~100 rows). Required columns:

| Column | Meaning (synthetic) |
|---|---|
| `asset_id` | Stable id (`A-001` …) |
| `asset_type` | UAV, Ground Vehicle, Generator, Communications Relay, Rotary Wing |
| `engine_temperature` | Operating temperature proxy |
| `vibration_level` | Vibration proxy |
| `operating_hours` | Cumulative usage |
| `component_age` | Component age in months |
| `hours_since_service` | Usage since last service |
| `maintenance_age` | Months since major maintenance |
| `fuel_consumption` | Fuel-use proxy |
| `service_count` | Lifetime service events |
| `last_service_date` | ISO date |
| `failure_label` | Noisy synthetic training target (not a real failure log) |

## Synthetic-data generation

`src/data/generate_dataset.py` uses a fixed seed (`42`).

- Asset types have different baseline envelopes.
- Each row is drawn from a **healthy / warning / high-stress** mixture.
- Drivers are correlated (heat and vibration raise fuel use; overdue service tracks utilization) with enough noise that labels are **not** a single if-then rule.
- `failure_label` is a Bernoulli draw from a sigmoid of a latent stress score.

Regenerate:

```powershell
.\.venv\Scripts\python.exe -m src.data.generate_dataset
```

## Feature engineering

`src/data/feature_engineering.py` adds:

- `days_since_service`
- `expected_service_gap` (hours since service vs hours per historical service)
- `temp_vibration_stress`
- `utilization_intensity`
- `fuel_per_hour`

Missing values are imputed in `src/data/preprocessing.py` (numeric median, categorical mode, invalid dates → median date).

## Risk model

Hybrid, chosen for explainability:

1. **Logistic regression** on standardized engineered features, trained on the synthetic `failure_label`.
2. **Domain score** — how far key drivers sit above fleet medians (IQR scaling).
3. Blend: `0.70 * p_ml + 0.30 * p_domain` (weight in `ThresholdConfig.ml_blend_weight`).

Thresholds live in `src/utils/config.py` (`ThresholdConfig`). Do not scatter cut-offs in call sites.

## Risk score

For each asset:

- `failure_probability` — blended probability in `(0.01, 0.99)`
- `health_score` — `100 * (1 - failure_probability)`
- `risk_level` — `LOW` / `MEDIUM` / `HIGH` from probability and health cut-offs

## Readiness classification

Derived from risk/health, never from `asset_id`:

| Status | Rule (defaults) |
|---|---|
| `NOT_READY` | `risk_level == HIGH` or `health_score < 40` |
| `WARNING` | `risk_level == MEDIUM` or `health_score < 65` |
| `READY` | otherwise |

## Explainability

Logistic coefficients × standardized feature values yield per-asset contributions. The largest **positive** contributions are mapped to phrases such as “High vibration level”. Output: up to three `top_risk_factors` plus a `recommended_action`.

## Python API

Import from the repo root:

```python
from src.services.risk_engine import (
    get_all_assets,
    get_asset_status,
    get_failure_risk,
    get_maintenance_priority,
)

get_all_assets()                      # list of all 100 assets
get_asset_status("A-017")            # readiness status + evidence
get_failure_risk("A-017")            # failure probability + risk factors
get_maintenance_priority("A-017")    # priority score + rank
```

Unknown IDs raise `src.utils.exceptions.AssetNotFoundError`.

Or construct `RiskEngine` directly with an explicit `AppConfig` in tests and services.

## How to run the risk engine

```powershell
pip install -r requirements.txt
python -m src.data.generate_dataset
python -m src
```

## How to run tests

```powershell
python -m pytest -v
```

Expected: 71 tests passing. See `docs/setup-guide.md` for the full test breakdown.
