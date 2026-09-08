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
from styling import apply_styling
import os
import base64



# Authenticatie
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Algemene Spider styling
apply_styling("kennisgraaf")

# Centrale sidebar
toon_sidebar()    


# ============================================================
# KENNISGRAAF STYLING
# ============================================================

afbeelding_pad = os.path.join(
    os.path.dirname(__file__),
    "..",
    "assets",
    "achtergrond.png"
)

with open(afbeelding_pad, "rb") as afbeelding:
    afbeelding_base64 = base64.b64encode(
        afbeelding.read()
    ).decode()


st.markdown(
     f"""
      <style>
  

  
  

    /* ======================================================
       HERO BOVENAAN
       ====================================================== */

    .kg-hero {{
        position: relative;
        overflow: hidden;

        min-height: 270px;

        border-radius: 28px;

        background:
            linear-gradient(
                90deg,
                rgba(234, 243, 250, 1) 0%,
                rgba(234, 243, 250, 0.96) 42%,
                rgba(234, 243, 250, 0.45) 68%,
                rgba(234, 243, 250, 0.12) 100%
            ),
            url("data:image/jpeg;base64,{afbeelding_base64}");

        background-size: cover;
        background-position: center right;

        padding: 48px 52px;

        margin-bottom: 30px;

        border: 1px solid rgba(96, 125, 155, 0.15);

        box-shadow:
            0 12px 35px rgba(11, 31, 58, 0.08);
    }}


    .kg-hero-content {{
        position: relative;
        z-index: 2;

        width: 55%;
    }}


    .kg-label {{
        display: inline-block;

        background: rgba(255,255,255,0.72);

        color: #607D9B;

        padding: 7px 13px;

        border-radius: 999px;

        font-size: 13px;
        font-weight: 700;

        letter-spacing: 0.6px;

        margin-bottom: 15px;
    }}


    .kg-title {{
        color: #0B1F3A;

        font-size: 42px;
        font-weight: 800;

        line-height: 1.08;

        margin-bottom: 14px;
    }}


    .kg-description {{
        color: #607D9B;

        font-size: 18px;
        line-height: 1.55;

        max-width: 520px;
    }}


    /* ======================================================
       INPUTVELDEN
       ====================================================== */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {{
        background-color: #FFFFFF;

        border-radius: 12px;

        border-color: #D5E2EC;
    }}


    /* ======================================================
       KNOPPEN OP DE HOOFDPAGINA
       ====================================================== */

    section.main div.stButton > button {{
        background-color: #F07814;

        color: white;

        border: none;

        border-radius: 11px;

        font-weight: 700;

        min-height: 44px;

        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease,
            background-color 0.15s ease;
    }}


    section.main div.stButton > button p {{
        color: white !important;
    }}


    section.main div.stButton > button:hover {{
        background-color: #D9670C;

        color: white;

        transform: translateY(-1px);

        box-shadow:
            0 6px 15px rgba(240, 120, 20, 0.22);
    }}




    /* ======================================================
       KENNISGRAAF
       ====================================================== */

    iframe {{
        background: white;

        border-radius: 20px;

        border:
            1px solid #DCE8F1 !important;

        box-shadow:
            0 10px 30px rgba(11, 31, 58, 0.08);
    }}


    /* Dividers iets zachter */
    hr {{
        border-color: #DCE8F1 !important;
    }}

    </style>


<div class="kg-hero">
<div class="kg-hero-content">
<div class="kg-label">SPIDER • AMSTERDAM UMC</div>
<div class="kg-title">🕸️ Kennisgraaf</div>
<div class="kg-description">
Ontdek de verbanden tussen onderzoekers en hun expertise binnen Amsterdam UMC.
</div>
</div>
</div>
    """,
    unsafe_allow_html=True
)

# Database verbinding

db_path = os.path.join(os.path.dirname(__file__),"..", "spider.db")
conn = sqlite3.connect(db_path)
personen = pd.read_sql("SELECT * FROM persons", conn)
expertise = pd.read_sql("SELECT * FROM expertise", conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn)



# ============================================================
# FILTERS EN NAVIGATIE
# ============================================================

gefilterde_personen = personen.copy()

st.divider()

col1, col2, col3 = st.columns(
    [1, 1, 1],
    gap="large"
)


# ============================================================
# 1. FILTER KENNISGRAAF OP NAAM
# ============================================================

with col1:
    st.markdown("### 🔍 Filter kennisgraaf")

    naam_filter = st.text_input(
        "Zoek onderzoeker",
        placeholder="Bijvoorbeeld Robert",
        key="kg_naam_filter"
    )


# ============================================================
# 2. GA NAAR ONDERZOEKER
# ============================================================

with col2:
    st.markdown("### 👤 Ga naar onderzoeker")

    alle_namen = personen["name"].tolist()

    gekozen_naam = st.selectbox(
        "Selecteer onderzoeker",
        ["— kies —"] + alle_namen,
        key="kg_naam_select"
    )

    if gekozen_naam != "— kies —":

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


# ============================================================
# 3. GA NAAR EXPERTISE
# ============================================================

with col3:
    st.markdown("### 🔬 Ga naar expertise")

    expertise_opties = list(
        uitgewerkte_expertise.keys()
    )

    gekozen_exp = st.selectbox(
        "Selecteer expertise",
        ["— kies —"] + expertise_opties,
        key="kg_exp"
    )

    if gekozen_exp != "— kies —":

        if st.button(
            "Ga naar expertise",
            key="kg_naar_exp",
            use_container_width=True
        ):

            st.switch_page(
                uitgewerkte_expertise[gekozen_exp]
            )


# ============================================================
# NAAMFILTER TOEPASSEN OP KENNISGRAAF
# ============================================================

if naam_filter:

    gefilterde_personen = personen[
        personen["name"].str.contains(
            naam_filter,
            case=False,
            na=False
        )
    ]            

# Maak kennisgraaf
net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="#0B1F3A")
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


