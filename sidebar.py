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
        st.switch_page("app.py")


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


        if rol == "beheerder":

            if st.sidebar.button(
                "⚙️ Beheer",
                use_container_width=True,
                key="sidebar_beheer"
            ):
                st.switch_page(
                    "pages/beheer.py"
                )


    st.sidebar.divider()


    # ========================================================
    # LOGIN / LOGOUT
    # ========================================================

    if ingelogd:

        if st.sidebar.button(
            "🚪 Uitloggen",
            use_container_width=True,
            key="sidebar_logout"
        ):

            st.session_state.ingelogd = False
            st.session_state.rol = None
            st.session_state.gebruikersnaam = ""
            st.session_state.person_id = None

            st.switch_page("app.py")

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

    # import streamlit as st


# def toon_sidebar():

#     gebruikersnaam = st.session_state.get(
#         "gebruikersnaam",
#         ""
#     )

#     st.sidebar.markdown(
#         f"### 👤 {gebruikersnaam}"
#     )

#     st.sidebar.divider()

#     if st.sidebar.button(
#         "🏠 Home",
#         use_container_width=True
#     ):
#         st.switch_page("app.py")

#     if st.sidebar.button(
#         "👤 Profiel",
#         use_container_width=True
#     ):
#         st.switch_page(
#             "pages/mijn_profiel.py"
#         )

#     if st.sidebar.button(
#         "🕸️ Kennisgraaf",
#         use_container_width=True
#     ):
#         st.switch_page(
#             "pages/kennisgraaf.py"
#         )

#     if (
#         st.session_state.get("rol")
#         == "beheerder"
#     ):

#         if st.sidebar.button(
#             "⚙️ Beheer",
#             use_container_width=True
#         ):
#             st.switch_page(
#                 "pages/beheer.py"
#             )

#     st.sidebar.divider()

#     if st.sidebar.button(
#         "🚪 Uitloggen",
#         use_container_width=True
#     ):

#         st.session_state.ingelogd = False
#         st.session_state.rol = None

#         st.rerun()

#     # Automatische Streamlit navigatie verbergen
#     st.markdown(
#         """
#         <style>
#         [data-testid="stSidebarNav"] {
#             display: none;
#         }
#         </style>
#         """,
#         unsafe_allow_html=True
#     )