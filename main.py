# main.py  (déployable sur Streamlit Cloud)

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from streamlit_option_menu import option_menu
import numpy as np
import unicodedata

# ───────────────────────────────────────────────────────────────────────────────
# 0) CONFIG
# ───────────────────────────────────────────────────────────────────────────────
st.set_page_config(page_title="Assurance Mobile – Mémoire", layout="wide", initial_sidebar_state="expanded")
primary_color   = "#E63947"
background_card = "#F8F9FA"

# Dossier racine du projet (où se trouve ce fichier)
ROOT = Path(__file__).resolve().parent

# Chemins relatifs des assets (⚠️ respect de la casse des noms de fichiers)
CSV_PATH  = ROOT / "Donnee" / "1_raw" / "AMV_GDT_P3M.csv"
LOGO_ORANGE = ROOT / "Assurance mobile orange.PNG"      # mets exactement le même nom que dans le repo
LOGO_UNIV   = ROOT / "Logo PARIS 1.PNG"

DATE_COL = "Datedeladernièreconnexion"  # nom de colonne dans le CSV

@st.cache_data(show_spinner=False)
def load_csv(path: Path) -> pd.DataFrame:
    """Lecture CSV robuste pour le cloud."""
    if not path.exists():
        st.error(f"Fichier introuvable : `{path.relative_to(ROOT)}`")
        st.stop()
    errors = []
    for enc in ("latin-1", "utf-8-sig", "cp1252"):
        try:
            df = pd.read_csv(path, sep=";", encoding=enc, parse_dates=[DATE_COL])
            return df
        except Exception as e:
            errors.append(f"{enc}: {e}")
    st.error("Impossible de lire le CSV. Tentatives:\n\n" + "\n".join(errors))
    st.stop()

# ───────────────────────────────────────────────────────────────────────────────
# 1) MENU LATÉRAL
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
            "nav-link-selected": {"background-color": primary_color, "color": "white"},
        },
    )

