"""Simple test runner script."""
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "-v", "--tb=short"],
    capture_output=False,
    text=True,
)
sys.exit(result.returncode)
