import streamlit as st
import pandas as pd
import datetime

from database import get_connection

conn = get_connection()


# ============================================================
# BEHEERDER TOEGANG
# ============================================================

if not st.session_state.get("ingelogd", False):
    st.warning("Je moet eerst inloggen.")
    st.switch_page("pages/login.py")
    st.stop()

if st.session_state.get("rol") != "beheerder":
    st.error("Deze pagina is alleen toegankelijk voor beheerders.")
    st.switch_page("app.py")
    st.stop()

# Log functie
def log_wijziging(actie, wat):
    cursor = conn.cursor()
    datum = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")
    door_wie = st.session_state.get("gebruikersnaam", "onbekend")
    cursor.execute(
        "INSERT INTO wijzigingen (datum, actie, wat, door_wie) VALUES (?, ?, ?, ?)",
        (datum, actie, wat, door_wie)
    )
    conn.commit()

# CSS
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.write(f"👤 **{st.session_state.get('gebruikersnaam', '')}**")
st.sidebar.divider()
if st.sidebar.button("📋 Geschiedenis"):
    st.switch_page("pages/geschiedenis.py")
st.sidebar.divider()
if st.sidebar.button("🏠 Home"):
    st.switch_page("app.py")
if st.sidebar.button("🚪 Uitloggen"):
    st.session_state.ingelogd = False
    st.session_state.rol = None
    st.rerun()

# ============================================================
# BEHEER
# ============================================================

st.title("⚙️ Beheer")
st.caption(
    "Beheer onderzoekersaccounts en instellingen van Spider."
)

st.divider()


# ============================================================
# ONDERZOEKERS BEHEREN
# ============================================================

st.subheader("👤 Onderzoekers beheren")

onderzoekers = pd.read_sql(
    """
    SELECT
        p.id,
        p.name,
        p.department,
        g.gebruikersnaam,
        g.rol
    FROM persons p
    LEFT JOIN gebruikers g
        ON g.person_id = p.id
    ORDER BY p.name
    """,
    conn
)


# ============================================================
# ZOEKEN EN FILTEREN
# ============================================================

kolom_zoek, kolom_filter = st.columns([2, 1])

with kolom_zoek:
    zoekterm = st.text_input(
        "Onderzoeker zoeken",
        placeholder="Zoek op naam...",
        key="beheer_onderzoeker_zoeken"
    )

with kolom_filter:
    account_filter = st.selectbox(
        "Filter",
        [
            "Alle onderzoekers",
            "Met account",
            "Zonder account"
        ],
        key="beheer_account_filter"
    )


gefilterde_onderzoekers = onderzoekers.copy()

if zoekterm.strip():
    gefilterde_onderzoekers = gefilterde_onderzoekers[
        gefilterde_onderzoekers["name"]
        .fillna("")
        .str.contains(
            zoekterm.strip(),
            case=False,
            regex=False
        )
    ]

if account_filter == "Met account":
    gefilterde_onderzoekers = gefilterde_onderzoekers[
        gefilterde_onderzoekers["gebruikersnaam"].notna()
    ]

elif account_filter == "Zonder account":
    gefilterde_onderzoekers = gefilterde_onderzoekers[
        gefilterde_onderzoekers["gebruikersnaam"].isna()
    ]


# ============================================================
# ONDERZOEKER SELECTEREN
# ============================================================

if gefilterde_onderzoekers.empty:

    st.info(
        "Geen onderzoekers gevonden met deze zoekopdracht "
        "en dit filter."
    )

