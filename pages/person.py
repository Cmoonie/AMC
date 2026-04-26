import streamlit as st
import pandas as pd

# Laad data
personen = pd.read_csv("data/persons.csv")
expertise = pd.read_csv("data/expertise.csv")
personen_expertise = pd.read_csv("data/persons_expertise.csv")
projecten = pd.read_csv("data/projects.csv")
personen_projecten = pd.read_csv("data/persons_projects.csv")

# Haal geselecteerde persoon op uit session state
if st.session_state.geselecteerde_persoon is None:
    st.warning("Geen onderzoeker geselecteerd. Ga terug naar de zoekpagina.")
else:
    persoon_id = st.session_state.geselecteerde_persoon
    persoon = personen[personen["id"] == persoon_id].iloc[0]

    # Naam en department
    st.title(persoon["name"])
    st.subheader(persoon["department"])

    # Expertise
    st.subheader("Expertise")
    exp_ids = personen_expertise[personen_expertise["person_id"] == persoon_id]["expertise_id"].tolist()
    exp_labels = expertise[expertise["id"].isin(exp_ids)]["label"].tolist()
    for label in exp_labels:
        st.write(f"🔬 {label}")

    # Projecten
    st.subheader("Projecten")
    proj_ids = personen_projecten[personen_projecten["person_id"] == persoon_id]["project_id"].tolist()
    proj_details = projecten[projecten["id"].isin(proj_ids)]
    for _, project in proj_details.iterrows():
        st.write(f"📁 **{project['title']}** — {project['description']}")

    # Terug knop
    if st.button("← Terug naar zoeken"):
        st.switch_page("app.py")