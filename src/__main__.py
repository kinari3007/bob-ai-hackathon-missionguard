"""CLI entry: generate data if needed, score the fleet, print a summary.

Run from the repository root:

    .venv\\Scripts\\python.exe -m src
"""

from src.data.generate_dataset import save_dataset
from src.services.risk_engine import RiskEngine, print_fleet_summary
from src.utils.config import DEFAULT_CONFIG


def main() -> None:
    if not DEFAULT_CONFIG.data_path.exists():
        save_dataset()
    engine = RiskEngine()
    engine.load()
    print_fleet_summary(engine)


if __name__ == "__main__":
    main()
