# eda_app/Essai_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from streamlit_option_menu import option_menu
import numpy as np

# ───────────────────────────────────────────────────────────────────────────────
# 0) CONFIGURATION GLOBALE
# ───────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Assurance Mobile – Mémoire",
    layout="wide",
    initial_sidebar_state="expanded"
)
primary_color   = "#E63946"
background_card = "#F8F9FA"

# ───────────────────────────────────────────────────────────────────────────────
# 1) MENU LATÉRAL À ONGLET
# ───────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    selection = option_menu(
        menu_title="Navigation",
        options=["Projet mémoire", "Suivi mensuel", "Dashboard"],
        icons=["house", "bar-chart-line", "speedometer2"],
        menu_icon="cast",
        default_index=1,
        styles={
            "container": {"background-color": "#ffffff", "padding": "10px"},
            "nav-link": {"font-size": "16px", "margin": "0px"},
            "nav-link-selected": {"background-color": primary_color, "color": "white"}
        }
    )

# ───────────────────────────────────────────────────────────────────────────────
# 2) PAGE “Projet mémoire”
# ───────────────────────────────────────────────────────────────────────────────
if selection == "Projet mémoire":
    st.markdown(f"<h1 style='color:{primary_color};'>📚 Projet mémoire</h1>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background-color:#fff; padding:20px; border-radius:8px;'>
        <h3>Contexte</h3>
        <p>Enquête de satisfaction des abonnés Orange Mobile (France).</p>
        <h3>Objectifs</h3>
        <ul>
          <li>Charger, nettoyer et préparer les données.</li>
          <li>Explorer les réponses (EDA).</li>
          <li>Mettre en place un suivi mensuel interactif.</li>
          <li>Développer un dashboard final.</li>
        </ul>
        </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col1.image(
        "https://upload.wikimedia.org/wikipedia/fr/b/b2/Logo_Universit%C3%A9_Paris_1_Panth%C3%A9on-Sorbonne.svg",
        width=150
    )
    col2.image(
        "https://upload.wikimedia.org/wikipedia/commons/4/45/Logo_decathlon.svg",
        width=150
    )

# ───────────────────────────────────────────────────────────────────────────────
# 3) PAGE “Suivi mensuel”
# ───────────────────────────────────────────────────────────────────────────────
elif selection == "Suivi mensuel":
    st.markdown(f"<h1 style='color:{primary_color};'>📊 Suivi mensuel des réponses</h1>", unsafe_allow_html=True)

    # Chargement des données
    @st.cache_data
    def load_data():
        base     = Path(__file__).resolve().parent.parent
        csv_path = base / "Donnee" / "1_raw" / "AMV_GDT_P3M.csv"
        return pd.read_csv(
            csv_path,
            sep=";",
            encoding="latin-1",
            parse_dates=["Datedeladernièreconnexion"]
        )

    df = load_data()
    code_map = {1: "Complété", 2: "Abandonné", 0: "Interrompu"}
    df["disposition"] = df["Codededisposition"].map(code_map).fillna("Autre")

    # Sidebar : filtres
    st.sidebar.markdown(f"<h4 style='color:{primary_color};'>Filtres</h4>", unsafe_allow_html=True)
    sel_code = st.sidebar.selectbox("Code de disposition", ["Tous"] + list(code_map.values()))
    if sel_code != "Tous":
        inv = {v: k for k, v in code_map.items()}
        df = df[df["Codededisposition"] == inv[sel_code]]

    # Calcul safe des bornes de date
    min_ts = df["Datedeladernièreconnexion"].min()
    max_ts = df["Datedeladernièreconnexion"].max()
    if pd.isna(min_ts) or pd.isna(max_ts):
        st.error("La colonne ‘Datedeladernièreconnexion’ contient trop de NaT ou est mal formatée.")
        st.stop()
    min_d = min_ts.date()
    max_d = max_ts.date()

    # Slider ergonomique de dates
    start_date, end_date = st.sidebar.slider(
        "Période",
        min_value=min_d,
        max_value=max_d,
        value=(min_d, max_d),
        format="DD/MM/YYYY"
    )
    mask_date = df["Datedeladernièreconnexion"].dt.date.between(start_date, end_date)
    mask_zero = df["Codededisposition"] == 0
    df = df[mask_date | mask_zero]

    # KPI cards
    total = df["Codededisposition"].isin([0,1,2]).sum()
    comp  = (df["Codededisposition"] == 1).sum()
    inter = (df["Codededisposition"] == 2).sum()
    pct_c = comp/total*100 if total else 0
    pct_i = inter/total*100 if total else 0

    k1, k2, k3 = st.columns(3, gap="large")
    def render_card(col, icon, title, value, delta=None):
        col.markdown(
            f"<div style='background:{background_card}; padding:20px; "
            f"border-radius:8px; text-align:center;'>"
            f"<h3>{icon} {title}</h3><h1>{value}</h1>"
            + (f"<p style='color:{primary_color}; margin:0;'>{delta}</p>" if delta else "") +
            "</div>", unsafe_allow_html=True
        )

    render_card(k1, "👥", "Total sollicités", total)
    render_card(k2, "✅", "Complétés", comp, f"{pct_c:.1f}%")
    render_card(k3, "⏸️", "Interrompus", inter, f"{pct_i:.1f}%")

    st.markdown("---")

    # DataFrame détaillé sous expander
    with st.expander("🔍 Voir le détail des réponses filtrées"):
        st.dataframe(df, use_container_width=True)

    # Pie chart
    counts = df["disposition"].value_counts().rename_axis("disp").reset_index(name="count")
    fig = px.pie(
        counts,
        names="disp",
        values="count",
        hole=0.35,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig.update_traces(textinfo="label+value+percent", textposition="outside")
    fig.update_layout(
        margin=dict(t=40, b=10, l=10, r=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
    )
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────────────────────────────────────────────────────
# 4) PAGE “Dashboard”
# ───────────────────────────────────────────────────────────────────────────────
else:
    st.markdown(f"<h1 style='color:{primary_color};'>📈 Dashboard final</h1>", unsafe_allow_html=True)
    st.info("Bientôt disponible : visualisations avancées et analyses prédictives.")
