import streamlit as st
import pandas as pd
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "spider.db")
conn = sqlite3.connect(db_path)

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

# Haal persoon op
persoon_id = st.session_state.get("lopende_projecten_persoon")
personen = pd.read_sql("SELECT * FROM persons", conn)

if persoon_id:
    persoon = personen[personen["id"] == persoon_id]
    if not persoon.empty:
        naam = persoon.iloc[0]["name"]
        st.title(f"🔬 Lopende projecten — {naam}")
    else:
        st.title("🔬 Lopende projecten")
else:
    st.title("🔬 Lopende projecten")

st.subheader("Kies een project om meer te lezen")
st.divider()

# Laad projecten
if persoon_id:
    projecten = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE leider_id = {persoon_id}", conn)
else:
    projecten = pd.read_sql("SELECT * FROM lopende_projecten", conn)

if projecten.empty:
    st.info("Geen lopende projecten gevonden.")
else:
    for _, project in projecten.iterrows():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**🟢 {project['naam']}**")
            st.write(f"{project['beschrijving'][:120]}...")
            st.write(f"📅 Start: {project['datum']}")
            if project.get('einddatum'):
                st.write(f"📅 Einde: {project['einddatum']}")
        with col2:
            if st.button("Bekijk", key=f"overzicht_{project['id']}"):
                st.session_state.geselecteerd_lopend_project = int(project["id"])
                st.switch_page("pages/lopend_project.py")
        st.divider()

if st.button("← Terug"):
    st.switch_page("app.py")