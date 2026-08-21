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

st.title("📊 Epidemiologie")

st.subheader("Wat is epidemiologie?")
st.write("""
Epidemiologie is de wetenschap die bestudeert hoe ziekten zich verspreiden in 
bevolkingsgroepen en welke factoren bijdragen aan het ontstaan van ziekten. 
Het is de basis van de volksgezondheid en helpt bij het ontwikkelen van 
preventiestrategieën en richtlijnen.
""")

st.divider()

st.subheader("Hoe werkt het?")
st.write("""
Epidemiologen verzamelen en analyseren gegevens over grote groepen mensen over 
langere perioden. Ze zoeken naar verbanden tussen risicofactoren en ziekten, 
en evalueren de effectiviteit van interventies. Moderne epidemiologie maakt 
steeds meer gebruik van big data en AI om complexe patronen te ontdekken.
""")

st.divider()

st.subheader("Wat doet het?")
st.write("""
Epidemiologisch onderzoek levert de wetenschappelijke basis voor medische 
richtlijnen, vaccinatieprogramma's en volksgezondheidsbeleid. Het beantwoordt 
vragen als: Wie loopt risico? Waarom worden mensen ziek? Welke behandelingen 
werken het best voor welke groepen?
""")

st.divider()

st.subheader("📊 Onderzoek — Martijn C Schut")
st.write("""
Prof. Martijn C Schut past epidemiologische methoden toe in zijn onderzoek naar 
AI in de gezondheidszorg. Hij onderzoekt hoe AI-modellen presteren in diverse 
patiëntenpopulaties en hoe epidemiologische principes kunnen helpen bij het 
eerlijk en effectief implementeren van AI-systemen in de klinische praktijk.
""")

st.divider()
st.subheader("📄 Relevante publicaties")
publicaties = pd.read_sql("""
    SELECT title, year, pubmed_url FROM publications 
    WHERE LOWER(abstract) LIKE '%epidemiology%'
    OR LOWER(keywords) LIKE '%epidemiology%'
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
    