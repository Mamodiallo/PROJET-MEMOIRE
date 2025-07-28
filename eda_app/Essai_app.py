# eda_app/Essai_app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from streamlit_option_menu import option_menu
import numpy as np
import unicodedata
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

def render_card(col, icon, title, value, delta=None):
    col.markdown(
        f"<div style='background:{background_card}; padding:20px; "
        f"border-radius:8px; text-align:center;'>"
        f"<h3>{icon} {title}</h3><h1>{value}</h1>"
        + (f"<p style='color:{primary_color}; margin:0;'>{delta}</p>" if delta else "") +
        "</div>", unsafe_allow_html=True
    )

def show_chart(fig, chart_type, key=None):
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.caption(f"Type de graphique : {chart_type}")

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
    code_map = {1: "Complétés", 2: "Abandonnés", 0: "Interrompus"}
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
    show_chart(fig, "Camembert")
# ───────────────────────────────────────────────────────────────────────────────
# 4) PAGE “Dashboard”
# ───────────────────────────────────────────────────────────────────────────────
else:
    # — Titre et intro —
    st.markdown(
        f"<h1 style='color:{primary_color}; text-align:center;'>📈 Dashboard Final</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:gray;'>Suivi des indicateurs clés</p>",
        unsafe_allow_html=True
    )
    st.markdown("---")

    # --- Chargement & filtres ---
    @st.cache_data
    def load_data_dashboard():
        base = Path(__file__).resolve().parent.parent
        path = base / "Donnee" / "1_raw" / "AMV_GDT_P3M.csv"
        return pd.read_csv(
            path,
            sep=";",
            encoding="latin-1",
            parse_dates=["Datedeladernièreconnexion"]
        )

    df = load_data_dashboard()
    
    # ───────────────────────────────────────────────────────────────────────────
    # Filtres TYPEPC / TYPEPC2 (uniquement ici, dans Dashboard)
    # ───────────────────────────────────────────────────────────────────────────
    typepc_vals = ["Tous"] + sorted(df["TYPEPC"].dropna().unique().tolist())
    sel_typepc  = st.sidebar.selectbox("TYPEPC", typepc_vals)
    if sel_typepc != "Tous":
        df = df[df["TYPEPC"] == sel_typepc]

    
    start_date = st.sidebar.date_input(
        "Date de début", df["Datedeladernièreconnexion"].min()
    )
    end_date   = st.sidebar.date_input(
        "Date de fin",   df["Datedeladernièreconnexion"].max()
    )
    dispo      = st.sidebar.multiselect(
        "Disposition", [0, 1, 2], default=[1]
    )

    df = df[
        (df["Datedeladernièreconnexion"] >= pd.to_datetime(start_date)) &
        (df["Datedeladernièreconnexion"] <= pd.to_datetime(end_date)) &
        (df["Codededisposition"].isin(dispo))
    ]

    # — Calculs sur complétés —
    df_comp  = df[df["Codededisposition"] == 1]
    q1_vals  = pd.to_numeric(df_comp["Q1"],  errors="coerce").dropna()
    nps_vals = pd.to_numeric(df_comp["Q16"], errors="coerce").dropna().astype(int)

    # Q1
    mean_q1 = q1_vals.mean() if not q1_vals.empty else 0.0

    # NPS
    prom       = nps_vals[nps_vals >= 9].count()
    passiv     = nps_vals.between(7, 8).sum()
    detract    = nps_vals[nps_vals <= 6].count()
    total_nps  = prom + passiv + detract
    pct_prom   = prom / total_nps * 100 if total_nps else 0
    pct_det    = detract / total_nps * 100 if total_nps else 0
    nps_score  = pct_prom - pct_det

    # — INDICATEURS GLOBAUX —
    st.subheader("🔎 INDICATEURS GLOBAUX")
    c1, c2, c3 = st.columns(3, gap="large")
    c1.metric("✔️ Total complétés", f"{len(df_comp)}")
    c2.metric("⭐ Note satisfaction globale",       f"{mean_q1:.2f}/10")
    c3.metric(
        "📊 Score NPS",
        f"{nps_score:.1f}",
        delta=f"{pct_prom:.1f}% – {pct_det:.1f}%"
    )
    st.markdown("---")

    # — Choix du graphique Q1 / NPS —
    choix = st.radio(
        "Sélectionnez la répartition à afficher",
        ("Répartition de la satisfaction globale", "Répartition NPS"),
        horizontal=True
    )

    if choix == "Répartition de la satisfaction globale":
        dist_q1 = (
            q1_vals.value_counts()
                   .sort_index()
                   .pipe(lambda s: (s / s.sum() * 100).round(1))
                   .reset_index(name="pct")
                   .rename(columns={"index": "Q1"})
        )
        fig = px.bar(
            dist_q1,
            x="Q1", y="pct",
            color="pct",
            color_continuous_scale="Viridis",
            labels={"pct": "% répondants"},
            title="Répartition des notes Q1 (%)"
        )
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    else:
        nps_df = pd.DataFrame({
            "Segment":    ["Promoters", "Passives", "Detractors"],
            "Pourcentage": [pct_prom, 100 - (pct_prom + pct_det), pct_det]
        })
        fig = px.bar(
            nps_df,
            x="Segment", y="Pourcentage",
            color="Pourcentage",
            color_continuous_scale="Viridis",
            labels={"Pourcentage": "% répondants"},
            title="Répartition NPS (%)"
        )
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
        fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))

    show_chart(fig, "Barres")

    # ───────────────────────────────────────────────────────────────────────────
    # 5) DISTRIBUTION Q15 (4 catégories)
    # ───────────────────────────────────────────────────────────────────────────
    

    # On travaille toujours sur les complétés
    q15 = df_comp["Q15"].dropna().astype(str).str.strip().str.lower()

    # 1) Masques
    mask_tres_simples = q15.str.contains("très simple", na=False)
    mask_simples      = q15.str.contains("simple", na=False) & ~mask_tres_simples
    mask_tres_comp    = q15.str.contains("très compliqu", na=False)
    mask_compliques   = q15.str.contains("compliqu", na=False) & ~mask_tres_comp

    # 2) Comptages
    n_tres_simples = int(mask_tres_simples.sum())
    n_simples      = int(mask_simples.sum())
    n_tres_comp    = int(mask_tres_comp.sum())
    n_compliques   = int(mask_compliques.sum())
    total15        = n_tres_simples + n_simples + n_tres_comp + n_compliques

    # 3) Pourcentages
    pct_tres_s = round(n_tres_simples / total15 * 100, 1) if total15 else 0.0
    pct_s      = round(n_simples      / total15 * 100, 1) if total15 else 0.0
    pct_tres_c = round(n_tres_comp    / total15 * 100, 1) if total15 else 0.0
    pct_c      = round(n_compliques   / total15 * 100, 1) if total15 else 0.0

    # ───────────────────────────────────────────────────────────────────────────
    # KPI AGGLOMÉRÉS Q15
    # ───────────────────────────────────────────────────────────────────────────
    total_simples     = n_tres_simples + n_simples
    total_compliquees = n_tres_comp   + n_compliques

    pct_simples     = round(total_simples     / total15 * 100, 1) if total15 else 0.0
    pct_compliquees = round(total_compliquees / total15 * 100, 1) if total15 else 0.0

    k1, k2 = st.columns(2, gap="large")
    k1.metric(
        label="✅ TOTAL SIMPLES",
        value=f"{pct_simples:.1f} %",
        delta=f"{total_simples} réponses"
    )
    k2.metric(
        label="🔧 TOTAL COMPLIQUÉES",
        value=f"{pct_compliquees:.1f} %",
        delta=f"{total_compliquees} réponses"
    )

    st.markdown("---")

        # 6) Bar chart Q15
    df_q15 = pd.DataFrame({
        "Catégorie":   ["Très simples", "Simples", "Très compliquées", "Compliquées"],
        "Pourcentage": [pct_tres_s, pct_s, pct_tres_c, pct_c]
    })
    fig_q15 = px.bar(
        df_q15,
        x="Catégorie",
        y="Pourcentage",
        text="Pourcentage",
        color="Catégorie",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"Pourcentage": "% répondants"},
        title="Q15. Comment qualifiez-vous les démarches nécessaires à la gestion de votre sinistre ?"  # le sous-titre est déjà en st.subheader
    )
    fig_q15.update_traces(texttemplate="%{text:.1f} %", textposition="outside")
    fig_q15.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis=dict(range=[0, 100], showgrid=False),
        legend=dict(
            orientation="v",
            xanchor="right",
            x=1,
            yanchor="top",
            y=1
        ),
        coloraxis_showscale=False
    )
    show_chart(fig_q15, "Barres")
         # ───────────────────────────────────────────────────────────
    # 6) Q3 – Souscription du contrat (version accent-insensible)
    # ───────────────────────────────────────────────────────────
    import unicodedata

    st.subheader("🔑 Souscription du contrat")

    # on travaille toujours sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # 1) Nettoyage : on normalise (supprime accents), on enlève apostrophes, on met en minuscule
    q3_raw = df_comp["Q3"].astype(str).fillna("")
    q3 = (
        q3_raw
        .apply(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
        .str.replace("'", "", regex=False)
        .str.replace("’", "", regex=False)
        .str.lower()
        .str.strip()
    )

    # 2) Masques exacts / contains
    mask_tres_compl = q3.str.contains(r"\btres completes\b", regex=True)
    mask_suffis     = q3.str.contains(r"\bsuffisantes\b",    regex=True)
    mask_insuff     = q3.str.contains(r"\binsuffisantes\b",  regex=True)
    mask_nil        = q3.str.contains(r"je nai pas eu dinformations sur ces sujets", regex=True)

    # 3) Comptages
    n_tres_compl = int(mask_tres_compl.sum())
    n_suffis     = int(mask_suffis.sum())
    n_insuff     = int(mask_insuff.sum())
    n_nil        = int(mask_nil.sum())

    # 4) Totaux agglomérés
    total_suff_compl = n_tres_compl + n_suffis
    total_insuff_nil = n_insuff + n_nil
    total_q3        = total_suff_compl + total_insuff_nil

    # 5) Calcul des pourcentages
    pct_suff_compl = (total_suff_compl / total_q3 * 100) if total_q3 else 0.0
    pct_insuff_nil = (total_insuff_nil / total_q3 * 100) if total_q3 else 0.0

    # 6) KPI agglomérés avec pourcentage
    c1, c2 = st.columns(2, gap="large")
    c1.metric(
        "✅ TOTAL Suffisantes + complétées",
        f"{total_suff_compl} réponses",
        delta=f"{pct_suff_compl:.1f}%"
    )
    c2.metric(
        "⚠️ TOTAL Insuffisantes + Nul",
        f"{total_insuff_nil} réponses",
        delta=f"{pct_insuff_nil:.1f}%"
    )

    st.markdown("---")

    # 7) Distribution détaillée Q3 (%)
    dist_q3 = pd.DataFrame({
        "Catégorie": ["Très complètes", "Suffisantes", "Insuffisantes", "Nul"],
        "Count":     [n_tres_compl,    n_suffis,      n_insuff,      n_nil]
    })
    dist_q3["pct"] = (dist_q3["Count"] / dist_q3["Count"].sum() * 100).round(1)

    fig_q3 = px.bar(
        dist_q3,
        x="Catégorie",
        y="Count",
        text="pct",
        labels={"Count":"Nombre de réponses", "pct":"% répondants"},
        title="Q3. Comment qualifiez-vous les explications données par le vendeur sur Assurance Mobile (%)",
        color="Catégorie",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_q3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_q3.update_layout(
        margin=dict(t=40, b=20, l=20, r=20),
        yaxis=dict(showgrid=False),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1)
    )
    show_chart(fig_q3, "Barres")
     # ───────────────────────────────────────────────────────────
    # 7) Q4 – Distribution de la question Q4
    # ───────────────────────────────────────────────────────────

    # (Re)définition de df_comp : on ne fait que les complétés
    df_comp = df[df["Codededisposition"] == 1]

    

    # Construire le DataFrame de comptages
    df_q4 = (
        df_comp["Q4"]
        .fillna("Sans réponse")
        .astype(str)
        .str.strip()
        .value_counts()
        .reset_index()
    )
    df_q4.columns = ["Réponse", "Count"]
    df_q4["Percentage"] = (df_q4["Count"] / df_q4["Count"].sum() * 100).round(1)

    # Afficher le graphique
    fig_q4 = px.bar(
        df_q4,
        x="Réponse",
        y="Count",
        text="Percentage",
        labels={"Count": "Nombre de réponses", "Réponse": "Réponse Q4"},
        title="Q4. Suite à votre souscription, avez-vous bien reçu tous les documents contractuels ?"
    )
    fig_q4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_q4.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis_title="Nombre de réponses",
        xaxis_title="Réponse",
        showlegend=False
    )

    # clé unique pour éviter les duplications
    show_chart(fig_q4, "Barres", key="dist_q4_final")
    
    # ───────────────────────────────────────────────────────────
    # 8) Q6 – Déclaration du sinistre
    # ───────────────────────────────────────────────────────────
    st.subheader("📝 Déclaration du sinistre")

    # on reste sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # nettoyage basique
    q6 = (
        df_comp["Q6"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # comptage des 3 modalités
    n_boutique = int(q6.str.contains("boutique orange", na=False).sum())
    n_service  = int(q6.str.contains("service client orange", na=False).sum())
    n_direct   = int(q6.str.contains("contact.*assurance mobile", na=False).sum())

    # KPI agrégés – TOTAL Orange (boutique + service)
    total_orange = n_boutique + n_service
    total_q6     = n_boutique + n_service + n_direct
    pct_orange   = round(total_orange / total_q6 * 100, 1) if total_q6 else 0.0

    # Affichage des KPI : pourcentage en grand, effectif en petit
    k1, k2 = st.columns(2, gap="large")
    k1.metric(
        label="🔧 TOTAL Orange",
        value=f"{pct_orange:.1f} %",
        delta=f"{total_orange} réponses"
    )
    k2.write("")  # placeholder pour garder la colonne vide

    st.markdown("---")

    # camembert Q6
    dist_q6 = pd.DataFrame({
        "Catégorie": [
            "En boutique Orange",
            "Service client Orange",
            "Contact Assurance Mobile"
        ],
        "Count": [n_boutique, n_service, n_direct]
    })
    dist_q6["Pourcentage"] = (dist_q6["Count"] / total_q6 * 100).round(1)

    fig_q6 = px.pie(
        dist_q6,
        names="Catégorie",
        values="Count",
        hole=0.3,
        title="Q6. A qui vous êtes-vous adressé en premier pour déclarer votre sinistre ?"
    )
    fig_q6.update_traces(textinfo="label+percent", textposition="outside")
    fig_q6.update_layout(
        margin=dict(t=40, b=20, l=20, r=20),
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1)
    )
    show_chart(fig_q6, "Camembert", key="chart_q6")
        # ───────────────────────────────────────────────────────────
    # 9) Q5 – Distribution en barres (modalités raccourcies)
    # ───────────────────────────────────────────────────────────
    
    # on reste sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # on nettoie et passe tout en minuscules
    q5 = (
        df_comp["Q5"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # 1) Masques basés sur des sous-chaînes clés
    mask_parfaite   = q5.str.contains("connaissais parfaitement", na=False)
    mask_partielle  = q5.str.contains("connaissance partielle",  na=False)
    mask_interesse  = q5.str.contains("intéressé",               na=False)
    mask_ignorance  = q5.str.contains("ne connaissais pas",      na=False) | \
                      q5.str.contains("ignorais pas",         na=False)

    # 2) Comptages
    n_parfaite   = int(mask_parfaite.sum())
    n_partielle  = int(mask_partielle.sum())
    n_interesse  = int(mask_interesse.sum())
    n_ignorance  = int(mask_ignorance.sum())
    total_q5     = n_parfaite + n_partielle + n_interesse + n_ignorance

    # 3) Pourcentages
    pct_parfaite   = round(n_parfaite  / total_q5 * 100, 1) if total_q5 else 0.0
    pct_partielle  = round(n_partielle / total_q5 * 100, 1) if total_q5 else 0.0
    pct_interesse  = round(n_interesse / total_q5 * 100, 1) if total_q5 else 0.0
    pct_ignorance  = round(n_ignorance / total_q5 * 100, 1) if total_q5 else 0.0

    # 4) DataFrame pour le tracé
    dist_q5 = pd.DataFrame({
        "Modalité": ["Parfaite", "Partielle", "Intéressé·e", "Ignorance"],
        "pct":       [pct_parfaite, pct_partielle, pct_interesse, pct_ignorance]
    })

    # 5) Bar chart
    fig_q5 = px.bar(
        dist_q5,
        x="Modalité",
        y="pct",
        text="pct",
        color="Modalité",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"pct": "% répondants"},
        title="Q5. Quel était votre niveau de connaissance des conditions de garantie au moment de la déclaration de votre sinistre ?"
    )
    fig_q5.update_traces(texttemplate="%{text:.1f} %", textposition="outside")
    fig_q5.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1
        ),
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis=dict(
            title="% répondants",
            range=[0, dist_q5["pct"].max() * 1.1],
            showgrid=False
        )
    )
    show_chart(fig_q5, "Barres", key="bar_q5")
    
        # ───────────────────────────────────────────────────────────
    # 10) Q7 – Distribution en barres (2 modalités)
    # ───────────────────────────────────────────────────────────
    

    # on reste sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # nettoyage & passage en minuscules
    q7 = (
        df_comp["Q7"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # 1) Masques pour chaque modalité
    mask_oui = q7.str.contains(r"\boui\b", na=False)
    mask_non = q7.str.contains(r"\bnon\b", na=False)

    # 2) Comptages
    n_oui = int(mask_oui.sum())
    n_non = int(mask_non.sum())
    total_q7 = n_oui + n_non

    # 3) Pourcentages
    pct_oui = round(n_oui / total_q7 * 100, 1) if total_q7 else 0.0
    pct_non = round(n_non / total_q7 * 100, 1) if total_q7 else 0.0

    # 4) DataFrame pour le tracé
    dist_q7 = pd.DataFrame({
        "Modalité": ["Oui", "Non"],
        "pct":       [pct_oui, pct_non]
    })

    # 5) Bar chart
    fig_q7 = px.bar(
        dist_q7,
        x="Modalité",
        y="pct",
        text="pct",
        color="Modalité",
        color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"pct": "% répondants"},
        title="Q7. Les informations reçues lors de ce premier contact étaient-elles cohérentes avec celles communiquées ensuite par Assurance Mobile ?"
    )
    fig_q7.update_traces(texttemplate="%{text:.1f} %", textposition="outside")
    fig_q7.update_layout(
        showlegend=True,
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="right",
            x=1
        ),
        margin=dict(t=20, b=20, l=20, r=20),
        yaxis=dict(
            title="% répondants",
            range=[0, dist_q7["pct"].max() * 1.1],
            showgrid=False
        )
    )

    show_chart(fig_q7, "Barres", key="bar_q7")
    
        # ───────────────────────────────────────────────────────────
    # 10) Suivi du dossier & Délai (Q8 & Q13)
    # ───────────────────────────────────────────────────────────
    st.subheader("🕒 Suivi du dossier & Délai")

    # on reste sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # --- Q8 ---
    q8 = (
        df_comp["Q8"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
    dist_q8 = (
        q8
        .value_counts(dropna=False)
        .rename_axis("Modalité")
        .reset_index(name="count")
    )
    total_q8 = dist_q8["count"].sum()
    dist_q8["pct"] = (dist_q8["count"] / total_q8 * 100).round(1)

    fig_q8 = px.pie(
        dist_q8,
        names="Modalité",
        values="count",
        hole=0.3,
        title="Q8 – Satisfaction du delai global"
    )
    fig_q8.update_traces(textinfo="label+percent", textposition="outside")
    fig_q8.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=20, r=20)
    )

    # --- Q13 ---
    q13 = (
        df_comp["Q13"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
    dist_q13 = (
        q13
        .value_counts(dropna=False)
        .rename_axis("Modalité")
        .reset_index(name="count")
    )
    total_q13 = dist_q13["count"].sum()
    dist_q13["pct"] = (dist_q13["count"] / total_q13 * 100).round(1)

    fig_q13 = px.pie(
        dist_q13,
        names="Modalité",
        values="count",
        hole=0.3,
        title="Q13 – Suivi du dossier"
    )
    fig_q13.update_traces(textinfo="label+percent", textposition="outside")
    fig_q13.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=20, r=20)
    )

    # ───────────────────────────────────────────────────────────
    # Affichage côte à côte
    # ───────────────────────────────────────────────────────────
    col1, col2 = st.columns(2, gap="large")
    with col1:
        show_chart(fig_q8, "Camembert", key="chart_q8")
    with col2:
        show_chart(fig_q13, "Camembert", key="chart_q13")
        
        # ───────────────────────────────────────────────────────────
    # 11) Réception du téléphone (Q9 & Q11)
    # ───────────────────────────────────────────────────────────
    st.subheader("📱 Réception du téléphone")

    # on reste sur les complétés
    df_comp = df[df["Codededisposition"] == 1]

    # --- Q9 ---
    q9 = (
        df_comp["Q9"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
    dist_q9 = (
        q9
        .value_counts(dropna=False)
        .rename_axis("Modalité")
        .reset_index(name="count")
    )
    total_q9 = dist_q9["count"].sum()
    dist_q9["pct"] = (dist_q9["count"] / total_q9 * 100).round(1)

    fig_q9 = px.pie(
        dist_q9,
        names="Modalité",
        values="count",
        hole=0.3,
        title="Q9 – Etes-vous satisfait(e) de la qualité de la réparation / du mobile de remplacement ?"
    )
    fig_q9.update_traces(textinfo="label+percent", textposition="outside")
    fig_q9.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=20, r=20)
    )

    # --- Q11 ---
    q11 = (
        df_comp["Q11"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
    )
    dist_q11 = (
        q11
        .value_counts(dropna=False)
        .rename_axis("Modalité")
        .reset_index(name="count")
    )
    total_q11 = dist_q11["count"].sum()
    dist_q11["pct"] = (dist_q11["count"] / total_q11 * 100).round(1)

    fig_q11 = px.pie(
        dist_q11,
        names="Modalité",
        values="count",
        hole=0.3,
        title="Q11 – Réception du téléphone"
    )
    fig_q11.update_traces(textinfo="label+percent", textposition="outside")
    fig_q11.update_layout(
        showlegend=True,
        legend=dict(orientation="v", yanchor="top", y=1, xanchor="right", x=1),
        margin=dict(t=40, b=20, l=20, r=20)
    )

    # afficher côte à côte
    col1, col2 = st.columns(2, gap="large")
    with col1:
        show_chart(fig_q9, "Camembert", key="chart_q9")
    with col2:
        show_chart(fig_q11, "Camembert", key="chart_q11")




