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
st.title("🧬 Gene Expression")

# 1. Wat is het?
st.subheader("Wat is gene expression?")
st.write("""
Gene expression is het proces waarbij informatie uit een gen wordt gebruikt om 
een functioneel product te maken — meestal een eiwit. Het is de manier waarop 
genetische instructies worden uitgevoerd in een cel. Niet alle genen zijn altijd 
actief — welke genen 'aan' of 'uit' staan bepaalt wat een cel doet en hoe het zich 
gedraagt.
""")

st.divider()

# 2. Hoe werkt het?
st.subheader("Hoe werkt het in het lichaam?")
st.write("""
Het proces bestaat uit twee stappen:
1. **Transcriptie** — het DNA wordt afgelezen en omgezet naar RNA
2. **Translatie** — het RNA wordt omgezet naar een eiwit

Verschillende cellen hebben hetzelfde DNA maar andere gene expression patronen — 
daarom is een hartcel anders dan een hersencel, ook al bevatten ze dezelfde genen.
""")

st.divider()

# 3. Wat doet het?
st.subheader("Wat doet het?")
st.write("""
Gene expression bepaalt welke eiwitten een cel aanmaakt en daarmee alle functies 
van die cel. Verstoorde gene expression speelt een rol bij veel ziekten — waaronder 
kanker, auto-immuunziekten en erfelijke aandoeningen. Door gene expression te meten 
kunnen onderzoekers ziekten beter begrijpen en nieuwe behandelingen ontwikkelen.
""")

st.divider()

# 4. Onderzoek Robert de Jonge
st.subheader("🔬 Onderzoek — Robert de Jonge")
st.write("""
Prof. dr. Robert de Jonge onderzoekt gene expression patronen in relatie tot 
laboratorium diagnostiek en farmacologie. Zijn werk richt zich op het begrijpen 
van hoe genen betrokken bij het metabolisme van geneesmiddelen zoals methotrexaat 
worden gereguleerd, en hoe variaties in gene expression de effectiviteit en 
bijwerkingen van behandelingen beïnvloeden bij patiënten met inflammatoire ziekten.
""")

# Relevante publicaties
st.divider()
st.subheader("📄 Relevante publicaties")
publicaties = pd.read_sql("""
    SELECT title, year, pubmed_url FROM publications 
    WHERE LOWER(abstract) LIKE '%gene expression%'
    OR LOWER(keywords) LIKE '%gene expression%'
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