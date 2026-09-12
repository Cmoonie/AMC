import streamlit as st

st.set_page_config(
    page_title='Clinical Decision Making - Spider',
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
#Algemene styling
apply_styling("expertise")

#Centrale sidebar
toon_sidebar()


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">EXPERTISE</div>',
        unsafe_allow_html=True
    )

    st.title('🤖 Clinical Decision Making')

    st.caption('Wetenschappelijke expertise binnen Amsterdam UMC')

    st.divider()

    st.subheader('📖 Wat is clinical decision making?')
    st.write("""Klinische beslissingsondersteuning (Clinical Decision Making) is het proces waarbij
artsen en zorgprofessionals gebruik maken van data, richtlijnen en AI-systemen om
betere medische beslissingen te nemen. Het combineert klinische expertise met
data-gedreven inzichten voor optimale patiëntenzorg.""")

    st.divider()

    st.subheader('🧠 Hoe werkt het?')
    st.write("""Moderne klinische beslissingsondersteuning maakt gebruik van machine learning modellen
die zijn getraind op grote datasets van patiëntgegevens. Deze modellen kunnen
voorspellingen doen over ziekterisico's, optimale behandelingen en mogelijke
complicaties. Ze fungeren als een digitale assistent voor de arts — niet als
vervanging, maar als aanvulling.""")

    st.divider()

    st.subheader('🎯 Wat doet het?')
    st.write("""Clinical decision making systemen helpen bij vroege diagnose, behandelkeuze en
monitoring van patiënten. Ze kunnen patronen herkennen in grote hoeveelheden data
die voor een mens moeilijk te overzien zijn. Dit leidt tot snellere diagnoses,
minder fouten en betere uitkomsten voor patiënten.""")

    st.divider()

    st.subheader('🤖 Onderzoek binnen Amsterdam UMC')
    st.write("""**👤 Martijn C Schut**

Prof. Martijn C Schut ontwikkelt AI-gedreven modellen voor klinische
beslissingsondersteuning in laboratoriumgeneeskunde. Zijn onderzoek richt zich
op het bouwen van voorspellende algoritmen voor vroege ziektedetectie en
gepersonaliseerde behandeling in oncologie, cardiologie en pediatrie. Hij legt
bijzondere nadruk op mensgerichte AI die zorgprofessionals ondersteunt in plaats
van vervangt.""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%clinical decision%'
        OR LOWER(keywords) LIKE '%clinical decision%'
        OR LOWER(abstract) LIKE '%decision support%'
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
