import streamlit as st

st.set_page_config(
    page_title="Methotrexaat - Spider",
    layout="wide"
)

import pandas as pd
import sqlite3
import os
import base64

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
# EXPERTISE ACHTERGROND
# ============================================================

achtergrond_pad = os.path.join(
    os.path.dirname(__file__),
    "..",
    "assets",
    "expertise_achtergrond.png"
)

if os.path.exists(achtergrond_pad):
    with open(achtergrond_pad, "rb") as afbeelding:
        achtergrond_base64 = base64.b64encode(
            afbeelding.read()
        ).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image:
                linear-gradient(
                    rgba(234, 243, 250, 0.30),
                    rgba(234, 243, 250, 0.30)
                ),
                url("data:image/png;base64,{achtergrond_base64}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        div[data-testid="stVerticalBlockBorderWrapper"] {{
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid #CED9E5 !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 24px rgba(0, 55, 65, 0.08) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">EXPERTISE</div>',
        unsafe_allow_html=True
    )

    st.title("💊 Methotrexaat")

    st.caption(
        "Wetenschappelijke expertise binnen Amsterdam UMC"
    )

    st.divider()


    # ========================================================
    # 1. WAT IS HET?
    # ========================================================

    st.subheader("📖 Wat is methotrexaat?")

    st.write(
        """
        Methotrexaat is een geneesmiddel dat oorspronkelijk werd ontwikkeld
        als chemotherapie voor kanker, maar nu ook veel wordt gebruikt bij
        auto-immuunziekten zoals reumatoïde artritis, de ziekte van Crohn
        en psoriasis.

        Het behoort tot de groep van antimetabolieten — stoffen die de
        aanmaak van DNA in cellen remmen.
        """
    )

    st.divider()


    # ========================================================
    # 2. HOE WERKT HET?
    # ========================================================

    st.subheader("🧬 Hoe werkt het in het lichaam?")

    st.write(
        """
        Methotrexaat werkt door het enzym dihydrofolaatreductase (DHFR)
        te blokkeren.

        Dit enzym is nodig voor de aanmaak van foliumzuur, dat cellen
        nodig hebben om zich te delen. Door dit te blokkeren remt
        methotrexaat de groei van snel delende cellen — zowel
        kankercellen als ontstekingscellen.
        """
    )

    st.divider()


    # ========================================================
    # 3. WAT DOET HET?
    # ========================================================

    st.subheader("💊 Wat doet het?")

    st.write(
        """
        Bij lage doses onderdrukt methotrexaat het immuunsysteem en
        vermindert het ontstekingen.

        Bij hogere doses doodt het snel delende cellen, wat het effectief
        maakt bij bepaalde vormen van kanker zoals leukemie.
        """
    )

    st.divider()


    # ========================================================
    # 4. ONDERZOEK
    # ========================================================

    st.subheader("🔬 Onderzoek binnen Amsterdam UMC")

    st.markdown("#### 👤 Robert de Jonge")

    st.write(
        """
        Prof. dr. Robert de Jonge heeft uitgebreid onderzoek gedaan naar
        methotrexaat-polyglutamaten — de actieve vorm van methotrexaat in
        rode bloedcellen.

        Zijn onderzoek richt zich op het meten van deze concentraties om
        de effectiviteit van de behandeling te monitoren bij kinderen met
        leukemie en patiënten met reumatoïde artritis.
        """
    )

    st.divider()


    # ========================================================
    # 5. RELEVANTE PUBLICATIES
    # ========================================================

    st.subheader("📄 Relevante publicaties")

    st.caption(
        "Publicaties uit Spider waarin methotrexaat voorkomt."
    )

    publicaties = pd.read_sql(
        """
        SELECT title, year, pubmed_url
        FROM publications
        WHERE LOWER(keywords) LIKE '%methotrexate%'
           OR LOWER(abstract) LIKE '%methotrexate%'
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


    # ========================================================
    # TERUG
    # ========================================================

    if st.button(
        "← Terug naar zoeken",
        key="terug_naar_zoeken"
    ):
        st.switch_page("app.py")
