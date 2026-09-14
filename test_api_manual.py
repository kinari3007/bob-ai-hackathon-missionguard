"""Manual API smoke test script."""

import json

try:
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    client = TestClient(app)
    results = {"tests": [], "status": "unknown"}
    
    # Test 1: Health check
    response = client.get("/health")
    results["tests"].append({
        "name": "GET /health",
        "status": "PASS" if response.status_code == 200 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Test 2: List assets
    response = client.get("/assets")
    data = response.json() if response.status_code == 200 else []
    results["tests"].append({
        "name": "GET /assets",
        "status": "PASS" if response.status_code == 200 and len(data) == 100 else "FAIL",
        "status_code": response.status_code,
        "count": len(data) if isinstance(data, list) else 0,
    })
    
    # Test 3: Asset status (valid)
    response = client.get("/assets/A-001/status")
    results["tests"].append({
        "name": "GET /assets/A-001/status",
        "status": "PASS" if response.status_code == 200 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Test 4: Asset risk (valid)
    response = client.get("/assets/A-050/risk")
    results["tests"].append({
        "name": "GET /assets/A-050/risk",
        "status": "PASS" if response.status_code == 200 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Test 5: Asset priority (valid)
    response = client.get("/assets/A-100/priority")
    results["tests"].append({
        "name": "GET /assets/A-100/priority",
        "status": "PASS" if response.status_code == 200 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Test 6: Unknown asset returns 404
    response = client.get("/assets/UNKNOWN-999/status")
    results["tests"].append({
        "name": "GET /assets/UNKNOWN-999/status (should be 404)",
        "status": "PASS" if response.status_code == 404 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Test 7: Docs endpoint
    response = client.get("/docs")
    results["tests"].append({
        "name": "GET /docs",
        "status": "PASS" if response.status_code == 200 else "FAIL",
        "status_code": response.status_code,
    })
    
    # Check if all passed
    all_passed = all(t["status"] == "PASS" for t in results["tests"])
    results["status"] = "SUCCESS" if all_passed else "FAILED"
    results["summary"] = f"{sum(1 for t in results['tests'] if t['status'] == 'PASS')}/{len(results['tests'])} tests passed"
    
except ImportError as e:
    results = {
        "status": "DEPENDENCY_ERROR",
        "error": "FastAPI dependencies not installed",
        "detail": str(e),
        "action": "Run: .venv\\Scripts\\pip.exe install -r requirements.txt",
    }
except Exception as e:
    results = {
        "status": "ERROR",
        "error": str(e),
        "type": type(e).__name__,
    }
    import traceback
    results["traceback"] = traceback.format_exc()

with open("api_test_result.json", "w") as f:
    json.dump(results, f, indent=2)

print(json.dumps(results, indent=2))
