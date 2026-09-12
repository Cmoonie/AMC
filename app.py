import streamlit as st

st.set_page_config(
    page_title="Spider",
    page_icon="🕷️",
    layout="wide"
)

from sidebar import toon_sidebar
import json
import os
import sqlite3

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer

from expertise_routes import uitgewerkte_expertise, pagina_namen
from styling import apply_styling





# ============================================================
# DATABASE + OMGEVINGSVARIABELEN
# ============================================================
db_path = os.path.join(os.path.dirname(__file__), "spider.db")
conn = sqlite3.connect(db_path)

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)


# ============================================================
# LOGIN
# ============================================================
if "ingelogd" not in st.session_state:
    st.session_state.ingelogd = False



gebruikersnaam = st.session_state.get("gebruikersnaam", "")
rol = st.session_state.get("rol", "")

toon_sidebar()

# ============================================================
# STYLING
# ============================================================
apply_styling("home")

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)




# ============================================================
# EMBEDDINGMODEL
# ============================================================
@st.cache_resource
def laad_model():
    return SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


model = laad_model()


# ============================================================
# FUNCTIES
# ============================================================
def semantisch_zoeken(zoekterm, top_n=15):
    """Zoek semantisch in publicatie-embeddings en bewaar de score."""
    zoek_embedding = model.encode(zoekterm)

    embeddings_df = pd.read_sql(
        "SELECT pmid, embedding FROM publication_embeddings",
        conn,
    )

    scores = []

    for _, rij in embeddings_df.iterrows():
        pub_embedding = np.array(json.loads(rij["embedding"]))

        noemer = np.linalg.norm(zoek_embedding) * np.linalg.norm(pub_embedding)

        if noemer == 0:
            continue

        score = np.dot(zoek_embedding, pub_embedding) / noemer

        scores.append(
            {
                "pmid": rij["pmid"],
                "score": float(score),
            }
        )

    scores.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return scores[:top_n]


def publicaties_van_persoon(relevante_publicaties, naam):
    """Filter de semantisch relevante publicaties op onderzoeker."""
    if relevante_publicaties.empty or "authors" not in relevante_publicaties.columns:
        return pd.DataFrame()

    auteurs = relevante_publicaties["authors"].fillna("").astype(str)

    volledige_naam = auteurs.str.contains(
        str(naam),
        case=False,
        regex=False,
    )

    resultaat_persoon = relevante_publicaties[volledige_naam]

    if not resultaat_persoon.empty:
        return resultaat_persoon

    naamdelen = str(naam).split()

    if not naamdelen:
        return pd.DataFrame()

    achternaam = naamdelen[-1]

    return relevante_publicaties[
        auteurs.str.contains(
            achternaam,
            case=False,
            regex=False,
        )
    ]


