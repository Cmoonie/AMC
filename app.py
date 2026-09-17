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
import re


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
    """
    Filter semantisch relevante publicaties op onderzoeker
    en sorteer altijd van hoogste naar laagste relevantie.
    """

    if (
        relevante_publicaties.empty
        or "authors" not in relevante_publicaties.columns
    ):
        return pd.DataFrame()

    auteurs = (
        relevante_publicaties["authors"]
        .fillna("")
        .astype(str)
    )

    volledige_naam = auteurs.str.contains(
        str(naam),
        case=False,
        regex=False,
    )

    resultaat_persoon = relevante_publicaties[
        volledige_naam
    ].copy()

    # Als de volledige naam resultaten geeft,
    # altijd expliciet sorteren op de echte similarity-score.
    if not resultaat_persoon.empty:

        if "similarity" in resultaat_persoon.columns:
            resultaat_persoon["similarity"] = pd.to_numeric(
                resultaat_persoon["similarity"],
                errors="coerce",
            )

            resultaat_persoon = resultaat_persoon.sort_values(
                by="similarity",
                ascending=False,
                na_position="last",
            )

        return resultaat_persoon

    # --------------------------------------------------------
    # FALLBACK: ACHTERNAAM
    # --------------------------------------------------------

    naamdelen = str(naam).split()

    if not naamdelen:
        return pd.DataFrame()

    achternaam = naamdelen[-1]

    resultaat_persoon = relevante_publicaties[
        auteurs.str.contains(
            achternaam,
            case=False,
            regex=False,
        )
    ].copy()

    # Ook de fallback altijd expliciet sorteren.
    if (
        not resultaat_persoon.empty
        and "similarity" in resultaat_persoon.columns
    ):
        resultaat_persoon["similarity"] = pd.to_numeric(
            resultaat_persoon["similarity"],
            errors="coerce",
        )

        resultaat_persoon = resultaat_persoon.sort_values(
            by="similarity",
            ascending=False,
            na_position="last",
        )

    return resultaat_persoon

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
    "Geef in het Nederlands een korte, concrete uitleg van maximaal 7 zinnen. "
    "Leg uit waarom de gevonden onderzoekers relevant zijn voor de zoekvraag en "
    "verwijs inhoudelijk naar de gevonden publicaties. "
    "Gebruik uitsluitend informatie die expliciet uit bovenstaande gegevens volgt. "
    "Leg geen verbanden tussen onderzoekers die niet expliciet uit de gegevens volgen. "
    "Beweer niet dat onderzoekers tot dezelfde onderzoeksgroep behoren tenzij dit "
    "expliciet in de gegevens staat. "
    "Gebruik woorden zoals 'waarschijnlijk', 'mogelijk' of 'vermoedelijk' niet "
    "om ontbrekende informatie in te vullen. "
    "Zeg niet dat iemand een specialist of expert is als dat niet uit de gegevens blijkt. "
    "Verzin geen feiten, relaties, functies of onderzoeksgebieden."
)

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

def genereer_project_samenvatting(zoekterm, project_resultaat):
    """
    Genereer een korte AI-uitleg over gevonden lopende projecten.
    """

    if project_resultaat.empty:
        return "Er zijn geen lopende projecten gevonden die bij deze zoekvraag passen."

    project_context = []

    for _, project in project_resultaat.head(10).iterrows():
        naam = project.get("naam", "Onbekend project")
        beschrijving = project.get("beschrijving", "")
        leider = project.get("leider_naam", "")
        datum = project.get("datum", "")
        einddatum = project.get("einddatum", "")

        regel = f"Project: {naam}."

        if pd.notna(leider) and str(leider).strip():
            regel += f" Projectleider: {leider}."

        if pd.notna(beschrijving) and str(beschrijving).strip():
            regel += f" Beschrijving: {str(beschrijving).strip()}"

        if pd.notna(datum) and str(datum).strip():
            regel += f" Startdatum: {datum}."

        if pd.notna(einddatum) and str(einddatum).strip():
            regel += f" Einddatum: {einddatum}."

        project_context.append(regel)

    context_tekst = "\n".join(project_context)

    prompt = (
        f"De gebruiker vraagt: '{zoekterm}'.\n\n"
        f"Er zijn {len(project_resultaat)} lopende projecten gevonden.\n\n"
        "Hieronder staan de gevonden projecten:\n"
        f"{context_tekst}\n\n"
        "Geef in het Nederlands een korte en duidelijke uitleg van maximaal "
        "4 zinnen over de gevonden lopende projecten. "
        "Vat de belangrijkste onderwerpen en overeenkomsten samen. "
        "Gebruik alleen informatie uit bovenstaande projectgegevens. "
        "Verzin geen informatie en verwijs niet naar publicaties of PubMed."
    )

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content

