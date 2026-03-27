def remove_duplicates(df):
    return df.drop_duplicates()

def remove_duplicates_subset(df, cols):
    return df.drop_duplicates(subset=cols)