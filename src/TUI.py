from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import DataTable, Header, Label, Select, Checkbox
from pathlib import Path
from typing import Optional, cast
from .scimago_processing import (
    load_data, 
    COLS_DISPLAY_NAMES, 
    VISIBLE_COLS_TABLE, 
    COLS_WIDTH,
    SORT_BY_COLS,
    REVERTED_ORDER
)

class SortBy(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            Label(content='Sort by', id='sort-by-label'),
            Select[str](options=[(c, c) for c in SORT_BY_COLS], 
                   prompt='Select column', 
                   id='sort-by-select')
        )
        yield Checkbox(label='Ascending', value=True, id='sort-by-checkbox')

class Filtering(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield SortBy()

class ScimagoDataFrame(DataTable):
    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.df = load_data(scimago_df_path)
        self.current_df = self.df.copy()
        self.reset_filters()

    def reset_filters(self) -> None:
        self.sort_by: Optional[str]  = None
        self.ascending: bool = True

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        for c in VISIBLE_COLS_TABLE:
            self.add_column(COLS_DISPLAY_NAMES[c], width=COLS_WIDTH[c])

        self.refresh_table()

    def refresh_table(self)-> None:
        self.clear()
        
        # reset df to original state
        self.current_df = self.df.copy()
        
        # sorting
        if self.sort_by is not None:
            ascending = self.ascending
            if self.sort_by in REVERTED_ORDER:
                ascending = not ascending
            
            self.current_df = self.current_df.sort_values(
                by=self.sort_by, 
                ascending=ascending
            )

        # populating table
        for row in self.current_df[VISIBLE_COLS_TABLE].head(100).itertuples(index=False, name=None):
            self.add_row(*[str(x) for x in row])
    
    def set_sort_column(self, value: Optional[str]) -> None:
        self.sort_by = value
        self.refresh_table()

    def set_sort_order(self, ascending: bool) -> None:
        self.ascending = ascending
        self.refresh_table()


class ScimagoExplorer(App):

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.scimago_df_path = scimago_df_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Filtering()
        yield ScimagoDataFrame(self.scimago_df_path)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "sort-by-select":
            table = self.query_one(ScimagoDataFrame)
            table.set_sort_column(cast(Optional[str], event.select.selection))

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == "sort-by-checkbox":
            table = self.query_one(ScimagoDataFrame)
            table.set_sort_order(event.checkbox.value)
