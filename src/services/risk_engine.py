"""Risk scoring orchestration and the Agent-2 Python API surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.data.data_loader import load_assets
from src.data.feature_engineering import engineer_features
from src.data.preprocessing import preprocess_assets
from src.models.risk_model import (
    FittedRiskModel,
    blended_failure_probability,
    fit_risk_model,
)
from src.services.explainability import explain_asset
from src.services.readiness import classify_readiness, classify_risk_level, recommend_action
from src.utils.config import DEFAULT_CONFIG, AppConfig
from src.utils.exceptions import AssetNotFoundError


class RiskEngine:
    """Load synthetic assets, fit the hybrid model, and score the fleet."""

    def __init__(self, config: AppConfig | None = None, data_path: Path | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.data_path = Path(data_path) if data_path is not None else self.config.data_path
        self._raw: pd.DataFrame | None = None
        self._featured: pd.DataFrame | None = None
        self._scored: pd.DataFrame | None = None
        self._model: FittedRiskModel | None = None
        self._records: dict[str, dict[str, Any]] = {}

    def load(self, *, persist_model: bool = True) -> "RiskEngine":
        raw = load_assets(self.data_path, config=self.config)
        cleaned = preprocess_assets(raw)
        featured = engineer_features(cleaned)
        model = self._load_or_fit(featured, persist_model=persist_model)
        scored = self._score_frame(featured, model)
        self._raw = raw
        self._featured = featured
        self._model = model
        self._scored = scored
        self._records = {row["asset_id"]: row for row in scored.to_dict(orient="records")}
        return self

    def _load_or_fit(self, featured: pd.DataFrame, persist_model: bool) -> FittedRiskModel:
        # Always refit from the current CSV so scores stay aligned with the data.
        # Persist a snapshot so later agents can inspect coefficients if needed.
        model = fit_risk_model(featured, random_seed=self.config.random_seed)
        if persist_model:
            model_path = self.config.model_path
            model_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(model, model_path)
        return model

    def _score_frame(self, featured: pd.DataFrame, model: FittedRiskModel) -> pd.DataFrame:
        thresholds = self.config.thresholds
        probabilities = blended_failure_probability(featured, model, thresholds)
        scored = featured.copy()
        scored["failure_probability"] = probabilities
        scored["health_score"] = (100.0 * (1.0 - scored["failure_probability"])).round(1)

        records: list[dict[str, Any]] = []
        for idx, row in scored.iterrows():
            health = float(row["health_score"])
            prob = float(row["failure_probability"])
            risk_level = classify_risk_level(prob, health, thresholds)
            factors = explain_asset(row, model, thresholds)
            readiness = classify_readiness(risk_level, health, thresholds)
            action = recommend_action(readiness, factors)
            records.append(
                {
                    "asset_id": str(row["asset_id"]),
                    "asset_type": str(row["asset_type"]),
                    "health_score": health,
                    "failure_probability": round(prob, 4),
                    "risk_level": risk_level,
                    "readiness_status": readiness,
                    "top_risk_factors": factors,
                    "recommended_action": action,
                    "engine_temperature": float(row["engine_temperature"]),
                    "vibration_level": float(row["vibration_level"]),
                    "operating_hours": float(row["operating_hours"]),
                    "hours_since_service": float(row["hours_since_service"]),
                }
            )
            _ = idx
        return pd.DataFrame(records)

    def _require_loaded(self) -> None:
        if not self._records:
            self.load()

    def get_all_assets(self) -> list[dict[str, Any]]:
        """Return scored records for every asset in the dataset."""
        self._require_loaded()
        return [self._public_record(item) for item in self._records.values()]

    def get_asset_status(self, asset_id: str) -> dict[str, Any]:
        """Return readiness classification and supporting evidence for one asset."""
        record = self._get_record(asset_id)
        return {
            "asset_id": record["asset_id"],
            "asset_type": record["asset_type"],
            "readiness_status": record["readiness_status"],
            "health_score": record["health_score"],
            "risk_level": record["risk_level"],
            "top_risk_factors": list(record["top_risk_factors"]),
            "recommended_action": record["recommended_action"],
        }

    def get_failure_risk(self, asset_id: str) -> dict[str, Any]:
        """Return failure probability, risk level, and explainable drivers."""
        record = self._get_record(asset_id)
        return {
            "asset_id": record["asset_id"],
            "health_score": record["health_score"],
            "failure_probability": record["failure_probability"],
            "risk_level": record["risk_level"],
            "top_risk_factors": list(record["top_risk_factors"]),
            "recommended_action": record["recommended_action"],
        }

    def get_maintenance_priority(self, asset_id: str) -> dict[str, Any]:
        """Return maintenance priority score and ranking information."""
        record = self._get_record(asset_id)
        priority_score = self._calculate_priority_score(record)
        
        # Calculate ranking among all assets
        all_assets = self.get_all_assets()
        priorities = [
            (a["asset_id"], self._calculate_priority_score(self._records[a["asset_id"]]))
            for a in all_assets
        ]
        priorities.sort(key=lambda x: x[1], reverse=True)
        rank = next(i + 1 for i, (aid, _) in enumerate(priorities) if aid == asset_id)
        
        return {
            "asset_id": record["asset_id"],
            "asset_type": record["asset_type"],
            "priority_score": round(priority_score, 2),
            "priority_rank": rank,
            "total_assets": len(all_assets),
            "readiness_status": record["readiness_status"],
            "risk_level": record["risk_level"],
            "health_score": record["health_score"],
            "priority_reasons": self._priority_reasons(record),
            "recommended_action": record["recommended_action"],
        }

    @staticmethod
    def _calculate_priority_score(record: dict[str, Any]) -> float:
        """Calculate maintenance priority score (0-100, higher = more urgent)."""
        # Base score from failure probability (0-50 points)
        prob_score = float(record["failure_probability"]) * 50.0
        
        # Readiness contribution (0-30 points)
        readiness_map = {"NOT_READY": 30.0, "WARNING": 15.0, "READY": 0.0}
        readiness_score = readiness_map.get(record["readiness_status"], 0.0)
        
        # Risk level contribution (0-20 points)
        risk_map = {"HIGH": 20.0, "MEDIUM": 10.0, "LOW": 0.0}
        risk_score = risk_map.get(record["risk_level"], 0.0)
        
        # Health penalty (0-10 points for low health)
        health = float(record["health_score"])
        health_penalty = max(0.0, (60.0 - health) / 6.0) if health < 60.0 else 0.0
        
        total = prob_score + readiness_score + risk_score + health_penalty
        return min(100.0, total)

    @staticmethod
    def _priority_reasons(record: dict[str, Any]) -> list[str]:
        """Generate human-readable reasons for priority ranking."""
        reasons = []
        
        if record["readiness_status"] == "NOT_READY":
            reasons.append("Asset not mission-ready")
        elif record["readiness_status"] == "WARNING":
            reasons.append("Asset status warning")
        
        if record["risk_level"] == "HIGH":
            reasons.append("High failure risk")
        elif record["risk_level"] == "MEDIUM":
            reasons.append("Moderate failure risk")
        
        health = float(record["health_score"])
        if health < 40.0:
            reasons.append("Critical health score")
        elif health < 65.0:
            reasons.append("Low health score")
        
        # Add top risk factor if available
        factors = record.get("top_risk_factors", [])
        if factors:
            reasons.append(f"Primary concern: {factors[0]}")
        
        return reasons if reasons else ["Routine maintenance"]

    def summary(self) -> dict[str, Any]:
        """Fleet-level counts used by the CLI validation printout."""
        assets = self.get_all_assets()
        readiness_counts = {"READY": 0, "WARNING": 0, "NOT_READY": 0}
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        health_sum = 0.0
        for asset in assets:
            readiness_counts[str(asset["readiness_status"])] += 1
            risk_counts[str(asset["risk_level"])] += 1
            health_sum += float(asset["health_score"])
        n = len(assets)
        return {
            "total_assets": n,
            "READY": readiness_counts["READY"],
            "WARNING": readiness_counts["WARNING"],
            "NOT_READY": readiness_counts["NOT_READY"],
            "HIGH": risk_counts["HIGH"],
            "MEDIUM": risk_counts["MEDIUM"],
            "LOW": risk_counts["LOW"],
            "average_health_score": round(health_sum / n, 2) if n else 0.0,
        }

    def _get_record(self, asset_id: str) -> dict[str, Any]:
        self._require_loaded()
        record = self._records.get(str(asset_id))
        if record is None:
            raise AssetNotFoundError(str(asset_id))
        return record

    @staticmethod
    def _public_record(record: dict[str, Any]) -> dict[str, Any]:
        return {
            "asset_id": record["asset_id"],
            "asset_type": record["asset_type"],
            "health_score": record["health_score"],
            "failure_probability": record["failure_probability"],
            "risk_level": record["risk_level"],
            "readiness_status": record["readiness_status"],
            "top_risk_factors": list(record["top_risk_factors"]),
            "recommended_action": record["recommended_action"],
        }


_ENGINE: RiskEngine | None = None


def get_engine(force_reload: bool = False) -> RiskEngine:
    """Lazy singleton so Agent 2 can call module-level API functions."""
    global _ENGINE
    if force_reload or _ENGINE is None:
        _ENGINE = RiskEngine()
        _ENGINE.load()
    return _ENGINE


def get_all_assets() -> list[dict[str, Any]]:
    return get_engine().get_all_assets()


def get_asset_status(asset_id: str) -> dict[str, Any]:
    return get_engine().get_asset_status(asset_id)


def get_failure_risk(asset_id: str) -> dict[str, Any]:
    return get_engine().get_failure_risk(asset_id)


def get_maintenance_priority(asset_id: str) -> dict[str, Any]:
    return get_engine().get_maintenance_priority(asset_id)


def print_fleet_summary(engine: RiskEngine | None = None) -> None:
    engine = engine or get_engine()
    stats = engine.summary()
    print("MissionGuard risk engine summary")
    print(f"  total assets:          {stats['total_assets']}")
    print(f"  READY:                 {stats['READY']}")
    print(f"  WARNING:               {stats['WARNING']}")
    print(f"  NOT_READY:             {stats['NOT_READY']}")
    print(f"  HIGH risk:             {stats['HIGH']}")
    print(f"  average health score:  {stats['average_health_score']}")

    high = [a for a in engine.get_all_assets() if a["risk_level"] == "HIGH"]
    if high:
        sample = min(high, key=lambda item: item["health_score"])
        print("\nExample high-risk asset:")
        print(f"  {sample}")
