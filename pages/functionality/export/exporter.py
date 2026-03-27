import pandas as pd
from io import BytesIO

def to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def to_excel_bytes(df):

    buffer = BytesIO()
    df.to_excel(buffer, index=False)

    return buffer.getvalue()