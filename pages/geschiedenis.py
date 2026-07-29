import streamlit as st
import pandas as pd
import sqlite3
import os
db_path = os.path.join(os.path.dirname(__file__), "spider.db")
conn = sqlite3.connect(db_path)

# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Alleen voor beheerder
if st.session_state.get("rol") != "beheerder":
    st.error("Je hebt geen toegang tot deze pagina!")
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
if st.sidebar.button("⚙️ Beheer"):
    st.switch_page("pages/beheer.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

# Pagina inhoud
st.title("📋 Wijzigingsgeschiedenis")
st.subheader("Alle wijzigingen door beheerders")

wijzigingen = pd.read_sql("SELECT * FROM wijzigingen", conn)
if wijzigingen.empty:
    st.info("Nog geen wijzigingen geregistreerd.")
else:
    st.dataframe(wijzigingen[::-1])