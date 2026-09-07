"""
styling.py — Gedeelde styling helper voor Spider
"""

import streamlit as st


# =========================
# ACHTERGRONDEN PER PAGINA
# =========================

PAGE_BACKGROUNDS = {
    "home": """
        radial-gradient(
            circle at 88% 8%,
            rgba(190, 216, 240, 0.55) 0px,
            rgba(210, 228, 244, 0.25) 180px,
            transparent 360px
        ),
        radial-gradient(
            circle at 15% 92%,
            rgba(203, 224, 242, 0.45) 0px,
            transparent 320px
        ),
        linear-gradient(
            135deg,
            #F8FBFE 0%,
            #EAF3FA 55%,
            #F7FAFC 100%
        )
    """,

    "profiel": """
        linear-gradient(
            135deg,
            #F8FAFC 0%,
            #EEF4F8 50%,
            #F8FAFC 100%
        )
    """,

    "expertise": """
        linear-gradient(
            135deg,
            #FFF9F7 0%,
            #F7F3F1 50%,
            #FFF9F7 100%
        )
    """,

    "projecten": """
        linear-gradient(
            135deg,
            #FFF9F4 0%,
            #F7F2EC 50%,
            #FFF9F4 100%
        )
    """,

    "kennisgraaf": """
        linear-gradient(
            135deg,
            #F7F9FC 0%,
            #EDF3F8 50%,
            #F7F9FC 100%
        )
    """,

    "beheer": """
        linear-gradient(
            135deg,
            #F5F6F7 0%,
            #ECEFF2 50%,
            #F5F6F7 100%
        )
    """,

    "geschiedenis": """
        linear-gradient(
            135deg,
            #F7F9FC 0%,
            #EDF3F8 50%,
            #F7F9FC 100%
        )
    """,
}


