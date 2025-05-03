import pandas as pd
from pathlib import Path

muscle_forces_path = Path("Summary-Muscle Forces.csv")
spinal_loads_path = Path("Summary-Spinal Loads.csv")


def clean_columns(df):
    df.columns = (
        df.columns.str.strip()
        .str.replace(" ", "_")
        .str.replace("(", "", regex=False)
        .str.replace(")", "", regex=False)
    )
    return df
