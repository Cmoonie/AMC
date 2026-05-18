import streamlit as st
import pandas as pd

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

# Sidebar
gebruikersnaam = st.session_state.get("gebruikersnaam", "")
rol = st.session_state.get("rol", "")

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
st.write("Jouw expertise wordt hier getoond.")
# Toon huidige expertise
if "profiel_expertise" not in st.session_state:
    st.session_state.profiel_expertise = []

for exp in st.session_state.profiel_expertise:
    st.write(f"🔬 {exp}")

# Expertise toevoegen
with st.expander("➕ Expertise toevoegen"):
    nieuwe_exp = st.text_input("Expertise", key="nieuwe_exp")
    if st.button("Toevoegen", key="exp_toevoegen"):
        if nieuwe_exp:
            st.session_state.profiel_expertise.append(nieuwe_exp)
            st.success(f"✅ {nieuwe_exp} toegevoegd!")
            st.rerun()

# Expertise wijzigen
if st.session_state.profiel_expertise:
    with st.expander("✏️ Expertise wijzigen"):
        te_wijzigen_exp = st.selectbox("Selecteer expertise", st.session_state.profiel_expertise, key="wijzig_exp_select")
        gewijzigde_exp = st.text_input("Nieuwe naam", value=te_wijzigen_exp, key="gewijzigde_exp")
        if st.button("Opslaan", key="exp_wijzigen"):
            index = st.session_state.profiel_expertise.index(te_wijzigen_exp)
            st.session_state.profiel_expertise[index] = gewijzigde_exp
            st.success(f"✅ Gewijzigd naar {gewijzigde_exp}!")
            st.rerun()            

st.divider()
st.subheader("📁 Projecten")
st.write("Jouw projecten worden hier getoond.")

# Toon huidige projecten
if "profiel_projecten" not in st.session_state:
    st.session_state.profiel_projecten = []

for proj in st.session_state.profiel_projecten:
    st.write(f"📁 {proj}")

# Project toevoegen
with st.expander("➕ Project toevoegen"):
    nieuw_proj = st.text_input("Projectnaam", key="nieuw_proj")
    if st.button("Toevoegen", key="proj_toevoegen"):
        if nieuw_proj:
            st.session_state.profiel_projecten.append(nieuw_proj)
            st.success(f"✅ {nieuw_proj} toegevoegd!")
            st.rerun()

# Project wijzigen
if st.session_state.profiel_projecten:
    with st.expander("✏️ Project wijzigen"):
        te_wijzigen_proj = st.selectbox("Selecteer project", st.session_state.profiel_projecten, key="wijzig_proj_select")
        gewijzigd_proj = st.text_input("Nieuwe naam", value=te_wijzigen_proj, key="gewijzigd_proj")
        if st.button("Opslaan", key="proj_wijzigen"):
            index = st.session_state.profiel_projecten.index(te_wijzigen_proj)
            st.session_state.profiel_projecten[index] = gewijzigd_proj
            st.success(f"✅ Gewijzigd naar {gewijzigd_proj}!")
            st.rerun()            

st.divider()
st.subheader("🎙️ Bestanden & Opnames")
uploaded_file = st.file_uploader("Kies een bestand", type=["pdf", "mp3", "mp4", "docx"])
if uploaded_file is not None:
    st.success(f"✅ {uploaded_file.name} is geüpload!")