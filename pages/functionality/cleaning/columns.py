def rename(df, old, new):
    return df.rename(columns={old: new})

def drop(df, col):
    return df.drop(columns=[col])

def create_ratio(df, col1, col2, new_col):
    df[new_col] = df[col1] / df[col2]
    return df