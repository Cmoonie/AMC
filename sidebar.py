import streamlit as st


def toon_sidebar():

    gebruikersnaam = st.session_state.get(
        "gebruikersnaam",
        ""
    )

    st.sidebar.markdown(
        f"### 👤 {gebruikersnaam}"
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🏠 Home",
        use_container_width=True
    ):
        st.switch_page("app.py")

    if st.sidebar.button(
        "👤 Profiel",
        use_container_width=True
    ):
        st.switch_page(
            "pages/mijn_profiel.py"
        )

    if st.sidebar.button(
        "🕸️ Kennisgraaf",
        use_container_width=True
    ):
        st.switch_page(
            "pages/kennisgraaf.py"
        )

    if (
        st.session_state.get("rol")
        == "beheerder"
    ):

        if st.sidebar.button(
            "⚙️ Beheer",
            use_container_width=True
        ):
            st.switch_page(
                "pages/beheer.py"
            )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Uitloggen",
        use_container_width=True
    ):

        st.session_state.ingelogd = False
        st.session_state.rol = None

        st.rerun()

    # Automatische Streamlit navigatie verbergen
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] {
            display: none;
        }
        </style>
        """,
        unsafe_allow_html=True
    )