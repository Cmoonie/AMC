import streamlit as st

st.set_page_config(
    page_title='Laboratorium Diagnostiek - Spider',
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

    st.title('🔬 Laboratorium Diagnostiek')

    st.caption('Wetenschappelijke expertise binnen Amsterdam UMC')

    st.divider()

    st.subheader('📖 Wat is laboratorium diagnostiek?')
    st.write("""Laboratorium diagnostiek is het vakgebied dat zich bezighoudt met het analyseren
van lichaamsmateriaal zoals bloed, urine en weefsel om ziekten te detecteren,
monitoren en behandelen. Het is de basis van moderne geneeskunde — meer dan 70%
van alle medische beslissingen is gebaseerd op laboratoriumuitslagen.""")

    st.divider()

    st.subheader('🧪 Hoe werkt het?')
    st.write("""Laboratoriumtests meten specifieke stoffen in het lichaam zoals eiwitten, enzymen,
hormonen en genetisch materiaal. De resultaten worden vergeleken met referentiewaarden
om te bepalen of iets normaal of afwijkend is. Moderne laboratoria gebruiken
geautomatiseerde systemen en AI om grote hoeveelheden tests snel en nauwkeurig
te verwerken.""")

    st.divider()

    st.subheader('🎯 Wat doet het?')
    st.write("""Laboratorium diagnostiek speelt een cruciale rol bij vroege opsporing van ziekten,
monitoring van behandelingen en het bepalen van de juiste dosering van medicijnen.
Zonder laboratoriumdiagnostiek zouden artsen veel vaker in het duister tasten bij
het stellen van diagnoses.""")

    st.divider()

    st.subheader('🔬 Onderzoek binnen Amsterdam UMC')
    st.write("""**👤 Robert de Jonge**

Prof. dr. Robert de Jonge is hoogleraar Laboratoriumgeneeskunde bij Amsterdam UMC.
Hij werkt aan de ontwikkeling en validatie van nieuwe diagnostische methoden,
waaronder geautomatiseerde mass spectrometrie systemen voor het meten van serum
analyten. Zijn onderzoek richt zich op het verbeteren van de nauwkeurigheid en
efficiëntie van laboratoriumtests in de klinische praktijk.""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%laboratory%'
        OR LOWER(abstract) LIKE '%diagnostics%'
        OR LOWER(keywords) LIKE '%laboratory%'
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