def apply_styling(pagina_type: str) -> None:

    achtergrond = PAGE_BACKGROUNDS.get(
        pagina_type,
        PAGE_BACKGROUNDS["home"]
    )

    st.markdown(
        f"""
        <style>

        /* =========================
            ALGEMENE TEKSTKLEUR
            ========================== */

            html,
            body,
            p,
            span,
            label,
            div,
            li,
            a,
            small,
            strong,
            [data-testid="stMarkdownContainer"],
            [data-testid="stCaptionContainer"] {{
                color: #0B1F3A;
            }}

        /* Tekst in invoervelden */
        input,
        textarea {{
            color: #0B1F3A !important;
        }}

        /* Placeholder tekst iets lichter blauw */
        input::placeholder,
        textarea::placeholder {{
            color: #607D9B !important;
            opacity: 1;
}}    

        /* =========================
           ALGEMENE PAGINA
        ========================== */

        [data-testid="stAppViewContainer"],
        .stApp {{
            background: {achtergrond} !important;
        }}

        [data-testid="stMain"] {{
            background: transparent !important;
        }}

        [data-testid="stHeader"] {{
            background: transparent !important;
        }}

        /* =========================
            ALGEMENE TEKST
        ========================== */

            p,
            label,
            .stMarkdown,
            .stCaption {{
                color: #0B1F3A !important;
                font-size: 14px !important;
}}


        /* =========================
           CONTENTBREEDTE
        ========================== */

        .block-container {{
            max-width: 1250px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }}

        /* =========================
        AI SAMENVATTING
        ========================== */

        .ai-summary {{
            color: #0B1F3A;
            font-size: 16px;
            line-height: 1.6;
            font-weight: 500;
        }}

        /* =========================
           TYPOGRAFIE
        ========================== */

        h1 {{
            color: #0B1F3A !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }}

        h2 {{
            color: #0B1F3A !important;
            font-weight: 650 !important;
        }}

        h3 {{
            color: #1D3557 !important;
            font-weight: 600 !important;
        }}

        p {{
            color: #425466;
        }}


        /* =========================
           HERO TEKST
        ========================== */

        .hero-label {{
            color: #607D9B;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.18em;
            text-transform: uppercase;
            margin-bottom: 0.8rem;
        }}

        .hero-title {{
            color: #0B1F3A;
            font-size: 2.5rem;
            line-height: 1.08;
            font-weight: 750;
            letter-spacing: -0.03em;
            max-width: 540px;
            margin-bottom: 1rem;
        }}

        .hero-text {{
            color: #526579;
            font-size: 1rem;
            line-height: 1.6;
            max-width: 500px;
            margin-bottom: 1.5rem;
        }}


        /* =========================
        HERO AFBEELDING
        ========================== */

    [data-testid="stImage"] img {{
        border-radius: 24px;

        filter:
            brightness(1.12)
            contrast(0.82)
            saturate(0.68);

        opacity: 0.82;

        /*
        Laat alle randen van de foto
        geleidelijk transparant worden.
        */
        -webkit-mask-image:
            radial-gradient(
                ellipse at center,
                black 45%,
                rgba(0, 0, 0, 0.95) 58%,
                rgba(0, 0, 0, 0.65) 72%,
                transparent 60%
            );

        mask-image:
            radial-gradient(
                ellipse at center,
                black 15%,
                rgba(0, 0, 0, 0.95) 58%,
                rgba(0, 0, 0, 0.65) 72%,
                transparent 94%
            );

        box-shadow: none !important;
}}

        /* =========================
           PRIMAIRE KNOPPEN
        ========================== */

        .stButton > button[kind="primary"] {{
            background-color: #F07814 !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            font-weight: 600 !important;
            padding: 0.55rem 1rem !important;
            transition: 0.2s ease;
        }}

        .stButton > button[kind="primary"]:hover {{
            background-color: #D9650E !important;
            transform: translateY(-1px);
        }}


        /* =========================
           SECUNDAIRE KNOPPEN
        ========================== */

        .stButton > button[kind="secondary"] {{
            background-color: white !important;
            color: #0B1F3A !important;
            border: 1px solid #D8E0E8 !important;
            border-radius: 10px !important;
            font-weight: 500 !important;
        }}

        .stButton > button[kind="secondary"]:hover {{
            border-color: #F07814 !important;
            color: #F07814 !important;
        }}


        /* =========================
           INPUTS
        ========================== */

        [data-testid="stTextInput"] input {{
            border-radius: 10px !important;
            border: 1px solid #D8E0E8 !important;
            background-color: rgba(255, 255, 255, 0.95) !important;
        }}

        [data-testid="stTextInput"] input:focus {{
            border-color: #F07814 !important;
            box-shadow: 0 0 0 1px #F07814 !important;
        }}


        /* =========================
           CARDS
        ========================== */

        .spider-card {{
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid #E5EAF0;
            border-radius: 16px;
            padding: 1.25rem;
            box-shadow: 0 4px 14px rgba(15, 35, 60, 0.05);
            margin-bottom: 1rem;
        }}


        /* =========================
           TAGS
        ========================== */

        .expertise-tag {{
            display: inline-block;
            background-color: #EDF4FA;
            color: #174A68;
            padding: 0.35rem 0.7rem;
            margin: 0.2rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 500;
        }}


        /* =========================
           STATUS BADGE
        ========================== */

        .status-active {{
            display: inline-block;
            background: #E9F7EF;
            color: #1F7A4D;
            padding: 0.3rem 0.65rem;
            border-radius: 999px;
            font-size: 0.8rem;
            font-weight: 600;
        }}

        .stButton > button[kind="secondary"] {{
        background-color: white !important;
        color: #0B1F3A !important;
        border: 1px solid #D8E0E8 !important;
}}

    .stButton > button[kind="primary"] {{
        background-color: #F07814 !important;
        color: white !important;
}}

        </style>
        """,
        unsafe_allow_html=True,
    )