import os
import base64
import hashlib
import hmac

import streamlit as st

from database import get_connection


# ============================================================
# PAGINA-INSTELLINGEN
# ============================================================

st.set_page_config(
    page_title="Inloggen - Spider",
    layout="wide"
)


# ============================================================
# WACHTWOORD CONTROLEREN
# ============================================================

def controleer_wachtwoord(wachtwoord, opgeslagen_waarde):
    """
    Controleert wachtwoorden die bij registratie met PBKDF2 zijn opgeslagen.

    Verwacht formaat:
    salt$hash
    """

    try:
        salt, opgeslagen_hash = opgeslagen_waarde.split("$", 1)

        nieuwe_hash = hashlib.pbkdf2_hmac(
            "sha256",
            wachtwoord.encode("utf-8"),
            salt.encode("utf-8"),
            200_000
        ).hex()

        return hmac.compare_digest(
            nieuwe_hash,
            opgeslagen_hash
        )

    except Exception:
        return False


# ============================================================
# LOGIN VIA DATABASE
# ============================================================

def login_via_database(gebruikersnaam, wachtwoord):
    """
    Probeert een geregistreerde onderzoeker in te loggen
    via de tabel gebruikers.
    """

    conn = get_connection()

    gebruiker = conn.execute(
        """
        SELECT
            id,
            naam,
            gebruikersnaam,
            wachtwoord,
            afdeling,
            rol,
            person_id
        FROM gebruikers
        WHERE LOWER(gebruikersnaam) = LOWER(?)
        """,
        (
            gebruikersnaam.strip(),
        )
    ).fetchone()

    conn.close()

    if gebruiker is None:
        return None

    if not controleer_wachtwoord(
        wachtwoord,
        gebruiker["wachtwoord"]
    ):
        return None

    return gebruiker


# ============================================================
# LOGINPAGINA
# ============================================================

