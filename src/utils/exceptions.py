"""Custom exceptions for the MissionGuard risk engine."""


class MissionGuardError(Exception):
    """Base error for this package."""


class DatasetError(MissionGuardError):
    """Raised when the synthetic dataset is missing, empty, or invalid."""


class AssetNotFoundError(MissionGuardError):
    """Raised when an asset_id is not present in the loaded dataset."""

    def __init__(self, asset_id: str) -> None:
        self.asset_id = asset_id
        super().__init__(f"Unknown asset_id: {asset_id!r}")
