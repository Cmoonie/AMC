import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import time



# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# CSS
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.write(f"👤 **{st.session_state.get('gebruikersnaam', '')}**")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

st.title("🕸️ Kennisgraaf")
st.subheader("Verbanden tussen onderzoekers en expertise")

# Database verbinding
import os
db_path = os.path.join(os.path.dirname(__file__),"..", "spider.db")
conn = sqlite3.connect(db_path)
personen = pd.read_sql("SELECT * FROM persons", conn)
expertise = pd.read_sql("SELECT * FROM expertise", conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn)

# Filters
col1, col2 = st.columns([1, 1])

with col1:
    expertise_opties = ["Alle"] + expertise["label"].tolist()
    expertise_filter = st.selectbox("🔬 Filter op expertise", expertise_opties)

with col2:
    naam_filter = st.text_input("🔍 Zoek op naam")

# Filter personen
if expertise_filter != "Alle":
    exp_id = expertise[expertise["label"] == expertise_filter]["id"].iloc[0]
    gefilterde_persoon_ids = personen_expertise[personen_expertise["expertise_id"] == exp_id]["person_id"].tolist()
    gefilterde_personen = personen[personen["id"].isin(gefilterde_persoon_ids)]
else:
    gefilterde_personen = personen

if naam_filter:
    gefilterde_personen = gefilterde_personen[gefilterde_personen["name"].str.contains(naam_filter, case=False)]

st.write(f"Expertise filter: {expertise_filter}")
st.write(f"Aantal gefilterde personen: {len(gefilterde_personen)}")


# Maak kennisgraaf
net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
net.set_options("""
{
  "interaction": {
    "navigationButtons": true,
    "keyboard": true
  }
}
""")

# Voeg personen toe als knopen
for _, persoon in gefilterde_personen.iterrows():
    net.add_node(f"p_{persoon['id']}", 
                 label=persoon['name'], 
                 color="#2E75B6",
                 size=30,
                 font={"size":16},
                 title=f"Onderzoeker: {persoon['name']}")

# Haal expertise ids op van gefilterde personen
gefilterde_persoon_ids = gefilterde_personen["id"].tolist()
gefilterde_koppelingen = personen_expertise[personen_expertise["person_id"].isin(gefilterde_persoon_ids)]
gefilterde_expertise_ids = gefilterde_koppelingen["expertise_id"].tolist()
gefilterde_expertise = expertise[expertise["id"].isin(gefilterde_expertise_ids)]

# Voeg alleen relevante expertise toe
for _, exp in gefilterde_expertise.iterrows():
    net.add_node(f"e_{exp['id']}", 
                 label=exp['label'], 
                 color="#70AD47",
                 size=20,
                 font={"size":16},
                 title=f"Expertise: {exp['label']}")

# Voeg verbindingen toe
for _, koppeling in gefilterde_koppelingen.iterrows():
    net.add_edge(f"p_{koppeling['person_id']}", 
                 f"e_{koppeling['expertise_id']}")

# Sla op als HTML
import time
bestandsnaam = f"kennisgraaf_{int(time.time())}.html"
net.save_graph(bestandsnaam)
# Toon in Streamlit
with open(bestandsnaam, "r", encoding="utf-8") as f:
    html = f.read()
components.html(html, height=650)

