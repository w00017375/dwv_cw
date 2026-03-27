import pandas as pd

def fill_mean(df, col):
    df[col] = df[col].fillna(df[col].mean())
    return df

def fill_median(df, col):
    df[col] = df[col].fillna(df[col].median())
    return df

def fill_mode(df, col):
    df[col] = df[col].fillna(df[col].mode()[0])
    return df

def fill_constant(df, col, value):
    df[col] = df[col].fillna(value)
    return df

def drop_rows(df, col):
    return df.dropna(subset=[col])

def forward_fill(df, col):
    df[col] = df[col].fillna(method="ffill")
    return df

def backward_fill(df, col):
    df[col] = df[col].fillna(method="bfill")
    return df