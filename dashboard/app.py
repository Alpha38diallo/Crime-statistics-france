import streamlit as st
import pandas as pd
import plotly.express as px
import os

from sqlalchemy import create_engine
from dotenv import load_dotenv

# ==================================================
# CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Délinquance France",
    page_icon="🇫🇷",
    layout="wide"
)

# ==================================================
# CHARGEMENT DES DONNEES
# ==================================================
@st.cache_data
def load_data():

    load_dotenv()

    engine = create_engine(
    f"postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}?sslmode=require"
    )
    # Données délinquance depuis PostgreSQL
    df = pd.read_sql(
        """
        SELECT
           "CODGEO_2026",
            annee,
            indicateur,
            nombre,
            taux_pour_mille
        FROM crime_stats
        """,
        engine
    )

    # Référentiel communes
    geo_df = pd.read_excel(
        "references/info-complements-data.gouv-2025-geographie2026-produit-le2026-06-25.xlsx"
    )
    # Harmonisation des codes communes
    df["CODGEO_2026"] = df["CODGEO_2026"].astype(str)
    geo_df["CODGEO"] = geo_df["CODGEO"].astype(str)

    # Jointure pour récupérer les noms des communes
    df = df.merge(
        geo_df[["CODGEO", "LIBGEO"]],
        left_on="CODGEO_2026",
        right_on="CODGEO",
        how="left"
    )

    # Conversion des colonnes numériques
    df["nombre"] = pd.to_numeric(
        df["nombre"],
        errors="coerce"
    )

    df["taux_pour_mille"] = (
        df["taux_pour_mille"]
        .astype(str)
        .str.replace(",", ".", regex=False)
    )

    df["taux_pour_mille"] = pd.to_numeric(
        df["taux_pour_mille"],
        errors="coerce"
    )

    return df

df = load_data()

# Tes filtres Streamlit
indicateurs = sorted(
    df["indicateur"].dropna().unique()
)
# ==================================================
# SIDEBAR
# ==================================================

st.sidebar.title("Filtres")

infractions = sorted(
    df["indicateur"].dropna().unique()
)

infraction_selectionnee = st.sidebar.selectbox(
    "Type d'infraction",
    infractions
)

annees = sorted(
    df["annee"].dropna().unique()
)

annee_selectionnee = st.sidebar.selectbox(
    "Année",
    annees,
    index=len(annees) - 1
)

# ==================================================
# FILTRAGE
# ==================================================

df_filtered = df[
    (df["indicateur"] == infraction_selectionnee)
]

df_annee = df[
    (df["indicateur"] == infraction_selectionnee)
    &
    (df["annee"] == annee_selectionnee)
]

# ==================================================
# TITRE
# ==================================================

st.markdown(
    """
    <h1 style="
        font-size: 34px;
        margin-bottom: 0;
    ">
        🇫🇷 Tableau de bord de la délinquance en France
    </h1>
    """,
    unsafe_allow_html=True
)
st.caption(
    "Analyse des infractions enregistrées en France par la Police et la Gendarmerie nationales"
)
st.divider()

# ==================================================
# KPI
# ==================================================

st.markdown("""
<style>

.kpi-card {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    padding: 12px;
    border-radius: 30px;
    border: 1px solid #2a2d35;
    text-align: center;
    min-height: 90px;
}

.kpi-title {
    color: #bdbdbd;
    font-size: 18px;
    margin-bottom: 5px;
    font-weight: 600;
}

.kpi-value {
    color: white;
    font-size: 50px;
    font-weight: bold;
    line-height: 1;
    white-space: nowrap;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🏘️ Communes</div>
        <div class="kpi-value">
            {df_annee['CODGEO_2026'].nunique():,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">🚨 Infractions</div>
        <div class="kpi-value">
            {int(df_annee['nombre'].sum()):,}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📊 Taux moyen</div>
        <div class="kpi-value">
            {round(df_annee['taux_pour_mille'].mean(),2)}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">📅Année</div>
        <div class="kpi-value">
            {annee_selectionnee}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================================================
# COURBE + CAMEMBERT
# ==================================================

col1, col2 = st.columns([2, 1.5])

with col1:

    st.markdown("### Nombre de faits enregistrés par année")

    evolution = (
        df_filtered
        .groupby("annee")["nombre"]
        .sum()
        .reset_index()
    )

    fig_line = px.line(
        evolution,
        x="annee",
        y="nombre",
        markers=True,
        template="plotly_dark"
    )

    fig_line.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="Année",
        yaxis_title="Nombre de faits",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )

    st.plotly_chart(
        fig_line,
        width="stretch"
    )

with col2:

    st.markdown("### 10 des communes les plus touchées")

    repartition = (
        df_annee.groupby(["CODGEO_2026", "LIBGEO"])["nombre"]
        .sum()
        .reset_index()
        .sort_values("nombre", ascending=False)
        .head(10)
    )

    fig_pie = px.pie(
        repartition,
        names="LIBGEO",
        values="nombre",
        hole=0.65,
        template="plotly_dark"
    )

    fig_pie.update_layout(
        height=500,
        legend=dict(
            orientation="h",
            y=-0.1,
            x=0.5,
            xanchor="center"
        ),
        margin=dict(
            t=20,
            b=80,
            l=20,
            r=20
        )
    )

    st.plotly_chart(
        fig_pie,
        width="stretch"
    )

# ==================================================
# TOP 10 COMMUNES AVEC LE TAUX LE PLUS ELEVE
# ==================================================

st.markdown("### Communes aux taux les plus élevés")

top_taux = (
    df_annee[
        ["CODGEO_2026", "LIBGEO", "taux_pour_mille"]
    ]
    .dropna()
    .sort_values(
        "taux_pour_mille",
        ascending=False
    )
    .head(10)
)

top_taux["taux_pour_mille"] = (
    top_taux["taux_pour_mille"]
    .round(2)
)

top_taux["CODGEO_2026"] = (
    top_taux["CODGEO_2026"]
    .astype(str)
)

fig_top_taux = px.bar(
    top_taux,
    x="taux_pour_mille",
    y="LIBGEO",
    orientation="h",
    text="taux_pour_mille",
    template="plotly_dark",
    color="taux_pour_mille"
)

fig_top_taux.update_layout(
    height=600,
    xaxis_title="Taux pour 1000 habitants",
    yaxis_title="Commune",
    yaxis=dict(type="category"),
    coloraxis_showscale=False
)

fig_top_taux.update_traces(
    textposition="outside"
)

st.plotly_chart(
    fig_top_taux,
    width="stretch"
)