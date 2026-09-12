import streamlit as st

st.set_page_config(
    page_title="Lopende projecten - Spider",
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
    os.path.dirname(__file__),
    "..",
    "spider.db"
)

conn = sqlite3.connect(db_path)


# ============================================================
# AUTHENTICATIE
# ============================================================

# if (
#     "ingelogd" not in st.session_state
#     or not st.session_state.ingelogd
# ):
#     st.warning("Je moet eerst inloggen!")
#     st.switch_page("app.py")
#     st.stop()


# ============================================================
# CENTRALE STYLING + SIDEBAR
# ============================================================

apply_styling("projecten")
toon_sidebar()


# ============================================================
# DATA
# ============================================================

persoon_id = st.session_state.get(
    "lopende_projecten_persoon"
)

personen = pd.read_sql(
    "SELECT * FROM persons",
    conn
)

if persoon_id:
    projecten = pd.read_sql(
        """
        SELECT *
        FROM lopende_projecten
        WHERE leider_id = ?
        """,
        conn,
        params=(persoon_id,)
    )
else:
    projecten = pd.read_sql(
        "SELECT * FROM lopende_projecten",
        conn
    )


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">LOPENDE PROJECTEN</div>',
        unsafe_allow_html=True
    )

    if persoon_id:
        persoon = personen[
            personen["id"] == persoon_id
        ]

        if not persoon.empty:
            naam = persoon.iloc[0]["name"]
            st.title(
                f"🔬 Lopende projecten — {naam}"
            )
        else:
            st.title("🔬 Lopende projecten")
    else:
        st.title("🔬 Lopende projecten")

    st.caption(
        "Bekijk lopende onderzoeksprojecten binnen Amsterdam UMC."
    )

    st.divider()

    if projecten.empty:
        st.info("Geen lopende projecten gevonden.")

    else:
        for _, project in projecten.iterrows():

            with st.container(border=True):

                col1, col2 = st.columns(
                    [5, 1],
                    vertical_alignment="center"
                )

                with col1:
                    st.markdown(
                        f"### 🟢 {project['naam']}"
                    )

                    beschrijving = (
                        str(project["beschrijving"])
                        if pd.notna(project["beschrijving"])
                        else ""
                    )

                    if len(beschrijving) > 180:
                        beschrijving = (
                            beschrijving[:180] + "..."
                        )

                    st.write(beschrijving)

                    datum = project.get("datum")

                    if pd.notna(datum):
                        st.write(
                            f"📅 **Start:** {datum}"
                        )

                    einddatum = project.get("einddatum")

                    if (
                        pd.notna(einddatum)
                        and str(einddatum).strip()
                    ):
                        st.write(
                            f"📅 **Einde:** {einddatum}"
                        )

                with col2:
                    if st.button(
                        "Bekijk",
                        key=f"overzicht_{project['id']}",
                        type="primary",
                        use_container_width=True
                    ):
                        st.session_state[
                            "geselecteerd_lopend_project"
                        ] = int(project["id"])

                        st.switch_page(
                            "pages/lopend_project.py"
                        )

    st.divider()

    if st.button(
        "← Terug",
        key="terug_naar_zoeken"
    ):
        st.switch_page("app.py")