else:

    onderzoeker_opties = {
        f"{rij['name']} — ID {rij['id']}": rij["id"]
        for _, rij in gefilterde_onderzoekers.iterrows()
    }

    geselecteerde_optie = st.selectbox(
        "Selecteer onderzoeker",
        list(onderzoeker_opties.keys()),
        key="beheer_onderzoeker_selecteren"
    )

    geselecteerde_id = onderzoeker_opties[
        geselecteerde_optie
    ]

    onderzoeker = onderzoekers[
        onderzoekers["id"] == geselecteerde_id
    ].iloc[0]


    # ========================================================
    # DETAILS
    # ========================================================

    st.divider()
    st.subheader(onderzoeker["name"])

    kolom1, kolom2, kolom3 = st.columns(3)

    with kolom1:
        st.caption("Person ID")
        st.write(onderzoeker["id"])

    with kolom2:
        st.caption("Afdeling")
        st.write(
            onderzoeker["department"]
            if pd.notna(onderzoeker["department"])
            else "Niet ingevuld"
        )

    with kolom3:
        st.caption("Account")
        st.write(
            "Aanwezig"
            if pd.notna(onderzoeker["gebruikersnaam"])
            else "Geen account"
        )

    if pd.notna(onderzoeker["gebruikersnaam"]):
        st.caption("Gebruikersnaam")
        st.write(onderzoeker["gebruikersnaam"])

        st.caption("Rol")
        st.write(
            onderzoeker["rol"]
            if pd.notna(onderzoeker["rol"])
            else "Niet ingesteld"
        )


    # ========================================================
    # GEKOPPELDE GEGEVENS
    # ========================================================

    aantal_aliasen = conn.execute(
        """
        SELECT COUNT(*)
        FROM person_author_aliases
        WHERE person_id = ?
        """,
        (geselecteerde_id,)
    ).fetchone()[0]

    aantal_expertise = conn.execute(
        """
        SELECT COUNT(*)
        FROM persons_expertise
        WHERE person_id = ?
        """,
        (geselecteerde_id,)
    ).fetchone()[0]

    aantal_projecten = conn.execute(
        """
        SELECT COUNT(*)
        FROM persons_projects
        WHERE person_id = ?
        """,
        (geselecteerde_id,)
    ).fetchone()[0]

    st.markdown("#### Gekoppelde gegevens")

    info1, info2, info3 = st.columns(3)

    with info1:
        st.metric(
            "Auteursaliassen",
            aantal_aliasen
        )

    with info2:
        st.metric(
            "Expertisegebieden",
            aantal_expertise
        )

    with info3:
        st.metric(
            "Projecten",
            aantal_projecten
        )


# ========================================================
# ONDERZOEKER VERWIJDEREN
# ========================================================

st.divider()
st.markdown("#### Onderzoeker verwijderen")

st.warning(
    "Hiermee wordt de onderzoeker uit Spider verwijderd. "
    "Gedeelde PubMed-publicaties blijven behouden."
)

bevestigd = st.checkbox(
    f"Ik begrijp dat '{onderzoeker['name']}' definitief "
    "uit Spider wordt verwijderd.",
    key=f"verwijder_bevestiging_{geselecteerde_id}"
)

