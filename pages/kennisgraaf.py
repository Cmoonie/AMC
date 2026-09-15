import base64
import os
import sqlite3
import time

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network

from sidebar import toon_sidebar
from styling import apply_styling


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Kennisgraaf - Spider",
    layout="wide"
)

apply_styling("kennisgraaf")
toon_sidebar()


# ============================================================
# HERO + PAGINA-STYLING
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

    /* Multiselect tags */
    div[data-baseweb="tag"],
    div[data-baseweb="tag"] > span,
    div[data-baseweb="tag"] > div {{
        background: #F4F8FC !important;
        background-color: #F4F8FC !important;
        color: #0B1F3A !important;
    }}

    div[data-baseweb="tag"] span {{
        color: #0B1F3A !important;
        font-weight: 600 !important;
    }}

    div[data-baseweb="tag"] svg {{
        fill: #0B1F3A !important;
        color: #0B1F3A !important;
    }}

    div[data-baseweb="tag"] {{
        border: 1px solid #CED9E5 !important;
        border-radius: 8px !important;
    }}

    /* Hero */
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
        box-shadow: 0 12px 35px rgba(11, 31, 58, 0.08);
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
        max-width: 560px;
    }}

    /* Inputs */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {{
        background-color: #FFFFFF;
        border-radius: 12px;
        border-color: #D5E2EC;
    }}

    /* Buttons */
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
        box-shadow: 0 6px 15px rgba(240, 120, 20, 0.22);
    }}

    /* Kennisgraaf */
    iframe {{
        background: white;
        border-radius: 20px;
        border: 1px solid #DCE8F1 !important;
        box-shadow: 0 10px 30px rgba(11, 31, 58, 0.08);
    }}

    hr {{
        border-color: #DCE8F1 !important;
    }}

    </style>

    <div class="kg-hero">
        <div class="kg-hero-content">
            <div class="kg-label">SPIDER • AMSTERDAM UMC</div>
            <div class="kg-title">🕸️ Kennisgraaf</div>
            <div class="kg-description">
                Ontdek de verbanden tussen onderzoekers, expertise,
                publicaties en lopende projecten binnen Amsterdam UMC.
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

db_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "spider.db"
)

conn = sqlite3.connect(db_path)

personen = pd.read_sql(
    "SELECT * FROM persons",
    conn
)

expertise = pd.read_sql(
    "SELECT * FROM expertise",
    conn
)

personen_expertise = pd.read_sql(
    "SELECT * FROM persons_expertise",
    conn
)

publicaties = pd.read_sql(
    "SELECT * FROM publications",
    conn
)

try:
    auteur_aliases = pd.read_sql(
        "SELECT * FROM person_author_aliases",
        conn
    )
except Exception:
    auteur_aliases = pd.DataFrame(
        columns=["id", "person_id", "author_name"]
    )

lopende_projecten = pd.read_sql(
    "SELECT * FROM lopende_projecten",
    conn
)

try:
    project_deelnemers = pd.read_sql(
        "SELECT * FROM project_deelnemers",
        conn
    )
except Exception:
    project_deelnemers = pd.DataFrame(
        columns=["project_id", "persoon_id"]
    )


# ============================================================
# TITEL + FILTERS
# ============================================================

st.markdown("## Kennisgraaf")

st.caption(
    "Ontdek de relaties tussen onderzoekers, expertise, "
    "publicaties en lopende projecten binnen Amsterdam UMC."
)

# Beschikbare afdelingen bepalen
afdelingen = (
    personen["department"]
    .dropna()
    .astype(str)
    .str.strip()
)

afdelingen = sorted(
    [
        afdeling
        for afdeling in afdelingen.unique().tolist()
        if afdeling
    ]
)

# Alleen een afdelingsfilter tonen als er
# daadwerkelijk meerdere afdelingen zijn.
if len(afdelingen) > 1:

    filter_zoek, filter_afdeling, filter_type = st.columns(
        [2.2, 1.3, 2.2]
    )

else:

    filter_zoek, filter_type = st.columns(
        [2.2, 2.2]
    )

with filter_zoek:
    zoekterm = st.text_input(
        "Zoek in de kennisgraaf",
        placeholder="Bijvoorbeeld Robert of Amyloid",
        label_visibility="visible",
        key="kg_zoekterm"
    )

