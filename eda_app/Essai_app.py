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
    def render_card(col, icon, title, value, delta=None):
        col.markdown(
            f"<div style='background:{background_card}; padding:20px; "
            f"border-radius:8px; text-align:center;'>"
            f"<h3>{icon} {title}</h3><h1>{value}</h1>"
            + (f"<p style='color:{primary_color}; margin:0;'>{delta}</p>" if delta else "") +
            "</div>", unsafe_allow_html=True
        )

    render_card(k1, "👥", "Total sollicités", total)
    render_card(k2, "✅", "Complétés", f"{pct_c:.1f}%", comp)
    render_card(k3, "⏸️", "Interrompus", f"{pct_i:.1f}%", inter)

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

    # — Style global pour espacer les titres et définir les blocs —
    st.markdown("""
        <style>
            h2 { padding-top: 10px; color: #2F4F4F; }
            .block-header { 
                display: flex; 
                align-items: center; 
                padding-bottom: 10px; 
                border-left: 5px solid #2F4F4F; 
                margin-bottom: 20px; 
            }
            .metric-card { 
                background: #ffffff; 
                padding: 20px; 
                border-radius: 8px; 
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); 
                text-align: center; 
                margin-bottom: 10px; 
            }
            .metric-label { 
                margin: 0; 
                font-weight: 600; 
                color: #555; 
            }
            .metric-value { 
                margin: 5px 0; 
                font-size: 1.5rem; 
                font-weight: 700; 
                color: #333; 
            }
        </style>
    """, unsafe_allow_html=True)

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

    # Filtres TYPEPC
    typepc_vals = ["Tous"] + sorted(df["TYPEPC"].dropna().unique().tolist())
    sel_typepc  = st.sidebar.selectbox("TYPEPC", typepc_vals)
    if sel_typepc != "Tous":
        df = df[df["TYPEPC"] == sel_typepc]

    # Filtres dates et disposition
    start_date = st.sidebar.date_input("Date de début", df["Datedeladernièreconnexion"].min())
    end_date   = st.sidebar.date_input("Date de fin",   df["Datedeladernièreconnexion"].max())
    dispo      = st.sidebar.multiselect("Disposition", [0, 1, 2], default=[1])
    df = df[
        (df["Datedeladernièreconnexion"] >= pd.to_datetime(start_date)) &
        (df["Datedeladernièreconnexion"] <= pd.to_datetime(end_date)) &
        (df["Codededisposition"].isin(dispo))
    ]

    # — Calculs sur complétés —
    df_comp = df[df["Codededisposition"] == 1]

    # 1) Q1 – Note de satisfaction
    q1_vals = pd.to_numeric(df_comp["Q1"], errors="coerce").dropna()
    mean_q1 = q1_vals.mean() if not q1_vals.empty else 0.0

    # 2) NPS
    nps_vals  = pd.to_numeric(df_comp["Q16"], errors="coerce").dropna().astype(int)
    prom       = nps_vals[nps_vals >= 9].count()
    passiv     = nps_vals.between(7, 8).sum()
    detract    = nps_vals[nps_vals <= 6].count()
    total_nps  = prom + passiv + detract
    pct_prom   = prom / total_nps * 100 if total_nps else 0.0
    pct_det    = detract / total_nps * 100 if total_nps else 0.0
    nps_score  = pct_prom - pct_det

    # 3) Choix du graphique Q1 / NPS
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
            dist_q1, x="Q1", y="pct",
            color="pct", color_continuous_scale="Viridis",
            labels={"pct": "% répondants"},
            title="Répartition des notes Q1 (%)"
        )
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    else:
        nps_df = pd.DataFrame({
            "Segment": ["Promoters", "Passives", "Detractors"],
            "Pourcentage": [pct_prom, 100 - (pct_prom + pct_det), pct_det]
        })
        fig = px.bar(
            nps_df, x="Segment", y="Pourcentage",
            color="Pourcentage", color_continuous_scale="Viridis",
            labels={"Pourcentage": "% répondants"},
            title="Répartition NPS (%)"
        )
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")

    # 4) Q15 – Distribution (4 catégories)
    q15 = df_comp["Q15"].dropna().astype(str).str.strip().str.lower()
    mask_ts = q15.str.contains("très simple", na=False)
    mask_s  = q15.str.contains("simple", na=False) & ~mask_ts
    mask_tc = q15.str.contains("très compliqu", na=False)
    mask_c  = q15.str.contains("compliqu", na=False) & ~mask_tc
    n_ts = int(mask_ts.sum()); n_s = int(mask_s.sum())
    n_tc = int(mask_tc.sum()); n_c = int(mask_c.sum())
    total15 = n_ts + n_s + n_tc + n_c
    pct_ts = round(n_ts  / total15 * 100, 1) if total15 else 0.0
    pct_s  = round(n_s   / total15 * 100, 1) if total15 else 0.0
    pct_tc = round(n_tc  / total15 * 100, 1) if total15 else 0.0
    pct_c  = round(n_c   / total15 * 100, 1) if total15 else 0.0
    df_q15 = pd.DataFrame({
        "Catégorie":   ["Très simples", "Simples", "Très compliquées", "Compliquées"],
        "Pourcentage": [pct_ts, pct_s, pct_tc, pct_c]
    })
    fig_q15 = px.bar(
        df_q15, x="Catégorie", y="Pourcentage", text="Pourcentage",
        color="Catégorie", color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"Pourcentage": "% répondants"},
        title="Q15. Comment qualifiez-vous les démarches nécessaires à la gestion de votre sinistre ?"
    )
    fig_q15.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    # 5) Q3 – Souscription du contrat
    q3_raw = df_comp["Q3"].astype(str).fillna("")
    q3 = (
        q3_raw
        .apply(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
        .str.replace("'", "", regex=False)
        .str.replace("’", "", regex=False)
        .str.lower().str.strip()
    )
    mask_tc3 = q3.str.contains(r"\btres completes\b", regex=True)
    mask_s3  = q3.str.contains(r"\bsuffisantes\b",    regex=True)
    mask_i3  = q3.str.contains(r"\binsuffisantes\b",  regex=True)
    mask_n3  = q3.str.contains(r"je nai pas eu dinformations sur ces sujets", regex=True)
    n_tc3 = int(mask_tc3.sum()); n_s3 = int(mask_s3.sum())
    n_i3  = int(mask_i3.sum()); n_n3 = int(mask_n3.sum())
    total_q3 = n_tc3 + n_s3 + n_i3 + n_n3
    total_suff_compl = n_tc3 + n_s3
    total_insuff_nil = n_i3  + n_n3
    pct_suff_compl   = (total_suff_compl / total_q3 * 100) if total_q3 else 0.0
    pct_insuff_nil   = (total_insuff_nil / total_q3 * 100) if total_q3 else 0.0
    dist_q3 = pd.DataFrame({
        "Catégorie": ["Très complètes", "Suffisantes", "Insuffisantes", "Nul"],
        "Count":     [n_tc3,        n_s3,         n_i3,        n_n3]
    })
    dist_q3["pct"] = (dist_q3["Count"] / dist_q3["Count"].sum() * 100).round(1)
    fig_q3 = px.bar(
        dist_q3, x="Catégorie", y="Count", text="pct",
        labels={"Count": "Nombre de réponses", "pct": "% répondants"},
        title="Q3. Comment qualifiez-vous les explications données par le vendeur sur Assurance Mobile (%)",
        color="Catégorie", color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_q3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

    # 6) Q6 – Déclaration du sinistre
    q6 = df_comp["Q6"].fillna("").astype(str).str.strip().str.lower()
    n_boutique = int(q6.str.contains("boutique orange",        na=False).sum())
    n_service  = int(q6.str.contains("service client orange",  na=False).sum())
    n_direct   = int(q6.str.contains("contact.*assurance mobile", na=False).sum())
    total_orange = n_boutique + n_service
    total_q6     = total_orange + n_direct
    pct_orange   = round(total_orange / total_q6 * 100, 1) if total_q6 else 0.0
    dist_q6 = pd.DataFrame({
        "Catégorie": ["En boutique Orange", "Service client Orange", "Contact Assurance Mobile"],
        "Count":      [n_boutique,           n_service,                n_direct]
    })
    dist_q6["Pourcentage"] = (dist_q6["Count"] / total_q6 * 100).round(1)
    fig_q6 = px.pie(
        dist_q6, names="Catégorie", values="Count", hole=0.3,
        title="Q6. A qui vous êtes-vous adressé en premier pour déclarer votre sinistre ?"
    )
    fig_q6.update_traces(textinfo="label+percent", textposition="outside")

    # 7) Q5 – Connaissance des conditions
    q5 = df_comp["Q5"].fillna("").astype(str).str.strip().str.lower()
    mask_p  = q5.str.contains("connaissais parfaitement", na=False)
    mask_pa = q5.str.contains("connaissance partielle",  na=False)
    mask_i5 = q5.str.contains("intéressé",               na=False)
    mask_ig = q5.str.contains("ne connaissais pas",      na=False) | q5.str.contains("ignorais pas", na=False)
    n_p  = int(mask_p.sum());  n_pa = int(mask_pa.sum())
    n_i5 = int(mask_i5.sum()); n_ig = int(mask_ig.sum())
    total_q5 = n_p + n_pa + n_i5 + n_ig
    pct_p  = round(n_p  / total_q5 * 100, 1) if total_q5 else 0.0
    pct_pa = round(n_pa / total_q5 * 100, 1) if total_q5 else 0.0
    pct_i5 = round(n_i5 / total_q5 * 100, 1) if total_q5 else 0.0
    pct_ig = round(n_ig / total_q5 * 100, 1) if total_q5 else 0.0
    dist_q5 = pd.DataFrame({
        "Modalité": ["Parfaite", "Partielle", "Intéressé·e", "Ignorance"],
        "pct":       [pct_p, pct_pa, pct_i5, pct_ig]
    })
    fig_q5 = px.bar(
        dist_q5, x="Modalité", y="pct", text="pct",
        color="Modalité", color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"pct": "% répondants"},
        title="Q5. Quel était votre niveau de connaissance des conditions de garantie au moment de la déclaration de votre sinistre ?"
    )
    fig_q5.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    # 8) Q7 – Cohérence des informations
    q7 = df_comp["Q7"].fillna("").astype(str).str.strip().str.lower()
    mask_oui = q7.str.contains(r"\boui\b", na=False)
    mask_non = q7.str.contains(r"\bnon\b", na=False)
    n_oui = int(mask_oui.sum()); n_non = int(mask_non.sum())
    total_q7 = n_oui + n_non
    pct_oui = round(n_oui / total_q7 * 100, 1) if total_q7 else 0.0
    pct_non = round(n_non / total_q7 * 100, 1) if total_q7 else 0.0
    dist_q7 = pd.DataFrame({
        "Modalité": ["Oui", "Non"],
        "pct":      [pct_oui, pct_non]
    })
    fig_q7 = px.bar(
        dist_q7, x="Modalité", y="pct", text="pct",
        color="Modalité", color_discrete_sequence=px.colors.qualitative.Pastel,
        labels={"pct": "% répondants"},
        title="Q7. Les informations reçues lors de ce premier contact étaient-elles cohérentes avec celles communiquées ensuite par Assurance Mobile ?"
    )
    fig_q7.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    # 9) Q8 & Q13 – Suivi & délai
    q8 = df_comp["Q8"].fillna("").astype(str).str.strip().str.lower()
    dist_q8 = (
        q8.value_counts(dropna=False)
          .rename_axis("Modalité")
          .reset_index(name="count")
    )
    dist_q8["pct"] = (dist_q8["count"] / dist_q8["count"].sum() * 100).round(1)
    fig_q8 = px.pie(
        dist_q8, names="Modalité", values="count", hole=0.3,
        title="Q8 – Satisfaction du délai global"
    )
    fig_q8.update_traces(textinfo="label+percent", textposition="outside")

    q13 = df_comp["Q13"].fillna("").astype(str).str.strip().str.lower()
    dist_q13 = (
        q13.value_counts(dropna=False)
           .rename_axis("Modalité")
           .reset_index(name="count")
    )
    dist_q13["pct"] = (dist_q13["count"] / dist_q13["count"].sum() * 100).round(1)
    fig_q13 = px.pie(
        dist_q13, names="Modalité", values="count", hole=0.3,
        title="Q13 – Suivi du dossier"
    )
    fig_q13.update_traces(textinfo="label+percent", textposition="outside")

    # 10) Q9 & Q11 – Réception du téléphone
    q9 = df_comp["Q9"].fillna("").astype(str).str.strip().str.lower()
    dist_q9 = (
        q9.value_counts(dropna=False)
          .rename_axis("Modalité")
          .reset_index(name="count")
    )
    dist_q9["pct"] = (dist_q9["count"] / dist_q9["count"].sum() * 100).round(1)
    fig_q9 = px.pie(
        dist_q9, names="Modalité", values="count", hole=0.3,
        title="Q9 – Etes-vous satisfait(e) de la qualité de la réparation / du mobile de remplacement ?"
    )
    fig_q9.update_traces(textinfo="label+percent", textposition="outside")

    q11 = df_comp["Q11"].fillna("").astype(str).str.strip().str.lower()
    dist_q11 = (
        q11.value_counts(dropna=False)
           .rename_axis("Modalité")
           .reset_index(name="count")
    )
    dist_q11["pct"] = (dist_q11["count"] / dist_q11["count"].sum() * 100).round(1)
    fig_q11 = px.pie(
        dist_q11, names="Modalité", values="count", hole=0.3,
        title="Q11 – Réception du téléphone"
    )
    fig_q11.update_traces(textinfo="label+percent", textposition="outside")

    # ──────────────── AFFICHAGE STYLÉ ────────────────

    # 1. INDICATEURS GLOBAUX
    with st.container():
        st.markdown(
            "<div style='background-color: #F7F9FA; padding: 30px; "
            "border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-header'><h2>🔎 INDICATEURS GLOBAUX</h2></div>", unsafe_allow_html=True)

        cols = st.columns(3, gap='large')
        metrics = [
            {'label': '✔️ Total complétés', 'value': len(df_comp)},
            {'label': '⭐ Note moyenne Q1',    'value': f"{mean_q1:.2f}/10"},
            {'label': '📊 Score NPS',         'value': f"{nps_score:.1f}"}
        ]
        for col, m in zip(cols, metrics):
            with col:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<p class='metric-label'>{m['label']}</p>"
                    f"<p class='metric-value'>{m['value']}</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )

        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig_q15, use_container_width=True)

        subtots = st.columns(2, gap='large')
        subtots[0].markdown(
            f"<div class='metric-card'>"
            f"<p class='metric-label'>✅ TOTAL SIMPLES</p>"
            f"<p class='metric-value'>{(pct_ts + pct_s):.1f}%</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        subtots[1].markdown(
            f"<div class='metric-card'>"
            f"<p class='metric-label'>🔧 TOTAL COMPLIQUÉES</p>"
            f"<p class='metric-value'>{(pct_tc + pct_c):.1f}%</p>"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("</div>", unsafe_allow_html=True)

    # 2. SOUSCRIPTION DU CONTRAT
    with st.container():
        st.markdown(
            "<div style='background-color: #FCFCFC; padding: 30px; "
            "border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-header'><h2>🔑 Souscription du contrat</h2></div>", unsafe_allow_html=True)

        st.plotly_chart(fig_q3, use_container_width=True)
        c1, c2 = st.columns(2, gap='large')
        for col, (label, count, pct) in zip([c1, c2], [
            ('✅ Suffisantes + complétées', total_suff_compl, pct_suff_compl),
            ('⚠️ Insuffisantes + Nul',     total_insuff_nil, pct_insuff_nil)
        ]):
            with col:
                st.markdown(
                    f"<div class='metric-card'>"
                    f"<p class='metric-label'>{label}</p>"
                    f"<p class='metric-value'>{count} ({pct:.1f}%)</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        st.markdown("</div>", unsafe_allow_html=True)

    # 3. DÉCLARATION DU SINISTRE
    with st.container():
        st.markdown(
            "<div style='background-color:#F1F7ED;padding:30px;border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,0.05); margin-bottom:40px;'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-header'><h2>📝 Déclaration du sinistre</h2></div>", unsafe_allow_html=True)

        st.plotly_chart(fig_q6, use_container_width=True)
        st.markdown(
            f"<div class='metric-card' style='margin-top:20px;'><p class='metric-label'>🔧 TOTAL Orange</p>"
            f"<p class='metric-value'>{pct_orange:.1f}% ({total_orange})</p></div>",
            unsafe_allow_html=True
        )

        # Affichage séquentiel Q5 puis Q7
        st.plotly_chart(fig_q5, use_container_width=True)
        st.plotly_chart(fig_q7, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)
        
    # 4. SUIVI DU DOSSIER & DÉLAI
    with st.container():
        st.markdown(
            "<div style='background-color: #FAF3F0; padding: 30px; "
            "border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-header'><h2>🕒 Suivi du dossier & Délai</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.plotly_chart(fig_q8, use_container_width=True)
        with col2:
            st.plotly_chart(fig_q13, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # 5. RÉCEPTION DU TÉLÉPHONE
    with st.container():
        st.markdown(
            "<div style='background-color: #F7F9FA; padding: 30px; "
            "border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>",
            unsafe_allow_html=True
        )
        st.markdown("<div class='block-header'><h2>📱 Réception du téléphone</h2></div>", unsafe_allow_html=True)

        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.plotly_chart(fig_q9, use_container_width=True)
        with col2:
            st.plotly_chart(fig_q11, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
