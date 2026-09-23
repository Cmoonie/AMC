import streamlit as st
import pandas as pd

from database import get_connection
from sidebar import toon_sidebar


# ============================================================
# TOEGANGSCONTROLE
# ============================================================

if (
    not st.session_state.get("ingelogd", False)
    or st.session_state.get("rol") != "beheerder"
):
    st.error(
        "Deze pagina is alleen beschikbaar voor beheerders."
    )
    st.switch_page("app.py")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

toon_sidebar()


# ============================================================
# DATABASE
# ============================================================

conn = get_connection()

# ----------------------
# Pagina inhoud
# ----------------------
st.title("📋 Wijzigingsgeschiedenis")
st.subheader("Alle wijzigingen door beheerders")

wijzigingen = pd.read_sql("SELECT * FROM wijzigingen", conn)
if wijzigingen.empty:
    st.info("Nog geen wijzigingen geregistreerd.")
else:
    st.dataframe(wijzigingen[::-1])