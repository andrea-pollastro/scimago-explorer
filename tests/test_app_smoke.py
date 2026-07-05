import asyncio

import pandas as pd

from src.scimago_explorer import ExplorerConfig, ScimagoExplorer


def _make_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Title": ["Journal A", "Journal B", "Journal C"],
            "Type": ["journal", "journal", "book series"],
            "Publisher": ["Pub A", "Pub B", "n/a"],
            "SJR": [1.5, 0.8, 2.1],
            "SJR Best Quartile": ["Q1", "Q2", "Q1"],
            "H index": [50, 20, 80],
            "Areas": ["Computer Science", "Medicine", "Computer Science; Medicine"],
            "Categories": [
                "Artificial Intelligence (Q1)",
                "Oncology (Q2)",
                "Software (Q1); Oncology (Q3)",
            ],
            "_areas_lower": ["computer science", "medicine", "computer science; medicine"],
            "_categories_lower": [
                "artificial intelligence (q1)",
                "oncology (q2)",
                "software (q1); oncology (q3)",
            ],
            "_title_lower": ["journal a", "journal b", "journal c"],
        }
    )


def _make_config() -> ExplorerConfig:
    return ExplorerConfig(
        page_size=2,
        min_width=80,
        min_height=24,
        display_columns=["Title", "Publisher", "SJR", "SJR Best Quartile", "H index"],
        column_width_weights={},
        search_bar_weights={},
    )


def test_app_smoke():
    async def scenario():
        app = ScimagoExplorer(df=_make_df(), config=_make_config())
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.pause()
            table = app.query_one("#results_table")
            assert table.row_count == 2  # page_size=2, first page of 3 rows

            app.action_next_page()
            await pilot.pause()
            assert table.row_count == 1

            app.action_prev_page()
            await pilot.pause()
            assert table.row_count == 2

            app.action_toggle_dark()
            await pilot.pause()

    asyncio.run(scenario())