if len(afdelingen) > 1:

    with filter_afdeling:
        afdeling_filter = st.selectbox(
            "Afdeling",
            ["Alle afdelingen"] + afdelingen,
            label_visibility="visible",
            key="kg_afdeling"
        )

else:

    # Bij nul of één afdeling is een dropdown niet nodig.
    afdeling_filter = "Alle afdelingen"

with filter_type:
    zichtbare_types = st.multiselect(
        "Toon in kennisgraaf",
        [
            "🔵 Onderzoekers",
            "🟠 Expertise",
            "🟢 Lopende projecten",
            "🟣 Publicaties"
        ],
        default=[
            "🔵 Onderzoekers",
            "🟠 Expertise",
            "🟢 Lopende projecten",
            "🟣 Publicaties"
        ],
        label_visibility="visible",
        key="kg_types"
    )

zichtbare_types = [
    type_naam.replace("🔵 ", "")
             .replace("🟠 ", "")
             .replace("🟢 ", "")
             .replace("🟣 ", "")
    for type_naam in zichtbare_types
]

st.markdown("#### 👥 Onderzoekers tonen")

onderzoeker_namen = (
    personen["name"]
    .dropna()
    .astype(str)
    .sort_values()
    .tolist()
)

geselecteerde_onderzoekers = st.multiselect(
    "Kies één of meer onderzoekers",
    options=onderzoeker_namen,
    placeholder="Laat leeg om alle onderzoekers te tonen",
    key="kg_onderzoekers_selectie"
)

# ============================================================
# FILTERDATA BEREKENEN
# ============================================================

gefilterde_personen = personen.copy()

if geselecteerde_onderzoekers:

    gefilterde_personen = gefilterde_personen[
        gefilterde_personen["name"].isin(
            geselecteerde_onderzoekers
        )
    ]

if afdeling_filter != "Alle afdelingen":
    gefilterde_personen = gefilterde_personen[
        gefilterde_personen["department"] == afdeling_filter
    ]

if zoekterm:
    naam_match = gefilterde_personen[
        gefilterde_personen["name"].str.contains(
            zoekterm,
            case=False,
            na=False
        )
    ]

    expertise_match = expertise[
        expertise["label"].str.contains(
            zoekterm,
            case=False,
            na=False
        )
    ]

    expertise_ids_zoek = expertise_match["id"].tolist()

    personen_via_expertise = personen_expertise[
        personen_expertise["expertise_id"].isin(
            expertise_ids_zoek
        )
    ]["person_id"].tolist()

    extra_personen = gefilterde_personen[
        gefilterde_personen["id"].isin(
            personen_via_expertise
        )
    ]

    gefilterde_personen = pd.concat(
        [
            naam_match,
            extra_personen
        ],
        ignore_index=True
    ).drop_duplicates(
        subset=["id"]
    )

persoon_ids = gefilterde_personen["id"].tolist()

gefilterde_koppelingen = personen_expertise[
    personen_expertise["person_id"].isin(
        persoon_ids
    )
]

expertise_ids = (
    gefilterde_koppelingen["expertise_id"]
    .dropna()
    .unique()
    .tolist()
)

gefilterde_expertise = expertise[
    expertise["id"].isin(
        expertise_ids
    )
]


# ============================================================
# PROJECTEN BEREKENEN
# ============================================================

project_ids = set()

if not lopende_projecten.empty:
    projecten_leider = lopende_projecten[
        lopende_projecten["leider_id"].isin(
            persoon_ids
        )
    ]

    project_ids.update(
        projecten_leider["id"].tolist()
    )

if not project_deelnemers.empty:
    deelnemers_matches = project_deelnemers[
        project_deelnemers["persoon_id"].isin(
            persoon_ids
        )
    ]

    project_ids.update(
        deelnemers_matches["project_id"].tolist()
    )

gefilterde_projecten = lopende_projecten[
    lopende_projecten["id"].isin(
        list(project_ids)
    )
]


#============================================================
# PUBLICATIES KOPPELEN
# ============================================================

publicatie_koppelingen = []
max_publicaties = 300


def onderzoeker_in_auteurs(auteurs, namen):
    """
    Controleert of één van de bekende namen van een onderzoeker
    voorkomt in het auteursveld van een publicatie.
    """

    if pd.isna(auteurs):
        return False

    auteurs = str(auteurs).lower()

    for naam in namen:

        if not naam:
            continue

        naam = str(naam).strip().lower()

        if not naam:
            continue

        # Exacte naam/alias komt voor
        if naam in auteurs:
            return True

    return False


