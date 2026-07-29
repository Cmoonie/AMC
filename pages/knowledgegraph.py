import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components

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
db_path = os.path.join(os.path.dirname(__file__), "spider.db")
conn = sqlite3.connect(db_path)
personen = pd.read_sql("SELECT * FROM persons", conn)
expertise = pd.read_sql("SELECT * FROM expertise", conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn)

# Maak kennisgraaf
net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
net.barnes_hut(gravity=-5000, central_gravity=0.3, spring_length=200)

# Voeg personen toe als knopen
for _, persoon in personen.iterrows():
    net.add_node(f"p_{persoon['id']}", 
                 label=persoon['name'], 
                 color="#2E75B6",
                 size=30,
                 font={"size":16},
                 title=f"Onderzoeker: {persoon['name']}")

# Voeg expertise toe als knopen en verbindingen
for _, exp in expertise.iterrows():
    net.add_node(f"e_{exp['id']}", 
                 label=exp['label'], 
                 color="#70AD47",
                 size=20,
                 font={"size":16},
                 title=f"Expertise: {exp['label']}")

# Voeg verbindingen toe
for _, koppeling in personen_expertise.iterrows():
    net.add_edge(f"p_{koppeling['person_id']}", 
                 f"e_{koppeling['expertise_id']}")

# Sla op als HTML
net.save_graph("knowlegdegrapgh.html")

# Toon in Streamlit
with open("knowledgegraph.html", "r", encoding="utf-8") as f:
    html = f.read()
components.html(html, height=650)