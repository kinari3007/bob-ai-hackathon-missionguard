"""Type coercion, missing-value handling, and light cleaning."""

from __future__ import annotations

import pandas as pd

from src.utils.config import CATEGORICAL_COLUMNS, NUMERIC_COLUMNS, REQUIRED_COLUMNS
from src.utils.exceptions import DatasetError


def preprocess_assets(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned copy with imputed numeric/categorical fields.

    Missing numeric values are filled with column medians. Missing asset types
    are filled with the mode (or ``Unknown`` if the column is entirely empty).
    Dates that cannot be parsed are replaced with the median valid date.
    """
    if frame.empty:
        raise DatasetError("Cannot preprocess an empty dataset.")

    cleaned = frame.copy()

    for column in REQUIRED_COLUMNS:
        if column not in cleaned.columns:
            raise DatasetError(f"Missing required column during preprocess: {column}")

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")
        median = cleaned[column].median()
        if pd.isna(median):
            median = 0.0
        cleaned[column] = cleaned[column].fillna(median)

    cleaned["service_count"] = cleaned["service_count"].clip(lower=0).round().astype(int)

    for column in CATEGORICAL_COLUMNS:
        cleaned[column] = cleaned[column].astype("string").replace({pd.NA: None})
        mode = cleaned[column].mode(dropna=True)
        fill_value = str(mode.iloc[0]) if not mode.empty else "Unknown"
        cleaned[column] = cleaned[column].fillna(fill_value)

    parsed_dates = pd.to_datetime(cleaned["last_service_date"], errors="coerce")
    if parsed_dates.notna().any():
        parsed_dates = parsed_dates.fillna(parsed_dates.median())
    else:
        parsed_dates = pd.Series(pd.Timestamp("2026-09-01"), index=cleaned.index)
    cleaned["last_service_date"] = parsed_dates.dt.strftime("%Y-%m-%d")

    cleaned["asset_id"] = cleaned["asset_id"].astype(str)
    return cleaned.reset_index(drop=True)
