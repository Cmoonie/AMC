import streamlit as st
import pandas as pd

from dotenv import load_dotenv #laad de .enc library
import os                      #laad de os library om bestanden te lezen

load_dotenv()                  # open het .env bestand
api_key = os.getenv("GROQ_API_KEY") # haal de sleutel eruit
#st.write(api_key) #debug regel


from groq import Groq
client = Groq(api_key=api_key)

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

personen = pd.read_csv("data/persons.csv") #personen inladen
expertise = pd.read_csv("data/expertise.csv") #expertise inladen
personen_expertise = pd.read_csv("data/persons_expertise.csv") #tussentabel inladen
projecten = pd.read_csv("data/projects.csv")                  #projecten inladen
personen_projecten = pd.read_csv("data/persons_projects.csv") #tussentabel inladen

st.title("Spider")
st.subheader("Zoek onderzoeksexpertise binnen Division 9")

department_filter = st.selectbox(
    "Filter op department",
    ["Alle"] + personen["department"].unique().tolist()
)

# st.write(expertise) Debug regel

zoekterm = st.text_input("Zoek op naam, project of expertise")

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
   

    # Zoek op projecten
    project_match = projecten[projecten["title"].str.contains(zoekterm, case=False) | projecten["description"].str.contains(zoekterm, case=False)]
    project_ids = project_match["id"].tolist()
    personen_ids_project = personen_projecten[personen_projecten["project_id"].isin(project_ids)]["person_id"].tolist()
    project_resultaat = personen[personen["id"].isin(personen_ids_project)]
   
   #combineer alles
    resultaat = pd.concat([naam_resultaat, expertise_resultaat, project_resultaat]).drop_duplicates()
    st.success(f"{len(resultaat)} onderzoeker(s) gevonden")
    st.dataframe(resultaat)

    st.subheader("Gevonden onderzoekers")
    for _, persoon in resultaat.iterrows():
        if st.button(f"👤 {persoon['name']}"):
            st.session_state.geselecteerde_persoon = persoon["id"]
            st.switch_page("pages/person.py")

    # Toon expertise per gevonden persoon
    st.subheader("Expertise")
    for _, persoon in resultaat.iterrows():
        exp_ids = personen_expertise[personen_expertise["person_id"] == persoon["id"]]["expertise_id"].tolist()
        exp_details = expertise[expertise["id"].isin(exp_ids)]
        st.write(f"**{persoon['name']}:**")
        for _, exp in exp_details.iterrows():
            if st.button(f"🔬 {exp['label']}", key=f"exp_{persoon['id']}_{exp['id']}"):
                st.session_state.geselecteerde_expertise = exp["id"]
                st.switch_page("pages/expertise.py")

        # Toon projecten per gevonden persoon
    st.subheader("Projecten")
    for _, persoon in resultaat.iterrows():
        proj_ids = personen_projecten[personen_projecten["person_id"] == persoon["id"]]["project_id"].tolist()
        proj_details = projecten[projecten["id"].isin(proj_ids)]
        for _, project in proj_details.iterrows():
            if st.button(f"📁 {project['title']}", key=f"proj_{persoon['id']}_{project['id']}"):
                st.session_state.geselecteerd_project = project["id"]
                st.switch_page("pages/project.py")   

    if not resultaat.empty:
        with st.spinner("Samenvatting genereren ..."):
            samenvatting = genereer_samenvatting(zoekterm, resultaat)
            st.info(samenvatting)

else:
    st.info("Typ een naam, expertise of project om te zoeken.")