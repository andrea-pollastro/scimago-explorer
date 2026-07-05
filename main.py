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

PROJECT_ROOT = Path(__file__).resolve().parent

if __name__ == '__main__':
    setup_logging(enabled=False, level=logging.DEBUG)

    # ingest scimago data
    with open(PROJECT_ROOT / "conf" / "scimago_data.yaml" , 'r') as f:
        yaml_config = yaml.safe_load(f)
    yaml_config["path"] = str(PROJECT_ROOT / yaml_config["path"].lstrip('/'))

    scimago_config = ScimagoConfig(**yaml_config)
    df = ingest_data(config=scimago_config)

    # loading explorer config
    with open(PROJECT_ROOT / "conf" / "explorer.yaml" , 'r') as f:
        explorer_config = yaml.safe_load(f)
    explorer_config = ExplorerConfig(**explorer_config)

    # Running the app
    app = ScimagoExplorer(df=df, config=explorer_config)
    app.run()
