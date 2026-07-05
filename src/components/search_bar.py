from textual.app import ComposeResult
from textual.widgets import (
    Label,
    Input,
    Select,
    Switch,
)
from textual.containers import HorizontalGroup, VerticalGroup

class TextComponent(VerticalGroup):
    def __init__(self, label: str, placeholder: str, widget_id: str, weight: float = 1):
        super().__init__()
        self.label = label
        self.placeholder = placeholder
        self.widget_id = widget_id
        self.styles.width = f"{weight}fr"

    def compose(self) -> ComposeResult:
        yield Label(content=self.label)
        yield Input(placeholder=self.placeholder, type="text", id=self.widget_id)


class NumericalComponent(VerticalGroup):
    def __init__(self, label: str, placeholder: str, widget_id: str, weight: float = 1):
        super().__init__()
        self.label = label
        self.placeholder = placeholder
        self.widget_id = widget_id
        self.styles.width = f"{weight}fr"

    def compose(self) -> ComposeResult:
        yield Label(content=self.label)
        yield Input(placeholder=self.placeholder, type="number", id=self.widget_id)


class SelectComponent(VerticalGroup):
    def __init__(self, label: str, options: list[tuple[str, str]], widget_id: str, weight: float = 1):
        super().__init__()
        self.label = label
        self.options = options
        self.widget_id = widget_id
        self.styles.width = f"{weight}fr"

    def compose(self) -> ComposeResult:
        yield Label(content=self.label)
        yield Select(options=self.options, id=self.widget_id)
        

class SortOrderComponent(VerticalGroup):
    def __init__(self, label: str, widget_id: str, weight: float = 1):
        super().__init__()
        self.label = label
        self.widget_id = widget_id
        self.styles.width = f"{weight}fr"

    def compose(self) -> ComposeResult:
        yield Label(content=self.label)
        yield Switch(value=False, id=self.widget_id)


class SearchBar(HorizontalGroup):
    def __init__(
        self,
        type_options: list[tuple[str, str]],
        sort_by_options: list[tuple[str, str]],
        field_weights: dict[str, float] | None = None,
    ):
        super().__init__()
        self.type_options = type_options
        self.sort_by_options = sort_by_options
        self.weights = field_weights or {}

    def compose(self) -> ComposeResult:
        yield SelectComponent(
            label="Type", options=self.type_options, widget_id="type_filter",
            weight=self.weights.get("type_filter", 1),
        )
        yield NumericalComponent(
            label="min. SJR", placeholder="e.g. 1.2", widget_id="min_sjr",
            weight=self.weights.get("min_sjr", 1),
        )
        yield SelectComponent(
            label="Sort by", options=self.sort_by_options, widget_id="sort_by",
            weight=self.weights.get("sort_by", 1),
        )
        yield SortOrderComponent(
            label="Asc.", widget_id="sort_order",
            weight=self.weights.get("sort_order", 1),
        )
        yield TextComponent(
            label="Areas", placeholder="e.g. Computer Science, Engineering", widget_id="areas_filter",
            weight=self.weights.get("areas_filter", 1),
        )
        yield TextComponent(
            label="Categories", placeholder="e.g. Oncology, Cardiology", widget_id="categories_filter",
            weight=self.weights.get("categories_filter", 1),
        )
        yield TextComponent(
            label="Journal name", placeholder="e.g. Pattern Recognition", widget_id="journal_name_filter",
            weight=self.weights.get("journal_name_filter", 1),
        )
