import streamlit as st
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Database verbinding
conn = sqlite3.connect("spider.db")

from dotenv import load_dotenv #laad de .enc library
import os                      #laad de os library om bestanden te lezen

load_dotenv()                  # open het .env bestand
api_key = os.getenv("GROQ_API_KEY") # haal de sleutel eruit
#st.write(api_key) #debug regel
# st.write(st.session_state.get("rol")) #debug regel

from groq import Groq
from login import login_pagina


if "ingelogd" not in st.session_state:
    st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    login_pagina()
    st.stop()

gebruikersnaam = st.session_state.get("gebruikersnaam", "")
rol = st.session_state.get("rol", "")



# Sidebar menu
st.sidebar.write(f"👤 **{gebruikersnaam}**")
st.sidebar.divider()

if st.sidebar.button("👤 Profiel"):
    st.switch_page("pages/my_profile.py")

st.sidebar.divider()    
if st.sidebar.button("🕸️ Kennisgraaf"):
    st.switch_page("pages/knowledgegraph.py")

if st.session_state.get("rol") == "beheerder":
    if st.sidebar.button("⚙️ Beheer"):
        st.switch_page("pages/beheer.py")

st.sidebar.divider()
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)




client = Groq(api_key=api_key)

# Laad embedding model
@st.cache_resource
def laad_model():
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

model = laad_model()

def semantisch_zoeken(zoekterm, top_n=15):
    # Maak embedding van zoekterm
    zoek_embedding = model.encode(zoekterm)
    
    # Laad alle embeddings uit database
    embeddings_df = pd.read_sql("SELECT pmid, embedding FROM publication_embeddings", conn)
    
    scores = []
    for _, rij in embeddings_df.iterrows():
        pub_embedding = np.array(json.loads(rij["embedding"]))
        score = np.dot(zoek_embedding, pub_embedding) / (np.linalg.norm(zoek_embedding) * np.linalg.norm(pub_embedding))
        scores.append((rij["pmid"], float(score)))
    
    # Sorteer op score
    scores.sort(key=lambda x: x[1], reverse=True)
    top_pmids = [s[0] for s in scores[:top_n]]
    
    return top_pmids

if "geselecteerde_persoon" not in st.session_state:
    st.session_state.geselecteerde_persoon = None

def genereer_samenvatting(zoekterm, resultaat):   # Haal alle namen op uit de resultaten tabel als een lijst
    namen = resultaat["name"].tolist()
    # Maak een prompt aan voor het AI model
    # f-string zodat we variabelen kunnen invoegen in de tekst
    prompt = f" Een gebruiker zoekt naar ' {zoekterm}'.De colgende onderzoekers zijn gevonden:     {namen}. Geef een korte samenvatting in 2 zinnen over wie deze onderzoekers zijn en wat ze doen."

# Stuur de prompt naar Groq en wacht op een antwoord
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    # Geef de tekst terug uit het eerste antwoord van het model

    return response.choices[0]. message.content

personen = pd.read_sql("SELECT * FROM persons", conn) #personen inladen
expertise = pd.read_sql("SELECT * FROM expertise", conn) #expertise inladen
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn) #tussentabel inladen


st.title("Spider")
st.subheader("Zoek onderzoeksexpertise binnen Division 9")

department_filter = st.selectbox(
    "Filter op department",
    ["Alle"] + personen["department"].unique().tolist()
)

# st.write(expertise) Debug regel
if "laatste_zoekterm" not in st.session_state:
    st.session_state.laatste_zoekterm = ""
zoekterm = st.text_input("Zoek op naam, project of expertise")
if zoekterm:
    st.session_state.laatste_zoekterm = zoekterm
if zoekterm:

    if department_filter != "Alle":
        personen_gefilterd = personen[personen["department"] == department_filter]
    else:
        personen_gefilterd = personen
    # Zoek op personen
    naam_resultaat = personen_gefilterd[personen_gefilterd["name"].str.contains(zoekterm, case=False)|
    personen_gefilterd["department"].str.contains(zoekterm, case=False)]

    # Zoek op expertise
    expertise_match = expertise[expertise["label"].str.contains(zoekterm, case=False)]
    expertise_ids = expertise_match["id"].tolist()
    personen_ids = personen_expertise[personen_expertise["expertise_id"].isin(expertise_ids)]["person_id"].tolist()
    expertise_resultaat = personen[personen["id"].isin(personen_ids)]
   

 
   
   #combineer alles
    resultaat = pd.concat([naam_resultaat, expertise_resultaat]).drop_duplicates()

    # Semantisch zoeken via publicaties
    top_pmids = semantisch_zoeken(zoekterm)
    semantische_resultaten = pd.read_sql(f"""
    SELECT DISTINCT p.* FROM persons p
    JOIN publications pub ON (
        LOWER(pub.authors) LIKE LOWER('%' || p.name || '%')
        OR LOWER(pub.authors) LIKE LOWER('%' || SUBSTR(p.name, INSTR(p.name, ' ') + 1) || '%')
    )
    WHERE pub.pmid IN ({','.join(['?']*len(top_pmids))})
""", conn, params=top_pmids)    
    
    # Voeg toe aan resultaten
    resultaat = pd.concat([resultaat, semantische_resultaten]).drop_duplicates()
    st.success(f"{len(resultaat)} onderzoeker(s) gevonden")

    # Gevonden onderzoekers
    st.subheader("Gevonden onderzoekers")
    for _, persoon in resultaat.iterrows():
        if st.button(f"👤 {persoon['name']}", key=f"persoon_{persoon['id']}"):
            st.session_state.geselecteerde_persoon = persoon["id"]
            st.switch_page("pages/researcher.py")

    # Expertise — apart blok buiten de loop hierboven
    st.subheader("Expertise")
    for _, persoon in resultaat.iterrows():
        exp_ids = personen_expertise[personen_expertise["person_id"] == persoon["id"]]["expertise_id"].tolist()
        exp_details = expertise[expertise["id"].isin(exp_ids)]
        if not exp_details.empty:
            st.write(f"**{persoon['name']}:**")
            for _, exp in exp_details.iterrows():
                if st.button(f"🔬 {exp['label']}", key=f"exp_{persoon['id']}_{exp['id']}"):
                    st.session_state.geselecteerde_expertise = exp["id"]
                    st.switch_page("pages/expertise.py")

    if not resultaat.empty:
        with st.spinner("Samenvatting genereren ..."):
            samenvatting = genereer_samenvatting(zoekterm, resultaat)
            st.info(samenvatting)