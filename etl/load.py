import pandas as pd
from pathlib import Path

def load_raw( path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin-1",
    )
    return df

if __name__ == "__main__":
    # Petit test en ligne de commande : python etl/load.py
    base = Path(__file__).resolve().parent.parent
    raw_path = base / "data" / "1_raw" / "AMV_GDT_P3M.csv"
    df = load_raw(raw_path)
    print("Shape    :", df.shape)
    print("colonnes :", df.columns.tolist())
    print(df.head())