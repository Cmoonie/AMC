import streamlit as st
import pandas as pd

#Aunthenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

st.title ("⚙️Beheer")
st.subheader("Voeg toe, pas aan of verwijder gegevens")

# Tabs voor elke entiteit
tab1, tab2, tab3 = st.tabs(["👤 Personen", "📁 Projecten", "🔬 Expertise"])
with tab1:
    st.subheader("Personen beheren")
    #Laad data
    personen = pd.read_csv("data/persons.csv")
    
    st.write("**Huidige personen:**")
    st.dataframe(personen)
    
    st.divider() #CRUD
    #Update
    st.subheader("✏️ Persoon aanpassen")
    
    persoon_opties2 = personen["name"].tolist()
    te_aanpassen = st.selectbox("Selecteer persoon om aan te passen", persoon_opties2, key="aanpassen_selectbox")
    
    huidige = personen[personen["name"] == te_aanpassen].iloc[0]
    
    nieuwe_naam_update = st.text_input("Nieuwe naam", value=huidige["name"], key="update_naam")
    nieuwe_dept_update = st.text_input("Nieuwe department", value=huidige["department"], key="update_dept")
    
    if st.button("Opslaan"):
        personen.loc[personen["name"] == te_aanpassen, "name"] = nieuwe_naam_update
        personen.loc[personen["name"] == te_aanpassen, "department"] = nieuwe_dept_update
        personen.to_csv("data/persons.csv", index=False)
        st.success(f"{te_aanpassen} is aangepast!")
        st.rerun()

    #Delete
    st.subheader("🗑️ Persoon verwijderen")
    
    persoon_opties = personen["name"].tolist()
    te_verwijderen = st.selectbox("Selecteer persoon", persoon_opties)
    
    st.warning(f"⚠️ Weet je zeker dat je {te_verwijderen} wil verwijderen? Dit kan niet ongedaan worden gemaakt!")
    
    bevestig = st.checkbox("Ja, ik weet het zeker")
    
    if st.button("Verwijderen"):
        if bevestig:
            personen = personen[personen["name"] != te_verwijderen]
            personen.to_csv("data/persons.csv", index=False)
            st.success(f"{te_verwijderen} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan om te verwijderen!")
    #Create
    st.subheader("➕ Persoon toevoegen")
    
    nieuwe_naam = st.text_input("Naam")
    nieuwe_department = st.text_input("Department")
    
    if st.button("Toevoegen"):
        if nieuwe_naam and nieuwe_department:
            nieuw_id = personen["id"].max() + 1
            nieuwe_rij = {"id": nieuw_id, "name": nieuwe_naam, "department": nieuwe_department}
            personen = pd.concat([personen, pd.DataFrame([nieuwe_rij])], ignore_index=True)
            personen.to_csv("data/persons.csv", index=False)
            st.success(f"{nieuwe_naam} is toegevoegd!")
            st.rerun()
        else:
            st.error("Vul alle velden in!")

with tab2:
    st.subheader("Projecten beheren")
    
    projecten = pd.read_csv("data/projects.csv")
    
    st.write("**Huidige projecten:**")
    st.dataframe(projecten)
    
    st.divider()
    st.divider()
    st.subheader("🗑️ Project verwijderen")
    
    project_opties = projecten["title"].tolist()
    te_verwijderen_project = st.selectbox("Selecteer project", project_opties, key="project_verwijderen_select")
    
    st.warning(f"⚠️ Weet je zeker dat je {te_verwijderen_project} wil verwijderen?")
    bevestig_project = st.checkbox("Ja, ik weet het zeker", key="project_bevestig")
    
    if st.button("Verwijderen", key="project_verwijderen"):
        if bevestig_project:
            projecten = projecten[projecten["title"] != te_verwijderen_project]
            projecten.to_csv("data/projects.csv", index=False)
            st.success(f"{te_verwijderen_project} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan!")

    st.divider()
    st.subheader("✏️ Project aanpassen")
    
    project_opties2 = projecten["title"].tolist()
    te_aanpassen_project = st.selectbox("Selecteer project", project_opties2, key="project_aanpassen_select")
    
    huidig_project = projecten[projecten["title"] == te_aanpassen_project].iloc[0]
    
    nieuwe_titel_update = st.text_input("Nieuwe titel", value=huidig_project["title"], key="update_titel")
    nieuwe_desc_update = st.text_input("Nieuwe beschrijving", value=huidig_project["description"], key="update_desc")
    
    if st.button("Opslaan", key="project_opslaan"):
        projecten.loc[projecten["title"] == te_aanpassen_project, "title"] = nieuwe_titel_update
        projecten.loc[projecten["title"] == te_aanpassen_project, "description"] = nieuwe_desc_update
        projecten.to_csv("data/projects.csv", index=False)
        st.success(f"{te_aanpassen_project} is aangepast!")
        st.rerun()

    st.subheader("➕ Project toevoegen")
    
    nieuwe_titel = st.text_input("Titel")
    nieuwe_beschrijving = st.text_input("Beschrijving")
    nieuwe_methoden = st.text_input("Methoden")
    nieuwe_datum = st.date_input("Datum")
    
    if st.button("Toevoegen", key="project_toevoegen"):
        if nieuwe_titel and nieuwe_beschrijving:
            nieuw_id = projecten["id"].max() + 1
            nieuwe_rij = {"id": nieuw_id, "title": nieuwe_titel, "description": nieuwe_beschrijving, "methods": nieuwe_methoden, "date": nieuwe_datum}
            projecten = pd.concat([projecten, pd.DataFrame([nieuwe_rij])], ignore_index=True)
            projecten.to_csv("data/projects.csv", index=False)
            st.success(f"{nieuwe_titel} is toegevoegd!")
            st.rerun()
        else:
            st.error("Vul minimaal titel en beschrijving in!")            
with tab3:
    st.subheader("Expertise beheren")
    
    expertise = pd.read_csv("data/expertise.csv")
    
    st.write("**Huidige expertise:**")
    st.dataframe(expertise)
    
    st.divider()
    st.subheader("➕ Expertise toevoegen")
    
    nieuwe_expertise = st.text_input("Expertise label", key="expertise_input")
    
    if st.button("Toevoegen", key="expertise_toevoegen"):
        if nieuwe_expertise:
            nieuw_id = expertise["id"].max() + 1
            nieuwe_rij = {"id": nieuw_id, "label": nieuwe_expertise}
            expertise = pd.concat([expertise, pd.DataFrame([nieuwe_rij])], ignore_index=True)
            expertise.to_csv("data/expertise.csv", index=False)
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
            expertise = expertise[expertise["label"] != te_verwijderen_exp]
            expertise.to_csv("data/expertise.csv", index=False)
            st.success(f"{te_verwijderen_exp} is verwijderd!")
            st.rerun()
        else:
            st.error("Vink de bevestiging aan!")

    st.divider()
    st.subheader("✏️ Expertise aanpassen")
    
    expertise_opties2 = expertise["label"].tolist()
    te_aanpassen_exp = st.selectbox("Selecteer expertise", expertise_opties2, key="expertise_aanpassen_select")
    
    huidige_exp = expertise[expertise["label"] == te_aanpassen_exp].iloc[0]
    
    nieuwe_exp_update = st.text_input("Nieuw label", value=huidige_exp["label"], key="update_exp")
    
    if st.button("Opslaan", key="expertise_opslaan"):
        expertise.loc[expertise["label"] == te_aanpassen_exp, "label"] = nieuwe_exp_update
        expertise.to_csv("data/expertise.csv", index=False)
        st.success(f"{te_aanpassen_exp} is aangepast!")
        st.rerun()  