import streamlit as st
import pandas as pd

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
expertise = pd.read_csv("data/expertise.csv")
personen_expertise = pd.read_csv("data/persons_expertise.csv")

# Haal geselecteerde expertise op uit session state
if "geselecteerde_expertise" not in st.session_state or st.session_state.geselecteerde_expertise is None:
    st.warning("Geen expertise geselecteerd. Ga terug naar de zoekpagina.")
else:
    expertise_id = st.session_state.geselecteerde_expertise
    exp = expertise[expertise["id"] == expertise_id].iloc[0]

    # Titel
    st.title(f"🔬 {exp['label']}")

    # Betrokken onderzoekers
    st.divider()
    st.subheader("Onderzoekers met deze expertise")
    persoon_ids = personen_expertise[personen_expertise["expertise_id"] == expertise_id]["person_id"].tolist()
    betrokken = personen[personen["id"].isin(persoon_ids)]
    for _, persoon in betrokken.iterrows():
        if st.button(f"👤 {persoon['name']}", key=f"exp_persoon_{persoon['id']}"):
            st.session_state.geselecteerde_persoon = persoon["id"]
            st.switch_page("pages/person.py")

    # Terug knop
    if st.button("← Terug naar zoeken"):
        st.switch_page("app.py")