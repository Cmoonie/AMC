import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import date
db_path = os.path.join(os.path.dirname(__file__),"..", "spider.db")
conn = sqlite3.connect(db_path)


# Login check
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Sidebar CSS
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

#Gebruikersnaam ophalen
gebruikersnaam = st.session_state.get("gebruikersnaam", "")
rol = st.session_state.get("rol", "")

# Haal persoon id op van ingelogde gebruiker
cursor = conn.cursor()
cursor.execute("SELECT id FROM persons WHERE name = ?", (gebruikersnaam,))
result = cursor.fetchone()
persoon_id = result[0] if result else None

st.write(f"gebruikersnaam: {gebruikersnaam}")
st.write(f"persoon_id: {persoon_id}")

# Laad profiel uit database
cursor = conn.cursor()
cursor.execute("SELECT * FROM profiel_data WHERE gebruikersnaam = ?", (gebruikersnaam,))
profiel = cursor.fetchone()

# Als profiel nog niet bestaat, maak het aan
if not profiel:
    cursor.execute("INSERT INTO profiel_data (gebruikersnaam, email, bio, expertise, projecten) VALUES (?, ?, ?, ?, ?)",
                   (gebruikersnaam, "", "", "", ""))
    conn.commit()
    cursor.execute("SELECT * FROM profiel_data WHERE gebruikersnaam = ?", (gebruikersnaam,))
    profiel = cursor.fetchone()



# Sidebar
st.sidebar.write(f"👤 **{gebruikersnaam}**")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if rol == "beheerder":
    if st.sidebar.button("⚙️ Beheer"):
        st.switch_page("pages/beheer.py")
st.sidebar.divider()
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

st.set_page_config(layout="wide")

# Pagina inhoud

st.title(f"👤 {gebruikersnaam}")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(rol.capitalize())
    st.write("Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.")

with col2:
    st.image("https://picsum.photos/300/400", width=300)

st.divider()
st.subheader("📧 Contact")


st.write("📧 emailadres@amsterdamumc.nl")

with st.expander("Klik om aan te passen"):
    nieuwe_naam = st.text_input("Naam", value=gebruikersnaam)
    nieuw_email = st.text_input("Email", value="emailadres@amsterdamumc.nl")
    nieuwe_bio = st.text_area("Bio", value="Lorem ipsum dolor sit amet...")
    
    if st.button("💾 Opslaan"):
        st.session_state.gebruikersnaam = nieuwe_naam
        st.session_state.email = nieuw_email
        st.session_state.bio = nieuwe_bio
        st.success("✅ Profiel opgeslagen!")
        st.rerun()


st.divider()
st.subheader("🔬 Expertise")

# Laad expertise uit database
expertise_opgeslagen = profiel[4] if profiel[4] else ""
expertise_lijst = expertise_opgeslagen.split(",") if expertise_opgeslagen else []

for exp in expertise_lijst:
    if exp:
        st.write(f"🔬 {exp}")

with st.expander("➕ Expertise toevoegen"):
    nieuwe_exp = st.text_input("Expertise", key="nieuwe_exp")
    if st.button("Toevoegen", key="exp_toevoegen"):
        if nieuwe_exp:
            expertise_lijst.append(nieuwe_exp)
            cursor.execute("UPDATE profiel_data SET expertise = ? WHERE gebruikersnaam = ?",
                           (",".join(expertise_lijst), gebruikersnaam))
            conn.commit()
            st.success(f"✅ {nieuwe_exp} toegevoegd!")
            st.rerun()

# Expertise wijzigen
if expertise_lijst:
    with st.expander("✏️ Expertise wijzigen"):
        te_wijzigen_exp = st.selectbox("Selecteer expertise", expertise_lijst, key="wijzig_exp_select")
        gewijzigde_exp = st.text_input("Nieuwe naam", value=te_wijzigen_exp, key="gewijzigde_exp")
        if st.button("Opslaan", key="exp_wijzigen"):
            index = expertise_lijst.index(te_wijzigen_exp)
            expertise_lijst[index] = gewijzigde_exp
            cursor.execute("UPDATE profiel_data SET expertise = ? WHERE gebruikersnaam = ?",
                           (",".join(expertise_lijst), gebruikersnaam))
            conn.commit()
            st.success(f"✅ Gewijzigd naar {gewijzigde_exp}!")
            st.rerun()           


    

st.divider()
st.subheader("🎙️ Bestanden & Opnames")
st.info("Upload hier je bestanden — PDF, Word of Google Docs link")

uploaded_file = st.file_uploader(
    "Kies een bestand", 
    type=["pdf", "docx", "txt"]
)

