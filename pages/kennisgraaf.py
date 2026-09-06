import streamlit as st
import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import time
from expertise_routes import uitgewerkte_expertise


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

# Standaard alle personen tonen
gefilterde_personen = personen

st.divider()
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("👤 Ga naar onderzoeker")
    alle_namen = personen["name"].tolist()
    gekozen_naam = st.selectbox("Selecteer onderzoeker", ["— kies —"] + alle_namen, key="kg_naam")
    if gekozen_naam != "— kies —":
        if st.button(f"Ga naar profiel", key="kg_naar_profiel"):
            persoon = personen[personen["name"] == gekozen_naam].iloc[0]
            st.session_state.geselecteerde_persoon = int(persoon["id"])
            st.switch_page("pages/onderzoeker.py")

with col2:
    st.subheader("🔬 Ga naar expertise")
    expertise_opties = list(uitgewerkte_expertise.keys())
    gekozen_exp = st.selectbox("Selecteer expertise", ["— kies —"] + expertise_opties, key="kg_exp")
    if gekozen_exp != "— kies —":
        if st.button("Ga naar expertise pagina", key="kg_naar_exp"):
            st.switch_page(uitgewerkte_expertise[gekozen_exp])


# Filters
# col1, col2 = st.columns([1, 1])

# with col1:
#     expertise_opties = ["Alle"] + expertise["label"].tolist()
#     expertise_filter = st.selectbox("🔬 Filter op expertise", expertise_opties,key="kg_expertise_filter" )

# with col2:
#     naam_filter = st.text_input(
#     "🔍 Zoek op naam",
#     key="kg_naam_filter"
# )

# # Filter personen
# if expertise_filter != "Alle":
#     exp_id = expertise[expertise["label"] == expertise_filter]["id"].iloc[0]
#     gefilterde_persoon_ids = personen_expertise[personen_expertise["expertise_id"] == exp_id]["person_id"].tolist()
#     gefilterde_personen = personen[personen["id"].isin(gefilterde_persoon_ids)]
# else:
#     gefilterde_personen = personen

# if naam_filter:
#     gefilterde_personen = gefilterde_personen[gefilterde_personen["name"].str.contains(naam_filter, case=False)]

# st.write(f"Expertise filter: {expertise_filter}")
# st.write(f"Aantal gefilterde personen: {len(gefilterde_personen)}")


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
# Voeg personen toe als knopen
# for _, persoon in gefilterde_personen.iterrows():
#     net.add_node(f"p_{persoon['id']}", 
#                  label=persoon['name'], 
#                  color="#2E75B6",
#                  size=30,
# #                  font={"size":16},
# #                  title=f"Onderzoeker: {persoon['name']}")

# # Haal expertise ids op van gefilterde personen
# gefilterde_persoon_ids = gefilterde_personen["id"].tolist()
# gefilterde_koppelingen = personen_expertise[personen_expertise["person_id"].isin(gefilterde_persoon_ids)]
# gefilterde_expertise_ids = gefilterde_koppelingen["expertise_id"].tolist()
# gefilterde_expertise = expertise[expertise["id"].isin(gefilterde_expertise_ids)]

# # Voeg alleen relevante expertise toe
# for _, exp in gefilterde_expertise.iterrows():
#     net.add_node(f"e_{exp['id']}", 
#                  label=exp['label'], 
#                  color="#70AD47",
#                  size=20,
#                  font={"size":16},
#                  title=f"Expertise: {exp['label']}")

# Voeg verbindingen toe
for _, koppeling in gefilterde_koppelingen.iterrows():
    net.add_edge(f"p_{koppeling['person_id']}", 
                 f"e_{koppeling['expertise_id']}")

# Sla op als HTML
import time
bestandsnaam = f"kennisgraaf_{int(time.time())}.html"
# JavaScript voor klikbare nodes
net.options = {
    "interaction": {
        "navigationButtons": True,
        "keyboard": True,
        "hover": True
    }
}
net.save_graph(bestandsnaam)

# Voeg JavaScript toe voor klikbare nodes
with open(bestandsnaam, "r", encoding="utf-8") as f:
    html_content = f.read()

# Injecteer JavaScript die berichten stuurt naar Streamlit
click_js = """
<script>
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        network.on("click", function(params) {
            if (params.nodes.length > 0) {
                var nodeId = params.nodes[0];
                var url = window.location.href.split('?')[0] + '?node=' + nodeId;
                window.parent.location.href = url;
            }
        });
    }, 1000);
});
</script>
"""

html_content = html_content.replace("</body>", click_js + "</body>")

with open(bestandsnaam, "w", encoding="utf-8") as f:
    f.write(html_content)

components.html(html_content, height=650)

# Verwerk klik via URL parameter
node_id = st.query_params.get("node")

if node_id:
    if node_id.startswith("p_"):
        persoon_id = int(node_id.replace("p_", ""))

        st.session_state.geselecteerde_persoon = persoon_id

        st.query_params.clear()

        st.switch_page("pages/onderzoeker.py")

    elif node_id.startswith("e_"):
        expertise_id = int(node_id.replace("e_", ""))

        exp = expertise[expertise["id"] == expertise_id]

        if not exp.empty:
            label = exp.iloc[0]["label"].lower()

            if label in uitgewerkte_expertise:
                st.query_params.clear()
                st.switch_page(uitgewerkte_expertise[label])


# # Pas daarna de kennisgraaf tonen
# components.html(html_content, height=650)

# st.divider()
# col1, col2 = st.columns([1, 1])

# with col1:
#     st.subheader("👤 Ga naar onderzoeker")
#     alle_namen = personen["name"].tolist()
#     gekozen_naam = st.selectbox("Selecteer onderzoeker", ["— kies —"] + alle_namen, key="kg_naam")
#     if gekozen_naam != "— kies —":
#         if st.button(f"Ga naar profiel", key="kg_naar_profiel"):
#             persoon = personen[personen["name"] == gekozen_naam].iloc[0]
#             st.session_state.geselecteerde_persoon = int(persoon["id"])
#             st.switch_page("pages/onderzoeker.py")

# with col2:
#     st.subheader("🔬 Ga naar expertise")
#     expertise_opties = list(uitgewerkte_expertise.keys())
#     gekozen_exp = st.selectbox("Selecteer expertise", ["— kies —"] + expertise_opties, key="kg_exp")
#     if gekozen_exp != "— kies —":
#         if st.button("Ga naar expertise pagina", key="kg_naar_exp"):
#             st.switch_page(uitgewerkte_expertise[gekozen_exp])

