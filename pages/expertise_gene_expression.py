import streamlit as st

st.set_page_config(
    page_title='Gene Expression - Spider',
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

    st.title('🧬 Gene Expression')

    st.caption('Wetenschappelijke expertise binnen Amsterdam UMC')

    st.divider()

    st.subheader('📖 Wat is gene expression?')
    st.write("""Gene expression is het proces waarbij informatie uit een gen wordt gebruikt om
een functioneel product te maken — meestal een eiwit. Het is de manier waarop
genetische instructies worden uitgevoerd in een cel. Niet alle genen zijn altijd
actief — welke genen 'aan' of 'uit' staan bepaalt wat een cel doet en hoe het zich
gedraagt.""")

    st.divider()

    st.subheader('🧬 Hoe werkt het in het lichaam?')
    st.write("""Het proces bestaat uit twee stappen:

1. **Transcriptie** — het DNA wordt afgelezen en omgezet naar RNA
2. **Translatie** — het RNA wordt omgezet naar een eiwit

Verschillende cellen hebben hetzelfde DNA maar andere gene expression patronen —
daarom is een hartcel anders dan een hersencel, ook al bevatten ze dezelfde genen.""")

    st.divider()

    st.subheader('🎯 Wat doet het?')
    st.write("""Gene expression bepaalt welke eiwitten een cel aanmaakt en daarmee alle functies
van die cel. Verstoorde gene expression speelt een rol bij veel ziekten — waaronder
kanker, auto-immuunziekten en erfelijke aandoeningen. Door gene expression te meten
kunnen onderzoekers ziekten beter begrijpen en nieuwe behandelingen ontwikkelen.""")

    st.divider()

    st.subheader('🔬 Onderzoek binnen Amsterdam UMC')
    st.write("""**👤 Robert de Jonge**

Prof. dr. Robert de Jonge onderzoekt gene expression patronen in relatie tot
laboratorium diagnostiek en farmacologie. Zijn werk richt zich op het begrijpen
van hoe genen betrokken bij het metabolisme van geneesmiddelen zoals methotrexaat
worden gereguleerd, en hoe variaties in gene expression de effectiviteit en
bijwerkingen van behandelingen beïnvloeden bij patiënten met inflammatoire ziekten.""")

    st.divider()

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider die bij deze expertise aansluiten."
    )

    publicaties = pd.read_sql(
        """        SELECT title, year, pubmed_url FROM publications
        WHERE LOWER(abstract) LIKE '%gene expression%'
        OR LOWER(keywords) LIKE '%gene expression%'
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
