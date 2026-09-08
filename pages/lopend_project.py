import streamlit as st

st.set_page_config(
    page_title="Lopend project - Spider",
    layout="wide"
)

import pandas as pd
import sqlite3
import os

from sidebar import toon_sidebar
from styling import apply_styling


# ============================================================
# DATABASE
# ============================================================

db_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "spider.db"
)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()


# ============================================================
# AUTHENTICATIE
# ============================================================

if (
    "ingelogd" not in st.session_state
    or not st.session_state.ingelogd
):
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()


# ============================================================
# CENTRALE STYLING + SIDEBAR
# ============================================================

apply_styling("projecten")
toon_sidebar()


# ============================================================
# DATA
# ============================================================

personen = pd.read_sql("SELECT * FROM persons", conn)
projecten = pd.read_sql("SELECT * FROM lopende_projecten", conn)
deelnemers = pd.read_sql("SELECT * FROM project_deelnemers", conn)


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">LOPEND PROJECT</div>',
        unsafe_allow_html=True
    )

    if (
        "geselecteerd_lopend_project" not in st.session_state
        or st.session_state.geselecteerd_lopend_project is None
    ):
        st.title("🔬 Lopend project")
        st.warning("Geen project geselecteerd.")

        if st.button(
            "← Terug naar zoeken",
            key="terug_geen_project"
        ):
            st.switch_page("app.py")

    else:
        project_id = int(
            st.session_state.geselecteerd_lopend_project
        )

        project_selectie = projecten[
            projecten["id"] == project_id
        ]

        if project_selectie.empty:
            st.title("🔬 Lopend project")
            st.warning("Dit project kon niet worden gevonden.")

        else:
            project = project_selectie.iloc[0]

            leider_selectie = personen[
                personen["id"] == project["leider_id"]
            ]

            leider_naam = (
                leider_selectie.iloc[0]["name"]
                if not leider_selectie.empty
                else "Onbekend"
            )

            st.title(project["naam"])

            st.caption(
                "Lopend onderzoeksproject binnen Amsterdam UMC"
            )

            st.write(f"**Projectleider:** {leider_naam}")
            st.write(f"**Gestart:** {project['datum']}")

            einddatum = project.get("einddatum")

            if pd.notna(einddatum) and str(einddatum).strip():
                st.write(f"**Einddatum:** {einddatum}")

            st.write(project["beschrijving"])

            st.divider()

            # Ingelogde gebruiker ophalen
            gebruikersnaam = st.session_state.get(
                "gebruikersnaam",
                ""
            )

            cursor.execute(
                "SELECT id FROM persons WHERE name = ?",
                (gebruikersnaam,)
            )

            result = cursor.fetchone()
            eigen_id = result[0] if result else None

            # Deelnemers
            st.subheader("👥 Deelnemers")
            
            deelnemer_ids = deelnemers[
                deelnemers["project_id"] == project_id
            ]["persoon_id"].tolist()

            betrokken = personen[
                personen["id"].isin(deelnemer_ids)
            ]

            aantal_deelnemers = len(betrokken)

            with st.expander(
                f"👥 Deelnemers ({aantal_deelnemers})",
                expanded=False
            ):
                if betrokken.empty:
                    st.write("Nog geen deelnemers gekoppeld.")
                else:
                    for _, persoon in betrokken.iterrows():
                        st.write(f"👤 {persoon['name']}")

            # Documenten
            st.subheader("📎 Documenten")

            documenten = pd.read_sql(
                """
                SELECT *
                FROM project_documenten
                WHERE project_id = ?
                """,
                conn,
                params=(project_id,)
            )

            if documenten.empty:
                st.write("Geen documenten beschikbaar.")
            else:
                for _, doc in documenten.iterrows():
                    st.markdown(
                        f"📄 [{doc['naam']}]({doc['url']})"
                    )

            st.divider()

            # Audio / Video
            st.subheader("🎥 Audio & Video")

            st.markdown("""
📹 [Projectpresentatie — Teams Recording](#)  
🎙️ [Podcast interview onderzoeker](#)  
📺 [Seminar opname Amsterdam UMC](#)
""")

            st.caption(
                "⚠️ Demo: links verwijzen naar externe bronnen "
                "zoals Microsoft Teams of YouTube."
            )

            st.divider()

            # Rol van ingelogde gebruiker
            if eigen_id == project["leider_id"]:
                st.info("✅ Jij bent de projectleider.")

            elif eigen_id in deelnemer_ids:
                st.info(
                    "✅ Je bent aangemeld voor dit project."
                )

                if st.button(
                    "❌ Afmelden",
                    key="afmelden_project"
                ):
                    cursor.execute(
                        """
                        DELETE FROM project_deelnemers
                        WHERE project_id = ?
                        AND persoon_id = ?
                        """,
                        (project_id, eigen_id)
                    )

                    conn.commit()
                    st.success("✅ Je bent afgemeld!")
                    st.rerun()

            if st.button(
                "← Terug naar zoeken",
                key="terug_naar_zoeken"
            ):
                st.switch_page("app.py")
