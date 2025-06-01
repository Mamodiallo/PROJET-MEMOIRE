# etl/export.py
from pathlib import Path
import pandas as pd

def export_clean(df: pd.DataFrame, out_path: Path):
    """
    Exporte le DataFrame `df` au format CSV vers `out_path`.
    Crée automatiquement le dossier parent si besoin.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
