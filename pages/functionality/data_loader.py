import pandas as pd

def load_file(file):

    try:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)

        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        elif file.name.endswith(".json"):
            df = pd.read_json(file)

        else:
            raise ValueError("Unsupported file format")

        return df

    except Exception as e:
        raise ValueError(f"Error reading file: {str(e)}")