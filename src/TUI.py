from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header
from pathlib import Path
from .scimago_processing import load_data, COLS_DISPLAY_NAMES, VISIBLE_COLS_TABLE

class ScimagoExplorer(App):

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.df = load_data(scimago_df_path)

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        table.cursor_type = 'row'
        table.zebra_stripes = True

        table.add_columns(*[COLS_DISPLAY_NAMES[c] for c in VISIBLE_COLS_TABLE])
        for row in self.df[VISIBLE_COLS_TABLE].head(100).itertuples(index=False, name=None):
            table.add_row(*[str(x) for x in row])
