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

# Pagina inhoud
st.title("💊 Methotrexaat")

# 1. Wat is het?
st.subheader("Wat is methotrexaat?")
st.write("""
Methotrexaat is een geneesmiddel dat oorspronkelijk werd ontwikkeld als chemotherapie 
voor kanker, maar nu ook veel wordt gebruikt bij auto-immuunziekten zoals reumatoïde 
artritis, de ziekte van Crohn en psoriasis. Het behoort tot de groep van antimetabolieten 
— stoffen die de aanmaak van DNA in cellen remmen.
""")

st.divider()

# 2. Hoe werkt het?
st.subheader("Hoe werkt het in het lichaam?")
st.write("""
Methotrexaat werkt door het enzym dihydrofolaatreductase (DHFR) te blokkeren. 
Dit enzym is nodig voor de aanmaak van foliumzuur, dat cellen nodig hebben om zich 
te delen. Door dit te blokkeren remt methotrexaat de groei van snel delende cellen 
— zowel kankercellen als ontstekingscellen.
""")

st.divider()

# 3. Wat doet het?
st.subheader("Wat doet het?")
st.write("""
Bij lage doses onderdrukt methotrexaat het immuunsysteem en vermindert ontstekingen. 
Bij hogere doses doodt het snel delende cellen, wat het effectief maakt bij bepaalde 
vormen van kanker zoals leukemie.
""")

st.divider()

# 4. Onderzoek Robert de Jonge
st.subheader("🔬 Onderzoek — Robert de Jonge")
st.write("""
Prof. dr. Robert de Jonge heeft uitgebreid onderzoek gedaan naar methotrexaat 
polyglutamaten — de actieve vorm van methotrexaat in rode bloedcellen. Zijn onderzoek 
richt zich op het meten van deze concentraties om de effectiviteit van de behandeling 
te monitoren bij kinderen met leukemie en patiënten met reumatoïde artritis.
""")

# Relevante publicaties
st.divider()
st.subheader("📄 Relevante publicaties")
publicaties = pd.read_sql("""
    SELECT title, year, pubmed_url FROM publications 
    WHERE LOWER(keywords) LIKE '%methotrexate%'
    OR LOWER(abstract) LIKE '%methotrexate%'
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