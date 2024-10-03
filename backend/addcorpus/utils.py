import datetime
import os
from typing import Dict, Optional, Union

import numpy as np
import pandas as pd


def get_csv_info(path: Union[str, os.PathLike], **kwargs) -> Dict:
    df = pd.read_csv(path, **kwargs)
    info = {
        col_name: map_col(df[col_name]) for col_name in df.columns
    }
    return info


def map_col(col: pd.Series) -> str:
    if col.dtypes == object:
        if is_date_col(col):
            return 'date'
        return 'text'
    elif col.dtypes == np.float64:
        return 'float'
    elif col.dtypes == np.int64:
        return 'integer'
    elif col.dtypes == bool:
        return 'boolean'
    return 'text'


def is_date_col(col: pd.Series) -> bool:
    mask = col.transform(is_date)
    return mask.all()


def is_date(input: str) -> Optional[datetime.datetime]:
    try:
        datetime.datetime.strptime(input, '%Y-%m-%d')
        return True
    except (ValueError, TypeError):
        return False
