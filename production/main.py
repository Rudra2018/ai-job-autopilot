import json
from pathlib import Path
from .agents import SuperCoordinatorAgent


def run_pipeline(config: dict | None = None) -> dict:
    coordinator = SuperCoordinatorAgent()
    return coordinator.process(config)


def main() -> None:
    dashboard = run_pipeline()
    out_path = Path("final_dashboard.json")
    out_path.write_text(json.dumps(dashboard, indent=2))
    print(f"Dashboard written to {out_path}")


if __name__ == "__main__":
    main()
