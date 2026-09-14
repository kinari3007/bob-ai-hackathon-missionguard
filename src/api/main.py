"""FastAPI backend for MissionGuard AI.

This is a thin wrapper around the Agent 1 ML/risk foundation. It provides REST
endpoints that call the validated Python APIs without reimplementing any scoring logic.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import (
    get_all_assets,
    get_asset_status,
    get_failure_risk,
    get_maintenance_priority,
)
from src.utils.exceptions import AssetNotFoundError

# Create FastAPI application
app = FastAPI(
    title="MissionGuard AI API",
    description="Mission Readiness & Predictive Maintenance Copilot for IBM BoB AI Hackathon 2026",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8501",  # Streamlit default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Health check endpoint.
    
    Returns:
        Simple status indicating the API is running.
    """
    return {
        "status": "ok",
        "service": "MissionGuard API",
        "version": "1.0.0",
    }


@app.get("/assets", tags=["Assets"])
def list_assets() -> list[dict[str, Any]]:
    """Get all assets with risk scores and readiness status.
    
    This endpoint calls the Agent 1 foundation's `get_all_assets()` function,
    which returns pre-computed risk scores, readiness classifications, and
    maintenance recommendations for the entire fleet.
    
    Returns:
        List of asset records with:
        - asset_id: Unique identifier
        - asset_type: Asset category
        - health_score: 0-100 health score
        - failure_probability: 0-1 failure probability
        - risk_level: LOW, MEDIUM, or HIGH
        - readiness_status: READY, WARNING, or NOT_READY
        - top_risk_factors: List of contributing risk factors
        - recommended_action: Maintenance recommendation
    """
    return get_all_assets()


@app.get("/assets/{asset_id}/status", tags=["Assets"])
def asset_status(asset_id: str) -> dict[str, Any]:
    """Get readiness status and supporting evidence for a specific asset.
    
    Args:
        asset_id: Asset identifier (e.g., "A-001")
    
    Returns:
        Asset status record with:
        - asset_id: Identifier
        - asset_type: Asset category
        - readiness_status: READY, WARNING, or NOT_READY
        - health_score: 0-100 health score
        - risk_level: LOW, MEDIUM, or HIGH
        - top_risk_factors: Contributing risk factors
        - recommended_action: Maintenance recommendation
    
    Raises:
        HTTPException(404): Asset not found
    """
    try:
        return get_asset_status(asset_id)
    except AssetNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        ) from e


@app.get("/assets/{asset_id}/risk", tags=["Assets"])
def asset_risk(asset_id: str) -> dict[str, Any]:
    """Get failure risk analysis for a specific asset.
    
    Args:
        asset_id: Asset identifier (e.g., "A-001")
    
    Returns:
        Risk analysis record with:
        - asset_id: Identifier
        - health_score: 0-100 health score
        - failure_probability: 0-1 probability
        - risk_level: LOW, MEDIUM, or HIGH
        - top_risk_factors: Explainable risk drivers
        - recommended_action: Maintenance recommendation
    
    Raises:
        HTTPException(404): Asset not found
    """
    try:
        return get_failure_risk(asset_id)
    except AssetNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        ) from e


@app.get("/assets/{asset_id}/priority", tags=["Assets"])
def asset_priority(asset_id: str) -> dict[str, Any]:
    """Get maintenance priority score and ranking for a specific asset.
    
    Args:
        asset_id: Asset identifier (e.g., "A-001")
    
    Returns:
        Priority record with:
        - asset_id: Identifier
        - asset_type: Asset category
        - priority_score: 0-100 urgency score (higher = more urgent)
        - priority_rank: 1 to N ranking (1 = highest priority)
        - total_assets: Total fleet size
        - readiness_status: READY, WARNING, or NOT_READY
        - risk_level: LOW, MEDIUM, or HIGH
        - health_score: 0-100 health score
        - priority_reasons: List of factors driving priority
        - recommended_action: Maintenance recommendation
    
    Raises:
        HTTPException(404): Asset not found
    """
    try:
        return get_maintenance_priority(asset_id)
    except AssetNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"Asset {asset_id} not found",
        ) from e


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions gracefully."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
        },
    )
