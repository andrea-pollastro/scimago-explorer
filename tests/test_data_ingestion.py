import pandas as pd
import pytest

from src.data_ingestion import ScimagoConfig, ingest_data

CSV_CONTENT = (
    "Rank;Title;Type;Publisher;SJR;Areas;Categories\n"
    '1;Journal A;journal;;"1,234";Computer Science;Artificial Intelligence (Q1)\n'
    "2;Journal B;journal;Pub B;0.8;Medicine;Oncology (Q2)\n"
)


@pytest.fixture
def csv_path(tmp_path):
    path = tmp_path / "scimago.csv"
    path.write_text(CSV_CONTENT, encoding="utf-8")
    return path


def test_ingest_data(csv_path):
    config = ScimagoConfig(
        path=str(csv_path),
        sep=";",
        columns_to_drop=["Rank"],
        nan_map={"Publisher": "n/a"},
    )

    df = ingest_data(config=config)

    assert "Rank" not in df.columns
    assert df["Publisher"].tolist() == ["n/a", "Pub B"]
    assert df["SJR"].tolist() == pytest.approx([1.234, 0.8])
    assert df["_title_lower"].tolist() == ["journal a", "journal b"]
    assert df["_areas_lower"].tolist() == ["computer science", "medicine"]
    assert df["_categories_lower"].tolist() == [
        "artificial intelligence (q1)",
        "oncology (q2)",
    ]


def test_ingest_data_missing_drop_column_is_ignored(csv_path):
    config = ScimagoConfig(path=str(csv_path), sep=";", columns_to_drop=["DoesNotExist"])

    df = ingest_data(config=config)

    assert isinstance(df, pd.DataFrame)
    assert "Rank" in df.columns
