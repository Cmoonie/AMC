import streamlit as st

st.set_page_config(
    page_title="Amyloid Beta - Spider",
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

apply_styling("expertise")
toon_sidebar()


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">EXPERTISE</div>',
        unsafe_allow_html=True
    )

    st.title("🧬 Amyloid Beta")

    st.caption(
        "Wetenschappelijke expertise binnen Amsterdam UMC"
    )

    st.divider()

    st.subheader("📖 Wat is amyloid beta?")
    st.write("""
Amyloid beta is een eiwit dat van nature voorkomt in de hersenen. Bij sommige
mensen hoopt dit eiwit zich op en vormt het klonters — amyloid plaques — die
zenuwcellen beschadigen. Deze plaques zijn een van de belangrijkste kenmerken
van de ziekte van Alzheimer.
""")

    st.divider()

    st.subheader("🧬 Hoe werkt het in het lichaam?")
    st.write("""
Amyloid beta wordt geproduceerd door de afbraak van het amyloid precursor eiwit (APP).
Normaal gesproken wordt amyloid beta afgebroken en verwijderd. Bij Alzheimer raakt
dit systeem verstoord, waardoor amyloid beta zich ophoopt en plaques vormt tussen
zenuwcellen. Dit leidt tot ontsteking en uiteindelijk het afsterven van neuronen.
""")

    st.divider()

    st.subheader("🎯 Wat doet het?")
    st.write("""
Amyloid beta speelt een centrale rol bij de ontwikkeling van Alzheimer. Het meten
van amyloid beta in bloed of hersenvloeistof wordt gebruikt als vroege biomarker
voor Alzheimer — jaren voordat symptomen optreden. Nieuwe behandelingen richten
zich op het verwijderen van amyloid plaques om de ziekte te vertragen.
""")

    st.divider()

    st.subheader("🧠 Onderzoek binnen Amsterdam UMC")

    st.markdown("**👤 Sjors In 't Veld**")
    st.write("""
Dr. Sjors In 't Veld onderzoekt amyloid beta als biomarker voor neurodegeneratieve
ziekten. Zijn werk richt zich op de diagnostische waarde van plasma amyloid beta
metingen voor vroege opsporing van Alzheimer en andere amyloid-gerelateerde
aandoeningen, waaronder hereditaire transthyretine amyloidose.
""")

    st.markdown("**👤 Martijn C Schut**")
    st.write("""
Prof. Martijn C Schut onderzoekt de rol van amyloid biomarkers in het kader
van AI-gestuurde diagnostiek. Hij werkt aan voorspellende modellen voor vroege
detectie van amyloid-gerelateerde aandoeningen zoals Alzheimer, met behulp van
bloedtesten en machine learning.
""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """
        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%amyloid%'
        OR LOWER(keywords) LIKE '%amyloid%'
        LIMIT 5
        """,
        conn
    )

    if publicaties.empty:
        st.info("Geen publicaties gevonden.")
    else:
        for _, pub in publicaties.iterrows():
            titel = pub["title"]

            if len(titel) > 100:
                titel = titel[:100] + "..."

            jaar = pub["year"]

            if pub["pubmed_url"]:
                st.markdown(
                    f"📄 **[{titel}]({pub['pubmed_url']})**  \n"
                    f"*{jaar}*"
                )
            else:
                st.markdown(
                    f"📄 **{titel}**  \n"
                    f"*{jaar}*"
                )

    st.divider()

    if st.button(
        "← Terug naar zoeken",
        key="terug_naar_zoeken"
    ):
        st.switch_page("app.py")
