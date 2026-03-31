from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.widgets import DataTable, Header, Select, Static
from pathlib import Path
from .scimago_processing import (
    load_data, 
    COLS_DISPLAY_NAMES, 
    VISIBLE_COLS_TABLE, 
    COLS_WIDTH
)


class ScimagoExplorer(App):

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.df = load_data(scimago_df_path)
        self.current_df = self.df.copy()

    def compose(self) -> ComposeResult:
        sort_options = [
            (COLS_DISPLAY_NAMES[col], col)
            for col in VISIBLE_COLS_TABLE
        ]

        yield Header()

        with Vertical(id="controls"):
            yield Static("Sort by")
            yield Select(
                options=sort_options,
                prompt="Choose a column...",
                id="sort-select",
            )

        with Vertical(id="table-container"):
            yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        table.cursor_type = "row"
        table.zebra_stripes = True
        for c in VISIBLE_COLS_TABLE:
            table.add_column(COLS_DISPLAY_NAMES[c], width=COLS_WIDTH[c])

        self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        for row in self.current_df[VISIBLE_COLS_TABLE].head(100).itertuples(index=False, name=None):
            table.add_row(*[str(x) for x in row])

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id != "sort-select":
            return

        selected_col = str(event.value)
        self.current_df = (
            self.df.copy()
            if selected_col is Select.BLANK
            else self.df.sort_values(by=selected_col, ascending=False)
        )
        self._refresh_table()