if uploaded_file is not None:
    st.success(f"✅ {uploaded_file.name} is geüpload!")
    st.warning("⚠️ Let op: bestanden worden nog niet permanent opgeslagen. Dit komt in een volgende versie.")

# Google Docs link
st.subheader("🔗 Google Docs link toevoegen")
google_link = st.text_input("Plak hier je Google Docs link")
if st.button("💾 Link opslaan", key="save_link"):
    if google_link:
        st.success("✅ Link opgeslagen!")                   

st.divider()
st.subheader("🔬 Lopend project starten")

with st.expander("➕ Nieuw project starten"):
    project_naam = st.text_input("Projectnaam", key="nieuw_project_naam")
    project_beschrijving = st.text_area("Beschrijving", key="nieuw_project_beschrijving")
    
    if st.button("💾 Project starten", key="start_project"):
        if project_naam:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lopende_projecten (naam, beschrijving, leider_id, datum)
                VALUES (?, ?, ?, ?)
            """, (project_naam, project_beschrijving, persoon_id, str(date.today())))
            conn.commit()
            st.success(f"✅ Project '{project_naam}' gestart!")
            st.rerun()
        else:
            st.error("Vul een projectnaam in!")

# Toon eigen lopende projecten
st.divider()
st.subheader("📋 Mijn lopende projecten")

mijn_projecten = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE leider_id = {persoon_id}", conn) if persoon_id else pd.DataFrame() 


cursor.execute("""
    INSERT INTO lopende_projecten (naam, beschrijving, leider_id, datum)
    VALUES (?, ?, ?, ?)
""", (project_naam, project_beschrijving, persoon_id, str(date.today())))

if mijn_projecten.empty:
    st.info("Je hebt nog geen lopende projecten.")
else:
    for _, project in mijn_projecten.iterrows():
        st.write(f"🔬 **{project['naam']}** — {project['beschrijving'][:50]}...")
        
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        if st.button("🔗 Bekijk project", key=f"bekijk_{project['id']}"):
            st.session_state.geselecteerd_lopend_project = int(project["id"])
            st.switch_page("pages/lopend_project.py")
    with col2:
        if st.button("✏️ Aanpassen", key=f"aanpas_{project['id']}"):
            st.session_state.aanpassen_project_id = project["id"]
    with col3:
        if st.button("🗑️ Verwijderen", key=f"verwijder_{project['id']}"):
            cursor.execute("DELETE FROM lopende_projecten WHERE id = ?", (project["id"],))
            cursor.execute("DELETE FROM project_deelnemers WHERE project_id = ?", (project["id"],))
            conn.commit()
            st.success("✅ Project verwijderd!")
            st.rerun()

# Aanpassen formulier
if "aanpassen_project_id" in st.session_state and st.session_state.aanpassen_project_id:
    project_id = st.session_state.aanpassen_project_id
    huidig_df = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE id = {project_id}", conn)
    if not huidig_df.empty:
        huidig = huidig_df.iloc[0]
        st.divider()
        st.subheader("✏️ Project aanpassen")
        nieuwe_naam = st.text_input("Naam", value=huidig["naam"], key="aanpas_naam")
        nieuwe_beschrijving = st.text_area("Beschrijving", value=huidig["beschrijving"], key="aanpas_beschrijving")
        if st.button("💾 Opslaan", key="opslaan_project"):
            cursor.execute("UPDATE lopende_projecten SET naam = ?, beschrijving = ? WHERE id = ?",
                           (nieuwe_naam, nieuwe_beschrijving, project_id))
            conn.commit()
            st.session_state.aanpassen_project_id = None
            st.success("✅ Project bijgewerkt!")
            st.rerun()
            
    st.divider()
    st.subheader("✏️ Project aanpassen")
    nieuwe_naam = st.text_input("Naam", value=huidig["naam"], key="aanpas_naam")
    nieuwe_beschrijving = st.text_area("Beschrijving", value=huidig["beschrijving"], key="aanpas_beschrijving")
    
    if st.button("💾 Opslaan", key="opslaan_project"):
        cursor = conn.cursor()
        cursor.execute("UPDATE lopende_projecten SET naam = ?, beschrijving = ? WHERE id = ?",
                       (nieuwe_naam, nieuwe_beschrijving, project_id))
        conn.commit()
        st.session_state.aanpassen_project_id = None
        st.success("✅ Project bijgewerkt!")
        st.rerun()        

    # Terug knop onderaan
    if st.button("← Terug naar zoeken", key="terug_onder"):
        st.switch_page("app.py")