if st.button(
    "🗑️ Onderzoeker definitief verwijderen",
    type="primary",
    disabled=not bevestigd,
    key=f"verwijder_onderzoeker_{geselecteerde_id}"
):

    try:
        cursor = conn.cursor()

        # Account verwijderen
        cursor.execute(
            """
            DELETE FROM gebruikers
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Profielgegevens verwijderen
        cursor.execute(
            """
            DELETE FROM profiel_data
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Auteursaliassen verwijderen
        cursor.execute(
            """
            DELETE FROM person_author_aliases
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Expertise-koppelingen verwijderen
        cursor.execute(
            """
            DELETE FROM persons_expertise
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Projectkoppelingen verwijderen
        cursor.execute(
            """
            DELETE FROM persons_projects
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Onderzoekerbestanden verwijderen uit database
        cursor.execute(
            """
            DELETE FROM onderzoeker_bestanden
            WHERE person_id = ?
            """,
            (geselecteerde_id,)
        )

        # Naam bewaren voor de geschiedenis
        verwijderde_naam = onderzoeker["name"]

        # Onderzoeker zelf als laatste verwijderen
        cursor.execute(
            """
            DELETE FROM persons
            WHERE id = ?
            """,
            (geselecteerde_id,)
        )

        # Wijziging registreren
        cursor.execute(
            """
            INSERT INTO wijzigingen (
                datum,
                actie,
                wat,
                door_wie
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                datetime.datetime.now().strftime("%d-%m-%Y %H:%M"),
                "Onderzoeker verwijderd",
                verwijderde_naam,
                st.session_state.get("gebruikersnaam", "Onbekend")
            )
        )

        conn.commit()

        st.success(
            f"{onderzoeker['name']} is verwijderd uit Spider. "
            "PubMed-publicaties zijn behouden."
        )

        st.rerun()

    except Exception as fout:

        conn.rollback()

        st.error(
            f"Verwijderen is mislukt. "
            f"Er is niets definitief gewijzigd: {fout}"
        )
# ============================================================
# KENNISGRAAF
# ============================================================

st.divider()
st.subheader("🕸️ Kennisgraaf")

st.caption(
    "De categorieën van de kennisgraaf worden centraal door Spider "
    "beheerd. Afgeleide categorieën worden automatisch opgebouwd "
    "uit onderzoeksdata en kunnen hier niet handmatig worden "
    "toegevoegd, hernoemd of verwijderd."
)


# ============================================================
# AANTALLEN OPHALEN
# ============================================================

aantal_onderzoekers = conn.execute(
    """
    SELECT COUNT(*)
    FROM persons
    """
).fetchone()[0]

aantal_expertise = conn.execute(
    """
    SELECT COUNT(*)
    FROM expertise
    """
).fetchone()[0]

aantal_projecten = conn.execute(
    """
    SELECT COUNT(*)
    FROM lopende_projecten
    """
).fetchone()[0]

aantal_publicaties = conn.execute(
    """
    SELECT COUNT(*)
    FROM publications
    """
).fetchone()[0]

aantal_methoden = conn.execute(
    """
    SELECT COUNT(DISTINCT waarde)
    FROM publicatie_verrijkingen
    WHERE categorie = ?
    """,
    ("Onderzoeksmethode",)
).fetchone()[0]

aantal_methode_koppelingen = conn.execute(
    """
    SELECT COUNT(*)
    FROM publicatie_verrijkingen
    WHERE categorie = ?
    """,
    ("Onderzoeksmethode",)
).fetchone()[0]


# ============================================================
# VASTE BASISCATEGORIEËN
# ============================================================

st.markdown("#### Vaste basiscategorieën")

st.caption(
    "Deze categorieën vormen de basis van de kennisgraaf."
)

basis1, basis2, basis3, basis4 = st.columns(4)

with basis1:
    st.metric(
        "👤 Onderzoekers",
        aantal_onderzoekers
    )

with basis2:
    st.metric(
        "🔬 Expertise",
        aantal_expertise
    )

with basis3:
    st.metric(
        "🧪 Lopende projecten",
        aantal_projecten
    )

with basis4:
    st.metric(
        "📚 Publicaties",
        aantal_publicaties
    )


# ============================================================
# AUTOMATISCH AFGELEIDE CATEGORIEËN
# ============================================================

st.markdown("#### Automatisch afgeleide categorieën")

st.caption(
    "Deze categorieën worden uit publicatiegegevens afgeleid. "
    "De bron van iedere koppeling wordt opgeslagen zodat "
    "de classificatie herleidbaar blijft."
)

with st.container(border=True):

    methode1, methode2, methode3 = st.columns([2, 1, 1])

    with methode1:
        st.markdown("##### 🟡 Onderzoeksmethoden")
        st.write(
            "Automatisch herkend op basis van titel, "
            "keywords en MeSH-termen van publicaties."
        )

    with methode2:
        st.metric(
            "Unieke methoden",
            aantal_methoden
        )

    with methode3:
        st.metric(
            "Koppelingen",
            aantal_methode_koppelingen
        )


# ============================================================
# TOEKOMSTIGE UITBREIDINGEN
# ============================================================

st.markdown("#### Mogelijke uitbreidingen")

st.caption(
    "Dezelfde verrijkingsstructuur kan later worden gebruikt "
    "voor aanvullende dimensies."
)

st.info(
    "Onderwerpen • Ziekten/aandoeningen • Populaties • Technologieën"
)