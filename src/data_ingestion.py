# data_ingestion.py
from dataclasses import dataclass, field
import pandas as pd
import logging
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class ScimagoConfig:
    path: str
    sep: str = ';'
    columns_to_drop: list[str] = field(default_factory=list)
    nan_map: dict[str, str] = field(default_factory=dict)


def ingest_data(config: ScimagoConfig) -> pd.DataFrame:
    logger.info("Starting ingestion pipeline | path=%s", config.path)

    df = _load_data(path=config.path, sep=config.sep)
    df = _drop_unused_cols(df=df, cols=config.columns_to_drop)
    df = _replace_nan(df=df, nan_map=config.nan_map)
    df = _sjr_to_float(df=df)
    df = _precompute_lowercase(df=df)    

    logger.info("Pipeline completed | rows=%d cols=%d", len(df), df.shape[1])
    return df


def _load_data(path: str, sep: str) -> pd.DataFrame:
    logger.debug("Reading CSV | path=%s sep=%r", path, sep)
    df = pd.read_csv(path, sep=sep)
    logger.info("CSV loaded | rows=%d cols=%d", len(df), df.shape[1])
    return df


def _drop_unused_cols(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        logger.warning("Columns to drop not found in dataframe: %s", missing)

    df = df.drop(columns=cols, errors="ignore")
    logger.info("Columns dropped | removed=%d remaining=%d", len(cols) - len(missing), df.shape[1])
    return df


def _replace_nan(df: pd.DataFrame, nan_map: dict[str, str]) -> pd.DataFrame:
    for k, v in nan_map.items():
        n_missing = df[k].isna().sum()
        df[k] = df[k].fillna(v)
        logger.debug("NaN replaced | column=%s value=%r n=%d", k, v, n_missing)
    return df

def _sjr_to_float(df: pd.DataFrame) -> pd.DataFrame:
    df['SJR'] = (
        df['SJR']
        .astype(str)
        .str.replace(',', '.', regex=False)
        .replace('nan', np.nan)
        .astype(float)
    )
    logger.debug("SJR convertita a float | NaN residui=%d", df['SJR'].isna().sum())
    return df

def _precompute_lowercase(df: pd.DataFrame) -> pd.DataFrame:
    df['_areas_lower'] = df['Areas'].str.lower()
    df['_categories_lower'] = df['Categories'].str.lower()
    df['_title_lower'] = df['Title'].str.lower()
    return df