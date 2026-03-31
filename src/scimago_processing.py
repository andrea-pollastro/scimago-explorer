from pathlib import Path 
from typing import Dict, List, Tuple
import pandas as pd
import numpy as np

COLS_DISPLAY_NAMES = {
    'title': 'Title',
    'type': 'Type',
    'publisher': 'Publisher', 
    'open_access': 'OA', 
    'open_access_diamond': 'OAD', 
    'sjr': 'SJR', 
    'sjr_best_quartile': 'SJR Q', 
    'h_index': 'H-index', 
    'country': 'Country', 
    'categories': 'Categories', 
    'areas': 'Areas', 
}
VISIBLE_COLS_TABLE = ['title', 'publisher', 'sjr', 'sjr_best_quartile', 'h_index', 'areas']
COLS_WIDTH = {
    'title': 40,
    'type': 10,
    'publisher': 30, 
    'open_access': 10, 
    'open_access_diamond': 10, 
    'sjr': 8, 
    'sjr_best_quartile': 8, 
    'h_index': 8, 
    'country': 30, 
    'categories': 50, 
    'areas': None, 
}

def clean_dataframe(df: pd.DataFrame) -> None:
    COLUMNS_TO_DROP: List[str] = [
        'Rank',
        'Sourceid',
        'Issn',
        'Total Docs. (2024)',
        'Total Docs. (3years)',
        'Total Refs.',
        'Total Citations (3years)',
        'Citable Docs. (3years)',
        'Citations / Doc. (2years)',
        'Ref. / Doc.',
        r'%Female',
        'Coverage',
        'Overton',
        'SDG',
        'Region',
        'Publisher.1'
    ]
    df.drop(columns=COLUMNS_TO_DROP, inplace=True)
    
    # Convert SJR from str -> number 
    # NOTE there are some NaNs; they must not be converted to 0s
    df["SJR"] = (
        df["SJR"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .pipe(pd.to_numeric, errors="coerce")
    )

    # All the columns are capitalized -> lowercase
    df.columns = (
        df.columns
        .str.lower()
        .str.replace(' ', '_')
    )

def get_categories(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    categories = (
        df["categories"]
        .str.split(";")
        .explode()
        .str.strip()
        .str.replace(r"\s*\(Q\d\)", "", regex=True)
        .dropna()
        .unique()
    )

    areas = (
        df["areas"]
        .str.split(";")
        .explode()
        .str.strip()
        .dropna()
        .unique()
    )

    return {
        'type': df['type'].unique(),
        'country': df['country'].unique(),
        'publisher': df['publisher'].unique(),
        'categories': categories,
        'areas': areas,
    }

def load_data(path: Path) -> pd.DataFrame:
    if path.suffix == '.csv':
        df = pd.read_csv(path, sep=';')
    else:
        raise ValueError(f'Invalid path: {path}')
    
    clean_dataframe(df)

    return df
