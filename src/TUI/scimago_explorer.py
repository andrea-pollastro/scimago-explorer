from textual.app import App, ComposeResult
from textual.widgets import Header, Select, Checkbox, Input, Footer
from pathlib import Path
from typing import Optional, cast
from .filtering import Filtering
from .scimago_datatable import ScimagoDataTable
from .sidebar import Sidebar

class ScimagoExplorer(App):
    CSS_PATH = Path('css') / 'scimago.tcss'

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.scimago_df_path = scimago_df_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Filtering()
        yield Sidebar(classes='-hidden')
        yield ScimagoDataTable(self.scimago_df_path)
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == 'sort-by-select':
            table = self.query_one(ScimagoDataTable)
            table.set_sort_column(cast(Optional[str], event.select.selection))

    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        if event.checkbox.id == 'sort-by-checkbox':
            table = self.query_one(ScimagoDataTable)
            table.set_sort_order(event.checkbox.value)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == 'sjr-filter-min':
            table = self.query_one(ScimagoDataTable)

            if not event.value:
                table.set_sjr_min(float('-inf'))
                return
            
            if event.validation_result is not None and not event.validation_result.is_valid:
                return
            
            table.set_sjr_min(float(event.value))

    def on_scimago_data_table_row_opened(self, event: ScimagoDataTable.RowOpened) -> None:
        sidebar = self.query_one(Sidebar)
        sidebar.update_details(event.row_data)
