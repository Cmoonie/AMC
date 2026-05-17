import streamlit as st
import pandas as pd

#Aunthenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()


#Custom CSS
st.set_page_config(layout="wide")

st.markdown("""
    <style>
    h1 {
        font-size: 3rem !important;
        margin-bottom: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# Laad data
personen = pd.read_csv("data/persons.csv")
projecten = pd.read_csv("data/projects.csv")
personen_projecten = pd.read_csv("data/persons_projects.csv")
expertise = pd.read_csv("data/expertise.csv")
personen_expertise = pd.read_csv("data/persons_expertise.csv")

# Haal geselecteerd project op uit session state
if "geselecteerd_project" not in st.session_state or st.session_state.geselecteerd_project is None:
    st.warning("Geen project geselecteerd. Ga terug naar de zoekpagina.")
else:
    project_id = st.session_state.geselecteerd_project
    project = projecten[projecten["id"] == project_id].iloc[0]

    # Titel en beschrijving
    st.title(project["title"])
    st.write(project["description"])
    st.write(f"📅 **Datum:** {project['date']}")
    st.write(f"🔧 **Methoden:** {project['methods']}")

    # Betrokken onderzoekers
    st.divider()
    st.subheader("Betrokken onderzoekers")
    persoon_ids = personen_projecten[personen_projecten["project_id"] == project_id]["person_id"].tolist()
    betrokken = personen[personen["id"].isin(persoon_ids)]
    for _, persoon in betrokken.iterrows():
        if st.button(f"👤 {persoon['name']}"):
            st.session_state.geselecteerde_persoon = persoon["id"]
            st.switch_page("pages/person.py")

    # Terug knop
    if st.button("← Terug naar zoeken"):
        st.switch_page("app.py")