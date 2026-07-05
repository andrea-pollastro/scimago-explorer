import re
from textual.widgets import Static
from textual.containers import VerticalScroll
from textual.app import ComposeResult

class DetailPanel(VerticalScroll):
    QUARTILE_COLORS = {"Q1": "green", "Q2": "yellow", "Q3": "orange", "Q4": "red"}

    def compose(self) -> ComposeResult:
        yield Static("Select a journal and press Enter to see details", id="detail_content", markup=True)

    def show_journal(self, row_data: dict) -> None:
        fields = {k: v for k, v in row_data.items() if not k.startswith("_")}
        title = self._clean(fields.pop("Title", ""))

        lines = [f"[bold]{title}[/bold]\n"]

        areas = fields.pop("Areas", None)
        categories = fields.pop("Categories", None)

        for label, value in fields.items():
            value = self._render_quartile(value) if "quartile" in label.lower() else self._clean(value)
            lines.append(f"[bold]{label}:[/bold] {value}")

        lines.append(self._render_list_section("Categories", self._parse_categories(categories)))
        lines.append(self._render_list_section("Areas", [(a, None) for a in self._split(areas)]))

        self.query_one("#detail_content", Static).update("\n".join(lines))

    def _render_list_section(self, label: str, items: list[tuple[str, str | None]]) -> str:
        if not items:
            return f"\n[bold]{label}:[/bold]\n-"
        rows = "\n".join(self._render_item(name, quartile) for name, quartile in items)
        return f"\n[bold]{label}:[/bold]\n{rows}"

    def _render_item(self, name: str, quartile: str | None) -> str:
        color = self.QUARTILE_COLORS.get(quartile) if quartile else None
        bullet = f"[{color}]■[/]" if color else "•"
        return f"{bullet} {name}"

    def _render_quartile(self, value) -> str:
        value = self._clean(value)
        color = self.QUARTILE_COLORS.get(value)
        return f"[{color}]■[/] {value}" if color else value

    def _clean(self, value) -> str:
        text = str(value).strip()
        return text if text and text.lower() != "nan" else "-"

    def _split(self, value) -> list[str]:
        return [v.strip() for v in str(value or "").split(";") if v.strip()]

    def _parse_categories(self, value) -> list[tuple[str, str | None]]:
        items = self._split(value)
        parsed = []
        for item in items:
            match = re.search(r"\((Q\d)\)\s*$", item)
            quartile = match.group(1) if match else None
            name = re.sub(r"\s*\((Q\d)\)\s*$", "", item).strip()
            parsed.append((name, quartile))
        return parsed