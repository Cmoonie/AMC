import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date

# Database verbinding
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "spider.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# CSS
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.write(f"👤 **{st.session_state.get('gebruikersnaam', '')}**")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

# Laad data
personen = pd.read_sql("SELECT * FROM persons", conn)
projecten = pd.read_sql("SELECT * FROM lopende_projecten", conn)
deelnemers = pd.read_sql("SELECT * FROM project_deelnemers", conn)

# Pagina
st.title("🔬 Lopend project")

# Haal project op uit session state
if "geselecteerd_lopend_project" not in st.session_state or st.session_state.geselecteerd_lopend_project is None:
    st.warning("Geen project geselecteerd.")
    if st.button("← Terug naar zoeken"):
        st.switch_page("app.py")
else:
    project_id = st.session_state.geselecteerd_lopend_project
    project = projecten[projecten["id"] == project_id].iloc[0]
    leider = personen[personen["id"] == project["leider_id"]].iloc[0]

    st.title(project["naam"])
    st.write(f"**Projectleider:** {leider['name']}")
    st.write(f"**Gestart:** {project['datum']}")
    st.write(project["beschrijving"])

    st.divider()
    
    # Haal ingelogde gebruiker op
    gebruikersnaam = st.session_state.get("gebruikersnaam", "")
    cursor.execute("SELECT id FROM persons WHERE name = ?", (gebruikersnaam,))
    result = cursor.fetchone()
    eigen_id = result[0] if result else None

    # Deelnemers tonen
    st.subheader("👥 Deelnemers")
    deelnemer_ids = deelnemers[deelnemers["project_id"] == project_id]["persoon_id"].tolist()
    betrokken = personen[personen["id"].isin(deelnemer_ids)]
    for _, persoon in betrokken.iterrows():
        st.write(f"👤 {persoon['name']}")

    st.divider()

    # Aanmelden check
if eigen_id == project["leider_id"]:
        st.info("✅ Jij bent de projectleider.")
elif eigen_id in deelnemer_ids:
        st.info("✅ Je bent aangemeld voor dit project.")
        if st.button("❌ Afmelden"):
            cursor.execute("DELETE FROM project_deelnemers WHERE project_id = ? AND persoon_id = ?",
                           (project_id, eigen_id))
            conn.commit()
            st.success("✅ Je bent afgemeld!")
            st.rerun()


if st.button("← Terug naar zoeken"):
      
        st.switch_page("app.py")