def login_pagina():

    # ========================================================
    # PAD NAAR ACHTERGROND
    # ========================================================

    achtergrond_pad = os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "loginpagina.png"
    )

    achtergrond_base64 = ""

    if os.path.exists(achtergrond_pad):
        with open(achtergrond_pad, "rb") as afbeelding:
            achtergrond_base64 = base64.b64encode(
                afbeelding.read()
            ).decode()


    # ========================================================
    # STYLING
    # ========================================================

    st.markdown(
        f"""
        <style>

        /* Sidebar verbergen */
        [data-testid="stSidebar"] {{
            display: none !important;
        }}

        /* Streamlit header transparant */
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

        /* Algemene tekst */
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

        /* Login label */
        .login-label {{
            color: #607D9B !important;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.22em;
            text-transform: uppercase;
            text-align: center;
            margin-bottom: 0.7rem;
        }}

        /* Login titel */
        .login-title {{
            color: #0B1F3A !important;
            font-size: 2.4rem;
            font-weight: 750;
            letter-spacing: -0.03em;
            line-height: 1.1;
            text-align: center;
            margin-bottom: 0.7rem;
        }}

        /* Login tekst */
        .login-text {{
            color: #526579 !important;
            font-size: 15px;
            line-height: 1.55;
            text-align: center;
            max-width: 520px;
            margin: 0 auto 1.5rem auto;
        }}

        /* Login kaart */
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

        /* Invoervelden */
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

        /* Knoppen */
        .stButton > button {{
            min-height: 54px !important;
            border-radius: 12px !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            transition: 0.2s ease;
        }}

        /* Primaire knop */
        .stButton > button[kind="primary"] {{
            background: #F07814 !important;
            color: white !important;
            border: 1px solid #F07814 !important;
        }}

        .stButton > button[kind="primary"]:hover {{
            background: #D9650B !important;
            border-color: #D9650B !important;
            transform: translateY(-1px);
        }}

        .stButton > button[kind="primary"] p {{
            color: white !important;
        }}

        /* Registratieknop */
        .stButton > button[kind="secondary"] {{
            background: white !important;
            color: #003741 !important;
            border: 1px solid #CED9E5 !important;
        }}

        .stButton > button[kind="secondary"]:hover {{
            color: #F07814 !important;
            border-color: #F07814 !important;
            transform: translateY(-1px);
        }}

        /* Foutmeldingen */
        [data-testid="stAlert"] {{
            border-radius: 12px !important;
        }}

        /* Tekst registratie */
        .register-text {{
            color: #0B1F3A !important;
            font-size: 18px;
            font-weight: 700;
            margin-top: 1.2rem;
            margin-bottom: 0.2rem;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN KAART
    # ========================================================

    st.markdown(
        '<div class="login-card">'
        '<div class="login-label">AMSTERDAM UMC</div>'
        '<div class="login-title">Welkom bij Spider</div>'
        '<div class="login-text">'
        'Log in om onderzoekers, expertise, projecten en publicaties '
        'binnen Amsterdam UMC te vinden.'
        '</div>'
        '</div>',
        unsafe_allow_html=True
    )


    # ========================================================
    # LOGIN VELDEN
    # ========================================================

    gebruikersnaam = st.text_input(
        "Gebruikersnaam",
        placeholder="Vul je gebruikersnaam in"
    )

    wachtwoord = st.text_input(
        "Wachtwoord",
        type="password",
        placeholder="Vul je wachtwoord in"
    )


    # ========================================================
    # LOGIN KNOP
    # ========================================================

    if st.button(
        "Inloggen",
        type="primary",
        use_container_width=True
    ):

        # ====================================================
        # BEHEERDER
        # ====================================================

        if (
            gebruikersnaam == "admin"
            and wachtwoord == "spider2026"
        ):

            st.session_state.ingelogd = True
            st.session_state.rol = "beheerder"
            st.session_state.gebruikersnaam = "Admin"
            st.session_state.person_id = None

            st.switch_page(
                "pages/beheer.py"
            )


        # ====================================================
        # ROBERT
        # ====================================================

        elif (
            gebruikersnaam == "robert"
            and wachtwoord == "test123"
        ):

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Robert de Jonge"
            st.session_state.person_id = 1

            st.switch_page(
                "app.py"
            )


        # ====================================================
        # SJORS
        # ====================================================

        elif (
            gebruikersnaam == "sjors"
            and wachtwoord == "test123"
        ):

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Sjors In 't Veld"
            st.session_state.person_id = 2

            st.switch_page(
                "app.py"
            )


        # ====================================================
        # MARTIJN
        # ====================================================

        elif (
            gebruikersnaam == "martijn"
            and wachtwoord == "test123"
        ):

            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Martijn C Schut"
            st.session_state.person_id = 3

            st.switch_page(
                "app.py"
            )


        # ====================================================
        # GEREGISTREERDE ONDERZOEKER UIT DATABASE
        # ====================================================

        else:

            gebruiker = login_via_database(
                gebruikersnaam,
                wachtwoord
            )

            if gebruiker is not None:

                st.session_state.ingelogd = True
                st.session_state.rol = gebruiker["rol"]
                st.session_state.gebruikersnaam = gebruiker["naam"]
                st.session_state.person_id = gebruiker["person_id"]

                st.switch_page(
                    "app.py"
                )

            else:

                st.error(
                    "Onjuiste gebruikersnaam of wachtwoord."
                )


    # ========================================================
    # REGISTREREN
    # ========================================================

    st.markdown(
        """
        <div class="register-text">
            Nog geen onderzoekersaccount?
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        "Registreren",
        use_container_width=True
    ):
        st.switch_page(
            "pages/registreren.py"
        )


# ============================================================
# LOGINPAGINA STARTEN
# ============================================================

login_pagina()
# import os
# import base64
# import streamlit as st
# import hashlib
# import hmac

# from database import get_connection


# def login_pagina():

#     # ============================================================
#     # PAD NAAR ACHTERGROND
#     # ============================================================

#     achtergrond_pad = os.path.join(
#         os.path.dirname(__file__),
#         "..",
#         "assets",
#         "loginpagina.png"
#     )

#     # Afbeelding omzetten naar base64 zodat we hem als CSS-achtergrond kunnen gebruiken
#     achtergrond_base64 = ""

#     if os.path.exists(achtergrond_pad):
#         with open(achtergrond_pad, "rb") as afbeelding:
#             achtergrond_base64 = base64.b64encode(
#                 afbeelding.read()
#             ).decode()


#     # ============================================================
#     # STYLING LOGINPAGINA
#     # ============================================================

#     st.markdown(
#         f"""
#         <style>

#         /* Sidebar volledig verbergen */
#         [data-testid="stSidebar"] {{
#             display: none !important;
#         }}

#         /* Bovenste Streamlit balk transparant */
#         [data-testid="stHeader"] {{
#             background: transparent !important;
#         }}

#         /* Achtergrond */
#         [data-testid="stAppViewContainer"] {{
#             background-image:
#                 linear-gradient(
#                     rgba(240, 248, 255, 0.08),
#                     rgba(240, 248, 255, 0.08)
#                 ),
#                 url("data:image/png;base64,{achtergrond_base64}");

