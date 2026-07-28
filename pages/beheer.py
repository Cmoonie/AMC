import streamlit as st
import pandas as pd
import sqlite3
import datetime

conn = sqlite3.connect("spider.db")

# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Log functie
def log_wijziging(actie, wat):
    cursor = conn.cursor()
    datum = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    door_wie = st.session_state.get("gebruikersnaam", "onbekend")
    cursor.execute(
        "INSERT INTO wijzigingen (datum, actie, wat, door_wie) VALUES (?, ?, ?, ?)",
        (datum, actie, wat, door_wie)
    )
    conn.commit()

# CSS
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.write(f"👤 **{st.session_state.get('gebruikersnaam', '')}**")
st.sidebar.divider()
if st.sidebar.button("📋 Geschiedenis"):
    st.switch_page("pages/geschiedenis.py")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

st.title("⚙️ Beheer")
st.subheader("Voeg toe, pas aan of verwijder gegevens")

tab1, tab2, tab3 = st.tabs(["👤 Personen", "📁 Projecten", "🔬 Expertise"])

with tab1:
    st.subheader("Personen beheren")
    personen = pd.read_sql("SELECT * FROM persons", conn)
    st.write("**Huidige personen:**")
    st.dataframe(personen)

    st.divider()
    st.subheader("✏️ Persoon aanpassen")
    persoon_opties2 = personen["name"].tolist()
    te_aanpassen = st.selectbox("Selecteer persoon om aan te passen", persoon_opties2, key="aanpassen_selectbox")
    huidige = personen[personen["name"] == te_aanpassen].iloc[0]
    nieuwe_naam_update = st.text_input("Nieuwe naam", value=huidige["name"], key="update_naam")
    nieuwe_dept_update = st.text_input("Nieuwe department", value=huidige["department"], key="update_dept")
    if st.button("Opslaan"):
        cursor = conn.cursor()
        cursor.execute("UPDATE persons SET name = ?, department = ? WHERE name = ?",
                       (nieuwe_naam_update, nieuwe_dept_update, te_aanpassen))
        conn.commit()
        log_wijziging("Aangepast", te_aanpassen)
        st.success(f"{te_aanpassen} is aangepast!")
        st.rerun()

    st.divider()
    st.subheader("🗑️ Persoon verwijderen")
    persoon_opties = personen["name"].tolist()
    te_verwijderen = st.selectbox("Selecteer persoon", persoon_opties)
    st.warning(f"⚠️ Weet je zeker dat je {te_verwijderen} wil verwijderen?")
    bevestig = st.checkbox("Ja, ik weet het zeker")
    if st.button("Verwijderen"):
        if bevestig:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM persons WHERE name = ?", (te_verwijderen,))
            conn.commit()
            log_wijziging("Verwijderd", te_verwijderen)
            st.success(f"{te_verwijderen} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan!")

    st.divider()
    st.subheader("➕ Persoon toevoegen")
    nieuwe_naam = st.text_input("Naam")
    nieuwe_department = st.text_input("Department")
    if st.button("Toevoegen"):
        if nieuwe_naam and nieuwe_department:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO persons (name, department) VALUES (?, ?)",
                           (nieuwe_naam, nieuwe_department))
            conn.commit()
            log_wijziging("Toegevoegd", nieuwe_naam)
            st.success(f"{nieuwe_naam} is toegevoegd!")
            st.rerun()
        else:
            st.error("Vul alle velden in!")

with tab2:
    st.subheader("Projecten beheren")
    projecten = pd.read_sql("SELECT * FROM projects", conn)
    st.write("**Huidige projecten:**")
    st.dataframe(projecten)

    st.divider()
    st.subheader("🗑️ Project verwijderen")
    project_opties = projecten["title"].tolist()
    te_verwijderen_project = st.selectbox("Selecteer project", project_opties, key="project_verwijderen_select")
    st.warning(f"⚠️ Weet je zeker dat je {te_verwijderen_project} wil verwijderen?")
    bevestig_project = st.checkbox("Ja, ik weet het zeker", key="project_bevestig")
    if st.button("Verwijderen", key="project_verwijderen"):
        if bevestig_project:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM projects WHERE title = ?", (te_verwijderen_project,))
            conn.commit()
            log_wijziging("Verwijderd", te_verwijderen_project)
            st.success(f"{te_verwijderen_project} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan!")
            
