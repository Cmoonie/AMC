import os
import base64
import streamlit as st


def login_pagina():

    # ============================================================
    # PAD NAAR ACHTERGROND
    # ============================================================

    achtergrond_pad = os.path.join(
        os.path.dirname(__file__),
        "assets",
        "loginpagina.png"
    )

    # Afbeelding omzetten naar base64 zodat we hem als CSS-achtergrond kunnen gebruiken
    achtergrond_base64 = ""

    if os.path.exists(achtergrond_pad):
        with open(achtergrond_pad, "rb") as afbeelding:
            achtergrond_base64 = base64.b64encode(
                afbeelding.read()
            ).decode()


    # ============================================================
    # STYLING LOGINPAGINA
    # ============================================================

    st.markdown(
        f"""
        <style>

        /* Sidebar volledig verbergen */
        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        /* Bovenste Streamlit balk transparant */
        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        /* Achtergrond */
        [data-testid="stAppViewContainer"] {{
            background-image:
                linear-gradient(
                    rgba(240, 248, 255, 0.08),
                    rgba(240, 248, 255, 0.08)
                ),
                url("data:image/png;base64,{achtergrond_base64}");

            background-size: cover;
            background-position: center center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        [data-testid="stMain"] {{
            background: transparent !important;
        }}

        /* Pagina-inhoud */
        .block-container {{
            max-width: 650px;
            padding-top: 20rem;
            padding-bottom: 4rem;
        }}

        /* ======================================================
           ALLE TEKST BLAUW
           ====================================================== */

        h1,
        h2,
        h3,
        p,
        label,
        span,
        small,
        strong,
        [data-testid="stMarkdownContainer"],
        [data-testid="stCaptionContainer"] {{
            color: #0B1F3A !important;
        }}

        /* ======================================================
           LOGIN TITEL
           ====================================================== */

        .login-label {{
            color: #607D9B !important;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 0.7rem;
        }}

        .login-title {{
            color: #0B1F3A !important;
            font-size: 2.4rem;
            font-weight: 750;
            letter-spacing: -0.03em;
            line-height: 1.1;
            text-align: center;
            margin-bottom: 0.7rem;
        }}

        .login-text {{
            color: #526579 !important;
            font-size: 15px;
            line-height: 1.55;
            text-align: center;
            max-width: 520px;
            margin: 0 auto 1.5rem auto;
        }}

        /* ======================================================
           LOGIN BOX
           ====================================================== */

        .login-card {{
            background: rgba(236, 248, 255, 0.78);
            border: 1px solid rgba(255, 255, 255, 0.75);
            border-radius: 28px;
            padding: 2.2rem 2.4rem 1.7rem 2.4rem;
            box-shadow:
                0 18px 45px rgba(20, 50, 80, 0.14);

            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }}

        /* ======================================================
           INVOERVELDEN
           ====================================================== */

        [data-testid="stTextInput"] {{
            margin-bottom: 0.25rem;
        }}

        [data-testid="stTextInput"] label {{
            color: white !important;
            font-size: 20px !important;
            font-weight: 800 !important;
            margin-bottom: 0.4rem !important;
            text-shadow: 0 1px 4px rgba(11, 31, 58, 0.55);
        }}

        [data-testid="stTextInput"] label p,
        [data-testid="stTextInput"] label span {{
            color: white !important;
            font-size: 20px !important;
            font-weight: 800 !important;
}}

        [data-testid="stTextInput"] input {{
            background-color: rgba(255, 255, 255, 0.97) !important;
            color: #0B1F3A !important;

            border:
                1px solid rgba(188, 205, 220, 0.9) !important;

            border-radius: 12px !important;
            min-height: 54px !important;

            font-size: 16px !important;
            font-weight: 500 !important;
        }}

        [data-testid="stTextInput"] input::placeholder {{
            color: #607D9B !important;
            opacity: 1 !important;
        }}

        [data-testid="stTextInput"] input:focus {{
            border-color: #F07814 !important;
            box-shadow:
                0 0 0 1px #F07814 !important;
        }}

        /* ======================================================
           LOGIN KNOP
           ====================================================== */

        .stButton > button {{
            background: #0B2FB8 !important;
            color: white !important;

            border: none !important;
            border-radius: 12px !important;

            min-height: 54px !important;
            width: 100% !important;

            font-size: 16px !important;
            font-weight: 700 !important;

            margin-top: 0.6rem !important;

            transition: 0.2s ease;
        }}

        .stButton > button:hover {{
            background: #08248F !important;
            transform: translateY(-1px);
        }}

        /* Zorgt dat tekst op blauwe knop wit blijft */
        .stButton > button p {{
            color: white !important;
        }}

        /* Foutmelding */
        [data-testid="stAlert"] {{
            border-radius: 12px !important;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


    # ============================================================
    # LOGIN KAART START
    # ============================================================

    st.markdown(
        """<div class="login-card">
    <div class="login-label">AMSTERDAM UMC</div>
    <div class="login-title">Welkom bij Spider</div>
    <div class="login-text">
    Log in om onderzoekers, expertise, projecten en publicaties
    binnen Amsterdam UMC te vinden.
    </div>
    </div>""",
        unsafe_allow_html=True
    )


    # ============================================================
    # LOGIN VELDEN
    # ============================================================

    gebruikersnaam = st.text_input(
        "Gebruikersnaam",
        placeholder="Vul je gebruikersnaam in"
    )

    wachtwoord = st.text_input(
        "Wachtwoord",
        type="password",
        placeholder="Vul je wachtwoord in"
    )


    # ============================================================
    # LOGIN KNOP
    # ============================================================

    if st.button(
        "Inloggen",
        type="primary",
        use_container_width=True
    ):

        # Beheerder
        if gebruikersnaam == "admin" and wachtwoord == "spider2026":

            st.session_state.ingelogd = True
            st.session_state.rol = "beheerder"
            st.session_state.gebruikersnaam = "Admin"

            st.switch_page(
                "pages/beheer.py"
            )


        # Robert
        elif gebruikersnaam == "robert" and wachtwoord == "test123":

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Robert de Jonge"

            st.rerun()


        # Sjors
        elif gebruikersnaam == "sjors" and wachtwoord == "test123":

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Sjors In 't Veld"

            st.rerun()


        # Martijn
        elif gebruikersnaam == "martijn" and wachtwoord == "test123":

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Martijn C Schut"

            st.rerun()


        # Fout
        else:

            st.error(
                "Onjuiste gebruikersnaam of wachtwoord."
            )