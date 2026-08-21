import streamlit as st
import pandas as pd
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "spider.db")
conn = sqlite3.connect(db_path)

if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

st.markdown("""<style>[data-testid="stSidebarNav"] { display: none; }</style>""", unsafe_allow_html=True)

st.sidebar.write(f"👤 **{st.session_state.get('gebruikersnaam', '')}**")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

st.title("🧬 Amyloid Beta")

st.subheader("Wat is amyloid beta?")
st.write("""
Amyloid beta is een eiwit dat van nature voorkomt in de hersenen. Bij sommige 
mensen hoopt dit eiwit zich op en vormt het klonters — amyloid plaques — die 
zenuwcellen beschadigen. Deze plaques zijn een van de belangrijkste kenmerken 
van de ziekte van Alzheimer.
""")

st.divider()

st.subheader("Hoe werkt het in het lichaam?")
st.write("""
Amyloid beta wordt geproduceerd door de afbraak van het amyloid precursor eiwit (APP). 
Normaal gesproken wordt amyloid beta afgebroken en verwijderd. Bij Alzheimer raakt 
dit systeem verstoord, waardoor amyloid beta zich ophoopt en plaques vormt tussen 
zenuwcellen. Dit leidt tot ontsteking en uiteindelijk het afsterven van neuronen.
""")

st.divider()

st.subheader("Wat doet het?")
st.write("""
Amyloid beta speelt een centrale rol bij de ontwikkeling van Alzheimer. Het meten 
van amyloid beta in bloed of hersenvloeistof wordt gebruikt als vroege biomarker 
voor Alzheimer — jaren voordat symptomen optreden. Nieuwe behandelingen richten 
zich op het verwijderen van amyloid plaques om de ziekte te vertragen.
""")

st.divider()

st.subheader("🧠 Onderzoek — Sjors In 't Veld")
st.write("""
Dr. Sjors In 't Veld onderzoekt amyloid beta als biomarker voor neurodegeneratieve 
ziekten. Zijn werk richt zich op de diagnostische waarde van plasma amyloid beta 
metingen voor vroege opsporing van Alzheimer en andere amyloid-gerelateerde 
aandoeningen, waaronder hereditaire transthyretine amyloidose.
""")

st.divider()
st.subheader("🤖 Onderzoek — Martijn C Schut")
st.write("""
Prof. Martijn C Schut onderzoekt de rol van amyloid biomarkers in het kader 
van AI-gestuurde diagnostiek. Hij werkt aan voorspellende modellen voor vroege 
detectie van amyloid-gerelateerde aandoeningen zoals Alzheimer, met behulp van 
bloedtesten en machine learning.
""")

st.divider()
st.subheader("📄 Relevante publicaties")
publicaties = pd.read_sql("""
    SELECT title, year, pubmed_url FROM publications 
    WHERE LOWER(abstract) LIKE '%amyloid%'
    OR LOWER(keywords) LIKE '%amyloid%'
    LIMIT 5
""", conn)

if publicaties.empty:
    st.write("Geen publicaties gevonden.")
else:
    for _, pub in publicaties.iterrows():
        if pub["pubmed_url"]:
            st.markdown(f"📄 [{pub['title'][:80]}...]({pub['pubmed_url']}) — *{pub['year']}*")
        else:
            st.write(f"📄 {pub['title'][:80]}... — *{pub['year']}*")

st.divider()
if st.button("← Terug naar zoeken"):
    st.switch_page("app.py")