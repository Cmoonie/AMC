import streamlit as st


def toon_sidebar():

    ingelogd = st.session_state.get(
        "ingelogd",
        False
    )

    rol = st.session_state.get(
        "rol"
    )

    gebruikersnaam = st.session_state.get(
        "gebruikersnaam",
        ""
    )


    # ========================================================
    # BOVENKANT SIDEBAR
    # ========================================================

    if ingelogd:
        st.sidebar.markdown(
            f"### 👤 {gebruikersnaam}"
        )
    else:
        st.sidebar.markdown(
            "### 🔎 Spider"
        )

    st.sidebar.divider()


    # ========================================================
    # OPENBARE PAGINA'S
    # ========================================================

    if st.sidebar.button(
        "🏠 Home",
        use_container_width=True,
        key="sidebar_home"
    ):
        st.switch_page(
            "app.py"
        )

    if st.sidebar.button(
        "🕸️ Kennisgraaf",
        use_container_width=True,
        key="sidebar_kennisgraaf"
    ):
        st.switch_page(
            "pages/kennisgraaf.py"
        )


    # ========================================================
    # ALLEEN INGELOGD
    # ========================================================

    if ingelogd:

        if st.sidebar.button(
            "👤 Profiel",
            use_container_width=True,
            key="sidebar_profiel"
        ):
            st.switch_page(
                "pages/mijn_profiel.py"
            )

        # Volledig beheer
        # Alleen beschikbaar voor beheerders.
        if rol == "beheerder":

            if st.sidebar.button(
                "⚙️ Beheer",
                use_container_width=True,
                key="sidebar_beheer"
            ):
                st.switch_page(
                    "pages/beheer.py"
                )


    # ========================================================
    # LOGIN / LOGOUT
    # ========================================================

    if ingelogd:

        if st.sidebar.button(
            "🚪 Uitloggen",
            use_container_width=True,
            key="sidebar_logout"
        ):

                        # Loginstatus wissen
            st.session_state.ingelogd = False
            st.session_state.rol = None
            st.session_state.gebruikersnaam = ""
            st.session_state.naam = ""
            st.session_state.person_id = None

            # Zoekstatus wissen zodat een volgende gebruiker
            # niet de zoekopdracht van de vorige gebruiker ziet.
            st.session_state.pop(
                "zoekterm_input",
                None,
            )
            st.session_state.pop(
                "laatste_zoekterm",
                None,
            )

            st.switch_page(
                "app.py"
            )

    else:

        if st.sidebar.button(
            "🔐 Inloggen",
            use_container_width=True,
            key="sidebar_login"
        ):
            st.switch_page(
                "pages/login.py"
            )


    # ========================================================
    # AUTOMATISCHE STREAMLIT NAVIGATIE VERBERGEN
    # ========================================================

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