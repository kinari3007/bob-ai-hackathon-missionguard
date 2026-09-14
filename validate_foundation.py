"""Simple validation script with JSON output."""
import json
import sys

results = {"tests": [], "status": "unknown"}

try:
    from src import (
        get_all_assets,
        get_asset_status,
        get_failure_risk,
        get_maintenance_priority,
    )
    
    # Test 1
    assets = get_all_assets()
    results["tests"].append({"name": "get_all_assets", "status": "PASS", "count": len(assets)})
    
    # Test 2
    test_id = assets[0]["asset_id"]
    status = get_asset_status(test_id)
    results["tests"].append({"name": "get_asset_status", "status": "PASS", "readiness": status["readiness_status"]})
    
    # Test 3
    risk = get_failure_risk(test_id)
    results["tests"].append({"name": "get_failure_risk", "status": "PASS", "risk_level": risk["risk_level"]})
    
    # Test 4
    priority = get_maintenance_priority(test_id)
    results["tests"].append({"name": "get_maintenance_priority", "status": "PASS", "priority_score": float(priority["priority_score"])})
    
    # Count stats
    stats = {
        "total_assets": len(assets),
        "risk_levels": {"LOW": 0, "MEDIUM": 0, "HIGH": 0},
        "readiness": {"READY": 0, "WARNING": 0, "NOT_READY": 0}
    }
    for a in assets:
        stats["risk_levels"][a["risk_level"]] += 1
        stats["readiness"][a["readiness_status"]] += 1
    results["stats"] = stats
    results["status"] = "SUCCESS"
    
except Exception as e:
    results["status"] = "FAILED"
    results["error"] = str(e)
    import traceback
    results["traceback"] = traceback.format_exc()

with open("validation_result.json", "w") as f:
    json.dump(results, f, indent=2)

sys.exit(0 if results["status"] == "SUCCESS" else 1)
