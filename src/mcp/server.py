"""
MissionGuard AI MCP Server

Exposes fleet readiness and maintenance intelligence through Model Context Protocol
tools for IBM Bob and other MCP-compatible AI agents.
"""

from typing import Any
from mcp.server import MCPServer

# Import MissionGuard ML/Risk Engine APIs (Agent 1)
from src import (
    get_all_assets,
    get_asset_status,
    get_failure_risk,
    get_maintenance_priority,
)
from src.utils.exceptions import AssetNotFoundError


def create_mcp_server() -> MCPServer:
    """
    Create and configure the MissionGuard MCP server.

    Returns:
        MCPServer: Configured MCP server ready to run
    """
    mcp = MCPServer("MissionGuard AI")

    @mcp.tool()
    def list_assets(
        readiness_filter: str | None = None,
        risk_filter: str | None = None,
        asset_type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        List fleet assets with risk scores and readiness information.

        Supports filtering by readiness status, risk level, and asset type.

        Args:
            readiness_filter: Filter by readiness status (READY, WARNING, NOT_READY)
            risk_filter: Filter by risk level (LOW, MEDIUM, HIGH)
            asset_type_filter: Filter by asset type (e.g., "UAV", "Ground Vehicle")

        Returns:
            List of assets with risk and readiness data

        Examples:
            "Which assets are not mission-ready?" -> readiness_filter="NOT_READY"
            "Show all high-risk assets" -> risk_filter="HIGH"
            "List all UAVs" -> asset_type_filter="UAV"
        """
        assets = get_all_assets()

        # Apply filters
        if readiness_filter:
            readiness_upper = readiness_filter.upper().replace(" ", "_")
            assets = [a for a in assets if a["readiness_status"] == readiness_upper]

        if risk_filter:
            risk_upper = risk_filter.upper()
            assets = [a for a in assets if a["risk_level"] == risk_upper]

        if asset_type_filter:
            assets = [
                a
                for a in assets
                if asset_type_filter.lower() in a["asset_type"].lower()
            ]

        return assets

    @mcp.tool()
    def get_asset_readiness(asset_id: str) -> dict[str, Any]:
        """
        Get mission-readiness status and supporting evidence for a specific asset.

        Args:
            asset_id: Unique asset identifier (e.g., "A-001")

        Returns:
            Asset readiness information including status, health score, risk factors,
            and recommended action

        Raises:
            ValueError: If asset_id is not found

        Examples:
            "What is the readiness status of A-042?"
            "Is asset A-017 mission-ready?"
        """
        try:
            return get_asset_status(asset_id)
        except AssetNotFoundError as e:
            raise ValueError(f"Asset {e.asset_id} not found in fleet") from e

    @mcp.tool()
    def get_asset_failure_risk(asset_id: str) -> dict[str, Any]:
        """
        Get failure risk analysis for a specific asset.

        Returns failure probability, risk level, explainable risk factors,
        and recommended action.

        Args:
            asset_id: Unique asset identifier (e.g., "A-001")

        Returns:
            Risk analysis including health score, failure probability, risk level,
            top risk factors, and recommended action

        Raises:
            ValueError: If asset_id is not found

        Examples:
            "Why is asset A-042 at risk?"
            "What are the risk factors for A-017?"
            "Explain the risk level of A-089"
        """
        try:
            return get_failure_risk(asset_id)
        except AssetNotFoundError as e:
            raise ValueError(f"Asset {e.asset_id} not found in fleet") from e

    @mcp.tool()
    def get_asset_maintenance(asset_id: str) -> dict[str, Any]:
        """
        Get maintenance priority information for a specific asset.

        Returns priority score (0-100, higher = more urgent), fleet-wide ranking,
        priority reasons, and recommended action.

        Args:
            asset_id: Unique asset identifier (e.g., "A-001")

        Returns:
            Maintenance priority data including score, rank, reasons, and action

        Raises:
            ValueError: If asset_id is not found

        Examples:
            "What is the maintenance priority of A-042?"
            "Should we service A-017 soon?"
        """
        try:
            return get_maintenance_priority(asset_id)
        except AssetNotFoundError as e:
            raise ValueError(f"Asset {e.asset_id} not found in fleet") from e

    @mcp.tool()
    def get_fleet_summary() -> dict[str, Any]:
        """
        Get high-level fleet health summary.

        Returns aggregate statistics including asset counts by readiness status
        and risk level, plus the top 10 highest-priority assets.

        Returns:
            Fleet summary with counts, percentages, and priority queue

        Examples:
            "Give me a fleet overview"
            "What's the overall fleet health?"
            "Which assets need service first?"
            "Show me the priority queue"
        """
        assets = get_all_assets()

        # Count by readiness
        readiness_counts = {"READY": 0, "WARNING": 0, "NOT_READY": 0}
        for asset in assets:
            status = asset["readiness_status"]
            if status in readiness_counts:
                readiness_counts[status] += 1

        # Count by risk level
        risk_counts = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
        for asset in assets:
            level = asset["risk_level"]
            if level in risk_counts:
                risk_counts[level] += 1

        # Get top 10 highest-priority assets
        priorities = []
        for asset in assets:
            try:
                priority_info = get_maintenance_priority(asset["asset_id"])
                priorities.append(
                    {
                        "asset_id": asset["asset_id"],
                        "asset_type": asset["asset_type"],
                        "priority_score": priority_info["priority_score"],
                        "priority_rank": priority_info["priority_rank"],
                        "readiness_status": asset["readiness_status"],
                        "risk_level": asset["risk_level"],
                        "recommended_action": asset["recommended_action"],
                    }
                )
            except AssetNotFoundError:
                continue

        # Sort by priority score (highest first)
        priorities.sort(key=lambda p: p["priority_score"], reverse=True)
        top_10 = priorities[:10]

        total_assets = len(assets)

        return {
            "total_assets": total_assets,
            "readiness": {
                "counts": readiness_counts,
                "percentages": {
                    k: round(v / total_assets * 100, 1) if total_assets else 0
                    for k, v in readiness_counts.items()
                },
            },
            "risk": {
                "counts": risk_counts,
                "percentages": {
                    k: round(v / total_assets * 100, 1) if total_assets else 0
                    for k, v in risk_counts.items()
                },
            },
            "top_priority_assets": top_10,
            "maintenance_focus": (
                f"{readiness_counts['NOT_READY']} assets NOT_READY, "
                f"{risk_counts['HIGH']} assets HIGH risk"
            ),
        }

    return mcp


# Standalone entry point for running the server directly
if __name__ == "__main__":
    import asyncio

    async def main():
        """Run the MCP server over stdio transport."""
        mcp = create_mcp_server()
        await mcp.run_stdio_async()

    asyncio.run(main())
