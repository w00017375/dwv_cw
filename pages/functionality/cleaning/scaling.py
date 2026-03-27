import numpy as np

def minmax(df, col):
    min_val = df[col].min()
    max_val = df[col].max()

    df[col] = (df[col] - min_val) / (max_val - min_val)
    return df

def zscore(df, col):
    mean = df[col].mean()
    std = df[col].std()

    df[col] = (df[col] - mean) / std
    return df