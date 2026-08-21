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

st.title("🔬 Laboratorium Diagnostiek")

st.subheader("Wat is laboratorium diagnostiek?")
st.write("""
Laboratorium diagnostiek is het vakgebied dat zich bezighoudt met het analyseren 
van lichaamsmateriaal zoals bloed, urine en weefsel om ziekten te detecteren, 
monitoren en behandelen. Het is de basis van moderne geneeskunde — meer dan 70% 
van alle medische beslissingen is gebaseerd op laboratoriumuitslagen.
""")

st.divider()

st.subheader("Hoe werkt het?")
st.write("""
Laboratoriumtests meten specifieke stoffen in het lichaam zoals eiwitten, enzymen, 
hormonen en genetisch materiaal. De resultaten worden vergeleken met referentiewaarden 
om te bepalen of iets normaal of afwijkend is. Moderne laboratoria gebruiken 
geautomatiseerde systemen en AI om grote hoeveelheden tests snel en nauwkeurig 
te verwerken.
""")

st.divider()

st.subheader("Wat doet het?")
st.write("""
Laboratorium diagnostiek speelt een cruciale rol bij vroege opsporing van ziekten, 
monitoring van behandelingen en het bepalen van de juiste dosering van medicijnen. 
Zonder laboratoriumdiagnostiek zouden artsen veel vaker in het duister tasten bij 
het stellen van diagnoses.
""")

st.divider()

st.subheader("🔬 Onderzoek — Robert de Jonge")
st.write("""
Prof. dr. Robert de Jonge is hoogleraar Laboratoriumgeneeskunde bij Amsterdam UMC. 
Hij werkt aan de ontwikkeling en validatie van nieuwe diagnostische methoden, 
waaronder geautomatiseerde mass spectrometrie systemen voor het meten van serum 
analyten. Zijn onderzoek richt zich op het verbeteren van de nauwkeurigheid en 
efficiëntie van laboratoriumtests in de klinische praktijk.
""")

st.divider()
st.subheader("📄 Relevante publicaties")
publicaties = pd.read_sql("""
    SELECT title, year, pubmed_url FROM publications 
    WHERE LOWER(abstract) LIKE '%laboratory%'
    OR LOWER(abstract) LIKE '%diagnostics%'
    OR LOWER(keywords) LIKE '%laboratory%'
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