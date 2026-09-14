import os
import sqlite3

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

from sidebar import toon_sidebar
from styling import apply_styling


# ============================================================
# PAGINA
# ============================================================

st.set_page_config(
    page_title="Expertise - Spider",
    layout="wide"
)

apply_styling("expertise")
toon_sidebar()


# ============================================================
# DATABASE
# ============================================================

db_path = os.path.join(
    os.path.dirname(__file__),
    "..",
    "spider.db"
)

conn = sqlite3.connect(db_path)


# ============================================================
# GESELECTEERDE EXPERTISE
# ============================================================

# Nieuwe session-state naam vanuit de kennisgraaf
expertise_id = st.session_state.get(
    "geselecteerde_expertise_id"
)

# Tijdelijk ook de oude naam ondersteunen
if expertise_id is None:
    expertise_id = st.session_state.get(
        "geselecteerde_expertise"
    )


if expertise_id is None:

    st.warning(
        "Geen expertise geselecteerd."
    )

    if st.button(
        "← Terug naar zoeken"
    ):
        conn.close()
        st.switch_page("app.py")

    conn.close()
    st.stop()


# ============================================================
# EXPERTISE OPHALEN
# ============================================================

expertise = pd.read_sql_query(
    """
    SELECT *
    FROM expertise
    WHERE id = ?
    """,
    conn,
    params=(expertise_id,)
)


if expertise.empty:

    st.error(
        "Deze expertise kon niet worden gevonden."
    )

    conn.close()
    st.stop()


exp = expertise.iloc[0]

expertise_label = str(
    exp["label"]
)


# ============================================================
# TITEL
# ============================================================

st.title(
    f"🔬 {expertise_label}"
)

st.caption(
    "Expertisegebied binnen Spider"
)


# ============================================================
# BESCHRIJVING VIA AI
# ============================================================

load_dotenv()

api_key = os.getenv(
    "GROQ_API_KEY"
)

cache_key = (
    f"expertise_uitleg_{expertise_id}"
)


if cache_key not in st.session_state:

    if api_key:

        try:

            client = Groq(
                api_key=api_key
            )

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
    {
        "role": "user",
        "content": (
            f"Schrijf een informatieve kennispagina over het "
            f"expertisegebied '{expertise_label}'. "
            f"De tekst is bedoeld voor onderzoekers en studenten "
            f"binnen een universitair medisch centrum. "
            f"De lezer moet voldoende inhoudelijke informatie krijgen "
            f"zonder eerst naar Google of een andere informatiebron "
            f"te hoeven gaan. "
            f"\n\n"
            f"Gebruik ongeveer 900 tot 1200 woorden en schrijf in "
            f"duidelijk, professioneel Nederlands. "
            f"Gebruik de volgende structuur met Markdown-koppen:\n\n"
            f"## Over dit expertisegebied\n"
            f"Leg uit wat het expertisegebied inhoudt en bespreek "
            f"de belangrijkste begrippen en principes.\n\n"
            f"## Toepassing binnen medisch onderzoek\n"
            f"Leg uit hoe dit onderwerp binnen medisch en "
            f"wetenschappelijk onderzoek wordt toegepast. Geef waar "
            f"mogelijk concrete voorbeelden van toepassingen.\n\n"
            f"## Belangrijke onderwerpen\n"
            f"Beschrijf belangrijke deelonderwerpen, technieken, "
            f"methoden of begrippen binnen het expertisegebied.\n\n"
            f"## Onderzoek en ontwikkelingen\n"
            f"Beschrijf belangrijke actuele onderzoeksvragen, "
            f"ontwikkelingen en uitdagingen binnen het vakgebied.\n\n"
            f"Maak geen bronnen of feiten op waar je niet zeker van bent. "
            f"Schrijf informatief en neutraal en vermijd een "
            f"reclameachtige schrijfstijl."
        )
    }
]
            )

            st.session_state[
                cache_key
            ] = response.choices[0].message.content

        except Exception:

            st.session_state[
                cache_key
            ] = (
                "Er kon op dit moment geen "
                "automatische beschrijving worden gemaakt."
            )

    else:

        st.session_state[
            cache_key
        ] = (
            "Voor deze expertise is momenteel "
            "geen beschrijving beschikbaar."
        )


st.markdown(
    st.session_state[
        cache_key
    ]
)


# ============================================================
# ONDERZOEKERS
# ============================================================

st.divider()

st.subheader(
    "👥 Onderzoekers met deze expertise"
)


