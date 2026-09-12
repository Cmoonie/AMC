import streamlit as st

st.set_page_config(
    page_title='Neurofilament Light Chain - Spider',
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

    st.title('🧠 Neurofilament Light Chain')

    st.caption('Wetenschappelijke expertise binnen Amsterdam UMC')

    st.divider()

    st.subheader('📖 Wat is neurofilament light chain?')
    st.write("""Neurofilament light chain (NfL) is een eiwit dat voorkomt in zenuwcellen.
Als zenuwcellen beschadigd raken of afsterven, komt NfL vrij in het bloed en
de hersenvloeistof. Het meten van NfL in bloed is daardoor een waardevolle
biomarker voor het detecteren van schade aan het zenuwstelsel.""")

    st.divider()

    st.subheader('🧠 Hoe werkt het in het lichaam?')
    st.write("""Neurofilamenten zijn eiwitten die het interne skelet van zenuwcellen vormen.
Ze zorgen voor de structuur en stevigheid van neuronen. Bij neurodegeneratieve
ziekten zoals Alzheimer, Parkinson en ALS worden zenuwcellen beschadigd,
waardoor NfL vrijkomt in de bloedbaan. Hoe hoger het NfL-niveau, hoe meer
zenuwschade er aanwezig is.""")

    st.divider()

    st.subheader('🎯 Wat doet het?')
    st.write("""NfL wordt gebruikt als biomarker voor het monitoren van neurodegeneratieve ziekten.
Het kan helpen bij vroege diagnose, het volgen van ziekteprogressie en het beoordelen
van de effectiviteit van behandelingen. Een bloedtest voor NfL is minimaal invasief
en veel toegankelijker dan hersenvloeistof analyse.""")

    st.divider()

    st.subheader('🧠 Onderzoek binnen Amsterdam UMC')
    st.write("""**👤 Sjors In 't Veld**

Dr. Sjors In 't Veld onderzoekt de diagnostische waarde van plasma neurofilament
light chain als biomarker voor neurodegeneratieve aandoeningen, waaronder Alzheimer,
Lewy body ziekten en hereditaire transthyretine amyloidose. Zijn onderzoek richt
zich op het valideren van NfL als betrouwbare bloedtest voor vroege detectie van
neurologische schade.""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%neurofilament%'
        OR LOWER(keywords) LIKE '%neurofilament%'
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