aantal_unieke_publicaties = 0

for _, publicatie in publicaties.iterrows():

    gekoppelde_onderzoekers = []

    auteurs = publicatie.get(
        "authors",
        ""
    )

    for _, persoon in gefilterde_personen.iterrows():

        persoon_id = int(
            persoon["id"]
        )

        # Begin altijd met de gewone naam uit persons
        mogelijke_namen = [
            str(persoon["name"])
        ]

        # Voeg alle PubMed-auteursnamen van deze persoon toe
        aliases_persoon = auteur_aliases[
            auteur_aliases["person_id"] == persoon_id
        ]

        for _, alias in aliases_persoon.iterrows():

            author_name = str(
                alias["author_name"]
            ).strip()

            if author_name:
                mogelijke_namen.append(
                    author_name
                )

        # Controleer gewone naam + alle aliassen
        if onderzoeker_in_auteurs(
            auteurs,
            mogelijke_namen
        ):
            gekoppelde_onderzoekers.append(
                persoon_id
            )

    # Alleen publicaties toevoegen wanneer minimaal
    # één zichtbare onderzoeker eraan gekoppeld is
    if gekoppelde_onderzoekers:

        for gekoppeld_persoon_id in gekoppelde_onderzoekers:

            publicatie_koppelingen.append(
                {
                    "pmid": publicatie["pmid"],
                    "title": publicatie.get(
                        "title",
                        "Publicatie"
                    ),
                    "persoon_id": gekoppeld_persoon_id
                }
            )

        aantal_unieke_publicaties += 1

    if aantal_unieke_publicaties >= max_publicaties:
        break


publicatie_df = pd.DataFrame(
    publicatie_koppelingen
)


# ============================================================
# GEDEELDE ITEMS BEREKENEN
# ============================================================

gedeelde_expertise_ids = set()

if not gefilterde_koppelingen.empty:
    expertise_aantallen_nav = (
        gefilterde_koppelingen
        .groupby("expertise_id")["person_id"]
        .nunique()
    )

    gedeelde_expertise_ids = set(
        expertise_aantallen_nav[
            expertise_aantallen_nav > 1
        ].index.tolist()
    )


gedeelde_publicatie_ids = set()

if not publicatie_df.empty:
    publicatie_aantallen_nav = (
        publicatie_df
        .groupby("pmid")["persoon_id"]
        .nunique()
    )

    gedeelde_publicatie_ids = set(
        publicatie_aantallen_nav[
            publicatie_aantallen_nav > 1
        ].index.tolist()
    )


gedeelde_project_ids = set()

if not gefilterde_projecten.empty:
    for _, project in gefilterde_projecten.iterrows():
        betrokken_personen = set()

        if project["leider_id"] in persoon_ids:
            betrokken_personen.add(
                int(project["leider_id"])
            )

        if not project_deelnemers.empty:
            deelnemers_project = project_deelnemers[
                project_deelnemers["project_id"]
                == project["id"]
            ]

            for _, deelnemer in deelnemers_project.iterrows():
                deelnemer_id = int(
                    deelnemer["persoon_id"]
                )

                if deelnemer_id in persoon_ids:
                    betrokken_personen.add(
                        deelnemer_id
                    )

        if len(betrokken_personen) > 1:
            gedeelde_project_ids.add(
                int(project["id"])
            )


# ============================================================
# NAVIGATIE DIRECT ONDER DE FILTERS
# ============================================================

st.markdown("### 🔗 Bekijk onderdelen uit de kennisgraaf")

st.caption(
    "Selecteer een onderzoeker, expertisegebied, lopend project "
    "of publicatie. ★ betekent dat meerdere zichtbare onderzoekers "
    "dit item delen."
)

nav_onderzoeker, nav_expertise = st.columns(2)

with nav_onderzoeker:
    st.markdown("#### 👤 Onderzoeker")

    onderzoeker_opties = {
        str(persoon["name"]): int(persoon["id"])
        for _, persoon in gefilterde_personen.iterrows()
    }

    if onderzoeker_opties:
        gekozen_onderzoeker = st.selectbox(
            "Kies onderzoeker",
            list(onderzoeker_opties.keys()),
            key="kg_nav_onderzoeker"
        )

        if st.button(
            "👤 Bekijk onderzoeker",
            key="kg_open_onderzoeker",
            use_container_width=True
        ):
            st.session_state.geselecteerde_persoon = (
                onderzoeker_opties[
                    gekozen_onderzoeker
                ]
            )

            st.switch_page(
                "pages/onderzoeker.py"
            )
    else:
        st.info(
            "Geen onderzoekers zichtbaar."
        )


