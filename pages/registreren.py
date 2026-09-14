import hashlib
import hmac
import secrets
import streamlit as st

from database import get_connection, initialize_database
from styling import apply_styling


# ============================================================
# DATABASE CONTROLEREN
# ============================================================

initialize_database()


# ============================================================
# PAGINA INSTELLINGEN
# ============================================================

st.set_page_config(
    page_title="Registreren - Spider",
    page_icon="🕷️",
    layout="wide"
)

apply_styling("profiel")


# ============================================================
# WACHTWOORD HASHEN
# ============================================================

def hash_wachtwoord(wachtwoord):
    """
    Maakt een veilige wachtwoord-hash met PBKDF2.
    De salt wordt samen met de hash opgeslagen.
    """

    salt = secrets.token_hex(16)

    wachtwoord_hash = hashlib.pbkdf2_hmac(
        "sha256",
        wachtwoord.encode("utf-8"),
        salt.encode("utf-8"),
        200_000
    ).hex()

    return f"{salt}${wachtwoord_hash}"





# ============================================================
# REGISTRATIE OPSLAAN
# ============================================================

def registreer_onderzoeker(
    naam,
    wachtwoord
):
    """
    Maakt in één transactie aan:
    1. onderzoeker in persons
    2. account in gebruikers
    3. leeg profiel in profiel_data

    De volledige naam wordt voorlopig ook gebruikt
    als gebruikersnaam voor het inloggen.
    """

    conn = get_connection()

    try:

        cursor = conn.cursor()

        naam = naam.strip()

        # ----------------------------------------------------
        # CONTROLEREN OF ACCOUNT AL BESTAAT
        # ----------------------------------------------------

        bestaand = cursor.execute(
            """
            SELECT id
            FROM gebruikers
            WHERE LOWER(gebruikersnaam) = LOWER(?)
            """,
            (
                naam,
            )
        ).fetchone()

        if bestaand:

            return False, (
                "Er bestaat al een account met deze naam."
            )

        # ----------------------------------------------------
        # 1. ONDERZOEKER AANMAKEN
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO persons (
                name,
                department
            )
            VALUES (?, ?)
            """,
            (
                naam,
                ""
            )
        )

        person_id = cursor.lastrowid

        # ----------------------------------------------------
        # 2. WACHTWOORD HASHEN
        # ----------------------------------------------------

        wachtwoord_hash = hash_wachtwoord(
            wachtwoord
        )

        # ----------------------------------------------------
        # 3. ACCOUNT AANMAKEN
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO gebruikers (
                naam,
                gebruikersnaam,
                wachtwoord,
                afdeling,
                rol,
                person_id,
                aangemaakt_op
            )
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (
                naam,
                naam,
                wachtwoord_hash,
                "",
                "gebruiker",
                person_id
            )
        )

        # ----------------------------------------------------
        # 4. LEEG PROFIEL AANMAKEN
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT INTO profiel_data (
                person_id,
                gebruikersnaam,
                email,
                bio,
                expertise,
                projecten,
                links
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                naam,
                "",
                "",
                "",
                "",
                ""
            )
        )

        conn.commit()

        return True, person_id

    except Exception as e:

        conn.rollback()

        return False, str(e)

    finally:

        conn.close()


# ============================================================
# SESSION STATE
# ============================================================

if "registratie_gelukt" not in st.session_state:
    st.session_state.registratie_gelukt = False


# ============================================================
# PAGINA
# ============================================================
col1, col2 = st.columns([3, 2])

with col1:

    st.markdown("""
    <h1 style="
        margin-top: 0;
        color: #003741;
    ">
        Registreren bij Spider
    </h1>

    <p style="
        font-size: 18px;
        color: #003741;
        margin-bottom: 30px;
    ">
        Maak een account aan om je onderzoekersprofiel,
        projecten en publicaties te beheren.
    </p>
    """, unsafe_allow_html=True)

with col2:

    st.image(
        "assets/loginpagina.png",
        use_container_width=True
    )


# ============================================================
# SUCCESMELDING
# ============================================================

if st.session_state.registratie_gelukt:

    st.success(
        "Je account is aangemaakt. "
        "Je kunt nu inloggen."
    )

    if st.button(
        "🔐 Naar inloggen",
        type="primary",
        use_container_width=True
    ):
        st.session_state.registratie_gelukt = False
        st.switch_page("pages/login.py")

    st.stop()



# ============================================================
# REGISTRATIEFORMULIER
# ============================================================

with st.container(border=True):

    st.subheader("Account aanmaken")

    naam = st.text_input(
        "Volledige naam *",
        placeholder="Bijvoorbeeld: Robert de Jonge"
    )

    wachtwoord = st.text_input(
        "Wachtwoord *",
        type="password"
    )

    wachtwoord_bevestiging = st.text_input(
        "Herhaal wachtwoord *",
        type="password"
    )

    st.caption(
        "E-mailadres, afdeling en andere profielgegevens "
        "kun je na het inloggen toevoegen aan je profiel."
    )

    st.caption(
        "* Verplichte velden"
    )

    registreren = st.button(
        "Account aanmaken",
        type="primary",
        use_container_width=True
    )


# ============================================================
# FORMULIER VERWERKEN
# ============================================================

if registreren:

    fouten = []

    naam = naam.strip()


    # --------------------------------------------------------
    # VERPLICHTE VELDEN
    # --------------------------------------------------------

    if not naam:
        fouten.append(
            "Vul je volledige naam in."
        )


    if not wachtwoord:
        fouten.append(
            "Vul een wachtwoord in."
        )

    # # --------------------------------------------------------
    # # EMAIL EENVOUDIG CONTROLEREN
    # # --------------------------------------------------------

    # if email and (
    #     "@" not in email
    #     or "." not in email.split("@")[-1]
    # ):
    #     fouten.append(
    #         "Vul een geldig e-mailadres in."
    #     )

    # --------------------------------------------------------
    # WACHTWOORD
    # --------------------------------------------------------

    if wachtwoord and len(wachtwoord) < 8:
        fouten.append(
            "Het wachtwoord moet minimaal 8 tekens bevatten."
        )

    if wachtwoord != wachtwoord_bevestiging:
        fouten.append(
            "De wachtwoorden zijn niet hetzelfde."
        )

    # --------------------------------------------------------
    # GEBRUIKERSNAAM BESTAAT AL
    # --------------------------------------------------------

    # if (
    #     gebruikersnaam
    #     and gebruikersnaam_bestaat(
    #         gebruikersnaam
    #     )
    # ):
    #     fouten.append(
    #         "Deze gebruikersnaam bestaat al."
    #     )

    # --------------------------------------------------------
    # FOUTEN TONEN
    # --------------------------------------------------------

    if fouten:

        for fout in fouten:
            st.error(fout)

    else:

        gelukt, resultaat = registreer_onderzoeker(
            naam=naam,
            wachtwoord=wachtwoord,
            
        )

        if gelukt:

            st.session_state.registratie_gelukt = True
            st.rerun()

        else:

            st.error(
                "Registratie kon niet worden opgeslagen."
            )

            st.caption(
                f"Technische melding: {resultaat}"
            )


# ============================================================
# TERUG NAAR LOGIN
# ============================================================

st.write("")

if st.button(
    "← Terug naar inloggen",
    use_container_width=True
):
    st.switch_page("pages/login.py")