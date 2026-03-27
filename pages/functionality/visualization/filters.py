def filter_category(df, col, values):
    return df[df[col].isin(values)]


def filter_numeric(df, col, min_val, max_val):
    return df[(df[col] >= min_val) & (df[col] <= max_val)]