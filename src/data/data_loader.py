"""Load and validate the synthetic asset CSV."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.generate_dataset import save_dataset
from src.utils.config import DEFAULT_CONFIG, REQUIRED_COLUMNS, AppConfig
from src.utils.exceptions import DatasetError


def load_assets(
    path: Path | None = None,
    *,
    generate_if_missing: bool = True,
    config: AppConfig | None = None,
) -> pd.DataFrame:
    """Load ``data/assets.csv``, optionally generating it if absent."""
    config = config or DEFAULT_CONFIG
    csv_path = Path(path) if path is not None else config.data_path

    if not csv_path.exists():
        if not generate_if_missing:
            raise DatasetError(f"Dataset not found: {csv_path}")
        save_dataset(csv_path, config=config)

    try:
        frame = pd.read_csv(csv_path)
    except OSError as exc:
        raise DatasetError(f"Unable to read dataset: {csv_path}") from exc

    if frame.empty:
        raise DatasetError("Dataset is empty.")

    validate_columns(frame)
    return frame


def validate_columns(frame: pd.DataFrame) -> None:
    """Ensure required schema columns are present."""
    missing = [col for col in REQUIRED_COLUMNS if col not in frame.columns]
    if missing:
        raise DatasetError(
            "Dataset is missing required columns: " + ", ".join(missing)
        )


def required_columns_present(frame: pd.DataFrame) -> bool:
    return all(col in frame.columns for col in REQUIRED_COLUMNS)
