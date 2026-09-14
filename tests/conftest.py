"""Shared fixtures. Tests use a temp copy of the synthetic fleet, never CWD guesses."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.generate_dataset import generate_assets_dataframe
from src.services.risk_engine import RiskEngine
from src.utils.config import AppConfig


@pytest.fixture
def assets_frame() -> pd.DataFrame:
    return generate_assets_dataframe(n_assets=100, seed=42)


@pytest.fixture
def assets_csv(tmp_path: Path, assets_frame: pd.DataFrame) -> Path:
    path = tmp_path / "assets.csv"
    assets_frame.to_csv(path, index=False)
    return path


@pytest.fixture
def engine(tmp_path: Path, assets_csv: Path) -> RiskEngine:
    config = AppConfig(
        data_path=assets_csv,
        model_path=tmp_path / "risk_model.joblib",
    )
    return RiskEngine(config=config, data_path=assets_csv).load(persist_model=False)
