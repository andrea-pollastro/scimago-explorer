import time
import logging
logger = logging.getLogger(__name__)
from textual.app import App, ComposeResult
from textual.widgets import (
    Footer, 
    Header, 
    Input,
    Select,
    DataTable,
)
from textual.containers import Horizontal
from dataclasses import dataclass, field
from .components.detail_panel import DetailPanel
from .components.search_bar import SearchBar
import pandas as pd

@dataclass
class ExplorerConfig:
    display_columns: list[str] = field(default_factory=list)
    column_width_weights: dict[str, float] = field(default_factory=dict)
    search_bar_weights: dict[str, float] = field(default_factory=dict)

class ScimagoExplorer(App):
    """A Textual app to manage stopwatches."""
    CSS = """
    #results_table {
        width: 3fr;
    }
    #detail_panel {
        width: 1fr;
        border-left: solid $primary;
        padding: 1;
    }
    """

    BINDINGS = [("d", "toggle_dark", "Toggle dark mode")]

    def __init__(self, df: pd.DataFrame, config: ExplorerConfig):
        super().__init__()
        self.df = df
        self.type_options = [(t.capitalize(), t) for t in df['Type'].unique()]
        self.sort_by_options = [('H index', 'H index'), ('SJR', 'SJR')]
        self.config = config
        self._current_filtered = df

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield SearchBar(
            type_options=self.type_options, 
            sort_by_options=self.sort_by_options,
            field_weights=self.config.search_bar_weights,
        )
        with Horizontal():
            yield DataTable(id="results_table", cursor_type="row")
            yield DetailPanel(id="detail_panel")
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def on_mount(self) -> None:
        self.call_after_refresh(self._setup_table_columns)

    def _setup_table_columns(self) -> None:
        table = self.query_one("#results_table", DataTable)
        display_columns = self.config.display_columns
        column_width_weights = self.config.column_width_weights

        total_weight = sum(column_width_weights.get(col, 1) for col in display_columns) or 1
        available_width = table.size.width - 10

        for col in display_columns:
            w = int(available_width * column_width_weights.get(col, 1) / total_weight)
            table.add_column(col, width=w)

        self.apply_filters()

    def apply_filters(self) -> None:
        filtered = self.df

        type_value = self.query_one("#type_filter", Select).value
        if isinstance(type_value, str):
            filtered = filtered[filtered["Type"] == type_value]

        min_sjr_raw = self.query_one("#min_sjr", Input).value
        if min_sjr_raw:
            try:
                min_sjr = float(min_sjr_raw)
            except ValueError:
                min_sjr = None
            if min_sjr is not None:
                filtered = filtered[filtered["SJR"] >= min_sjr]

        areas_raw = self.query_one("#areas_filter", Input).value
        if areas_raw:
            terms = [t.strip().lower() for t in areas_raw.split(",") if t.strip()]
            for term in terms:
                filtered = filtered[filtered["_areas_lower"].str.contains(term, na=False, regex=False)]

        categories_raw = self.query_one("#categories_filter", Input).value
        if categories_raw:
            terms = [t.strip().lower() for t in categories_raw.split(",") if t.strip()]
            for term in terms:
                filtered = filtered[filtered["_categories_lower"].str.contains(term, na=False, regex=False)]

        journal_name_raw = self.query_one("#journal_name_filter", Input).value
        if journal_name_raw:
            filtered = filtered[filtered["_title_lower"].str.contains(journal_name_raw.lower(), na=False, regex=False)]

        sort_by_value = self.query_one("#sort_by", Select).value
        if isinstance(sort_by_value, str):
            filtered = filtered.sort_values(sort_by_value, ascending=False)

        self._current_filtered = filtered.reset_index(drop=True)

        display_columns = self.config.display_columns
        table = self.query_one(DataTable)
        table.clear(columns=False)

        start = time.perf_counter()
        table.add_rows(self._current_filtered[display_columns].itertuples(index=False, name=None))
        logger.debug("add_rows | rows=%d elapsed=%.3fs", len(self._current_filtered), time.perf_counter() - start)

    def on_input_changed(self, event: Input.Changed) -> None:
        if hasattr(self, "_filter_timer"):
            self._filter_timer.stop()
        self._filter_timer = self.set_timer(0.3, self.apply_filters)

    def on_select_changed(self, event: Select.Changed) -> None:
        self.apply_filters()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_index = event.cursor_row
        if row_index >= len(self._current_filtered):
            return

        row_data = self._current_filtered.iloc[row_index].to_dict()
        detail_panel = self.query_one("#detail_panel", DetailPanel)
        detail_panel.show_journal(row_data)