betrokken_onderzoekers = pd.read_sql_query(
    """
    SELECT DISTINCT
        p.id,
        p.name,
        p.department

    FROM persons p

    INNER JOIN persons_expertise pe
        ON pe.person_id = p.id

    WHERE pe.expertise_id = ?

    ORDER BY p.name
    """,
    conn,
    params=(expertise_id,)
)


if betrokken_onderzoekers.empty:

    st.info(
        "Er zijn nog geen onderzoekers "
        "aan deze expertise gekoppeld."
    )

else:

    st.caption(
        f"{len(betrokken_onderzoekers)} "
        "onderzoeker(s) gevonden"
    )

    for _, persoon in betrokken_onderzoekers.iterrows():

        with st.container(
            border=True
        ):

            kolom_info, kolom_knop = st.columns(
                [4, 1]
            )

            with kolom_info:

                st.markdown(
                    f"### 👤 {persoon['name']}"
                )

                afdeling = persoon.get(
                    "department"
                )

                if (
                    pd.notna(afdeling)
                    and str(afdeling).strip()
                ):
                    st.caption(
                        str(afdeling)
                    )

            with kolom_knop:

                if st.button(
                    "Bekijk onderzoeker",
                    key=(
                        f"exp_persoon_"
                        f"{persoon['id']}"
                    ),
                    use_container_width=True
                ):

                    st.session_state[
                        "geselecteerde_persoon"
                    ] = int(
                        persoon["id"]
                    )

                    conn.close()

                    st.switch_page(
                        "pages/onderzoeker.py"
                    )


# ============================================================
# PUBLICATIES
# ============================================================

st.divider()

st.subheader(
    "📚 Relevante publicaties"
)


zoekterm = f"%{expertise_label}%"


publicaties = pd.read_sql_query(
    """
    SELECT
        pmid,
        title,
        year,
        journal,
        authors,
        pubmed_url

    FROM publications

    WHERE
        LOWER(COALESCE(keywords, ''))
            LIKE LOWER(?)

        OR LOWER(COALESCE(mesh_terms, ''))
            LIKE LOWER(?)

        OR LOWER(COALESCE(abstract, ''))
            LIKE LOWER(?)

        OR LOWER(COALESCE(title, ''))
            LIKE LOWER(?)

    ORDER BY
        CASE
            WHEN year GLOB '[0-9][0-9][0-9][0-9]'
            THEN CAST(year AS INTEGER)
            ELSE 0
        END DESC

    LIMIT 20
    """,
    conn,
    params=(
        zoekterm,
        zoekterm,
        zoekterm,
        zoekterm
    )
)


if publicaties.empty:

    st.info(
        "Er zijn nog geen relevante "
        "publicaties gevonden."
    )

else:

    st.caption(
        f"{len(publicaties)} relevante "
        "publicatie(s) gevonden"
    )

    for _, publicatie in publicaties.iterrows():

        with st.container(
            border=True
        ):

            titel = str(
                publicatie["title"]
            )

            st.markdown(
                f"### 📄 {titel}"
            )

            details = []

            if (
                pd.notna(publicatie["year"])
                and str(
                    publicatie["year"]
                ).strip()
            ):
                details.append(
                    str(
                        publicatie["year"]
                    )
                )

            if (
                pd.notna(publicatie["journal"])
                and str(
                    publicatie["journal"]
                ).strip()
            ):
                details.append(
                    str(
                        publicatie["journal"]
                    )
                )

            if details:

                st.caption(
                    " • ".join(details)
                )

            if (
                pd.notna(publicatie["authors"])
                and str(
                    publicatie["authors"]
                ).strip()
            ):

                auteurs = str(
                    publicatie["authors"]
                )

                if len(auteurs) > 220:
                    auteurs = (
                        auteurs[:220]
                        + "..."
                    )

                st.write(
                    f"**Auteurs:** {auteurs}"
                )

            pubmed_url = publicatie[
                "pubmed_url"
            ]

            if (
                pd.notna(pubmed_url)
                and str(pubmed_url).strip()
            ):

                st.link_button(
                    "📚 Bekijk op PubMed",
                    str(pubmed_url)
                )

            elif (
                pd.notna(
                    publicatie["pmid"]
                )
            ):

                st.link_button(
                    "📚 Bekijk op PubMed",
                    (
                        "https://pubmed.ncbi.nlm.nih.gov/"
                        f"{publicatie['pmid']}/"
                    )
                )


# ============================================================
# TERUG
# ============================================================

st.divider()

if st.button(
    "← Terug naar zoeken"
):

    conn.close()

    st.switch_page(
        "app.py"
    )


conn.close()