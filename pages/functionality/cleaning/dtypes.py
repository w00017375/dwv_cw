import pandas as pd

def to_numeric(df, col):
    df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def to_datetime(df, col):
    df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def to_category(df, col):
    df[col] = df[col].astype("category")
    return df

def to_string(df, col):
    df[col] = df[col].astype(str)
    return df