from datetime import datetime

def generate_report(df, log):

    return {
        "generated_at": datetime.now().isoformat(),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "operations": log
    }