#             background-size: cover;
#             background-position: center center;
#             background-repeat: no-repeat;
#             background-attachment: fixed;
#         }}

#         [data-testid="stMain"] {{
#             background: transparent !important;
#         }}

#         /* Pagina-inhoud */
#         .block-container {{
#             max-width: 650px;
#             padding-top: 20rem;
#             padding-bottom: 4rem;
#         }}

#         /* ======================================================
#            ALLE TEKST BLAUW
#            ====================================================== */

#         h1,
#         h2,
#         h3,
#         p,
#         label,
#         span,
#         small,
#         strong,
#         [data-testid="stMarkdownContainer"],
#         [data-testid="stCaptionContainer"] {{
#             color: #0B1F3A !important;
#         }}

#         /* ======================================================
#            LOGIN TITEL
#            ====================================================== */

#         .login-label {{
#             color: #607D9B !important;
#             font-size: 12px;
#             font-weight: 700;
#             letter-spacing: 0.22em;
#             text-transform: uppercase;
#             text-align: center;
#             margin-bottom: 0.7rem;
#         }}

#         .login-title {{
#             color: #0B1F3A !important;
#             font-size: 2.4rem;
#             font-weight: 750;
#             letter-spacing: -0.03em;
#             line-height: 1.1;
#             text-align: center;
#             margin-bottom: 0.7rem;
#         }}

#         .login-text {{
#             color: #526579 !important;
#             font-size: 15px;
#             line-height: 1.55;
#             text-align: center;
#             max-width: 520px;
#             margin: 0 auto 1.5rem auto;
#         }}

#         /* ======================================================
#            LOGIN BOX
#            ====================================================== */

#         .login-card {{
#             background: rgba(236, 248, 255, 0.78);
#             border: 1px solid rgba(255, 255, 255, 0.75);
#             border-radius: 28px;
#             padding: 2.2rem 2.4rem 1.7rem 2.4rem;
#             box-shadow:
#                 0 18px 45px rgba(20, 50, 80, 0.14);

#             backdrop-filter: blur(14px);
#             -webkit-backdrop-filter: blur(14px);
#         }}

#         /* ======================================================
#            INVOERVELDEN
#            ====================================================== */

#         [data-testid="stTextInput"] {{
#             margin-bottom: 0.25rem;
#         }}

#         [data-testid="stTextInput"] label {{
#             color: white !important;
#             font-size: 20px !important;
#             font-weight: 800 !important;
#             margin-bottom: 0.4rem !important;
#             text-shadow: 0 1px 4px rgba(11, 31, 58, 0.55);
#         }}

#         [data-testid="stTextInput"] label p,
#         [data-testid="stTextInput"] label span {{
#             color: white !important;
#             font-size: 20px !important;
#             font-weight: 800 !important;
# }}

#         [data-testid="stTextInput"] input {{
#             background-color: rgba(255, 255, 255, 0.97) !important;
#             color: #0B1F3A !important;

#             border:
#                 1px solid rgba(188, 205, 220, 0.9) !important;

#             border-radius: 12px !important;
#             min-height: 54px !important;

#             font-size: 16px !important;
#             font-weight: 500 !important;
#         }}

#         [data-testid="stTextInput"] input::placeholder {{
#             color: #607D9B !important;
#             opacity: 1 !important;
#         }}

#         [data-testid="stTextInput"] input:focus {{
#             border-color: #F07814 !important;
#             box-shadow:
#                 0 0 0 1px #F07814 !important;
#         }}

#         /* ======================================================
#            LOGIN KNOP
#            ====================================================== */

#         .stButton > button {{
#             background: #0B2FB8 !important;
#             color: white !important;

#             border: none !important;
#             border-radius: 12px !important;

#             min-height: 54px !important;
#             width: 100% !important;

#             font-size: 16px !important;
#             font-weight: 700 !important;

#             margin-top: 0.6rem !important;

#             transition: 0.2s ease;
#         }}

#         .stButton > button:hover {{
#             background: #08248F !important;
#             transform: translateY(-1px);
#         }}

#         /* Zorgt dat tekst op blauwe knop wit blijft */
#         .stButton > button p {{
#             color: white !important;
#         }}

#         /* Foutmelding */
#         [data-testid="stAlert"] {{
#             border-radius: 12px !important;
#         }}

#         </style>
#         """,
#         unsafe_allow_html=True
#     )


#     # ============================================================
#     # LOGIN KAART START
#     # ============================================================