with nav_expertise:
    st.markdown("#### 🔬 Expertise")

    expertise_opties = {}

    for _, exp in gefilterde_expertise.iterrows():

        exp_id = int(
            exp["id"]
        )

        label = str(
            exp["label"]
        )

        weergave = label

        if exp_id in gedeelde_expertise_ids:
            weergave += " ★ gedeeld"

        expertise_opties[
            weergave
        ] = exp_id


    if expertise_opties:

        gekozen_expertise = st.selectbox(
            "Kies expertise",
            list(
                expertise_opties.keys()
            ),
            key="kg_nav_expertise"
        )


        if st.button(
            "🔬 Bekijk expertise",
            key="kg_open_expertise",
            use_container_width=True
        ):

            st.session_state[
                "geselecteerde_expertise_id"
            ] = expertise_opties[
                gekozen_expertise
            ]

            st.switch_page(
                "pages/expertise.py"
            )

    else:

        st.info(
            "Geen expertise zichtbaar."
        )

nav_project, nav_publicatie = st.columns(2)

with nav_project:
    st.markdown("#### 🧪 Lopend project")

    project_opties = {}

    for _, project in gefilterde_projecten.iterrows():
        project_id = int(project["id"])
        naam = str(project["naam"])

        weergave = naam

        if project_id in gedeelde_project_ids:
            weergave += " ★ gedeeld"

        project_opties[weergave] = project_id

    if project_opties:
        gekozen_project = st.selectbox(
            "Kies lopend project",
            list(project_opties.keys()),
            key="kg_nav_project"
        )

        if st.button(
            "🧪 Bekijk lopend project",
            key="kg_open_project",
            use_container_width=True
        ):
            st.session_state.geselecteerd_lopend_project = (
                project_opties[
                    gekozen_project
                ]
            )

            st.switch_page(
                "pages/lopend_project.py"
            )
    else:
        st.info(
            "Geen lopende projecten zichtbaar."
        )


with nav_publicatie:
    st.markdown("#### 📚 Publicatie")

    publicatie_opties = {}

    if not publicatie_df.empty:
        unieke_publicaties = (
            publicatie_df
            .drop_duplicates(
                subset=["pmid"]
            )
        )

        for _, publicatie in unieke_publicaties.iterrows():
            pmid = publicatie["pmid"]
            titel = str(publicatie["title"])

            weergave = titel

            if pmid in gedeelde_publicatie_ids:
                weergave += " ★ gedeeld"

            publicatie_opties[weergave] = str(
                pmid
            )

    if publicatie_opties:
        gekozen_publicatie = st.selectbox(
            "Kies publicatie",
            list(publicatie_opties.keys()),
            key="kg_nav_publicatie"
        )

        gekozen_pmid = publicatie_opties[
            gekozen_publicatie
        ]

        st.link_button(
            "📚 Bekijk publicatie",
            f"https://pubmed.ncbi.nlm.nih.gov/{gekozen_pmid}/",
            use_container_width=True
        )
    else:
        st.info(
            "Geen publicaties zichtbaar."
        )


# ============================================================
# LEGENDA
# ============================================================

