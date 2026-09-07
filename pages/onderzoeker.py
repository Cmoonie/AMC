import streamlit as st
import pandas as pd
import sqlite3
import os

# set_page_config MOET de allereerste Streamlit-aanroep zijn in het bestand
st.set_page_config(layout="wide")

db_path = os.path.join(os.path.dirname(__file__), "..", "spider.db")
conn = sqlite3.connect(db_path)

from groq import Groq
from dotenv import load_dotenv

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
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Styling
from styling import apply_styling
apply_styling("profiel")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Laad data
personen = pd.read_sql("SELECT * FROM persons", conn)
expertise = pd.read_sql("SELECT * FROM expertise", conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn)

# Mapping van expertise-label (lowercase) naar uitgewerkte pagina
# Zelfde dict als in app.py — hou deze twee synchroon
uitgewerkte_expertise = {
    # Robert
    "methotrexate": "pages/expertise_methotrexaat.py",
    "methotrexaat": "pages/expertise_methotrexaat.py",
    "methotrexate polyglutamates": "pages/expertise_methotrexaat.py",
    "methotrexate polyglutamate": "pages/expertise_methotrexaat.py",
    "gene expression": "pages/expertise_gene_expression.py",
    "laboratory medicine": "pages/expertise_laboratorium_diagnostiek.py",

    # Sjors
    "neurofilament light chain": "pages/expertise_neurofilament.py",
    "amyloid beta": "pages/expertise_amyloid.py",
    "systemic amyloidosis": "pages/expertise_amyloid.py",
    "attrv amyloidosis": "pages/expertise_amyloid.py",

    # Martijn
    "clinical decision making": "pages/expertise_clinical_decision.py",
    "clinical prediction models": "pages/expertise_clinical_decision.py",
    "epidemiology": "pages/expertise_epidemiology.py",
    "clinical practice guidelines": "pages/expertise_clinical_decision.py",
    "alzheimer": "pages/expertise_amyloid.py",
}

# Nette paginanamen voor de knoptekst
pagina_namen = {
    "pages/expertise_methotrexaat.py": "Methotrexaat",
    "pages/expertise_gene_expression.py": "Gene Expression",
    "pages/expertise_laboratorium_diagnostiek.py": "Laboratorium Diagnostiek",
    "pages/expertise_neurofilament.py": "Neurofilament Light Chain",
    "pages/expertise_amyloid.py": "Amyloid Beta",
    "pages/expertise_clinical_decision.py": "Clinical Decision Making",
    "pages/expertise_epidemiology.py": "Epidemiologie",
}

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

    # Naam + cirkel + department op zelfde rij
    initialen = "".join([naam[0] for naam in persoon['name'].split() if naam])[:2].upper()

    col_info, col_cirkel = st.columns([2, 1])
    with col_info:
        st.title(persoon["name"])
        st.subheader(persoon["department"])
        bio = genereer_bio(persoon["name"])
        if bio:
            st.write(bio)
    with col_cirkel:
        st.markdown(f"""
                <div style="
                    width: 200px;
                    height: 200px;
                    border-radius: 50%;
                    background-color: #003082;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin: auto;
                ">
                    <span style="
                        color: white;
                        font-size: 72px;
                        font-weight: bold;
                        font-family: Arial;
                    ">{initialen}</span>
                </div>
            """, unsafe_allow_html=True)

    st.divider()
    st.subheader("📧 Contact")
    st.write(f"📧 emailadres@amsterdamumc.nl")
    st.write(f"🔗 [Zoek op PubMed](https://pubmed.ncbi.nlm.nih.gov/?term={persoon['name'].replace(' ', '+')})")

    # Expertise — alleen tags uit uitgewerkte_expertise, 1 knop per unieke pagina
    st.divider()
    st.subheader("Expertise")

    exp_ids = personen_expertise[personen_expertise["person_id"] == persoon_id]["expertise_id"].tolist()
    exp_details = expertise[expertise["id"].isin(exp_ids)]
    gematchte = exp_details[exp_details["label"].str.lower().isin(uitgewerkte_expertise)]

    if gematchte.empty:
        st.write("Geen uitgewerkte expertise gevonden voor deze onderzoeker.")
    else:
        bestemmingen = {}
        for _, exp in gematchte.iterrows():
            pagina = uitgewerkte_expertise[exp["label"].lower()]
            if pagina not in bestemmingen:
                bestemmingen[pagina] = True

        for pagina in bestemmingen:
            naam = pagina_namen.get(pagina, pagina)
            if st.button(f"🔬 {naam}", key=f"exp_{persoon_id}_{pagina}"):
                st.switch_page(pagina)

    # Lopende projecten
    st.divider()
    st.subheader("🔬 Lopende projecten")

    lopende = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE leider_id = {persoon_id}", conn)
    
    # Haal eigen persoon_id op
    eigen_gebruikersnaam = st.session_state.get("gebruikersnaam", "")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM persons WHERE name = ?", (eigen_gebruikersnaam,))
    result = cursor.fetchone()
    eigen_id = result[0] if result else None

    if lopende.empty:
        st.write("Geen lopende projecten.")
    elif len(lopende) == 1:
        project = lopende.iloc[0]
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"🟢 {project['naam']}", key=f"project_link_{project['id']}"):
                st.session_state.geselecteerd_lopend_project = int(project["id"])
                st.switch_page("pages/lopend_project.py")
        with col2:
            cursor.execute("SELECT * FROM project_deelnemers WHERE project_id = ? AND persoon_id = ?",
                           (project["id"], eigen_id))
            al_aangemeld = cursor.fetchone()
            if al_aangemeld or eigen_id == persoon_id:
                st.write("✅ Aangemeld")
            else:
                if st.button("➕ Aanmelden", key=f"aanmeld_{project['id']}"):
                    cursor.execute("INSERT INTO project_deelnemers (project_id, persoon_id) VALUES (?, ?)",
                                   (project["id"], eigen_id))
                    conn.commit()
                    st.success("✅ Aangemeld!")
                    st.rerun()
    else:
        if st.button("📋 Bekijk alle lopende projecten"):
            st.session_state.lopende_projecten_persoon = persoon_id
            st.switch_page("pages/lopende_projecten_overzicht.py")
        
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