"""Dataset loading, schema, and missing-value tests."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.data_loader import load_assets, required_columns_present, validate_columns
from src.data.generate_dataset import generate_assets_dataframe
from src.data.preprocessing import preprocess_assets
from src.utils.config import NUMERIC_COLUMNS, REQUIRED_COLUMNS
from src.utils.exceptions import DatasetError


def test_dataset_generation_is_deterministic() -> None:
    first = generate_assets_dataframe(n_assets=100, seed=42)
    second = generate_assets_dataframe(n_assets=100, seed=42)
    pd.testing.assert_frame_equal(first, second)


def test_generated_dataset_has_required_columns(assets_frame: pd.DataFrame) -> None:
    for column in REQUIRED_COLUMNS:
        assert column in assets_frame.columns
    assert len(assets_frame) == 100
    assert assets_frame["asset_id"].is_unique


def test_load_assets_from_csv(assets_csv: Path) -> None:
    loaded = load_assets(assets_csv, generate_if_missing=False)
    assert required_columns_present(loaded)
    assert len(loaded) == 100


def test_validate_columns_rejects_missing_fields(assets_frame: pd.DataFrame) -> None:
    broken = assets_frame.drop(columns=["vibration_level"])
    with pytest.raises(DatasetError, match="vibration_level"):
        validate_columns(broken)


def test_missing_numeric_values_are_imputed(assets_frame: pd.DataFrame) -> None:
    dirty = assets_frame.copy()
    dirty.loc[0, "engine_temperature"] = None
    dirty.loc[3, "vibration_level"] = None
    dirty.loc[7, "hours_since_service"] = None
    dirty.loc[2, "asset_type"] = None
    dirty.loc[4, "last_service_date"] = "not-a-date"

    cleaned = preprocess_assets(dirty)
    for column in NUMERIC_COLUMNS:
        assert cleaned[column].isna().sum() == 0
    assert cleaned["asset_type"].isna().sum() == 0
    assert cleaned["last_service_date"].isna().sum() == 0
    parsed = pd.to_datetime(cleaned["last_service_date"], errors="coerce")
    assert parsed.isna().sum() == 0
