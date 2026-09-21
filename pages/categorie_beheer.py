import datetime

import pandas as pd
import streamlit as st

from database import get_connection
from sidebar import toon_sidebar


# ============================================================
# BASIS
# ============================================================

st.set_page_config(
    page_title="Kennisgraafcategorieën",
    page_icon="🗂️",
    layout="wide"
)

toon_sidebar()

conn = get_connection()


# ============================================================
# TOEGANG CONTROLEREN
# ============================================================

if not st.session_state.get("ingelogd", False):
    st.warning("Je moet eerst inloggen.")
    st.switch_page("pages/login.py")
    st.stop()

person_id = st.session_state.get("person_id")
rol = st.session_state.get("rol")

heeft_recht = False

if person_id is not None:
    recht = conn.execute(
        """
        SELECT 1
        FROM gebruikers_rechten
        WHERE person_id = ?
          AND recht = ?
        LIMIT 1
        """,
        (
            person_id,
            "kennisgraaf_categorieen"
        )
    ).fetchone()

    heeft_recht = recht is not None


if rol != "beheerder" and not heeft_recht:
    st.error(
        "Je hebt geen toegang tot het beheer van "
        "kennisgraafcategorieën."
    )
    st.switch_page("app.py")
    st.stop()


# ============================================================
# PAGINA
# ============================================================

st.title("🗂️ Kennisgraafcategorieën")

st.caption(
    "Voeg aanvullende categorieën en items toe voor "
    "toekomstige uitbreidingen van de kennisgraaf."
)


# ============================================================
# CATEGORIE TOEVOEGEN
# ============================================================

with st.expander("➕ Nieuwe categorie toevoegen", expanded=True):

    categorie_naam = st.text_input(
        "Naam categorie",
        placeholder="Bijvoorbeeld: Landen",
        key="categorie_gebruiker_naam"
    )

    beschrijving = st.text_area(
        "Beschrijving",
        placeholder="Waarvoor wordt deze categorie gebruikt?",
        key="categorie_gebruiker_beschrijving"
    )

    items_tekst = st.text_area(
        "Onderwerpen / items",
        placeholder=(
            "Voer één item per regel in.\n"
            "Bijvoorbeeld:\n"
            "Nederland\n"
            "België\n"
            "Duitsland"
        ),
        key="categorie_gebruiker_items"
    )

    if st.button(
        "Categorie opslaan",
        type="primary",
        key="categorie_gebruiker_opslaan"
    ):

        naam = categorie_naam.strip()

        items = [
            item.strip()
            for item in items_tekst.splitlines()
            if item.strip()
        ]

        items = list(dict.fromkeys(items))

        if not naam:
            st.warning("Vul eerst een categorienaam in.")

        elif not items:
            st.warning("Voeg minimaal één item toe.")

        else:
            try:
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO kennisgraaf_categorieen (
                        naam,
                        beschrijving
                    )
                    VALUES (?, ?)
                    """,
                    (
                        naam,
                        beschrijving.strip()
                    )
                )

                categorie_id = cursor.lastrowid

                for item in items:
                    cursor.execute(
                        """
                        INSERT INTO kennisgraaf_items (
                            categorie_id,
                            naam
                        )
                        VALUES (?, ?)
                        """,
                        (
                            categorie_id,
                            item
                        )
                    )

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
                        datetime.datetime.now().strftime(
                            "%d-%m-%Y %H:%M"
                        ),
                        "Kennisgraafcategorie toegevoegd",
                        naam,
                        st.session_state.get(
                            "gebruikersnaam",
                            "Onbekend"
                        )
                    )
                )

                conn.commit()

                st.success(
                    f"Categorie '{naam}' is toegevoegd "
                    f"met {len(items)} item(s)."
                )

            except Exception as fout:
                conn.rollback()

                if "UNIQUE constraint failed" in str(fout):
                    st.error(
                        "Er bestaat al een categorie met deze naam."
                    )
                else:
                    st.error(
                        f"Opslaan is mislukt: {fout}"
                    )


# ============================================================
# BESTAANDE CATEGORIEËN
# ============================================================

# st.divider()
# st.subheader("Bestaande categorieën")

# categorieen = pd.read_sql(
#     """
#     SELECT
#         c.id,
#         c.naam,
#         c.beschrijving,
#         COUNT(i.id) AS aantal_items
#     FROM kennisgraaf_categorieen c
#     LEFT JOIN kennisgraaf_items i
#         ON i.categorie_id = c.id
#     GROUP BY
#         c.id,
#         c.naam,
#         c.beschrijving
#     ORDER BY c.naam
#     """,
#     conn
# )

# if categorieen.empty:
#     st.info("Er zijn nog geen categorieën.")

# else:
#     for _, categorie in categorieen.iterrows():

#         with st.expander(
#             f"{categorie['naam']} "
#             f"({categorie['aantal_items']} items)"
#         ):

#             if categorie["beschrijving"]:
#                 st.write(categorie["beschrijving"])

#             items = pd.read_sql(
#                 """
#                 SELECT naam
#                 FROM kennisgraaf_items
#                 WHERE categorie_id = ?
#                 ORDER BY naam
#                 """,
#                 conn,
#                 params=(categorie["id"],)
#             )

#             if items.empty:
#                 st.caption("Geen items.")
#             else:
#                 for item in items["naam"]:
#                     st.write(f"• {item}")