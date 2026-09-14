# Solution Overview

## What We Built

A local Python risk engine that reads a synthetic asset CSV, scores each asset, and returns health, failure probability, risk level, readiness, top factors, and a recommended action.

IBM Bob and any UI are **not** part of this phase. They should wrap `src.services.risk_engine`.

## How It Works

1. Generate or load `data/assets.csv` (fixed seed).
2. Validate columns and impute missing values.
3. Engineer maintenance-gap and stress features.
4. Fit logistic regression on a noisy synthetic failure label; blend with a domain median/IQR score.
5. Map probability + health onto `LOW`/`MEDIUM`/`HIGH` and `READY`/`WARNING`/`NOT_READY`.
6. Convert positive model contributions into short factor phrases.

## Architecture Diagram

> See [`architecture.md`](architecture.md).

```
CSV → Loader → Preprocess → Features → Hybrid model → Scores + explanations → Python API
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Synthetic correlated data, not uniform random | Prototype looks like a fleet; model can learn structure |
| Logistic regression + domain blend | Explainable MVP; avoids a brittle single rule |
| Thresholds in `config.py` | Readiness rules stay tunable |
| Python functions, not FastAPI | Agent 2 can add HTTP/MCP without rewriting scoring |
| Isolated `.venv` | Reproducible installs; no global pip |

## IBM Technologies Used

None in this phase. The scoring API is the intended attachment point for IBM Bob / watsonx later.