def haal_expertise_op(persoon_id):
    """
    Haal alle gekoppelde expertise op voor één onderzoeker.
    """

    exp_ids = personen_expertise[
        personen_expertise["person_id"] == persoon_id
    ]["expertise_id"].tolist()

    exp_details = expertise[
        expertise["id"].isin(exp_ids)
    ].copy()

    exp_details = exp_details.sort_values(
        "label"
    )

    expertise_links = []

    for _, exp in exp_details.iterrows():

        expertise_links.append(
            {
                "id": int(exp["id"]),
                "naam": exp["label"],
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


def verwerk_project_zoekvraag(zoekterm):
    """
    Herkent of een gebruiker specifiek naar lopende projecten zoekt.

    Voorbeelden:
    - "Welke lopende onderzoeken zijn er?"
      -> project_intentie = True
      -> project_zoekterm = ""

    - "Welke lopende onderzoeken zijn er over Alzheimer?"
      -> project_intentie = True
      -> project_zoekterm = "alzheimer"

    - "machine learning"
      -> project_intentie = False
      -> project_zoekterm = "machine learning"
    """

    tekst = str(zoekterm).strip().lower()

def verwerk_project_zoekvraag(zoekterm):
    """
    Herkent of een gebruiker specifiek naar lopende projecten zoekt.

    Voorbeelden:
    - "Welke lopende onderzoeken zijn er?"
      -> project_intentie = True
      -> project_zoekterm = ""

    - "Welke lopende onderzoeken zijn er over Alzheimer?"
      -> project_intentie = True
      -> project_zoekterm = "alzheimer"

    - "machine learning"
      -> project_intentie = False
      -> project_zoekterm = "machine learning"
    """

    tekst = str(zoekterm).strip().lower()

    project_signalen = [
        "lopend onderzoek",
        "lopende onderzoeken",
        "lopende onderzoek",
        "lopend project",
        "lopende projecten",
        "projecten",
        "project",
    ]

    project_intentie = any(
        signaal in tekst
        for signaal in project_signalen
    )

    if not project_intentie:
        return False, tekst

    # Leestekens verwijderen
    schone_tekst = re.sub(
        r"[^\w\s-]",
        " ",
        tekst
    )

    woorden = schone_tekst.split()

    # Algemene vraagwoorden die niet inhoudelijk zijn
    stopwoorden = {
        "welke",
        "wat",
        "wie",
        "waar",
        "zijn",
        "is",
        "er",
        "de",
        "het",
        "een",
        "en",
        "van",
        "voor",
        "met",
        "over",
        "naar",
        "rond",
        "op",
        "binnen",
        "lopende",
        "lopend",
        "onderzoek",
        "onderzoeken",
        "project",
        "projecten",
        "toon",
        "geef",
        "laat",
        "zien",
        "mij",
    }

    inhoudelijke_woorden = [
        woord
        for woord in woorden
        if woord not in stopwoorden
    ]

    project_zoekterm = " ".join(
        inhoudelijke_woorden
    ).strip()

    return True, project_zoekterm    

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
    .str.strip()
)

# Lege afdelingen verwijderen
afdelingen = afdelingen[
    afdelingen != ""
]

# Dubbele waarden verwijderen
afdelingen = sorted(
    afdelingen.unique().tolist()
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
    # Zoeken in lopende projecten
    # --------------------------------------------------------

    project_intentie, project_zoekterm = (
        verwerk_project_zoekvraag(
            zoekterm
        )
    )

    # Normale zoekopdracht:
    # bijvoorbeeld "Alzheimer" of "machine learning"
    if not project_intentie:
        project_zoekterm = zoekterm

    # --------------------------------------------------------
    # Projectvraag zonder onderwerp:
    # "Welke lopende onderzoeken zijn er?"
    # -> alle lopende projecten tonen
    # --------------------------------------------------------

    if project_intentie and not project_zoekterm:

        project_resultaat = pd.read_sql(
            """
            SELECT
                lp.id,
                lp.naam,
                lp.beschrijving,
                lp.leider_id,
                lp.datum,
                lp.einddatum,
                p.name AS leider_naam,
                p.department AS leider_department
            FROM lopende_projecten lp
            LEFT JOIN persons p
                ON p.id = lp.leider_id
            ORDER BY lp.naam
            """,
            conn
        )

    # --------------------------------------------------------
    # Projectvraag met onderwerp:
    # "Welke lopende onderzoeken zijn er over Alzheimer?"
    #
    # Of normale zoekterm:
    # "Alzheimer"
    # --------------------------------------------------------

    else:

        zoekwaarde = f"%{project_zoekterm}%"

        project_resultaat = pd.read_sql(
            """
            SELECT
                lp.id,
                lp.naam,
                lp.beschrijving,
                lp.leider_id,
                lp.datum,
                lp.einddatum,
                p.name AS leider_naam,
                p.department AS leider_department
            FROM lopende_projecten lp
            LEFT JOIN persons p
                ON p.id = lp.leider_id
            WHERE
                LOWER(COALESCE(lp.naam, ''))
                    LIKE LOWER(?)

                OR LOWER(COALESCE(lp.beschrijving, ''))
                    LIKE LOWER(?)

                OR LOWER(COALESCE(p.name, ''))
                    LIKE LOWER(?)

            ORDER BY lp.naam
            """,
            conn,
            params=(
                zoekwaarde,
                zoekwaarde,
                zoekwaarde,
            )
        )

    # --------------------------------------------------------
    # Departmentfilter toepassen
    # --------------------------------------------------------

    if department_filter != "Alle":

        project_resultaat = project_resultaat[
            project_resultaat["leider_department"]
            == department_filter
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
    #
    # Alleen uitvoeren bij een normale zoekopdracht.
    # Bij een projectvraag zoeken we NIET in PubMed.
    # --------------------------------------------------------

    relevante_publicaties = pd.DataFrame()
    semantische_scores = []
    top_pmids = []

    if not project_intentie:

        # Als de zoekterm direct een onderzoeker op naam vindt,
        # voegen we geen extra onderzoekers toe via PubMed.
        naamzoekactie = not naam_resultaat.empty

        if not naamzoekactie:

            semantische_scores = semantisch_zoeken(
                zoekterm
            )

            top_pmids = [
                item["pmid"]
                for item in semantische_scores
            ]

        top_pmids = [
            item["pmid"]
            for item in semantische_scores
        ]

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


         # ========================================================
    # SPECIALE WEERGAVE VOOR PROJECTVRAGEN
    # ========================================================

    if project_intentie:

        st.success(
            f"{len(project_resultaat)} lopend(e) project(en) gevonden"
        )

        project_col, ai_col = st.columns(
            [1.25, 1],
            gap="large",
        )

        # ----------------------------------------------------
        # LINKERKOLOM - PROJECTEN
        # ----------------------------------------------------

        with project_col:

            st.subheader("📁 Gevonden lopende projecten")

            if project_resultaat.empty:

                st.info(
                    "Geen lopende projecten gevonden "
                    "voor deze zoekvraag."
                )

            else:

                for _, project in project_resultaat.iterrows():

                    project_id = int(project["id"])

                    with st.container(border=True):

                        st.markdown(
                            f"### 📁 {project['naam']}"
                        )

                        if (
                            pd.notna(project["leider_naam"])
                            and str(project["leider_naam"]).strip()
                        ):
                            st.caption(
                                f"Projectleider: "
                                f"{project['leider_naam']}"
                            )

                        beschrijving = project["beschrijving"]

                        if (
                            pd.notna(beschrijving)
                            and str(beschrijving).strip()
                        ):
                            beschrijving = str(
                                beschrijving
                            ).strip()

                            if len(beschrijving) > 300:
                                beschrijving = (
                                    beschrijving[:300]
                                    + "..."
                                )

                            st.write(beschrijving)

                        if st.button(
                            "Bekijk project",
                            key=f"project_zoekresultaat_{project_id}",
                            type="primary",
                            use_container_width=True,
                        ):
                            st.session_state[
                                "geselecteerd_lopend_project"
                            ] = project_id

                            st.switch_page(
                                "pages/lopend_project.py"
                            )

        # ----------------------------------------------------
        # RECHTERKOLOM - PROJECT AI
        # ----------------------------------------------------

        with ai_col:

            st.subheader("✨ AI-uitleg")

            if project_resultaat.empty:

                st.info(
                    "Er zijn geen projecten gevonden om "
                    "een samenvatting van te maken."
                )

            else:

                with st.spinner(
                    "Projecten samenvatten ..."
                ):

                    try:

                        project_samenvatting = (
                            genereer_project_samenvatting(
                                zoekterm,
                                project_resultaat,
                            )
                        )

                        st.markdown(
                            f"""
                            <div class="ai-summary">
                                {project_samenvatting}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    except Exception as fout:

                        st.warning(
                            "De AI-samenvatting kon op dit "
                            "moment niet worden gegenereerd."
                        )

                        st.caption(str(fout))

        # Heel belangrijk:
        # de normale onderzoeker-/PubMed-weergave
        # hieronder niet meer uitvoeren.
        st.stop()   

    # --------------------------------------------------------
    # Aantal resultaten
    # --------------------------------------------------------
        st.success(
        f"{len(resultaat)} onderzoeker(s) en "
        f"{len(project_resultaat)} lopend(e) project(en) gevonden"
    )

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
            # --------------------------------------------------------
            # Onderzoekers sorteren op hun beste relevante publicatie
            # --------------------------------------------------------
            resultaat = resultaat.copy()

            beste_scores = []

            for _, persoon in resultaat.iterrows():
                publicaties_persoon = publicaties_van_persoon(
                    relevante_publicaties,
                    persoon["name"],
                )

                if (
                    not publicaties_persoon.empty
                    and "similarity" in publicaties_persoon.columns
                ):
                    beste_score = pd.to_numeric(
                        publicaties_persoon["similarity"],
                        errors="coerce",
                    ).max()
                else:
                    beste_score = -1

                beste_scores.append(beste_score)

            resultaat["beste_similarity"] = beste_scores

            resultaat = resultaat.sort_values(
                by="beste_similarity",
                ascending=False,
                na_position="last",
            )

            # --------------------------------------------------------
            # Onderzoekers tonen
            # --------------------------------------------------------
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
                                        f"{exp['id']}"
                                    ),
                                    use_container_width=True,
                                ):

                                    st.session_state[
                                        "geselecteerde_expertise_id"
                                    ] = exp["id"]

                                    st.switch_page(
                                        "pages/expertise.py"
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

                            # Is dit het profiel van de ingelogde onderzoeker?
                            eigen_person_id = st.session_state.get(
                                "person_id"
                            )

                            if (
                                st.session_state.get("ingelogd", False)
                                and eigen_person_id is not None
                                and int(eigen_person_id) == int(persoon_id)
                            ):
                                # Eigen profiel → Mijn profiel
                                st.switch_page(
                                    "pages/mijn_profiel.py"
                                )

                            else:
                                # Andere onderzoeker / bezoeker → openbaar profiel
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
            # ====================================================
        # LOPENDE PROJECTEN
        # ====================================================

        st.divider()
        st.subheader("📁 Gevonden lopende projecten")

        if project_resultaat.empty:

            st.info(
                "Geen lopende projecten gevonden "
                "voor deze zoekterm."
            )

        else:

            for _, project in project_resultaat.iterrows():

                project_id = int(project["id"])

                with st.container(border=True):

                    st.markdown(
                        f"### 📁 {project['naam']}"
                    )

                    if (
                        pd.notna(project["leider_naam"])
                        and str(project["leider_naam"]).strip()
                    ):
                        st.caption(
                            f"Projectleider: "
                            f"{project['leider_naam']}"
                        )

                    beschrijving = project["beschrijving"]

                    if (
                        pd.notna(beschrijving)
                        and str(beschrijving).strip()
                    ):

                        beschrijving = str(
                            beschrijving
                        ).strip()

                        if len(beschrijving) > 250:
                            beschrijving = (
                                beschrijving[:250]
                                + "..."
                            )

                        st.write(
                            beschrijving
                        )

                    if st.button(
                        "Bekijk project",
                        key=f"zoek_project_{project_id}",
                        type="primary",
                        use_container_width=True,
                    ):

                        st.session_state[
                            "geselecteerd_lopend_project"
                        ] = project_id

                        st.switch_page(
                            "pages/lopend_project.py"
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
