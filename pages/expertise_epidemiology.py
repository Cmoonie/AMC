import streamlit as st

st.set_page_config(
    page_title='Epidemiologie - Spider',
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

    st.title('📊 Epidemiologie')

    st.caption('Wetenschappelijke expertise binnen Amsterdam UMC')

    st.divider()

    st.subheader('📖 Wat is epidemiologie?')
    st.write("""Epidemiologie is de wetenschap die bestudeert hoe ziekten zich verspreiden in
bevolkingsgroepen en welke factoren bijdragen aan het ontstaan van ziekten.
Het is de basis van de volksgezondheid en helpt bij het ontwikkelen van
preventiestrategieën en richtlijnen.""")

    st.divider()

    st.subheader('🔎 Hoe werkt het?')
    st.write("""Epidemiologen verzamelen en analyseren gegevens over grote groepen mensen over
langere perioden. Ze zoeken naar verbanden tussen risicofactoren en ziekten,
en evalueren de effectiviteit van interventies. Moderne epidemiologie maakt
steeds meer gebruik van big data en AI om complexe patronen te ontdekken.""")

    st.divider()

    st.subheader('🎯 Wat doet het?')
    st.write("""Epidemiologisch onderzoek levert de wetenschappelijke basis voor medische
richtlijnen, vaccinatieprogramma's en volksgezondheidsbeleid. Het beantwoordt
vragen als: Wie loopt risico? Waarom worden mensen ziek? Welke behandelingen
werken het best voor welke groepen?""")

    st.divider()

    st.subheader('📊 Onderzoek binnen Amsterdam UMC')
    st.write("""**👤 Martijn C Schut**

Prof. Martijn C Schut past epidemiologische methoden toe in zijn onderzoek naar
AI in de gezondheidszorg. Hij onderzoekt hoe AI-modellen presteren in diverse
patiëntenpopulaties en hoe epidemiologische principes kunnen helpen bij het
eerlijk en effectief implementeren van AI-systemen in de klinische praktijk.""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%epidemiology%'
        OR LOWER(keywords) LIKE '%epidemiology%'
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
