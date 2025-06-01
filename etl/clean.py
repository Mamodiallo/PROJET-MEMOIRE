# etl/clean.py
import pandas as pd

def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    print(df)
    """
    Nettoie le DataFrame brut.
    Pour l’instant, on ne fait que renvoyer df tel quel,
    mais ici vous ajouterez vos dropna, strip, anonymisation, etc.
    """
    # ex. supprimer les colonnes entièrement vides :
    # df = df.dropna(axis=1, how="all")
    return df

