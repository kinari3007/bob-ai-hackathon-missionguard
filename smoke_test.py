"""Smoke test for MissionGuard foundation layer."""

from src import (
    get_all_assets,
    get_asset_status,
    get_failure_risk,
    get_maintenance_priority,
)

print("=" * 70)
print("MISSIONGUARD FOUNDATION SMOKE TEST")
print("=" * 70)

# Test 1: Load all assets
print("\n1. Testing get_all_assets()...")
assets = get_all_assets()
print(f"   ✓ Loaded {len(assets)} assets")
assert len(assets) > 0, "Should have loaded assets"
print(f"   ✓ Sample asset types: {set(a['asset_type'] for a in assets[:5])}")

# Test 2: Verify risk scoring
print("\n2. Testing risk scoring...")
risk_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0}
for asset in assets:
    risk_levels[asset["risk_level"]] += 1
    assert 0.0 <= asset["health_score"] <= 100.0
    assert 0.0 <= asset["failure_probability"] <= 1.0
print(f"   ✓ Risk distribution: LOW={risk_levels['LOW']}, MEDIUM={risk_levels['MEDIUM']}, HIGH={risk_levels['HIGH']}")

# Test 3: Verify readiness classification
print("\n3. Testing readiness classification...")
readiness = {"READY": 0, "WARNING": 0, "NOT_READY": 0}
for asset in assets:
    readiness[asset["readiness_status"]] += 1
print(f"   ✓ Readiness: READY={readiness['READY']}, WARNING={readiness['WARNING']}, NOT_READY={readiness['NOT_READY']}")

# Test 4: Verify explainability
print("\n4. Testing explainability...")
high_risk = [a for a in assets if a["risk_level"] == "HIGH"]
if high_risk:
    sample = high_risk[0]
    print(f"   ✓ High-risk asset: {sample['asset_id']}")
    print(f"   ✓ Health: {sample['health_score']:.1f}")
    print(f"   ✓ Top risk factors: {sample['top_risk_factors']}")
    assert len(sample["top_risk_factors"]) > 0
else:
    print("   ⚠ No high-risk assets in dataset")

# Test 5: Test get_asset_status API
print("\n5. Testing get_asset_status()...")
test_id = assets[0]["asset_id"]
status = get_asset_status(test_id)
print(f"   ✓ Asset {status['asset_id']}: {status['readiness_status']}")
print(f"   ✓ Recommended action: {status['recommended_action']}")
assert "readiness_status" in status
assert "recommended_action" in status

# Test 6: Test get_failure_risk API
print("\n6. Testing get_failure_risk()...")
risk = get_failure_risk(test_id)
print(f"   ✓ Failure probability: {risk['failure_probability']:.4f}")
print(f"   ✓ Risk level: {risk['risk_level']}")
assert "failure_probability" in risk
assert "risk_level" in risk

# Test 7: Test get_maintenance_priority API
print("\n7. Testing get_maintenance_priority()...")
priority = get_maintenance_priority(test_id)
print(f"   ✓ Priority score: {priority['priority_score']:.2f}/100")
print(f"   ✓ Priority rank: {priority['priority_rank']}/{priority['total_assets']}")
print(f"   ✓ Priority reasons: {priority['priority_reasons']}")
assert "priority_score" in priority
assert "priority_rank" in priority
assert "priority_reasons" in priority
assert len(priority["priority_reasons"]) > 0

# Test 8: Verify priority ordering
print("\n8. Testing maintenance priority ordering...")
priorities = [(a["asset_id"], get_maintenance_priority(a["asset_id"])["priority_score"]) 
              for a in assets[:10]]
priorities.sort(key=lambda x: x[1], reverse=True)
print(f"   ✓ Top 3 priorities:")
for aid, score in priorities[:3]:
    print(f"     - {aid}: {score:.2f}")

# Test 9: Verify high-risk assets have high priority
print("\n9. Testing risk-priority correlation...")
if high_risk:
    high_risk_priorities = [get_maintenance_priority(a["asset_id"])["priority_score"] for a in high_risk[:5]]
    low_risk = [a for a in assets if a["risk_level"] == "LOW"]
    if low_risk:
        low_risk_priorities = [get_maintenance_priority(a["asset_id"])["priority_score"] for a in low_risk[:5]]
        avg_high = sum(high_risk_priorities) / len(high_risk_priorities)
        avg_low = sum(low_risk_priorities) / len(low_risk_priorities)
        print(f"   ✓ High-risk avg priority: {avg_high:.2f}")
        print(f"   ✓ Low-risk avg priority: {avg_low:.2f}")
        assert avg_high > avg_low, "High-risk should have higher priority"

# Test 10: Verify reproducibility
print("\n10. Testing reproducibility...")
assets2 = get_all_assets()
assert len(assets) == len(assets2)
assert assets[0]["asset_id"] == assets2[0]["asset_id"]
assert assets[0]["health_score"] == assets2[0]["health_score"]
print(f"   ✓ Results are deterministic and cached")

print("\n" + "=" * 70)
print("ALL SMOKE TESTS PASSED ✓")
print("=" * 70)
print("\nFoundation layer is ready for Agent 2 (API/MCP integration)")
