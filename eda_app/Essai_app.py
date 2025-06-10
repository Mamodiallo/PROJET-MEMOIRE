# eda_app/Essai_app.py

import streamlit as st

# ----------------------------------------------------------------
# 0) CONFIGURATION STREAMLIT (doit être la première commande Streamlit)
# ----------------------------------------------------------------
st.set_page_config(page_title="EDA – Orange Mobile", layout="wide")

import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

# ----------------------------------------------------------------
# 1) Mapping des codes de disposition
# ----------------------------------------------------------------
code_map = {
    1: "Complété",
    2: "Abandonné",
    0: "Interrompu"
}

# ----------------------------------------------------------------
# 2) Chargement des données
# ----------------------------------------------------------------
@st.cache_data
def load_data() -> pd.DataFrame:
    base = Path(__file__).resolve().parent.parent
    csv_path = base / "Donnee/1_raw/AMV_GDT_P3M.csv"
    df = pd.read_csv(
        csv_path,
        sep=";",
        encoding="latin-1",
        parse_dates=["Datedeladernièreconnexion"],
        dayfirst=True
    )
    return df

df = load_data()

# ----------------------------------------------------------------
# 3) Validation & conversion de la colonne date
# ----------------------------------------------------------------
if not pd.api.types.is_datetime64_any_dtype(df["Datedeladernièreconnexion"]):
    df["Datedeladernièreconnexion"] = pd.to_datetime(
        df["Datedeladernièreconnexion"],
        dayfirst=True,
        errors="coerce"
    )

min_ts = df["Datedeladernièreconnexion"].min()
max_ts = df["Datedeladernièreconnexion"].max()
if pd.isna(min_ts) or pd.isna(max_ts):
    st.error("⚠️ La colonne ‘Datedeladernièreconnexion’ est vide ou mal formatée.")
    st.stop()

min_date = min_ts.date()
max_date = max_ts.date()

# ----------------------------------------------------------------
# 4) Interface & filtres
# ----------------------------------------------------------------
st.title("Exploration des réponses – Orange Mobile")
st.sidebar.header("Filtres")

# 4.a Filtre code de disposition
options_code = ["Tous"] + list(code_map.values())
sel_code = st.sidebar.selectbox("Code de disposition", options_code)
if sel_code != "Tous":
    inv_map = {v: k for k, v in code_map.items()}
    df = df[df["Codededisposition"] == inv_map[sel_code]]

# 4.b Filtre période de connexion
start_date, end_date = st.sidebar.date_input(
    "Période de connexion",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)
mask = (
    (df["Datedeladernièreconnexion"] >= pd.Timestamp(start_date)) &
    (df["Datedeladernièreconnexion"] < pd.Timestamp(end_date) + pd.Timedelta(days=1))
)
df = df[mask]

# ----------------------------------------------------------------
# 5) Affichage du DataFrame filtré
# ----------------------------------------------------------------
st.subheader("Données après filtrage")
st.markdown(f"- **{df.shape[0]}** réponses sélectionnées")
st.dataframe(df, use_container_width=True)

# ----------------------------------------------------------------
# 6) Préparation du camembert
# ----------------------------------------------------------------
df["disposition"] = df["Codededisposition"].map(code_map).fillna("Autre")
counts = (
    df["disposition"]
      .value_counts(dropna=False)
      .rename_axis("disposition")
      .reset_index(name="count")
)
counts["percent"] = (counts["count"] / counts["count"].sum() * 100).round(1)

# ----------------------------------------------------------------
# 7) Affichage du camembert
# ----------------------------------------------------------------
fig = px.pie(
    counts,
    names="disposition",
    values="count",
    hole=0.3,
    title=f"Répartition des statuts du {start_date} au {end_date}"
)
fig.update_traces(
    textinfo="label+percent+value",
    textposition="outside"
)
fig.update_layout(margin=dict(t=40, b=0, l=0, r=0))

st.plotly_chart(fig, use_container_width=True)