if len(projecten) > 0:
    st.divider()
    st.subheader("✏️ Project aanpassen")
    project_opties2 = projecten["title"].tolist()
    te_aanpassen_project = st.selectbox("Selecteer project", project_opties2, key="project_aanpassen_select")
    huidig_project = projecten[projecten["title"] == te_aanpassen_project].iloc[0]
    nieuwe_titel_update = st.text_input("Nieuwe titel", value=huidig_project["title"], key="update_titel")
    nieuwe_desc_update = st.text_input("Nieuwe beschrijving", value=huidig_project["description"], key="update_desc")
    if st.button("Opslaan", key="project_opslaan"):
        cursor = conn.cursor()
        cursor.execute("UPDATE projects SET title = ?, description = ? WHERE title = ?",
                       (nieuwe_titel_update, nieuwe_desc_update, te_aanpassen_project))
        conn.commit()
        log_wijziging("Aangepast", te_aanpassen_project)
        st.success(f"{te_aanpassen_project} is aangepast!")
        st.rerun()

    st.divider()


with tab3:
    st.subheader("Expertise beheren")
    expertise = pd.read_sql("SELECT * FROM expertise", conn)
    st.write("**Huidige expertise:**")
    st.dataframe(expertise)

    st.divider()
    st.subheader("➕ Expertise toevoegen")
    nieuwe_expertise = st.text_input("Expertise label", key="expertise_input")
    if st.button("Toevoegen", key="expertise_toevoegen"):
        if nieuwe_expertise:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expertise (label) VALUES (?)", (nieuwe_expertise,))
            conn.commit()
            log_wijziging("Toegevoegd", nieuwe_expertise)
            st.success(f"{nieuwe_expertise} is toegevoegd!")
            st.rerun()
        else:
            st.error("Vul een expertise in!")

    st.divider()
    st.subheader("🗑️ Expertise verwijderen")
    expertise_opties = expertise["label"].tolist()
    te_verwijderen_exp = st.selectbox("Selecteer expertise", expertise_opties, key="expertise_verwijderen_select")
    st.warning(f"⚠️ Weet je zeker dat je {te_verwijderen_exp} wil verwijderen?")
    bevestig_exp = st.checkbox("Ja, ik weet het zeker", key="expertise_bevestig")
    if st.button("Verwijderen", key="expertise_verwijderen"):
        if bevestig_exp:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expertise WHERE label = ?", (te_verwijderen_exp,))
            conn.commit()
            log_wijziging("Verwijderd", te_verwijderen_exp)
            st.success(f"{te_verwijderen_exp} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan!")

if len(projecten) > 0:
    st.divider()
    st.subheader("✏️ Expertise aanpassen")
    expertise_opties2 = expertise["label"].tolist()
    te_aanpassen_exp = st.selectbox("Selecteer expertise", expertise_opties2, key="expertise_aanpassen_select")
    huidige_exp = expertise[expertise["label"] == te_aanpassen_exp].iloc[0]
    nieuwe_exp_update = st.text_input("Nieuw label", value=huidige_exp["label"], key="update_exp")
    if st.button("Opslaan", key="expertise_opslaan"):
        cursor = conn.cursor()
        cursor.execute("UPDATE expertise SET label = ? WHERE label = ?",
                       (nieuwe_exp_update, te_aanpassen_exp))
        conn.commit()
        log_wijziging("Aangepast", te_aanpassen_exp)
        st.success(f"{te_aanpassen_exp} is aangepast!")
        st.rerun()

st.divider()
st.subheader("📋 Wijzigingsgeschiedenis")
wijzigingen = pd.read_sql("SELECT * FROM wijzigingen", conn)
if wijzigingen.empty:
    st.info("Nog geen wijzigingen geregistreerd.")
else:
    st.dataframe(wijzigingen[::-1])