st.markdown(
    '<div style="'
    'background:white;'
    'border:1px solid #DCE8F1;'
    'border-radius:14px;'
    'padding:16px 18px;'
    'margin-top:20px;'
    'margin-bottom:14px;'
    'font-size:16px;'
    'color:#0B1F3A;'
    '">'

    '<div style="'
    'font-weight:700;'
    'margin-bottom:10px;'
    '">'
    'Legenda'
    '</div>'

    '<div style="'
    'display:flex;'
    'gap:24px;'
    'align-items:center;'
    'flex-wrap:wrap;'
    'margin-bottom:12px;'
    '">'

    '<span><b style="color:#69A9F5;font-size:20px;">●</b> Onderzoeker</span>'
    '<span><b style="color:#F07814;font-size:20px;">●</b> Expertise</span>'
    '<span><b style="color:#61C574;font-size:20px;">●</b> Lopend project</span>'
    '<span><b style="color:#8B5CF6;font-size:20px;">●</b> Publicatie</span>'

    '</div>'

    '<div style="'
    'display:flex;'
    'gap:28px;'
    'align-items:center;'
    'flex-wrap:wrap;'
    'padding-top:10px;'
    'border-top:1px solid #E5EDF4;'
    '">'

    '<span>'
    '<span style="'
    'display:inline-block;'
    'width:38px;'
    'border-top:2px solid #AFC4D6;'
    'vertical-align:middle;'
    'margin-right:8px;'
    '"></span>'
    'Directe relatie'
    '</span>'

    '<span>'
    '<span style="'
    'display:inline-block;'
    'width:38px;'
    'border-top:6px solid #F07814;'
    'vertical-align:middle;'
    'margin-right:8px;'
    '"></span>'
    'Gedeelde expertise'
    '</span>'

    '<span>'
    '<span style="'
    'display:inline-block;'
    'width:38px;'
    'border-top:6px solid #61C574;'
    'vertical-align:middle;'
    'margin-right:8px;'
    '"></span>'
    'Gedeeld project'
    '</span>'

    '<span>'
    '<span style="'
    'display:inline-block;'
    'width:38px;'
    'border-top:6px solid #8B5CF6;'
    'vertical-align:middle;'
    'margin-right:8px;'
    '"></span>'
    'Gedeelde publicatie'
    '</span>'

    '</div>'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# PYVIS KENNISGRAAF OPBOUWEN
# ============================================================

net = Network(
    height="690px",
    width="100%",
    bgcolor="#FFFFFF",
    font_color="#0B1F3A"
)

net.set_options(
    """
    {
        "nodes": {
            "borderWidth": 2,
            "shadow": {
                "enabled": true,
                "color": "rgba(11,31,58,0.15)",
                "size": 8,
                "x": 2,
                "y": 3
            }
        },
        "edges": {
            "color": {
                "color": "#AFC4D6",
                "highlight": "#607D9B",
                "hover": "#607D9B"
            },
            "width": 1.6,
            "smooth": {
                "enabled": true,
                "type": "continuous"
            }
        },
        "physics": {
            "enabled": true,
            "barnesHut": {
                "gravitationalConstant": -11500,
                "centralGravity": 0.22,
                "springLength": 145,
                "springConstant": 0.04,
                "damping": 0.18,
                "avoidOverlap": 0.55
            },
            "minVelocity": 0.75
        },
        "interaction": {
            "hover": true,
            "navigationButtons": true,
            "keyboard": true,
            "zoomView": true,
            "dragView": true
        }
    }
    """
)


# Onderzoekers
if "Onderzoekers" in zichtbare_types:
    for _, persoon in gefilterde_personen.iterrows():
        net.add_node(
            f"p_{persoon['id']}",
            label=persoon["name"],
            color={
                "background": "#69A9F5",
                "border": "#3F83CC",
                "highlight": {
                    "background": "#8BC0FF",
                    "border": "#2E75B6"
                }
            },
            size=29,
            shape="dot",
            font={
                "size": 17,
                "color": "#0B1F3A",
                "face": "Arial"
            },
            title=(
                f"Onderzoeker: {persoon['name']}"
            )
        )


# Expertise
if "Expertise" in zichtbare_types:
    for _, exp in gefilterde_expertise.iterrows():
        net.add_node(
            f"e_{exp['id']}",
            label=exp["label"],
            color={
                "background": "#F07814",
                "border": "#D9650B"
            },
            size=24,
            shape="dot",
            font={
                "size": 16,
                "color": "#0B1F3A"
            },
            title=(
                f"Expertise: {exp['label']}"
            )
        )


# Lopende projecten
if "Lopende projecten" in zichtbare_types:
    for _, project in gefilterde_projecten.iterrows():
        net.add_node(
            f"project_{project['id']}",
            label=project["naam"],
            color={
                "background": "#61C574",
                "border": "#3EA653"
            },
            size=26,
            shape="dot",
            font={
                "size": 15,
                "color": "#0B1F3A"
            },
            title=(
                f"Lopend project: {project['naam']}"
            )
        )


# Publicaties
if (
    "Publicaties" in zichtbare_types
    and not publicatie_df.empty
):
    for _, publicatie in publicatie_df.drop_duplicates(
        subset=["pmid"]
    ).iterrows():
        titel = str(
            publicatie["title"]
        )

        korte_titel = titel

        if len(korte_titel) > 32:
            korte_titel = (
                korte_titel[:29]
                + "..."
            )

        net.add_node(
            f"pub_{publicatie['pmid']}",
            label=korte_titel,
            color={
                "background": "#8B5CF6",
                "border": "#6D3FD4"
            },
            size=18,
            shape="dot",
            font={
                "size": 13,
                "color": "#0B1F3A"
            },
            title=titel
        )


# Relaties: persoon ↔ expertise
if (
    "Onderzoekers" in zichtbare_types
    and "Expertise" in zichtbare_types
):
    expertise_aantallen = (
        gefilterde_koppelingen
        .groupby("expertise_id")["person_id"]
        .nunique()
        .to_dict()
    )

    for _, koppeling in gefilterde_koppelingen.iterrows():
        expertise_id = koppeling["expertise_id"]

        gedeeld = (
            expertise_aantallen.get(
                expertise_id,
                0
            ) > 1
        )

        net.add_edge(
            f"p_{koppeling['person_id']}",
            f"e_{expertise_id}",
            color="#F07814" if gedeeld else "#AFC4D6",
            width=6 if gedeeld else 1.6,
            title=(
                "Gedeelde expertise"
                if gedeeld
                else "Expertise van onderzoeker"
            )
        )


# Relaties: onderzoeker ↔ lopend project
if (
    "Onderzoekers" in zichtbare_types
    and "Lopende projecten" in zichtbare_types
):
    for _, project in gefilterde_projecten.iterrows():
        betrokken_personen = set()

        if project["leider_id"] in persoon_ids:
            betrokken_personen.add(
                int(project["leider_id"])
            )

        if not project_deelnemers.empty:
            deelnemers_project = project_deelnemers[
                project_deelnemers["project_id"]
                == project["id"]
            ]

            for _, deelnemer in deelnemers_project.iterrows():
                deelnemer_id = int(
                    deelnemer["persoon_id"]
                )

                if deelnemer_id in persoon_ids:
                    betrokken_personen.add(
                        deelnemer_id
                    )

        gedeeld = len(betrokken_personen) > 1

        for betrokken_id in betrokken_personen:
            net.add_edge(
                f"p_{betrokken_id}",
                f"project_{project['id']}",
                color="#61C574" if gedeeld else "#AFC4D6",
                width=6 if gedeeld else 1.6,
                title=(
                    "Gedeeld lopend project"
                    if gedeeld
                    else "Lopend project"
                )
            )


# Relaties: persoon ↔ publicatie
if (
    "Onderzoekers" in zichtbare_types
    and "Publicaties" in zichtbare_types
    and not publicatie_df.empty
):
    publicatie_aantallen = (
        publicatie_df
        .groupby("pmid")["persoon_id"]
        .nunique()
        .to_dict()
    )

    for _, koppeling in publicatie_df.iterrows():
        pmid = koppeling["pmid"]

        gedeeld = (
            publicatie_aantallen.get(
                pmid,
                0
            ) > 1
        )

        net.add_edge(
            f"p_{koppeling['persoon_id']}",
            f"pub_{pmid}",
            color="#8B5CF6" if gedeeld else "#AFC4D6",
            width=6 if gedeeld else 1.6,
            title=(
                "Gedeelde publicatie"
                if gedeeld
                else "Publicatie van onderzoeker"
            )
        )


# ============================================================
# KENNISGRAAF TONEN
# ============================================================

os.makedirs(
    "temp",
    exist_ok=True
)

bestandsnaam = (
    f"temp/kennisgraaf_"
    f"{int(time.time())}.html"
)

net.save_graph(
    bestandsnaam
)

with open(
    bestandsnaam,
    "r",
    encoding="utf-8"
) as bestand:
    html_content = bestand.read()

components.html(
    html_content,
    height=730
)


# ============================================================
# STATISTIEKEN
# ============================================================

aantal_onderzoekers = len(
    gefilterde_personen
)

aantal_expertise = len(
    gefilterde_expertise
)

aantal_projecten = len(
    gefilterde_projecten
)

aantal_publicaties = (
    publicatie_df["pmid"].nunique()
    if not publicatie_df.empty
    else 0
)

st.caption(
    f"👤 {aantal_onderzoekers} onderzoekers   •   "
    f"🔬 {aantal_expertise} expertisegebieden   •   "
    f"🧪 {aantal_projecten} lopende projecten   •   "
    f"📚 {aantal_publicaties} publicaties"
)

conn.close()
