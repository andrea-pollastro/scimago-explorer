from textual.app import App, ComposeResult
from textual.widgets import Header, Select, Checkbox, Input, Footer, Static
from textual.binding import Binding
from pathlib import Path
from typing import Optional, cast
from .filtering import Filtering
from .scimago_datatable import ScimagoDataTable
from .sidebar import Sidebar

class ScimagoExplorer(App):
    CSS_PATH = Path('css') / 'scimago.tcss'

    BINDINGS = [
        Binding("s", "toggle_sidebar", "Toggle sidebar"),
    ]

    def __init__(self, scimago_df_path: Path):
        super().__init__()
        self.scimago_df_path = scimago_df_path

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            "Scimago Explorer: explore journal rankings from the ScimagoJR 2024 dataset.\n"
            "Use the filters below to search, filter, and sort journals.\n"
            "Click a row or press Enter to open the journal details panel."
        )
        yield Filtering()
        yield Sidebar(classes='-hidden')
        yield ScimagoDataTable(self.scimago_df_path)
        yield Footer()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == 'sort-by-select':
            table = self.query_one(ScimagoDataTable)
            table.set_sort_column(cast(Optional[str], event.select.selection))

        if event.select.id == 'type-select':
            table = self.query_one(ScimagoDataTable)
            table.set_type(cast(Optional[str], event.select.selection))

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
        
        elif event.input.id == 'areas-filter-input':
            table = self.query_one(ScimagoDataTable)
            table.set_areas(event.value)
        
        elif event.input.id == 'title-filter-input':
            table = self.query_one(ScimagoDataTable)
            table.set_title(event.value)

    def on_scimago_data_table_row_opened(self, event: ScimagoDataTable.RowOpened) -> None:
        sidebar = self.query_one(Sidebar)
        sidebar.update_details(event.row_data)
        sidebar.remove_class("-hidden")

    def action_toggle_sidebar(self) -> None:
        sidebar = self.query_one(Sidebar)
        sidebar.toggle_class("-hidden")
