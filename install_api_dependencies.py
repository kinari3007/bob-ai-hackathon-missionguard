"""Install FastAPI dependencies for Agent 2."""

import subprocess
import sys

packages = [
    "fastapi==0.115.12",
    "uvicorn[standard]==0.34.2",
    "httpx==0.28.2",
]

print("Installing FastAPI dependencies...")
for package in packages:
    print(f"  Installing {package}...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print(f"  ✓ {package} installed")
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Failed to install {package}: {e}")
        sys.exit(1)

print("\nAll dependencies installed successfully!")
print("\nYou can now run:")
print("  python -m pytest tests/test_api.py -v")
print("  python test_api_manual.py")
print("  uvicorn src.api.main:app --reload")
