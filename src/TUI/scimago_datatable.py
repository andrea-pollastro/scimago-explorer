from textual.widgets import DataTable
from textual.binding import Binding
from pathlib import Path
from typing import Optional
from textual.message import Message
import re
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
        self.mounted = False
        self.reset_filters()

    def reset_filters(self) -> None:
        self.sort_by: Optional[str]  = None
        self.ascending: bool = True
        self.sjr_min: float = float('-inf')
        self.type: Optional[str] = None
        self.areas: list[str] = []
        self.title: list[str] = []

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.zebra_stripes = True
        for c in VISIBLE_COLS_TABLE:
            self.add_column(COLS_DISPLAY_NAMES[c], width=COLS_WIDTH[c])

        self.mounted = True
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

    def set_type(self, value: Optional[str]) -> None:
        self.type = value
        self.refresh_table()
    
    def set_areas(self, value: str) -> None:
        if not value.strip():
            self.areas = []
        else:
            # Parse comma-separated values and strip whitespace
            self.areas = [area.strip() for area in value.split(',')]
        self.refresh_table()
    
    def set_title(self, value: str) -> None:
        if not value.strip():
            self.title = []
        else:
            # Parse comma-separated values and strip whitespace
            self.title = [t.strip() for t in value.split(',')]
        self.refresh_table()

    def action_select_row(self) -> None:
        if self.cursor_row is None:
            return

        displayed_df = self.current_df.head(100)
        selected_row = displayed_df.iloc[self.cursor_row]
        self.post_message(self.RowOpened(selected_row))

    def refresh_table(self)-> None:
        # reset df to original state
        self.current_df = self.df.copy()

        # filter by type
        if self.type is not None:
            self.current_df = self.current_df[self.current_df['type'] == self.type]

        # filter by areas (vectorized - very fast)
        # AND logic: all searched areas must be present in the row
        if self.areas:
            for search_area in self.areas:
                # Pattern: (^|;)\s*search_area (startswith - case insensitive)
                pattern = r'(?:^|;)\s*' + re.escape(search_area)
                self.current_df = self.current_df[
                    self.current_df['areas'].str.contains(pattern, case=False, na=False, regex=True)
                ]

        # filter by title (vectorized - very fast)
        # AND logic: all searched terms must be present in the title
        if self.title:
            for search_term in self.title:
                # Pattern: search_term (startswith - case insensitive)
                pattern = r'^' + re.escape(search_term)
                self.current_df = self.current_df[
                    self.current_df['title'].str.contains(pattern, case=False, na=False, regex=True)
                ]

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

        # Only populate table if widget is mounted
        if not self.mounted:
            return

        # populating table
        self.clear()
        for idx, row in self.current_df[VISIBLE_COLS_TABLE].head(100).iterrows():
            self.add_row(*[str(x) for x in row], key=str(idx))
    