def genereer_samenvatting(zoekterm, resultaat, relevante_publicaties):
    """Genereer een concrete AI-uitleg op basis van gevonden publicaties."""
    namen = resultaat["name"].tolist()

    publicatie_context = []

    if not relevante_publicaties.empty:
        for _, publicatie in relevante_publicaties.head(5).iterrows():
            titel = publicatie.get("title", "Onbekende titel")
            auteurs = publicatie.get("authors", "")
            score = publicatie.get("similarity", None)

            regel = f"Titel: {titel}. Auteurs: {auteurs}."

            if score is not None and pd.notna(score):
                regel += f" Semantische overeenkomst: {score:.3f}."

            if "abstract" in relevante_publicaties.columns:
                abstract = publicatie.get("abstract", "")
                if pd.notna(abstract) and str(abstract).strip():
                    regel += f" Abstract: {str(abstract)[:900]}"

            publicatie_context.append(regel)

    context_tekst = "\n".join(publicatie_context)

    prompt = (
        f"De gebruiker zoekt naar: '{zoekterm}'.\n"
        f"Gevonden onderzoekers: {namen}.\n\n"
        "Hieronder staan de publicaties die semantisch het sterkst aansluiten:\n"
        f"{context_tekst}\n\n"
        "Geef in het Nederlands een korte, concrete uitleg van maximaal 4 zinnen. "
        "Leg uit waarom de gevonden onderzoekers relevant zijn voor de zoekvraag en "
        "verwijs inhoudelijk naar de gevonden publicaties. Noem alleen informatie die "
        "uit bovenstaande gegevens volgt. Zeg niet dat iemand een specialist is als dat "
        "niet uit de gegevens blijkt."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content


def haal_expertise_op(persoon_id):
    """
    Haal unieke expertise + bijbehorende pagina op
    voor één onderzoeker.
    """
    exp_ids = personen_expertise[
        personen_expertise["person_id"] == persoon_id
    ]["expertise_id"].tolist()

    exp_details = expertise[
        expertise["id"].isin(exp_ids)
    ]

    gematchte = exp_details[
        exp_details["label"]
        .str.lower()
        .isin(uitgewerkte_expertise)
    ]

    expertise_links = []
    bestemmingen = set()

    for _, exp in gematchte.iterrows():
        pagina = uitgewerkte_expertise[
            exp["label"].lower()
        ]

        if pagina not in bestemmingen:
            bestemmingen.add(pagina)

            naam = pagina_namen.get(
                pagina,
                exp["label"],
            )

            expertise_links.append(
                {
                    "naam": naam,
                    "pagina": pagina,
                }
            )

    return expertise_links


def open_projecten_van_persoon(persoon_id):
    """Open direct één project of een overzicht bij meerdere projecten."""
    projecten_persoon = pd.read_sql(
        """
        SELECT id
        FROM lopende_projecten
        WHERE leider_id = ?
        """,
        conn,
        params=(persoon_id,),
    )

    if len(projecten_persoon) == 1:
        st.session_state.geselecteerd_lopend_project = int(
            projecten_persoon.iloc[0]["id"]
        )
        st.switch_page("pages/lopend_project.py")

    elif len(projecten_persoon) > 1:
        st.session_state.lopende_projecten_persoon = persoon_id
        st.switch_page("pages/lopende_projecten_overzicht.py")


# ============================================================
# SESSION STATE
# ============================================================
if "geselecteerde_persoon" not in st.session_state:
    st.session_state.geselecteerde_persoon = None

if "laatste_zoekterm" not in st.session_state:
    st.session_state.laatste_zoekterm = ""


# ============================================================
# DATA INLADEN
# ============================================================
personen = pd.read_sql("SELECT * FROM persons", conn)
expertise = pd.read_sql("SELECT * FROM expertise", conn)
personen_expertise = pd.read_sql("SELECT * FROM persons_expertise", conn)


# =========================
# HERO BOVENAAN ZOEKPAGINA
# =========================

hero_afbeelding = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "zoekpagina.jpg"
)

hero_links, hero_rechts = st.columns(
    [1.35, 1],
    gap="large"
)

with hero_links:
    st.markdown(
        """
        <div class="hero-label">
            Amsterdam UMC
        </div>

        <div class="hero-title">
            Eén zoekmachine voor medische kennis
        </div>

        <div class="hero-text">
            Vind onderzoekers, projecten en publicaties
            die het verschil maken.
        </div>
        """,
        unsafe_allow_html=True
    )

with hero_rechts:
    if os.path.exists(hero_afbeelding):
        st.image(
            hero_afbeelding,
            use_container_width=True
        )

# # ============================================================
# # PAGINAKOP
# # ============================================================
# st.title("Spider")
# st.subheader("Zoek onderzoeksexpertise binnen Division 9")


