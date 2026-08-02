import streamlit as st
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Database verbinding
# conn = sqlite3.connect("spider.db")
import os
db_path = os.path.join(os.path.dirname(__file__), "spider.db")
conn = sqlite3.connect(db_path)

from dotenv import load_dotenv #laad de .enc library
import os                      #laad de os library om bestanden te lezen

load_dotenv()                  # open het .env bestand
api_key = os.getenv("GROQ_API_KEY") # haal de sleutel eruit


from groq import Groq
from login import login_pagina


if "ingelogd" not in st.session_state:
    st.session_state.ingelogd = False

if not st.session_state.ingelogd:
    login_pagina()
    st.stop()

gebruikersnaam = st.session_state.get("gebruikersnaam", "")
rol = st.session_state.get("rol", "")



# Sidebar menu navigatie voor ingelogde gebruiker
st.sidebar.write(f"👤 **{gebruikersnaam}**")
st.sidebar.divider()

# Knop naar eigen profielpagina
if st.sidebar.button("👤 Profiel"):
    st.switch_page("pages/mijn_profiel.py")

# Knop naar kennisgraaf pagina
st.sidebar.divider()    
if st.sidebar.button("🕸️ Kennisgraaf"):
    st.switch_page("pages/kennisgraaf.py")

# Beheer knop alleen zichtbaar voor beheerder
if st.session_state.get("rol") == "beheerder":
    if st.sidebar.button("⚙️ Beheer"):
        st.switch_page("pages/beheer.py")
# Uitloggen — reset sessie en herlaad pagina
st.sidebar.divider()
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()
# Verberg automatische Streamlit navigatie in sidebar
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)



# Maak verbinding met Groq AI client
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

# Initialiseer geselecteerde persoon als leeg
if "geselecteerde_persoon" not in st.session_state:
    st.session_state.geselecteerde_persoon = None

def genereer_samenvatting(zoekterm, resultaat, taal="Nederlands"):
        # Haal namen op uit zoekresultaten
    namen = resultaat["name"].tolist()

       # Maak prompt op basis van gekozen taal 
    if taal == "Nederlands":
        prompt = f"Een gebruiker zoekt naar '{zoekterm}'. De volgende onderzoekers zijn gevonden: {namen}. Geef een korte samenvatting in 2 zinnen in het Nederlands."
    else:
        prompt = f"A user searches for '{zoekterm}'. The following researchers were found: {namen}. Give a short summary in 2 sentences in English."
        
        # Stuur prompt naar Groq AI en ontvang antwoord
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


personen = pd.read_sql("SELECT * FROM persons", conn) #personen inladen
expertise = pd.read_sql("SELECT * FROM expertise", conn) #expertise inladen
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn) #tussentabel inladen


st.title("Spider")
st.subheader("Zoek onderzoeksexpertise binnen Division 9")

department_filter = st.selectbox(
    "Filter op department",
    ["Alle"] + personen["department"].unique().tolist()
)
# Taal selectie
if "taal" not in st.session_state:
    st.session_state.taal = "Nederlands"

# taal = st.radio("🌐 Taal / Language:", ["Nederlands", "English"], #taalknop uitgeschakeld -  te veel werk om alles te vertalen.
                # horizontal=True,
                # index=0 if st.session_state.taal == "Nederlands" else 1)
# st.session_state.taal = taal


# Taal standaard Nederlands
taal = "Nederlands"
if "laatste_zoekterm" not in st.session_state:
    st.session_state.laatste_zoekterm = ""
zoekterm = st.text_input("Zoek op naam, project of expertise" if taal == "Nederlands" else "Search by name, project or expertise", 
                          value=st.session_state.laatste_zoekterm)  
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
   
 
   
# Combineer alles
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

    col_links, col_rechts = st.columns([1, 1])

    with col_links:
        st.subheader("Gevonden onderzoekers")
        lopende = pd.read_sql("SELECT leider_id FROM lopende_projecten", conn)
        actieve_leiders = lopende["leider_id"].tolist()

        for _, persoon in resultaat.iterrows():
            label = f"🟢 {persoon['name']}" if persoon["id"] in actieve_leiders else f"👤 {persoon['name']}"
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button(label, key=f"persoon_{persoon['id']}"):
                    st.session_state.geselecteerde_persoon = persoon["id"]
                    st.switch_page("pages/onderzoeker.py")
            with col2:
                if persoon["id"] in actieve_leiders:
                    if st.button("🔬 Project", key=f"project_{persoon['id']}"):
                        project = pd.read_sql(f"SELECT id FROM lopende_projecten WHERE leider_id = {persoon['id']} LIMIT 1", conn)
                        if not project.empty:
                            st.session_state.geselecteerd_lopend_project = int(project.iloc[0]["id"])
                            st.switch_page("pages/lopend_project.py")

        # Expertise
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

    with col_rechts:
        if not resultaat.empty:
            with st.spinner("Samenvatting genereren ..."):
                samenvatting = genereer_samenvatting(zoekterm, resultaat)
                st.info(samenvatting)

else:
    st.info("Typ een naam, expertise of project om te zoeken.")   