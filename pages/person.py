import streamlit as st
import pandas as pd

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
personen = pd.read_csv("data/persons.csv")
expertise = pd.read_csv("data/expertise.csv")
personen_expertise = pd.read_csv("data/persons_expertise.csv")
projecten = pd.read_csv("data/projects.csv")
personen_projecten = pd.read_csv("data/persons_projects.csv")

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
        st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    with col2:
        st.image("https://picsum.photos/300/400", width=300)

    # Expertise
    st.divider()
    st.subheader("Expertise")
    exp_ids = personen_expertise[personen_expertise["person_id"] == persoon_id]["expertise_id"].tolist()
    exp_details = expertise[expertise["id"].isin(exp_ids)]
    for _, exp in exp_details.iterrows():
        if st.button(f"🔬 {exp['label']}", key=f"exp_{exp['id']}"):
            st.session_state.geselecteerde_expertise = exp["id"]
            st.switch_page("pages/expertise.py")

    # Projecten
    st.divider()
    st.subheader("Projecten")
    proj_ids = personen_projecten[personen_projecten["person_id"] == persoon_id]["project_id"].tolist()
    proj_details = projecten[projecten["id"].isin(proj_ids)]
    for _, proj in proj_details.iterrows():
        if st.button(f"📁 {proj['title']}", key=f"proj_{proj['id']}"):
            st.session_state.geselecteerde_project = proj["id"]
            st.switch_page("pages/project.py")

    # Terug knop onderaan
    if st.button("← Terug naar zoeken", key="terug_onder"):
        st.switch_page("app.py")