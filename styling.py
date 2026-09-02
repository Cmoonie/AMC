"""
styling.py — Gedeelde styling helper voor Spider
Zet een lichte, pagina-specifieke achtergrondkleur zodat direct duidelijk is
in welk onderdeel van de app je zit. Gebaseerd op de officiële Amsterdam UMC
huisstijlkleuren, verlicht tot een subtiele tint.

Gebruik (bovenaan elke pagina, na st.set_page_config):

    from styling import set_background
    set_background("profiel")
"""

import streamlit as st

# Lichte tinten afgeleid van de Amsterdam UMC huisstijlkleuren
# (basiskleur -> ~90% richting wit gemengd, voor een subtiele achtergrond)
PAGE_COLORS = {
    "home":         "#FFFFFF",  # Zoekpagina — neutraal wit
    "profiel":      "#E6F2F3",  # Onderzoeker & mijn profiel — lichtblauw (van donkerblauw #003741)
    "expertise":    "#FCE8E9",  # Expertise-pagina's — lichtrood (van rood #E6000F)
    "projecten":    "#FDF0E4",  # Lopende projecten — lichtoranje (van oranje #F07814)
    "kennisgraaf":  "#EDF1F6",  # Kennisgraaf — lichtgrijsblauw (van koud grijs #CED9E5)
    "beheer":       "#F2F2F2",  # Beheerpagina — lichtgrijs (van zwart #131516)
    "geschiedenis": "#EDF1F6",  # Geschiedenis — lichtgrijsblauw (van koud grijs #CED9E5)
}


def set_background(pagina_type: str) -> None:
    """
    Zet een lichte, pagina-specifieke achtergrondkleur via CSS-injectie.

    Args:
        pagina_type: een van de keys in PAGE_COLORS
                     ("home", "profiel", "expertise", "projecten",
                      "kennisgraaf", "beheer", "geschiedenis")
    """
    kleur = PAGE_COLORS.get(pagina_type, PAGE_COLORS["home"])

    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"],
        .stApp {{
            background-color: {kleur} !important;
        }}
        [data-testid="stHeader"] {{
            background-color: transparent !important;
        }}
        [data-testid="stMain"] {{
            background-color: {kleur} !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )