import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sqlite3
import os
import io
from datetime import datetime, date
from scipy import stats

# ─── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriData Cameroun",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS CUSTOM ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.4rem;
    color: #1a4731;
    letter-spacing: -0.5px;
    margin-bottom: 0;
}
.subtitle {
    color: #4a7c59;
    font-size: 1rem;
    font-weight: 300;
    margin-top: 2px;
}
.metric-card {
    background: linear-gradient(135deg, #f0faf4 0%, #e8f5ee 100%);
    border: 1px solid #b7dfc7;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
}
.metric-val {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: #1a4731;
}
.metric-label {
    font-size: 0.78rem;
    color: #4a7c59;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 500;
}
.section-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: #1a4731;
    border-left: 4px solid #2d8c4e;
    padding-left: 12px;
    margin: 20px 0 12px;
}
.badge-culture {
    background: #d4f0de;
    color: #1a4731;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.82rem;
    font-weight: 500;
    display: inline-block;
}
.alert-success {
    background: #e8f5ee;
    border: 1px solid #2d8c4e;
    border-radius: 8px;
    padding: 10px 16px;
    color: #1a4731;
    font-size: 0.9rem;
}
div[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f2d1a 0%, #1a4731 100%);
}
div[data-testid="stSidebar"] * {
    color: #d4f0de !important;
}
div[data-testid="stSidebar"] .stRadio label {
    color: #a8d4ba !important;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)

# ─── DATABASE ────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agridata.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS rendements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, region TEXT, culture TEXT,
            superficie_ha REAL, production_tonnes REAL,
            rendement_t_ha REAL, qualite TEXT, remarques TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS meteo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT, region TEXT, station TEXT,
            temp_min REAL, temp_max REAL, temp_moy REAL,
            precipitation_mm REAL, humidite_pct REAL,
            vitesse_vent_kmh REAL, ensoleillement_h REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_conn():
    return sqlite3.connect(DB_PATH)

def load_rendements():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM rendements ORDER BY date DESC", conn)
    conn.close()
    return df

def load_meteo():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM meteo ORDER BY date DESC", conn)
    conn.close()
    return df

init_db()

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 AgriData")
    st.markdown("*Analyse agricole du Cameroun*")
    st.markdown("---")
    page = st.radio("Navigation", [
        "🏠 Tableau de bord",
        "📋 Saisie des données",
        "🔍 Recherche",
        "📊 Analyse descriptive",
        "📈 Visualisations",
        "💾 Gestion des données"
    ])
    st.markdown("---")
    df_r = load_rendements()
    df_m = load_meteo()
    st.markdown(f"**Rendements :** {len(df_r)} entrées")
    st.markdown(f"**Météo :** {len(df_m)} entrées")
    st.markdown("---")
    st.markdown("<small style='color:#7aaa8a'>INF 232 EC2 · TP Analyse de données</small>", unsafe_allow_html=True)

# ─── PAGE: TABLEAU DE BORD ────────────────────────────────────────────────────
if page == "🏠 Tableau de bord":
    st.markdown('<h1 class="main-title">AgriData Cameroun 🌾</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Plateforme de collecte et d\'analyse descriptive des données agricoles</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(df_r)}</div><div class="metric-label">Enregistrements rendements</div></div>', unsafe_allow_html=True)
    with col2:
        moy_rend = round(df_r["rendement_t_ha"].mean(), 2) if len(df_r) > 0 else "—"
        st.markdown(f'<div class="metric-card"><div class="metric-val">{moy_rend}</div><div class="metric-label">Rendement moy. (t/ha)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-val">{len(df_m)}</div><div class="metric-label">Relevés météorologiques</div></div>', unsafe_allow_html=True)
    with col4:
        nb_regions = df_r["region"].nunique() if len(df_r) > 0 else 0
        st.markdown(f'<div class="metric-card"><div class="metric-val">{nb_regions}</div><div class="metric-label">Régions couvertes</div></div>', unsafe_allow_html=True)

    st.markdown("")

    if len(df_r) > 0:
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="section-header">Rendements par culture</div>', unsafe_allow_html=True)
            fig = px.bar(
                df_r.groupby("culture")["rendement_t_ha"].mean().reset_index(),
                x="culture", y="rendement_t_ha",
                color="rendement_t_ha",
                color_continuous_scale=[[0,"#b7dfc7"],[0.5,"#2d8c4e"],[1,"#1a4731"]],
                labels={"rendement_t_ha": "Rendement (t/ha)", "culture": "Culture"},
                template="plotly_white"
            )
            fig.update_layout(showlegend=False, coloraxis_showscale=False,
                              margin=dict(t=10, b=20, l=10, r=10),
                              plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            st.markdown('<div class="section-header">Répartition par région</div>', unsafe_allow_html=True)
            region_counts = df_r["region"].value_counts().reset_index()
            region_counts.columns = ["region", "count"]
            fig2 = px.pie(region_counts, values="count", names="region",
                          color_discrete_sequence=px.colors.sequential.Greens_r,
                          template="plotly_white")
            fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10),
                               paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("📌 Aucune donnée disponible. Commencez par saisir des données dans l'onglet **Saisie des données**.")

        st.markdown('<div class="section-header">Exemple de données disponibles</div>', unsafe_allow_html=True)
        if st.button("🌱 Charger des données d'exemple"):
            conn = get_conn()
            cultures = ["Maïs", "Cacao", "Café", "Manioc", "Plantain", "Sorgho"]
            regions = ["Centre", "Littoral", "Ouest", "Nord", "Sud", "Adamaoua"]
            qualites = ["Excellente", "Bonne", "Moyenne", "Faible"]
            np.random.seed(42)
            for i in range(40):
                d = date(2023 + i//20, (i % 12) + 1, min((i % 28) + 1, 28))
                culture = np.random.choice(cultures)
                region = np.random.choice(regions)
                superficie = round(np.random.uniform(0.5, 50), 2)
                base_rend = {"Maïs":2.5,"Cacao":0.8,"Café":0.6,"Manioc":12,"Plantain":8,"Sorgho":1.5}
                rendement = round(base_rend[culture] * np.random.uniform(0.7, 1.4), 2)
                production = round(superficie * rendement, 2)
                qualite = np.random.choice(qualites)
                conn.execute("""INSERT INTO rendements (date,region,culture,superficie_ha,production_tonnes,rendement_t_ha,qualite,remarques)
                    VALUES (?,?,?,?,?,?,?,?)""",
                    (str(d), region, culture, superficie, production, rendement, qualite, ""))
            for i in range(40):
                d = date(2023 + i//20, (i % 12) + 1, min((i % 28) + 1, 28))
                region = np.random.choice(regions)
                temp_min = round(np.random.uniform(18, 24), 1)
                temp_max = round(temp_min + np.random.uniform(5, 12), 1)
                temp_moy = round((temp_min + temp_max) / 2, 1)
                precip = round(np.random.uniform(0, 200), 1)
                humidite = round(np.random.uniform(55, 95), 1)
                vent = round(np.random.uniform(5, 40), 1)
                ensol = round(np.random.uniform(3, 10), 1)
                conn.execute("""INSERT INTO meteo (date,region,station,temp_min,temp_max,temp_moy,precipitation_mm,humidite_pct,vitesse_vent_kmh,ensoleillement_h)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (str(d), region, f"Station {region}", temp_min, temp_max, temp_moy, precip, humidite, vent, ensol))
            conn.commit()
            conn.close()
            st.success("✅ Données d'exemple chargées avec succès !")
            st.rerun()

# ─── PAGE: SAISIE ─────────────────────────────────────────────────────────────
elif page == "📋 Saisie des données":
    st.markdown('<h1 class="main-title">Saisie des données</h1>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2 = st.tabs(["🌾 Rendements agricoles", "🌦️ Données météorologiques"])

    with tab1:
        st.markdown('<div class="section-header">Nouveau relevé de rendement</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            date_r = st.date_input("Date de récolte", value=date.today(), key="date_r")
            region_r = st.selectbox("Région", ["Centre","Littoral","Ouest","Nord","Sud","Adamaoua","Est","Nord-Ouest","Sud-Ouest","Extrême-Nord"], key="region_r")
        with col2:
            culture = st.selectbox("Type de culture", ["Maïs","Cacao","Café","Manioc","Plantain","Sorgho","Mil","Riz","Arachide","Coton","Autre"], key="culture_r")
            superficie = st.number_input("Superficie (ha)", min_value=0.01, max_value=10000.0, value=1.0, step=0.1, key="sup_r")
        with col3:
            production = st.number_input("Production (tonnes)", min_value=0.01, max_value=100000.0, value=2.0, step=0.1, key="prod_r")
            qualite = st.selectbox("Qualité de la récolte", ["Excellente","Bonne","Moyenne","Faible"], key="qual_r")
        remarques = st.text_area("Remarques / observations", height=80, placeholder="Conditions particulières, incidents, etc.", key="rem_r")
        if st.button("💾 Enregistrer le relevé", use_container_width=True, key="btn_r"):
            rendement_calc = round(production / superficie, 3) if superficie > 0 else 0
            conn = get_conn()
            conn.execute("""INSERT INTO rendements (date,region,culture,superficie_ha,production_tonnes,rendement_t_ha,qualite,remarques)
                VALUES (?,?,?,?,?,?,?,?)""",
                (str(date_r), region_r, culture, superficie, production, rendement_calc, qualite, remarques))
            conn.commit()
            conn.close()
            st.success(f"✅ Relevé enregistré ! Rendement calculé : {rendement_calc} t/ha")
            st.rerun()

        if len(df_r) > 0:
            st.markdown('<div class="section-header">Derniers enregistrements</div>', unsafe_allow_html=True)
            st.dataframe(
                df_r[["date","region","culture","superficie_ha","production_tonnes","rendement_t_ha","qualite"]].head(10),
                use_container_width=True, hide_index=True
            )

    with tab2:
        st.markdown('<div class="section-header">Nouveau relevé météorologique</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            date_m = st.date_input("Date du relevé", value=date.today(), key="date_m")
            region_m = st.selectbox("Région", ["Centre","Littoral","Ouest","Nord","Sud","Adamaoua","Est","Nord-Ouest","Sud-Ouest","Extrême-Nord"], key="reg_m")
            station = st.text_input("Station météo", placeholder="Ex: Station de Yaoundé", key="station_m")
        with col2:
            temp_min = st.number_input("Temp. min (°C)", min_value=-10.0, max_value=50.0, value=20.0, step=0.1, key="tmin")
            temp_max = st.number_input("Temp. max (°C)", min_value=-10.0, max_value=55.0, value=30.0, step=0.1, key="tmax")
            temp_moy = st.number_input("Temp. moy (°C)", min_value=-10.0, max_value=55.0, value=25.0, step=0.1, key="tmoy")
        with col3:
            precipitation = st.number_input("Précipitations (mm)", min_value=0.0, max_value=500.0, value=50.0, step=0.5, key="prec")
            humidite = st.number_input("Humidité relative (%)", min_value=0.0, max_value=100.0, value=75.0, step=0.5, key="hum")
            vent = st.number_input("Vitesse vent (km/h)", min_value=0.0, max_value=200.0, value=15.0, step=0.5, key="vent")
            ensol = st.number_input("Ensoleillement (h)", min_value=0.0, max_value=14.0, value=6.0, step=0.5, key="ensol")
        if st.button("💾 Enregistrer le relevé météo", use_container_width=True, key="btn_m"):
            conn = get_conn()
            conn.execute("""INSERT INTO meteo (date,region,station,temp_min,temp_max,temp_moy,precipitation_mm,humidite_pct,vitesse_vent_kmh,ensoleillement_h)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                (str(date_m), region_m, station, temp_min, temp_max, temp_moy, precipitation, humidite, vent, ensol))
            conn.commit()
            conn.close()
            st.success("✅ Relevé météorologique enregistré avec succès !")
            st.rerun()

        if len(df_m) > 0:
            st.markdown('<div class="section-header">Derniers relevés météo</div>', unsafe_allow_html=True)
            st.dataframe(
                df_m[["date","region","station","temp_min","temp_max","precipitation_mm","humidite_pct"]].head(10),
                use_container_width=True, hide_index=True
            )


# ─── PAGE: RECHERCHE ─────────────────────────────────────────────────────────
elif page == "🔍 Recherche":
    st.markdown('<h1 class="main-title">Recherche</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Filtrez et explorez les données selon vos critères</p>', unsafe_allow_html=True)
    st.markdown("---")

    tab_r, tab_m = st.tabs(["🌾 Rendements", "🌦️ Météo"])

    with tab_r:
        if len(df_r) == 0:
            st.info("Aucune donnée de rendement disponible.")
        else:
            st.markdown('<div class="section-header">Filtres</div>', unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                cultures_dispo = ["Toutes"] + sorted(df_r["culture"].dropna().unique().tolist())
                filtre_culture = st.selectbox("🌾 Par culture", cultures_dispo)
            with col2:
                regions_dispo = ["Toutes"] + sorted(df_r["region"].dropna().unique().tolist())
                filtre_region = st.selectbox("📍 Par région", regions_dispo)
            with col3:
                qualites_dispo = ["Toutes"] + sorted(df_r["qualite"].dropna().unique().tolist())
                filtre_qualite = st.selectbox("⭐ Par qualité", qualites_dispo)
            col4, col5 = st.columns(2)
            with col4:
                dates_r = pd.to_datetime(df_r["date"], errors="coerce").dropna()
                date_min_r = dates_r.min().date() if len(dates_r) > 0 else date(2020,1,1)
                date_max_r = dates_r.max().date() if len(dates_r) > 0 else date.today()
                filtre_date_debut = st.date_input("📅 Date début", value=date_min_r, key="rd1")
            with col5:
                filtre_date_fin = st.date_input("📅 Date fin", value=date_max_r, key="rd2")
            filtre_mot_cle = st.text_input("📝 Mot-clé dans les remarques", placeholder="Ex: irrigation, pluie, maladie...")
            df_filtre = df_r.copy()
            if filtre_culture != "Toutes":
                df_filtre = df_filtre[df_filtre["culture"] == filtre_culture]
            if filtre_region != "Toutes":
                df_filtre = df_filtre[df_filtre["region"] == filtre_region]
            if filtre_qualite != "Toutes":
                df_filtre = df_filtre[df_filtre["qualite"] == filtre_qualite]
            df_filtre["date_parsed"] = pd.to_datetime(df_filtre["date"], errors="coerce")
            df_filtre = df_filtre[
                (df_filtre["date_parsed"] >= pd.Timestamp(filtre_date_debut)) &
                (df_filtre["date_parsed"] <= pd.Timestamp(filtre_date_fin))
            ]
            if filtre_mot_cle.strip():
                df_filtre = df_filtre[df_filtre["remarques"].fillna("").str.contains(filtre_mot_cle, case=False)]
            st.markdown("---")
            st.markdown(f'<div class="section-header">Résultats : {len(df_filtre)} enregistrement(s)</div>', unsafe_allow_html=True)
            if len(df_filtre) == 0:
                st.warning("Aucun résultat ne correspond à vos critères.")
            else:
                cols_affich = ["date","region","culture","superficie_ha","production_tonnes","rendement_t_ha","qualite","remarques"]
                st.dataframe(df_filtre[cols_affich], use_container_width=True, hide_index=True)
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Rendement moyen", f"{df_filtre['rendement_t_ha'].mean():.2f} t/ha")
                with col_s2:
                    st.metric("Production totale", f"{df_filtre['production_tonnes'].sum():.2f} t")
                with col_s3:
                    st.metric("Superficie totale", f"{df_filtre['superficie_ha'].sum():.2f} ha")
                csv_exp = df_filtre.drop(columns=["date_parsed"],errors="ignore").to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter (CSV)", data=csv_exp,
                    file_name=f"recherche_rendements_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

    with tab_m:
        if len(df_m) == 0:
            st.info("Aucune donnée météo disponible.")
        else:
            st.markdown('<div class="section-header">Filtres</div>', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                regions_m = ["Toutes"] + sorted(df_m["region"].dropna().unique().tolist())
                filtre_region_m = st.selectbox("📍 Par région", regions_m, key="rm")
            with col2:
                stations_dispo = ["Toutes"] + sorted(df_m["station"].dropna().unique().tolist())
                filtre_station = st.selectbox("🏭 Par station", stations_dispo)
            col3, col4 = st.columns(2)
            with col3:
                dates_m2 = pd.to_datetime(df_m["date"], errors="coerce").dropna()
                date_min_m = dates_m2.min().date() if len(dates_m2) > 0 else date(2020,1,1)
                date_max_m = dates_m2.max().date() if len(dates_m2) > 0 else date.today()
                filtre_date_debut_m = st.date_input("📅 Date début", value=date_min_m, key="md1")
            with col4:
                filtre_date_fin_m = st.date_input("📅 Date fin", value=date_max_m, key="md2")
            col5, col6 = st.columns(2)
            with col5:
                filtre_temp = st.slider("🌡️ Température moy (°C)", -10.0, 50.0, (-10.0, 50.0))
            with col6:
                filtre_precip = st.slider("🌧️ Précipitations (mm)", 0.0, 500.0, (0.0, 500.0))
            df_filtre_m = df_m.copy()
            if filtre_region_m != "Toutes":
                df_filtre_m = df_filtre_m[df_filtre_m["region"] == filtre_region_m]
            if filtre_station != "Toutes":
                df_filtre_m = df_filtre_m[df_filtre_m["station"] == filtre_station]
            df_filtre_m["date_parsed"] = pd.to_datetime(df_filtre_m["date"], errors="coerce")
            df_filtre_m = df_filtre_m[
                (df_filtre_m["date_parsed"] >= pd.Timestamp(filtre_date_debut_m)) &
                (df_filtre_m["date_parsed"] <= pd.Timestamp(filtre_date_fin_m)) &
                (df_filtre_m["temp_moy"] >= filtre_temp[0]) &
                (df_filtre_m["temp_moy"] <= filtre_temp[1]) &
                (df_filtre_m["precipitation_mm"] >= filtre_precip[0]) &
                (df_filtre_m["precipitation_mm"] <= filtre_precip[1])
            ]
            st.markdown("---")
            st.markdown(f'<div class="section-header">Résultats : {len(df_filtre_m)} relevé(s)</div>', unsafe_allow_html=True)
            if len(df_filtre_m) == 0:
                st.warning("Aucun résultat ne correspond à vos critères.")
            else:
                cols_m = ["date","region","station","temp_min","temp_max","temp_moy","precipitation_mm","humidite_pct","vitesse_vent_kmh"]
                st.dataframe(df_filtre_m[cols_m], use_container_width=True, hide_index=True)
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric("Temp. moyenne", f"{df_filtre_m['temp_moy'].mean():.1f} °C")
                with col_s2:
                    st.metric("Précip. moyenne", f"{df_filtre_m['precipitation_mm'].mean():.1f} mm")
                with col_s3:
                    st.metric("Humidité moyenne", f"{df_filtre_m['humidite_pct'].mean():.1f} %")
                csv_m_exp = df_filtre_m.drop(columns=["date_parsed"],errors="ignore").to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter météo (CSV)", data=csv_m_exp,
                    file_name=f"recherche_meteo_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv")

# ─── PAGE: ANALYSE DESCRIPTIVE ────────────────────────────────────────────────
elif page == "📊 Analyse descriptive":
    st.markdown('<h1 class="main-title">Analyse descriptive</h1>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["🌾 Rendements", "🌦️ Météo", "🔗 Corrélations"])

    with tab1:
        if len(df_r) == 0:
            st.info("Aucune donnée de rendement disponible.")
        else:
            st.markdown('<div class="section-header">Statistiques globales — Rendements</div>', unsafe_allow_html=True)

            num_cols_r = ["superficie_ha", "production_tonnes", "rendement_t_ha"]
            labels = {"superficie_ha": "Superficie (ha)", "production_tonnes": "Production (t)", "rendement_t_ha": "Rendement (t/ha)"}

            stats_df = df_r[num_cols_r].describe().T
            stats_df.index = [labels[c] for c in stats_df.index]
            stats_df = stats_df.round(3)
            stats_df.columns = ["N", "Moyenne", "Écart-type", "Min", "Q1 (25%)", "Médiane", "Q3 (75%)", "Max"]
            st.dataframe(stats_df, use_container_width=True)

            st.markdown('<div class="section-header">Analyse par culture</div>', unsafe_allow_html=True)
            grp = df_r.groupby("culture")["rendement_t_ha"].agg(
                N="count", Moyenne="mean", Médiane="median",
                Écart_type="std", Min="min", Max="max"
            ).round(3).reset_index()
            grp.columns = ["Culture", "N", "Moyenne (t/ha)", "Médiane (t/ha)", "Écart-type", "Min", "Max"]
            st.dataframe(grp, use_container_width=True, hide_index=True)

            st.markdown('<div class="section-header">Analyse par région</div>', unsafe_allow_html=True)
            grp_reg = df_r.groupby("region")["rendement_t_ha"].agg(
                N="count", Moyenne="mean", Médiane="median", Écart_type="std"
            ).round(3).reset_index()
            grp_reg.columns = ["Région", "N", "Moyenne (t/ha)", "Médiane (t/ha)", "Écart-type"]
            st.dataframe(grp_reg, use_container_width=True, hide_index=True)

            st.markdown('<div class="section-header">Tests statistiques</div>', unsafe_allow_html=True)
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                stat_val, p_val = stats.shapiro(df_r["rendement_t_ha"]) if len(df_r) >= 3 else (None, None)
                if p_val is not None:
                    verdict = "✅ Distribution normale (p > 0.05)" if p_val > 0.05 else "⚠️ Distribution non-normale (p ≤ 0.05)"
                    st.metric("Test de Shapiro-Wilk (normalité)", f"p = {p_val:.4f}", delta=verdict)
            with col_t2:
                skew = df_r["rendement_t_ha"].skew()
                kurt = df_r["rendement_t_ha"].kurtosis()
                st.metric("Asymétrie (Skewness)", f"{skew:.3f}", delta="Symétrique si proche de 0")
                st.metric("Aplatissement (Kurtosis)", f"{kurt:.3f}", delta="Normale si proche de 0")

    with tab2:
        if len(df_m) == 0:
            st.info("Aucune donnée météorologique disponible.")
        else:
            st.markdown('<div class="section-header">Statistiques globales — Météo</div>', unsafe_allow_html=True)
            num_cols_m = ["temp_min","temp_max","temp_moy","precipitation_mm","humidite_pct","vitesse_vent_kmh","ensoleillement_h"]
            labels_m = {"temp_min":"T. min (°C)","temp_max":"T. max (°C)","temp_moy":"T. moy (°C)",
                        "precipitation_mm":"Précip. (mm)","humidite_pct":"Humidité (%)","vitesse_vent_kmh":"Vent (km/h)","ensoleillement_h":"Ensol. (h)"}
            stats_m = df_m[num_cols_m].describe().T
            stats_m.index = [labels_m.get(c, c) for c in stats_m.index]
            stats_m = stats_m.round(2)
            stats_m.columns = ["N", "Moyenne", "Écart-type", "Min", "Q1", "Médiane", "Q3", "Max"]
            st.dataframe(stats_m, use_container_width=True)

            st.markdown('<div class="section-header">Analyse par région</div>', unsafe_allow_html=True)
            grp_m = df_m.groupby("region")[["temp_moy","precipitation_mm","humidite_pct"]].mean().round(2).reset_index()
            grp_m.columns = ["Région", "Temp. moy (°C)", "Précip. moy (mm)", "Humidité moy (%)"]
            st.dataframe(grp_m, use_container_width=True, hide_index=True)

    with tab3:
        if len(df_r) < 3:
            st.info("Données insuffisantes pour calculer des corrélations (minimum 3 enregistrements).")
        else:
            st.markdown('<div class="section-header">Matrice de corrélation — Rendements</div>', unsafe_allow_html=True)
            corr_cols = ["superficie_ha","production_tonnes","rendement_t_ha"]
            corr_matrix = df_r[corr_cols].corr().round(3)
            corr_matrix.index = ["Superficie","Production","Rendement"]
            corr_matrix.columns = ["Superficie","Production","Rendement"]

            fig_corr = px.imshow(
                corr_matrix, text_auto=True, aspect="auto",
                color_continuous_scale=[[0,"#b7dfc7"],[0.5,"#2d8c4e"],[1,"#1a4731"]],
                zmin=-1, zmax=1, template="plotly_white"
            )
            fig_corr.update_layout(margin=dict(t=10,b=10,l=10,r=10),
                                   paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_corr, use_container_width=True)

            if len(df_m) >= 3:
                st.markdown('<div class="section-header">Matrice de corrélation — Météo</div>', unsafe_allow_html=True)
                corr_m_cols = ["temp_moy","precipitation_mm","humidite_pct","vitesse_vent_kmh","ensoleillement_h"]
                corr_m = df_m[corr_m_cols].corr().round(3)
                corr_m.index = corr_m.columns = ["T.moy","Précip.","Humidité","Vent","Ensol."]
                fig_corr2 = px.imshow(corr_m, text_auto=True, aspect="auto",
                    color_continuous_scale=[[0,"#cce5ff"],[0.5,"#3b8bd4"],[1,"#04345c"]],
                    zmin=-1, zmax=1, template="plotly_white")
                fig_corr2.update_layout(margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_corr2, use_container_width=True)

# ─── PAGE: VISUALISATIONS ─────────────────────────────────────────────────────
elif page == "📈 Visualisations":
    st.markdown('<h1 class="main-title">Visualisations</h1>', unsafe_allow_html=True)
    st.markdown("---")

    if len(df_r) == 0:
        st.info("Aucune donnée disponible pour la visualisation.")
    else:
        tab1, tab2, tab3 = st.tabs(["🌾 Rendements", "🌦️ Météo", "🔍 Analyse bivariée"])

        with tab1:
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.markdown('<div class="section-header">Distribution des rendements</div>', unsafe_allow_html=True)
                fig_hist = px.histogram(df_r, x="rendement_t_ha", nbins=15, color="culture",
                    color_discrete_sequence=px.colors.sequential.Greens_r,
                    labels={"rendement_t_ha": "Rendement (t/ha)", "count": "Fréquence"},
                    template="plotly_white")
                fig_hist.update_layout(margin=dict(t=10,b=20,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_hist, use_container_width=True)

            with col_v2:
                st.markdown('<div class="section-header">Boîtes à moustaches</div>', unsafe_allow_html=True)
                fig_box = px.box(df_r, x="culture", y="rendement_t_ha",
                    color="culture", color_discrete_sequence=px.colors.sequential.Greens,
                    labels={"rendement_t_ha": "Rendement (t/ha)", "culture": "Culture"},
                    template="plotly_white")
                fig_box.update_layout(showlegend=False, margin=dict(t=10,b=20,l=10,r=10),
                                      paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_box, use_container_width=True)

            st.markdown('<div class="section-header">Rendements moyens par région et culture</div>', unsafe_allow_html=True)
            pivot = df_r.groupby(["region","culture"])["rendement_t_ha"].mean().reset_index()
            fig_sun = px.sunburst(pivot, path=["region","culture"], values="rendement_t_ha",
                color="rendement_t_ha", color_continuous_scale=px.colors.sequential.Greens,
                template="plotly_white")
            fig_sun.update_layout(margin=dict(t=10,b=10,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_sun, use_container_width=True)

        with tab2:
            if len(df_m) == 0:
                st.info("Aucune donnée météo.")
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown('<div class="section-header">Températures par région</div>', unsafe_allow_html=True)
                    fig_temp = go.Figure()
                    for reg in df_m["region"].unique():
                        sub = df_m[df_m["region"] == reg]
                        fig_temp.add_trace(go.Box(y=sub["temp_moy"], name=reg))
                    fig_temp.update_layout(template="plotly_white", yaxis_title="Température (°C)",
                        margin=dict(t=10,b=20,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_temp, use_container_width=True)
                with col_m2:
                    st.markdown('<div class="section-header">Précipitations par région</div>', unsafe_allow_html=True)
                    fig_prec = px.bar(
                        df_m.groupby("region")["precipitation_mm"].mean().reset_index(),
                        x="region", y="precipitation_mm",
                        color="precipitation_mm",
                        color_continuous_scale=[[0,"#cce5ff"],[0.5,"#3b8bd4"],[1,"#042c53"]],
                        labels={"precipitation_mm":"Précip. moy (mm)", "region":"Région"},
                        template="plotly_white"
                    )
                    fig_prec.update_layout(showlegend=False, coloraxis_showscale=False,
                        margin=dict(t=10,b=20,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_prec, use_container_width=True)

        with tab3:
            st.markdown('<div class="section-header">Nuage de points : superficie vs rendement</div>', unsafe_allow_html=True)
            fig_scatter = px.scatter(df_r, x="superficie_ha", y="rendement_t_ha",
                color="culture", size="production_tonnes", hover_data=["region","qualite","date"],
                template="plotly_white",
                labels={"superficie_ha":"Superficie (ha)","rendement_t_ha":"Rendement (t/ha)","culture":"Culture"},
                color_discrete_sequence=px.colors.qualitative.Set2)
            fig_scatter.update_layout(margin=dict(t=10,b=20,l=10,r=10), paper_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig_scatter, use_container_width=True)

# ─── PAGE: GESTION DONNÉES ────────────────────────────────────────────────────
elif page == "💾 Gestion des données":
    st.markdown('<h1 class="main-title">Gestion des données</h1>', unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📤 Export", "📥 Import CSV", "🗑️ Administration"])

    with tab1:
        st.markdown('<div class="section-header">Exporter les données</div>', unsafe_allow_html=True)
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            if len(df_r) > 0:
                csv_r = df_r.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter rendements (CSV)", data=csv_r,
                    file_name=f"agridata_rendements_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True)
        with col_e2:
            if len(df_m) > 0:
                csv_m = df_m.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Exporter météo (CSV)", data=csv_m,
                    file_name=f"agridata_meteo_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv", use_container_width=True)

        if len(df_r) > 0:
            st.markdown('<div class="section-header">Aperçu complet — Rendements</div>', unsafe_allow_html=True)
            st.dataframe(df_r.drop(columns=["id","created_at"], errors="ignore"),
                         use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-header">Importer depuis un fichier CSV</div>', unsafe_allow_html=True)
        st.markdown("**Format attendu pour les rendements :** date, region, culture, superficie_ha, production_tonnes, rendement_t_ha, qualite, remarques")
        uploaded = st.file_uploader("Choisir un fichier CSV", type=["csv"])
        if uploaded:
            try:
                df_import = pd.read_csv(uploaded)
                st.success(f"✅ Fichier chargé : {len(df_import)} lignes")
                st.dataframe(df_import.head(), use_container_width=True)
                if st.button("Importer dans la base de données"):
                    conn = get_conn()
                    for _, row in df_import.iterrows():
                        try:
                            conn.execute("""INSERT INTO rendements (date,region,culture,superficie_ha,production_tonnes,rendement_t_ha,qualite,remarques)
                                VALUES (?,?,?,?,?,?,?,?)""",
                                (row.get("date",""), row.get("region",""), row.get("culture",""),
                                 row.get("superficie_ha",0), row.get("production_tonnes",0),
                                 row.get("rendement_t_ha",0), row.get("qualite",""), row.get("remarques","")))
                        except:
                            pass
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {len(df_import)} enregistrements importés !")
                    st.rerun()
            except Exception as e:
                st.error(f"Erreur lors de la lecture du fichier : {e}")

    with tab3:
        st.markdown('<div class="section-header">Administration de la base de données</div>', unsafe_allow_html=True)
        st.warning("⚠️ Les suppressions sont irréversibles.")
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("🗑️ Supprimer TOUS les rendements", type="secondary", use_container_width=True):
                conn = get_conn()
                conn.execute("DELETE FROM rendements")
                conn.commit()
                conn.close()
                st.success("Données rendements supprimées.")
                st.rerun()
        with col_a2:
            if st.button("🗑️ Supprimer TOUTES les données météo", type="secondary", use_container_width=True):
                conn = get_conn()
                conn.execute("DELETE FROM meteo")
                conn.commit()
                conn.close()
                st.success("Données météo supprimées.")
                st.rerun()
