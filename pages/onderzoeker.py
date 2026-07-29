import streamlit as st
import pandas as pd
import sqlite3
import os
db_path = os.path.join(os.path.dirname(__file__),"..", "spider.db")
conn = sqlite3.connect(db_path)

from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def genereer_bio(naam):
    naam_sql = naam.replace("'", "''")
    publicaties = pd.read_sql(f"""
        SELECT title, abstract FROM publications 
        WHERE authors LIKE '%{naam_sql}%'
        LIMIT 5
    """, conn)
    
    if publicaties.empty:
        return None
    
    titels = publicaties["title"].tolist()
    prompt = f"Geef een korte bio van 2-3 zinnen over onderzoeker {naam} op basis van deze publicaties: {titels}"
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# CSS
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Laad data
personen = pd.read_sql("SELECT * FROM persons" , conn)
expertise = pd.read_sql("SELECT * FROM expertise" , conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise" , conn)


# Check session state
if "geselecteerde_persoon" not in st.session_state or st.session_state.geselecteerde_persoon is None:
    st.warning("Geen onderzoeker geselecteerd.")
    if st.button("← Terug naar zoeken", key="terug_leeg"):
        st.switch_page("app.py")

else:
    persoon_id = st.session_state.geselecteerde_persoon
    persoon = personen[personen["id"] == persoon_id].iloc[0]

    # Terug knop bovenaan
    if st.button("← Terug naar zoeken", key="terug_boven"):
        st.switch_page("app.py")

    # Naam en info
    st.title(persoon["name"])
    col1, col2 = st.columns([2, 1])
    with col1:
         st.subheader(persoon["department"])
         bio = genereer_bio(persoon["name"]) 
    if bio:
        st.write(bio)       
    with col2:
        st.image("https://picsum.photos/300/400", width=300)

    st.divider()
    st.subheader("📧 Contact")
    st.write(f"📧 emailadres@amsterdamumc.nl")
    st.write(f"🔗 [Zoek op PubMed](https://pubmed.ncbi.nlm.nih.gov/?term={persoon['name'].replace(' ', '+')})")



    # Expertise
    st.divider()
    st.subheader("Expertise")
    exp_ids = personen_expertise[personen_expertise["person_id"] == persoon_id]["expertise_id"].tolist()
    exp_details = expertise[expertise["id"].isin(exp_ids)]
    for _, exp in exp_details.iterrows():
        if st.button(f"🔬 {exp['label']}", key=f"exp_{exp['id']}"):
            st.session_state.geselecteerde_expertise = exp["id"]
            st.switch_page("pages/expertise.py")

    # Publicaties
    st.divider()
    st.subheader("📄 Publicaties")
    
    naam_sql = persoon["name"].replace("'", "''")
    publicaties = pd.read_sql(f"""
        SELECT title, year, pubmed_url 
        FROM publications 
        WHERE authors LIKE '%{naam_sql}%'
        ORDER BY year DESC
        LIMIT 10
    """, conn)
    
    if publicaties.empty:
        st.write("Geen publicaties gevonden.")
    else:
        for _, pub in publicaties.iterrows():
            if pub["pubmed_url"]:
                st.markdown(f"📄 [{pub['title'][:80]}...]({pub['pubmed_url']}) — *{pub['year']}*")
            else:
                st.write(f"📄 {pub['title'][:80]}... — *{pub['year']}*")     

