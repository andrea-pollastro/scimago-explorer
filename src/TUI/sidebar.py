from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static
from ..scimago_processing import COLS_DISPLAY_NAMES
import re


class Sidebar(VerticalScroll):
    QUARTILE_COLORS = {
        "Q1": "green",
        "Q2": "yellow",
        "Q3": "orange",
        "Q4": "red",
    }

    def compose(self) -> ComposeResult:
        yield Static("No journal selected", classes="sidebar-placeholder")

    def clear_content(self) -> None:
        self.remove_children()

    def update_details(self, row_data) -> None:
        details = row_data.to_dict()
        self.clear_content()

        title = self._normalize_value(details.get("title"))
        self._mount_title(title)
        self._mount_section_header("Details")

        scalar_fields = [(COLS_DISPLAY_NAMES[k], k) 
                         for k in details.keys() 
                         if k not in ['areas', 'categories']
                         ]

        for label, key in scalar_fields:
            raw_value = details.get(key)
            value = (
                self._render_quartile(raw_value)
                if key == "sjr_best_quartile"
                else self._normalize_value(raw_value)
            )
            self._mount_field(label, value)

        self._mount_list_section(
            "Categories",
            self._parse_categories(details.get("categories")),
            colored_quartiles=True,
        )
        self._mount_list_section(
            "Areas",
            self._parse_areas(details.get("areas")),
            colored_quartiles=False,
        )

        self.remove_class("-hidden")

    def _mount_title(self, title: str) -> None:
        self.mount(
            Static(
                title,
                classes="sidebar-journal-title",
            )
        )

    def _mount_section_header(self, text: str) -> None:
        self.mount(
            Static(
                f"[b]{text}[/b]",
                classes="sidebar-title",
                markup=True,
            )
        )

    def _mount_field(self, label: str, value: str) -> None:
        self.mount(
            Static(
                f"[b]{label}:[/b] {value}",
                classes="sidebar-field",
                markup=True,
            )
        )

    def _mount_list_section(
        self,
        label: str,
        items,
        colored_quartiles: bool = False,
    ) -> None:
        self.mount(
            Static(
                f"[b]{label}:[/b]",
                classes="sidebar-section-title",
                markup=True,
            )
        )

        items = list(items)
        if not items:
            self.mount(Static("-", classes="sidebar-list-item"))
            return

        for item in items:
            self.mount(
                Static(
                    self._render_list_item(item, colored_quartiles=colored_quartiles),
                    classes="sidebar-list-item",
                    markup=True,
                )
            )

    def _render_list_item(self, item, colored_quartiles: bool = False) -> str:
        if colored_quartiles and isinstance(item, tuple):
            name, quartile = item
            color = self.QUARTILE_COLORS.get(quartile)
            bullet = f"[{color}]■[/]" if color else "•"
            return f"{bullet} {name}"

        if isinstance(item, tuple):
            name, _ = item
            return f"• {name}"

        return f"• {item}"

    def _render_quartile(self, value) -> str:
        value = self._normalize_value(value)
        color = self.QUARTILE_COLORS.get(value)
        return f"[{color}]■[/] {value}" if color else value

    def _normalize_value(self, value) -> str:
        if value is None:
            return "-"

        text = str(value).strip()
        return text if text and text.lower() != "nan" else "-"

    def _split_semicolon_values(self, value) -> list[str]:
        if value is None:
            return []

        return [item.strip() for item in str(value).split(";") if item.strip()]

    def _parse_areas(self, value) -> list[str]:
        return self._split_semicolon_values(value)

    def _parse_categories(self, value) -> list[tuple[str, str | None]]:
        return [self._parse_category(item) for item in self._split_semicolon_values(value)]

    def _parse_category(self, item: str) -> tuple[str, str | None]:
        match = re.search(r"\((Q\d)\)\s*$", item.strip())
        quartile = match.group(1) if match else None
        name = re.sub(r"\s*\((Q\d)\)\s*$", "", item).strip()
        return name, quartile