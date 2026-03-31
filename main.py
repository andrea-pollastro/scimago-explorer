from pathlib import Path
from src.TUI.scimago_explorer import ScimagoExplorer

if __name__ == "__main__":
    SCIMAGO_CSV_PATH = Path('data') / 'scimagojr 2024.csv'
    
    app = ScimagoExplorer(scimago_df_path=SCIMAGO_CSV_PATH)
    app.run()