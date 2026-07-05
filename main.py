import argparse
import logging
import yaml
from src.data_ingestion import ScimagoConfig, ingest_data
from pathlib import Path
from src.scimago_explorer import ScimagoExplorer, ExplorerConfig

def setup_logging(enabled: bool = True, level=logging.INFO, log_file: str = 'app.log'):
    if not enabled:
        logging.disable(logging.CRITICAL)
        return

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(log_file)],
    )

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scimago Explorer")
    parser.add_argument(
        "--log-level",
        default=None,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Enable logging at the given level (disabled by default)",
    )
    parser.add_argument("--log-file", default="app.log", help="Path to the log file")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    PROJECT_ROOT = Path(__file__).resolve().parent
    setup_logging(
        enabled=args.log_level is not None,
        level=getattr(logging, args.log_level or "INFO"),
        log_file=args.log_file,
    )

    # ingest scimago data
    with open(PROJECT_ROOT / "conf" / "scimago_data.yaml" , 'r') as f:
        yaml_config = yaml.safe_load(f)
    data_path = Path(yaml_config["path"])
    if not data_path.is_absolute():
        data_path = PROJECT_ROOT / data_path
    yaml_config["path"] = str(data_path)

    scimago_config = ScimagoConfig(**yaml_config)
    df = ingest_data(config=scimago_config)

    # loading explorer config
    with open(PROJECT_ROOT / "conf" / "explorer.yaml" , 'r') as f:
        explorer_config = yaml.safe_load(f)
    explorer_config = ExplorerConfig(**explorer_config)

    # Running the app
    app = ScimagoExplorer(df=df, config=explorer_config)
    app.run()
