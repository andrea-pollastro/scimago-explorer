from textual.widgets import DataTable
from textual.binding import Binding
from pathlib import Path
from typing import Optional
from textual.message import Message
from ..scimago_processing import (
    load_data, 
    COLS_DISPLAY_NAMES, 
    VISIBLE_COLS_TABLE, 
    COLS_WIDTH,
    REVERTED_ORDER
)

class ScimagoDataTable(DataTable):

    class RowOpened(Message):
        def __init__(self, row_data):
            self.row_data = row_data
            super().__init__()

    BINDINGS = [
        Binding("enter", "select_row", "Open details", show=True),
    ]

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.df = load_data(scimago_df_path)
        self.all_cols = list(self.df.columns)
        self.current_df = self.df.copy()
        self.reset_filters()

    def reset_filters(self) -> None:
        self.sort_by: Optional[str]  = None
        self.ascending: bool = True
        self.sjr_min: float = float('-inf')

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        for c in VISIBLE_COLS_TABLE:
            self.add_column(COLS_DISPLAY_NAMES[c], width=COLS_WIDTH[c])

        self.refresh_table()
    
    def set_sort_column(self, value: Optional[str]) -> None:
        self.sort_by = value
        self.refresh_table()

    def set_sort_order(self, value: bool) -> None:
        self.ascending = value
        self.refresh_table()

    def set_sjr_min(self, value: float) -> None:
        self.sjr_min = value
        self.refresh_table()

    def action_select_row(self) -> None:
        if self.cursor_row is None:
            return

        displayed_df = self.current_df.head(100)
        selected_row = displayed_df.iloc[self.cursor_row]
        self.post_message(self.RowOpened(selected_row))

    def refresh_table(self)-> None:
        self.clear()
        
        # reset df to original state
        self.current_df = self.df.copy()

        # set min sjr
        if self.sjr_min != float('-inf'):
            self.current_df = self.current_df[self.current_df['sjr'] > self.sjr_min]
        
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
        for idx, row in self.current_df[VISIBLE_COLS_TABLE].head(100).iterrows():
            self.add_row(*[str(x) for x in row], key=str(idx))
    