# ============================================================
# DEPARTMENTFILTER
# Alleen zichtbaar bij meerdere departments
# ============================================================
afdelingen = (
    personen["department"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

if len(afdelingen) > 1:
    department_filter = st.selectbox(
        "Filter op department",
        ["Alle"] + afdelingen,
    )
else:
    department_filter = "Alle"


# ============================================================
# ZOEKBALK
# ============================================================
zoek_col, knop_col = st.columns([5, 1])

with zoek_col:
    zoekterm = st.text_input(
        "Zoek op naam, project of expertise",
        value=st.session_state.laatste_zoekterm,
        placeholder="Waar ben je naar op zoek?",
        label_visibility="collapsed",
    )

with knop_col:
    if st.button(
        "🔍",
        type="primary",
        use_container_width=True,
    ):
        pass

if zoekterm:
    st.session_state.laatste_zoekterm = zoekterm


# ============================================================
# ZOEKEN
# ============================================================
if zoekterm:

    # --------------------------------------------------------
    # Departmentfilter toepassen
    # --------------------------------------------------------
    if department_filter != "Alle":
        personen_gefilterd = personen[
            personen["department"] == department_filter
        ]
    else:
        personen_gefilterd = personen


    # --------------------------------------------------------
    # Zoeken op naam / department
    # --------------------------------------------------------
    naam_resultaat = personen_gefilterd[
        personen_gefilterd["name"].str.contains(
            zoekterm,
            case=False,
            na=False,
        )
        |
        personen_gefilterd["department"].str.contains(
            zoekterm,
            case=False,
            na=False,
        )
    ]


    # --------------------------------------------------------
    # Zoeken op expertise
    # --------------------------------------------------------
    expertise_match = expertise[
        expertise["label"].str.contains(
            zoekterm,
            case=False,
            na=False,
        )
    ]

    expertise_ids = expertise_match["id"].tolist()

    personen_ids = personen_expertise[
        personen_expertise["expertise_id"].isin(expertise_ids)
    ]["person_id"].tolist()

    expertise_resultaat = personen_gefilterd[
        personen_gefilterd["id"].isin(personen_ids)
    ]


    # --------------------------------------------------------
    # Normale resultaten combineren
    # --------------------------------------------------------
    resultaat = pd.concat(
        [naam_resultaat, expertise_resultaat],
        ignore_index=True,
    ).drop_duplicates(subset=["id"])


    # --------------------------------------------------------
    # Semantisch zoeken via publicaties
    # --------------------------------------------------------
    semantische_scores = semantisch_zoeken(zoekterm)

    top_pmids = [
        item["pmid"]
        for item in semantische_scores
    ]

    relevante_publicaties = pd.DataFrame()

    if top_pmids:
        placeholders = ",".join(["?"] * len(top_pmids))

        semantische_resultaten = pd.read_sql(
            f"""
            SELECT DISTINCT p.*
            FROM persons p
            JOIN publications pub
                ON (
                    LOWER(pub.authors) LIKE LOWER('%' || p.name || '%')
                    OR LOWER(pub.authors) LIKE LOWER(
                        '%' ||
                        SUBSTR(
                            p.name,
                            INSTR(p.name, ' ') + 1
                        ) ||
                        '%'
                    )
                )
            WHERE pub.pmid IN ({placeholders})
            """,
            conn,
            params=top_pmids,
        )

        if department_filter != "Alle":
            semantische_resultaten = semantische_resultaten[
                semantische_resultaten["department"] == department_filter
            ]

        resultaat = pd.concat(
            [resultaat, semantische_resultaten],
            ignore_index=True,
        ).drop_duplicates(subset=["id"])

        relevante_publicaties = pd.read_sql(
            f"""
            SELECT *
            FROM publications
            WHERE pmid IN ({placeholders})
            """,
            conn,
            params=top_pmids,
        )

        # PMID aan beide kanten hetzelfde datatype geven
        score_lookup = {
            str(item["pmid"]).strip(): item["score"]
            for item in semantische_scores
        }

        relevante_publicaties["pmid_match"] = (
            relevante_publicaties["pmid"]
            .astype(str)
            .str.strip()
        )

        relevante_publicaties["similarity"] = (
            relevante_publicaties["pmid_match"]
            .map(score_lookup)
        )
        relevante_publicaties = relevante_publicaties.sort_values(
        "similarity",
        ascending=False,
    )

    # --------------------------------------------------------
    # Aantal resultaten
    # --------------------------------------------------------
    st.success(f"{len(resultaat)} onderzoeker(s) gevonden")


    # ========================================================
    # RESULTATENLAYOUT
    # ========================================================
    col_links, col_rechts = st.columns(
        [1, 1],
        gap="large",
    )


    # ========================================================
    # LINKERKOLOM — ONDERZOEKERS
    # ========================================================
    with col_links:
        st.subheader("Gevonden onderzoekers")

        lopende = pd.read_sql(
            "SELECT leider_id FROM lopende_projecten",
            conn,
        )

        actieve_leiders = set(
            lopende["leider_id"].tolist()
        )

        if resultaat.empty:
            st.info(
                "Geen onderzoekers gevonden voor deze zoekterm."
            )

        else:
            for _, persoon in resultaat.iterrows():

                persoon_id = persoon["id"]
                actief = persoon_id in actieve_leiders

                with st.container(border=True):

                    # ----------------------------------------
                    # Naam
                    # ----------------------------------------
                    st.markdown(
                        f"### 👤 {persoon['name']}"
                    )

                    # ----------------------------------------
                    # Status
                    # ----------------------------------------
                    if actief:
                        st.caption("🟢 Lopend project")
                    else:
                        st.caption("Onderzoeker")

                    # ----------------------------------------
                    # Expertise
                    # ----------------------------------------
                    expertise_links = haal_expertise_op(
                        persoon_id
                    )

                    if expertise_links:
                        st.markdown("**Expertise**")

                        aantal_kolommen = min(
                            len(expertise_links),
                            3,
                        )

                        expertise_kolommen = st.columns(
                            aantal_kolommen
                        )

                        for index, exp in enumerate(
                            expertise_links
                        ):
                            kolom = expertise_kolommen[
                                index % aantal_kolommen
                            ]

                            with kolom:
                                if st.button(
                                    f"🔬 {exp['naam']}",
                                    key=(
                                        f"expertise_"
                                        f"{persoon_id}_"
                                        f"{index}"
                                    ),
                                    use_container_width=True,
                                ):
                                    st.switch_page(
                                        exp["pagina"]
                                    )

                    # Kleine ruimte vóór actieknoppen
                    st.write("")

                    # ----------------------------------------
                    # Actieknoppen
                    # ----------------------------------------
                    knop_profiel, knop_project = st.columns(
                        [2, 1]
                    )

                    with knop_profiel:
                        if st.button(
                            "Bekijk profiel",
                            key=f"persoon_{persoon_id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state.geselecteerde_persoon = (
                                persoon_id
                            )

                            st.switch_page(
                                "pages/onderzoeker.py"
                            )

                    with knop_project:
                        if actief:
                            if st.button(
                                "🔬 Project",
                                key=f"project_{persoon_id}",
                                use_container_width=True,
                            ):
                                open_projecten_van_persoon(
                                    persoon_id
                                )

                    # ----------------------------------------
                    # Relevante publicaties van deze onderzoeker
                    # ----------------------------------------
                    publicaties_persoon = publicaties_van_persoon(
                        relevante_publicaties,
                        persoon["name"],
                    )

                    if not publicaties_persoon.empty:
                        st.divider()
                        st.markdown("**📚 Relevante publicaties**")

                        for _, publicatie in (
                            publicaties_persoon
                            .head(3)
                            .iterrows()
                        ):
                            titel = publicatie.get(
                                "title",
                                "Publicatie zonder titel",
                            )

                            score = publicatie.get(
                                "similarity",
                                None,
                            )

                            if score is None or pd.isna(score):
                                st.caption(
                                    "Relevantie kon niet worden berekend."
                                )
                                continue

                            # Dit is een indicatie van semantische overeenkomst,
                            # geen wetenschappelijke accuracy-score.
                            percentage = max(
                                0,
                                min(100, round(float(score) * 100)),
                            )

                            st.markdown(f"**{titel}**")
                            st.caption(
                                f"Relevantie voor zoekvraag: {percentage}%"
                            )
                            st.progress(percentage / 100)

                            # Link naar PubMed
                            pmid = publicatie["pmid"]

                            if pd.notna(pmid):
                                pmid = str(pmid).strip()

                                st.link_button(
                                    "🔗 Bekijk publicatie op PubMed",
                                    f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                                    use_container_width=True
                                )


    # ========================================================
    # RECHTERKOLOM — AI-UITLEG
    # ========================================================
    with col_rechts:
        st.subheader("✨ AI-uitleg")

        if resultaat.empty:
            st.info(
                "Er zijn geen onderzoekers gevonden om "
                "een samenvatting van te maken."
            )

        else:
            with st.spinner(
                "Samenvatting genereren ..."
            ):
                try:
                    samenvatting = genereer_samenvatting(
                        zoekterm,
                        resultaat,
                        relevante_publicaties,
                    )

                    st.markdown(
                        f"""
                        <div class="ai-summary">
                            {samenvatting}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                except Exception as fout:
                    st.warning(
                        "De AI-samenvatting kon op dit moment "
                        "niet worden gegenereerd."
                    )
                    st.caption(str(fout))