# ───────────────────────────────────────────────────────────────────────────────
# 2) PAGE “Projet mémoire”
# ───────────────────────────────────────────────────────────────────────────────
if selection == "Projet mémoire":
    styles = f"""
    <style>
      :root {{ --primary: {primary_color}; }}
      .app-title h1 {{ color: var(--primary); margin-bottom:.25rem; }}
      .subtitle {{ font-size:.95rem; color:#6b7280; margin-bottom:1.25rem; }}
      .card {{ background:#fff; border-radius:14px; padding:20px;
              box-shadow:0 6px 24px rgba(0,0,0,.06),0 2px 8px rgba(0,0,0,.04);
              border:1px solid #eef2f7; }}
      .section-title {{ margin:0 0 10px; font-size:1.15rem; color:#111827; }}
      .lead {{ font-size:.98rem; line-height:1.6; color:#1f2937; margin:0; }}
      .badge,.hero-tag {{ display:inline-flex; align-items:center; gap:8px;
              padding:6px 10px; border-radius:999px; font-size:.85rem;
              background:#f9fafb; border:1px solid #e5e7eb; }}
      .badge .dot {{ width:8px; height:8px; border-radius:50%; background:var(--primary); }}
      .checklist {{ list-style:none; padding:0; margin:0; }}
      .checklist li {{ padding:10px; margin:6px 0; border:1px dashed #e5e7eb;
                      border-radius:10px; background:#fcfcfd; display:flex; gap:10px; }}
      .checkmark {{ color:var(--primary); font-weight:700; }}
      .pill {{ padding:4px 10px; border-radius:999px; background:rgba(255,121,0,.08);
              color:var(--primary); border:1px solid rgba(255,121,0,.25); font-size:.85rem; }}
      .hero {{ border-radius:16px; padding:22px;
              background:linear-gradient(135deg,rgba(255,121,0,.12),rgba(255,121,0,.04));
              border:1px solid rgba(255,121,0,.25); margin-top:6px; position:relative; }}
      .hero-title {{ font-weight:700; display:flex; gap:8px; margin-bottom:8px; }}
      .hero-title .icon {{ width:28px; height:28px; border-radius:8px;
                          background:var(--primary); color:#fff; display:flex;
                          align-items:center; justify-content:center; }}
      .hero-list {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:12px; }}
      .hero-item {{ border:1px dashed #e5e7eb; border-radius:12px; padding:10px;
                   font-size:.92rem; display:flex; gap:10px; }}
      .hero-bullet {{ color:var(--primary); font-weight:700; }}
      @media(max-width:900px){{ .hero-list{{ grid-template-columns:1fr; }} }}
    </style>
    """
    st.markdown(styles, unsafe_allow_html=True)

    col_title, col_logo1, col_logo2 = st.columns([1.2, 1, 1])
    with col_title:
        st.markdown("<div class='app-title'><h1>📚 Projet mémoire</h1></div>", unsafe_allow_html=True)
        st.markdown("<p class='subtitle'>Suivi mensuel des enquêtes de satisfaction – Assurance mobile Orange</p>", unsafe_allow_html=True)

    for col, path, caption in zip(
        (col_logo1, col_logo2),
        (LOGO_ORANGE, LOGO_UNIV),
        ("Assurance mobile Orange", "Université Paris 1"),
    ):
        with col:
            if path.exists():
                st.image(str(path), caption=caption, use_container_width=True)
            else:
                st.caption(f"🔎 Logo {caption} introuvable : `{path.name}`")

    st.write("")

    c1, c2 = st.columns((1.4, 1))
    with c1:
        st.markdown("""
        <div class="card">
          <h3 class="section-title">Contexte</h3>
          <p class="lead">
            Dans le cadre du suivi de la qualité de service, une enquête de satisfaction est conduite mensuellement auprès des clients d’Orange ayant souscrit à une assurance mobile et ayant sollicité une prise en charge, que ce soit pour une réparation ou un remplacement de leur appareil.
          </p>
          <p class="lead" style="margin-top:12px;">
            Ce dispositif vise à évaluer de manière régulière le niveau de satisfaction des clients et à suivre l’évolution des principaux indicateurs de performance. Les résultats sont transmis au client chaque mois afin de disposer d’une vision claire et actualisée de la qualité perçue et d’orienter, le cas échéant, les actions d’amélioration.
          </p>
          <p class="lead" style="margin-top:12px;">
            Le présent dashboard a pour finalité d’automatiser ce processus de suivi, de centraliser les données collectées et de mettre à disposition une visualisation synthétique et dynamique des indicateurs clés.
          </p>
          <div class="badges" style="margin-top:14px;">
            <span class="badge"><span class="dot"></span> Suivi mensuel</span>
            <span class="badge"><span class="dot"></span> Satisfaction client</span>
            <span class="badge"><span class="dot"></span> Indicateurs de performance</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="card">
          <h3 class="section-title">Objectifs</h3>
          <ul class="checklist">
            <li><span class="checkmark">✓</span> Charger, nettoyer et préparer les données.</li>
            <li><span class="checkmark">✓</span> Explorer les réponses (EDA).</li>
            <li><span class="checkmark">✓</span> Mettre en place un suivi mensuel interactif.</li>
            <li><span class="checkmark">✓</span> Développer un dashboard final.</li>
          </ul>
          <p class="hint" style="margin-top:10px;">
            Astuce : utilisez les filtres ci-dessus pour limiter l’analyse par période, canal ou motif (réparation/remplacement).
          </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero">
      <div class="hero-title"><span class="icon">★</span><span>Introduction au module</span></div>
      <p class="hero-text">
        Accédez aux sections de données, d’analyses et de reporting pour suivre les tendances,
        comparer les périodes et produire vos KPI mensuels. Ce module centralise les informations
        essentielles pour un pilotage fluide de la satisfaction client.
      </p>
      <div class="hero-tags">
        <span class="hero-tag">Suivi mensuel</span>
        <span class="hero-tag">EDA & KPIs</span>
        <span class="hero-tag">Automatisation</span>
      </div>
      <div class="hero-list">
        <div class="hero-item"><span class="hero-bullet">•</span> Filtrez par période, canal ou motif (réparation / remplacement).</div>
        <div class="hero-item"><span class="hero-bullet">•</span> Surveillez l’évolution des indicateurs clés mois par mois.</div>
        <div class="hero-item"><span class="hero-bullet">•</span> Exportez des vues prêtes à communiquer aux parties prenantes.</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ───────────────────────────────────────────────────────────────────────────────
# 3) PAGE “Suivi mensuel”
# ───────────────────────────────────────────────────────────────────────────────
elif selection == "Suivi mensuel":
    st.markdown(f"<h1 style='color:{primary_color};'>📊 Suivi mensuel des réponses</h1>", unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def load_data():
        df = load_csv(CSV_PATH)
        # Colonnes à supprimer
        colonnes_a_supprimer = ["Courriel", "NIP", "NCLI", "NPOL", "EMAIL", "CIV", "NOM", "NOMMAG"]
        df = df.drop(columns=colonnes_a_supprimer, errors="ignore")
        return df

    df = load_data()
    code_map = {1: "Complétés", 2: "Abandonnés", 0: "Interrompus"}
    df["disposition"] = df["Codededisposition"].map(code_map).fillna("Autre")

    st.sidebar.markdown(f"<h4 style='color:{primary_color};'>Filtres</h4>", unsafe_allow_html=True)
    sel_code = st.sidebar.selectbox("Code de disposition", ["Tous"] + list(code_map.values()))
    if sel_code != "Tous":
        inv = {v: k for k, v in code_map.items()}
        df = df[df["Codededisposition"] == inv[sel_code]]

    min_ts = df[DATE_COL].min()
    max_ts = df[DATE_COL].max()
    if pd.isna(min_ts) or pd.isna(max_ts):
        st.error(f"La colonne ‘{DATE_COL}’ contient trop de NaT ou est mal formatée.")
        st.stop()
    min_d, max_d = min_ts.date(), max_ts.date()

    start_date, end_date = st.sidebar.slider("Période", min_value=min_d, max_value=max_d, value=(min_d, max_d), format="DD/MM/YYYY")
    mask_date = df[DATE_COL].dt.date.between(start_date, end_date)
    mask_zero = df["Codededisposition"] == 0
    df = df[mask_date | mask_zero]

    total = df["Codededisposition"].isin([0, 1, 2]).sum()
    comp  = (df["Codededisposition"] == 1).sum()
    inter = (df["Codededisposition"] == 2).sum()
    pct_c = comp/total*100 if total else 0
    pct_i = inter/total*100 if total else 0

    k1, k2, k3 = st.columns(3, gap="large")
    def render_card(col, icon, title, value, delta=None):
        col.markdown(
            f"<div style='background:{background_card}; padding:20px; border-radius:8px; text-align:center;'>"
            f"<h3>{icon} {title}</h3><h1>{value}</h1>"
            + (f"<p style='color:{primary_color}; margin:0;'>{delta}</p>" if delta else "")
            + "</div>",
            unsafe_allow_html=True,
        )
    render_card(k1, "👥", "Total sollicités", total)
    render_card(k2, "✅", "Complétés", f"{pct_c:.1f}%", comp)
    render_card(k3, "⏸️", "Interrompus", f"{pct_i:.1f}%", inter)

    st.markdown("---")

    with st.expander("🔍 Voir le détail des réponses filtrées"):
        st.dataframe(df, use_container_width=True)

    counts = df["disposition"].value_counts().rename_axis("disp").reset_index(name="count")
    fig = px.pie(counts, names="disp", values="count", hole=0.35, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textinfo="label+value+percent", textposition="outside")
    fig.update_layout(margin=dict(t=40, b=10, l=10, r=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
    st.plotly_chart(fig, use_container_width=True)

# ───────────────────────────────────────────────────────────────────────────────
# 4) PAGE “Dashboard”
# ───────────────────────────────────────────────────────────────────────────────
else:
    st.markdown(f"<h1 style='color:{primary_color}; text-align:center;'>📈 Dashboard Final</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray;'>Suivi des indicateurs clés</p>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("""
        <style>
            h2 { padding-top: 10px; color: #2F4F4F; }
            .block-header { display: flex; align-items: center; padding-bottom: 10px;
                            border-left: 5px solid #2F4F4F; margin-bottom: 20px; }
            .metric-card { background: #ffffff; padding: 20px; border-radius: 8px;
                           box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center; margin-bottom: 10px; }
            .metric-label { margin: 0; font-weight: 600; color: #555; }
            .metric-value { margin: 5px 0; font-size: 1.5rem; font-weight: 700; color: #333; }
        </style>
    """, unsafe_allow_html=True)

    @st.cache_data(show_spinner=False)
    def load_data_dashboard():
        return load_csv(CSV_PATH)

    df = load_data_dashboard()

    typepc_vals = ["Tous"] + sorted(df["TYPEPC"].dropna().unique().tolist())
    sel_typepc  = st.sidebar.selectbox("TYPEPC", typepc_vals)
    if sel_typepc != "Tous":
        df = df[df["TYPEPC"] == sel_typepc]

    start_date = st.sidebar.date_input("Date de début", df[DATE_COL].min())
    end_date   = st.sidebar.date_input("Date de fin",   df[DATE_COL].max())
    dispo      = st.sidebar.multiselect("Disposition", [0, 1, 2], default=[1])
    df = df[(df[DATE_COL] >= pd.to_datetime(start_date)) &
            (df[DATE_COL] <= pd.to_datetime(end_date)) &
            (df["Codededisposition"].isin(dispo))]

    df_comp = df[df["Codededisposition"] == 1]

    q1_vals = pd.to_numeric(df_comp["Q1"], errors="coerce").dropna()
    mean_q1 = q1_vals.mean() if not q1_vals.empty else 0.0

    nps_vals = pd.to_numeric(df_comp["Q16"], errors="coerce").dropna().astype(int)
    prom    = nps_vals[nps_vals >= 9].count()
    passiv  = nps_vals.between(7, 8).sum()
    detract = nps_vals[nps_vals <= 6].count()
    total_nps = prom + passiv + detract
    pct_prom  = prom / total_nps * 100 if total_nps else 0.0
    pct_det   = detract / total_nps * 100 if total_nps else 0.0
    nps_score = pct_prom - pct_det

    choix = st.radio("Sélectionnez la répartition à afficher",
                     ("Répartition de la satisfaction globale", "Répartition NPS"),
                     horizontal=True)
    if choix == "Répartition de la satisfaction globale":
        dist_q1 = (q1_vals.value_counts().sort_index().pipe(lambda s: (s / s.sum() * 100).round(1))
                   .reset_index(name="pct").rename(columns={"index": "Q1"}))
        fig = px.bar(dist_q1, x="Q1", y="pct", color="pct", color_continuous_scale="Viridis",
                     labels={"pct": "% répondants"}, title="Répartition des notes Q1 (%)")
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")
    else:
        nps_df = pd.DataFrame({"Segment": ["Promoters", "Passives", "Detractors"],
                               "Pourcentage": [pct_prom, 100 - (pct_prom + pct_det), pct_det]})
        fig = px.bar(nps_df, x="Segment", y="Pourcentage", color="Pourcentage",
                     color_continuous_scale="Viridis", labels={"Pourcentage": "% répondants"},
                     title="Répartition NPS (%)")
        fig.update_traces(texttemplate="%{y:.1f}%", textposition="outside")

    q15 = df_comp["Q15"].dropna().astype(str).str.strip().str.lower()
    mask_ts = q15.str.contains("très simple", na=False)
    mask_s  = q15.str.contains("simple", na=False) & ~mask_ts
    mask_tc = q15.str.contains("très compliqu", na=False)
    mask_c  = q15.str.contains("compliqu", na=False) & ~mask_tc
    n_ts, n_s, n_tc, n_c = int(mask_ts.sum()), int(mask_s.sum()), int(mask_tc.sum()), int(mask_c.sum())
    total15 = n_ts + n_s + n_tc + n_c
    pct_ts = round(n_ts / total15 * 100, 1) if total15 else 0.0
    pct_s  = round(n_s  / total15 * 100, 1) if total15 else 0.0
    pct_tc = round(n_tc / total15 * 100, 1) if total15 else 0.0
    pct_c  = round(n_c  / total15 * 100, 1) if total15 else 0.0
    df_q15 = pd.DataFrame({"Catégorie": ["Très simples", "Simples", "Très compliquées", "Compliquées"],
                           "Pourcentage": [pct_ts, pct_s, pct_tc, pct_c]})
    fig_q15 = px.bar(df_q15, x="Catégorie", y="Pourcentage", text="Pourcentage",
                     color="Catégorie", color_discrete_sequence=px.colors.qualitative.Pastel,
                     labels={"Pourcentage": "% répondants"},
                     title="Q15. Démarches nécessaires à la gestion du sinistre")
    fig_q15.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    q3_raw = df_comp["Q3"].astype(str).fillna("")
    q3 = (q3_raw.apply(lambda x: unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode())
          .str.replace("'", "", regex=False).str.replace("’", "", regex=False)
          .str.lower().str.strip())
    mask_tc3 = q3.str.contains(r"\btres completes\b", regex=True)
    mask_s3  = q3.str.contains(r"\bsuffisantes\b",    regex=True)
    mask_i3  = q3.str.contains(r"\binsuffisantes\b",  regex=True)
    mask_n3  = q3.str.contains(r"je nai pas eu dinformations sur ces sujets", regex=True)
    n_tc3, n_s3, n_i3, n_n3 = int(mask_tc3.sum()), int(mask_s3.sum()), int(mask_i3.sum()), int(mask_n3.sum())
    total_q3 = n_tc3 + n_s3 + n_i3 + n_n3
    total_suff_compl = n_tc3 + n_s3
    total_insuff_nil = n_i3  + n_n3
    pct_suff_compl   = (total_suff_compl / total_q3 * 100) if total_q3 else 0.0
    pct_insuff_nil   = (total_insuff_nil / total_q3 * 100) if total_q3 else 0.0
    dist_q3 = pd.DataFrame({"Catégorie": ["Très complètes", "Suffisantes", "Insuffisantes", "Nul"],
                            "Count": [n_tc3, n_s3, n_i3, n_n3]})
    dist_q3["pct"] = (dist_q3["Count"] / dist_q3["Count"].sum() * 100).round(1)
    fig_q3 = px.bar(dist_q3, x="Catégorie", y="Count", text="pct",
                    labels={"Count": "Nombre de réponses", "pct": "% répondants"},
                    title="Q3. Explications du vendeur – Assurance Mobile",
                    color="Catégorie", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_q3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")

    q6 = df_comp["Q6"].fillna("").astype(str).str.strip().str.lower()
    n_boutique = int(q6.str.contains("boutique orange", na=False).sum())
    n_service  = int(q6.str.contains("service client orange", na=False).sum())
    n_direct   = int(q6.str.contains("contact.*assurance mobile", na=False).sum())
    total_orange = n_boutique + n_service
    total_q6     = total_orange + n_direct
    pct_orange   = round(total_orange / total_q6 * 100, 1) if total_q6 else 0.0
    dist_q6 = pd.DataFrame({"Catégorie": ["En boutique Orange", "Service client Orange", "Contact Assurance Mobile"],
                            "Count": [n_boutique, n_service, n_direct]})
    dist_q6["Pourcentage"] = (dist_q6["Count"] / total_q6 * 100).round(1)
    fig_q6 = px.pie(dist_q6, names="Catégorie", values="Count", hole=0.3,
                    title="Q6. Premier interlocuteur pour déclarer le sinistre")
    fig_q6.update_traces(textinfo="label+percent", textposition="outside")

    q5 = df_comp["Q5"].fillna("").astype(str).str.strip().str.lower()
    mask_p  = q5.str.contains("connaissais parfaitement", na=False)
    mask_pa = q5.str.contains("connaissance partielle",  na=False)
    mask_i5 = q5.str.contains("intéressé",               na=False)
    mask_ig = q5.str.contains("ne connaissais pas",      na=False) | q5.str.contains("ignorais pas", na=False)
    n_p, n_pa, n_i5, n_ig = int(mask_p.sum()), int(mask_pa.sum()), int(mask_i5.sum()), int(mask_ig.sum())
    total_q5 = n_p + n_pa + n_i5 + n_ig
    pct_p, pct_pa = round(n_p/total_q5*100,1) if total_q5 else 0.0, round(n_pa/total_q5*100,1) if total_q5 else 0.0
    pct_i5, pct_ig = round(n_i5/total_q5*100,1) if total_q5 else 0.0, round(n_ig/total_q5*100,1) if total_q5 else 0.0
    dist_q5 = pd.DataFrame({"Modalité": ["Parfaite", "Partielle", "Intéressé·e", "Ignorance"],
                            "pct": [pct_p, pct_pa, pct_i5, pct_ig]})
    fig_q5 = px.bar(dist_q5, x="Modalité", y="pct", text="pct",
                    color="Modalité", color_discrete_sequence=px.colors.qualitative.Pastel,
                    labels={"pct": "% répondants"},
                    title="Q5. Niveau de connaissance des conditions de garantie")
    fig_q5.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    q7 = df_comp["Q7"].fillna("").astype(str).str.strip().str.lower()
    mask_oui = q7.str.contains(r"\boui\b", na=False)
    mask_non = q7.str.contains(r"\bnon\b", na=False)
    n_oui, n_non = int(mask_oui.sum()), int(mask_non.sum())
    total_q7 = n_oui + n_non
    pct_oui = round(n_oui / total_q7 * 100, 1) if total_q7 else 0.0
    pct_non = round(n_non / total_q7 * 100, 1) if total_q7 else 0.0
    dist_q7 = pd.DataFrame({"Modalité": ["Oui", "Non"], "pct": [pct_oui, pct_non]})
    fig_q7 = px.bar(dist_q7, x="Modalité", y="pct", text="pct",
                    color="Modalité", color_discrete_sequence=px.colors.qualitative.Pastel,
                    labels={"pct": "% répondants"},
                    title="Q7. Cohérence des informations")
    fig_q7.update_traces(texttemplate="%{text:.1f} %", textposition="outside")

    q8 = df_comp["Q8"].fillna("").astype(str).str.strip().str.lower()
    dist_q8 = q8.value_counts(dropna=False).rename_axis("Modalité").reset_index(name="count")
    dist_q8["pct"] = (dist_q8["count"] / dist_q8["count"].sum() * 100).round(1)
    fig_q8 = px.pie(dist_q8, names="Modalité", values="count", hole=0.3, title="Q8 – Satisfaction du délai global")
    fig_q8.update_traces(textinfo="label+percent", textposition="outside")

    q13 = df_comp["Q13"].fillna("").astype(str).str.strip().str.lower()
    dist_q13 = q13.value_counts(dropna=False).rename_axis("Modalité").reset_index(name="count")
    dist_q13["pct"] = (dist_q13["count"] / dist_q13["count"].sum() * 100).round(1)
    fig_q13 = px.pie(dist_q13, names="Modalité", values="count", hole=0.3, title="Q13 – Suivi du dossier")
    fig_q13.update_traces(textinfo="label+percent", textposition="outside")

    q9 = df_comp["Q9"].fillna("").astype(str).str.strip().str.lower()
    dist_q9 = q9.value_counts(dropna=False).rename_axis("Modalité").reset_index(name="count")
    dist_q9["pct"] = (dist_q9["count"] / dist_q9["count"].sum() * 100).round(1)
    fig_q9 = px.pie(dist_q9, names="Modalité", values="count", hole=0.3,
                    title="Q9 – Satisfaction qualité réparation / mobile de remplacement")
    fig_q9.update_traces(textinfo="label+percent", textposition="outside")

    q11 = df_comp["Q11"].fillna("").astype(str).str.strip().str.lower()
    dist_q11 = q11.value_counts(dropna=False).rename_axis("Modalité").reset_index(name="count")
    dist_q11["pct"] = (dist_q11["count"] / dist_q11["count"].sum() * 100).round(1)
    fig_q11 = px.pie(dist_q11, names="Modalité", values="count", hole=0.3, title="Q11 – Réception du téléphone")
    fig_q11.update_traces(textinfo="label+percent", textposition="outside")

    # — AFFICHAGE —
    with st.container():
        st.markdown("<div style='background-color: #F7F9FA; padding: 30px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>", unsafe_allow_html=True)
        st.markdown("<div class='block-header'><h2>🔎 INDICATEURS GLOBAUX</h2></div>", unsafe_allow_html=True)
        cols = st.columns(3, gap='large')
        metrics = [{'label': '✔️ Total complétés', 'value': len(df_comp)},
                   {'label': '⭐ Note moyenne Q1', 'value': f"{mean_q1:.2f}/10"},
                   {'label': '📊 Score NPS', 'value': f"{nps_score:.1f}"}]
        for col, m in zip(cols, metrics):
            with col:
                st.markdown(f"<div class='metric-card'><p class='metric-label'>{m['label']}</p><p class='metric-value'>{m['value']}</p></div>", unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.plotly_chart(fig_q15, use_container_width=True)
        subtots = st.columns(2, gap='large')
        subtots[0].markdown(f"<div class='metric-card'><p class='metric-label'>✅ TOTAL SIMPLES</p><p class='metric-value'>{(pct_ts + pct_s):.1f}%</p></div>", unsafe_allow_html=True)
        subtots[1].markdown(f"<div class='metric-card'><p class='metric-label'>🔧 TOTAL COMPLIQUÉES</p><p class='metric-value'>{(pct_tc + pct_c):.1f}%</p></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background-color: #FCFCFC; padding: 30px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>", unsafe_allow_html=True)
        st.markdown("<div class='block-header'><h2>🔑 Souscription du contrat</h2></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_q3, use_container_width=True)
        c1, c2 = st.columns(2, gap='large')
        for col, (label, count, pct) in zip([c1, c2], [('✅ Suffisantes + complétées', total_suff_compl, pct_suff_compl),
                                                     ('⚠️ Insuffisantes + Nul', total_insuff_nil, pct_insuff_nil)]):
            with col:
                st.markdown(f"<div class='metric-card'><p class='metric-label'>{label}</p><p class='metric-value'>{count} ({pct:.1f}%)</p></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background-color:#F1F7ED;padding:30px;border-radius:12px;box-shadow:0 2px 6px rgba(0,0,0,0.05); margin-bottom:40px;'>", unsafe_allow_html=True)
        st.markdown("<div class='block-header'><h2>📝 Déclaration du sinistre</h2></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_q6, use_container_width=True)
        st.markdown(f"<div class='metric-card' style='margin-top:20px;'><p class='metric-label'>🔧 TOTAL Orange</p><p class='metric-value'>{pct_orange:.1f}% ({total_orange})</p></div>", unsafe_allow_html=True)
        st.plotly_chart(fig_q5, use_container_width=True)
        st.plotly_chart(fig_q7, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background-color: #FAF3F0; padding: 30px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>", unsafe_allow_html=True)
        st.markdown("<div class='block-header'><h2>🕒 Suivi du dossier & Délai</h2></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap='large')
        with col1: st.plotly_chart(fig_q8, use_container_width=True)
        with col2: st.plotly_chart(fig_q13, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.container():
        st.markdown("<div style='background-color: #F7F9FA; padding: 30px; border-radius: 12px; box-shadow: 0 2px 6px rgba(0,0,0,0.05); margin-bottom: 40px;'>", unsafe_allow_html=True)
        st.markdown("<div class='block-header'><h2>📱 Réception du téléphone</h2></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2, gap='large')
        with col1: st.plotly_chart(fig_q9, use_container_width=True)
        with col2: st.plotly_chart(fig_q11, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