#     st.markdown(
#         """<div class="login-card">
#     <div class="login-label">AMSTERDAM UMC</div>
#     <div class="login-title">Welkom bij Spider</div>
#     <div class="login-text">
#     Log in om onderzoekers, expertise, projecten en publicaties
#     binnen Amsterdam UMC te vinden.
#     </div>
#     </div>""",
#         unsafe_allow_html=True
#     )


#     # ============================================================
#     # LOGIN VELDEN
#     # ============================================================

#     gebruikersnaam = st.text_input(
#         "Gebruikersnaam",
#         placeholder="Vul je gebruikersnaam in"
#     )

#     wachtwoord = st.text_input(
#         "Wachtwoord",
#         type="password",
#         placeholder="Vul je wachtwoord in"
#     )


#     # ============================================================
#     # LOGIN KNOP
#     # ============================================================

#     if st.button(
#         "Inloggen",
#         type="primary",
#         use_container_width=True
#     ):

#         # Beheerder
#         if gebruikersnaam == "admin" and wachtwoord == "spider2026":

#             st.session_state.ingelogd = True
#             st.session_state.rol = "beheerder"
#             st.session_state.gebruikersnaam = "Admin"
#             st.session_state.person_id = None

#             st.switch_page(
#                 "pages/beheer.py"
#             )


#         # Robert
#         elif gebruikersnaam == "robert" and wachtwoord == "test123":

#             st.session_state.ingelogd = True
#             st.session_state.rol = "gebruiker"
#             st.session_state.gebruikersnaam = "Robert de Jonge"
#             st.session_state.person_id = 1
#             st.switch_page("app.py")


#         # Sjors
#         elif gebruikersnaam == "sjors" and wachtwoord == "test123":

#             st.session_state.ingelogd = True
#             st.session_state.rol = "gebruiker"
#             st.session_state.gebruikersnaam = "Sjors In 't Veld"
#             st.session_state.person_id = 2

#             st.switch_page("app.py")


#         # Martijn
#         elif gebruikersnaam == "martijn" and wachtwoord == "test123":

#             st.session_state.ingelogd = True
#             st.session_state.rol = "gebruiker"
#             st.session_state.gebruikersnaam = "Martijn C Schut"
#             st.session_state.person_id = 3

#             st.switch_page("app.py")

#         else:

#             # Geen demo-account?
#             # Dan zoeken we het account in de database.
#             gebruiker = login_via_database(
#                 gebruikersnaam,
#                 wachtwoord
#     )

#         if gebruiker is not None:

#                 st.session_state.ingelogd = True
#                 st.session_state.rol = gebruiker["rol"]
#                 st.session_state.gebruikersnaam = gebruiker["naam"]
#                 st.session_state.person_id = gebruiker["person_id"]

#                 st.switch_page("app.py")

#         else:

#                 st.error(
#                     "Onjuiste gebruikersnaam of wachtwoord."
#         )

# st.write("")

# st.caption(
#         "Nog geen onderzoekersaccount?"
#     )

# if st.button(
#         "Registreren",
#         use_container_width=True
#     ):
#         st.switch_page("pages/registreren.py")                


# # ============================================================
# # LOGINPAGINA STARTEN
# # ============================================================            
# def controleer_wachtwoord(wachtwoord, opgeslagen_waarde):
#     """
#     Controleert wachtwoorden die bij registratie met PBKDF2 zijn opgeslagen.
#     Verwacht formaat:
#     salt$hash
#     """

#     try:
#         salt, opgeslagen_hash = opgeslagen_waarde.split("$", 1)

#         nieuwe_hash = hashlib.pbkdf2_hmac(
#             "sha256",
#             wachtwoord.encode("utf-8"),
#             salt.encode("utf-8"),
#             200_000
#         ).hex()

#         return hmac.compare_digest(
#             nieuwe_hash,
#             opgeslagen_hash
#         )

#     except Exception:
#         return False


# def login_via_database(gebruikersnaam, wachtwoord):
#     """
#     Probeert in te loggen via de gebruikers-tabel.
#     """

#     conn = get_connection()

#     gebruiker = conn.execute(
#         """
#         SELECT
#             id,
#             naam,
#             gebruikersnaam,
#             wachtwoord,
#             afdeling,
#             rol,
#             person_id
#         FROM gebruikers
#         WHERE LOWER(gebruikersnaam) = LOWER(?)
#         """,
#         (gebruikersnaam.strip(),)
#     ).fetchone()

#     conn.close()

#     if gebruiker is None:
#         return None

#     if not controleer_wachtwoord(
#         wachtwoord,
#         gebruiker["wachtwoord"]
#     ):
#         return None

#     return gebruiker
# # ============================================================
# # LOGINPAGINA STARTEN
# # ============================================================

# login_pagina()