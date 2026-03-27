def check_range(df, col, min_val, max_val):
    return df[(df[col] < min_val) | (df[col] > max_val)]

def check_not_null(df, col):
    return df[df[col].isnull()]

def check_allowed_values(df, col, allowed):
    return df[~df[col].isin(allowed)]