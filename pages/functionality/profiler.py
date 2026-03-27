import pandas as pd

def get_profile(df):

    return {
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str),
        "missing": df.isnull().sum(),
        "missing_pct": (df.isnull().sum() / len(df)) * 100,
        "duplicates": df.duplicated().sum()
    }