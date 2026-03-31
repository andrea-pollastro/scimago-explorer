from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Label, Select, Checkbox, Input
from textual.validation import Number
from ..scimago_processing import SORT_BY_COLS

class SortBy(VerticalGroup):
    DEFAULT_CLASSES = 'filter-widget'

    def compose(self) -> ComposeResult:
        yield Label(content='Sort by', id='sort-by-label')
        yield HorizontalGroup(
            Select[str](
                options=[(c, c) for c in SORT_BY_COLS], 
                prompt='Select column', 
                id='sort-by-select'
            ),
            Checkbox(label='Ascending', value=True, id='sort-by-checkbox'),
            id='sort-by-horizontal-group'
        )

class SJRMinFilter(VerticalGroup):
    DEFAULT_CLASSES = 'filter-widget'

    def compose(self) -> ComposeResult:
        yield Label(content='SJR', id='sjr-filter-label')
        yield Input(
            placeholder='Min', 
            type='number', 
            id='sjr-filter-min',
            validators=[Number(minimum=0)]
        )

class Filtering(HorizontalGroup):
    def compose(self) -> ComposeResult:
        yield SortBy()
        yield SJRMinFilter()