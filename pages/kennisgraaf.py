import streamlit as st

st.set_page_config(
    page_title="Kennisgraaf - Spider",
    layout="wide"
)

import pandas as pd
import sqlite3
from pyvis.network import Network
import streamlit.components.v1 as components
import time


from expertise_routes import uitgewerkte_expertise
from sidebar import toon_sidebar




# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

toon_sidebar()    

# CSS
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)



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

col1, col2, col3 = st.columns(
    [1, 1, 1],
    gap="large"
)

with col1:
    st.subheader("🔍 Filter kennisgraaf")

    naam_filter = st.text_input(
        "Zoek onderzoeker",
        placeholder="Bijvoorbeeld Robert",
        key="kg_naam_filter"
    )

# ============================================================
# FILTERS TOEPASSEN OP KENNISGRAAF
# ============================================================

gefilterde_personen = personen.copy()



st.divider()

# ============================================================
# 3 FILTERBALKEN NAAST ELKAAR
# ============================================================

col1, col2, col3 = st.columns([1, 1, 1])

# ------------------------------------------------------------
# 1. FILTER OP ONDERZOEKER
# ------------------------------------------------------------
with col1:
    st.subheader("👤 Onderzoeker")

    alle_namen = personen["name"].tolist()

    gekozen_naam = st.selectbox(
    "Selecteer onderzoeker",
    ["— kies —"] + alle_namen,
    key="kg_naam_select"
    )

# ------------------------------------------------------------
# 2. FILTER OP EXPERTISE
# ------------------------------------------------------------
with col2:
    st.subheader("🔬 Expertise")

    expertise_opties = expertise["label"].tolist()

    expertise_filter = st.selectbox(
        "Selecteer expertise",
        ["Alle expertises"] + expertise_opties,
        key="kg_expertise_filter"
    )

# ------------------------------------------------------------
# 3. DIRECT NAVIGEREN
# ------------------------------------------------------------
with col3:
    st.subheader("➡️ Ga direct naar")

    navigatie_keuze = st.selectbox(
        "Kies type",
        [
            "— kies —",
            "Onderzoekerprofiel",
            "Expertisepagina"
        ],
        key="kg_navigatie_type"
    )

    if navigatie_keuze == "Onderzoekerprofiel":

        gekozen_naam = st.selectbox(
            "Kies onderzoeker",
            alle_namen,
            key="kg_direct_onderzoeker"
        )

        if st.button(
            "Ga naar profiel",
            key="kg_naar_profiel",
            use_container_width=True
        ):
            persoon = personen[
                personen["name"] == gekozen_naam
            ].iloc[0]

            st.session_state.geselecteerde_persoon = int(
                persoon["id"]
            )

            st.switch_page(
                "pages/onderzoeker.py"
            )

    elif navigatie_keuze == "Expertisepagina":

        expertise_links = list(
            uitgewerkte_expertise.keys()
        )

        gekozen_exp = st.selectbox(
            "Kies expertise",
            expertise_links,
            key="kg_direct_expertise"
        )

        if st.button(
            "Ga naar expertise",
            key="kg_naar_exp",
            use_container_width=True
        ):
            st.switch_page(
                uitgewerkte_expertise[gekozen_exp]
            )

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
import os
os.makedirs("temp", exist_ok=True)
bestandsnaam = f"temp/kennisgraaf_{int(time.time())}.html"

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


