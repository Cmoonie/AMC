import streamlit as st
import pandas as pd
import sqlite3
import os
db_path = os.path.join(os.path.dirname(__file__), "spider.db")
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



    # Terug knop onderaan
    if st.button("← Terug naar zoeken", key="terug_onder"):
        st.switch_page("app.py")