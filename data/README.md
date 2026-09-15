# MissionGuard AI — Synthetic Fleet Dataset

`data/assets.csv` is the synthetic fleet dataset used by the MissionGuard risk engine.

---

## Overview

| Property | Value |
|---|---|
| File | `data/assets.csv` |
| Rows | 100 synthetic fleet assets |
| Seed | 42 (fixed — results are fully reproducible) |
| Source | Programmatically generated — **not real military or operational telemetry** |

> **Disclaimer:** All data in this file is entirely synthetic and fictional. It is a
> stand-in for the kind of sensor and maintenance data that might exist in a real fleet
> management system. Do not use for any operational or safety-critical purpose.

---

## How to Generate

```powershell
python -m src.data.generate_dataset
```

Safe to re-run. The fixed seed (42) ensures the same output every time.

---

## Column Reference

| Column | Type | Description |
|---|---|---|
| `asset_id` | string | Stable identifier (`A-001` … `A-100`) |
| `asset_type` | string | Asset category (UAV, Ground Vehicle, Generator, Communications Relay, Rotary Wing) |
| `engine_temperature` | float | Operating temperature proxy |
| `vibration_level` | float | Vibration intensity proxy |
| `operating_hours` | float | Cumulative usage hours |
| `component_age` | float | Component age in months |
| `hours_since_service` | float | Usage hours since last service |
| `maintenance_age` | float | Months since last major maintenance |
| `fuel_consumption` | float | Fuel-use proxy |
| `service_count` | int | Lifetime service events |
| `last_service_date` | date | Date of most recent service (ISO format) |
| `failure_label` | int | Noisy synthetic training target — **not observed failure data** |

---

## Data Generation Method

`src/data/generate_dataset.py` generates correlated synthetic data:

- Asset types have different baseline parameter distributions.
- Each row is drawn from a healthy / warning / high-stress mixture.
- Sensor drivers are correlated (heat and vibration raise fuel use; overdue service tracks utilization).
- `failure_label` is a Bernoulli draw from a sigmoid of a latent stress score — it is a synthetic training label, not an observed failure rate.

---

## Usage in the Risk Engine

The dataset is consumed by:

1. `src/data/data_loader.py` — loads and validates required columns
2. `src/data/preprocessing.py` — imputes missing values and parses dates
3. `src/data/feature_engineering.py` — derives additional features from the raw columns
4. `src/models/risk_model.py` — trains the hybrid risk model on `failure_label`
