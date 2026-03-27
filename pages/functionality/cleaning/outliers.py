def iqr_bounds(df, col):

    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1

    return Q1 - 1.5 * IQR, Q3 + 1.5 * IQR

def remove_outliers(df, col):

    lower, upper = iqr_bounds(df, col)

    return df[(df[col] >= lower) & (df[col] <= upper)]