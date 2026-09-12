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
# CONTROLE: BESTAAT GEBRUIKERSNAAM?
# ============================================================

def gebruikersnaam_bestaat(gebruikersnaam):
    conn = get_connection()

    bestaand = conn.execute(
        """
        SELECT id
        FROM gebruikers
        WHERE LOWER(gebruikersnaam) = LOWER(?)
        """,
        (gebruikersnaam,)
    ).fetchone()

    conn.close()

    return bestaand is not None


# ============================================================
# REGISTRATIE OPSLAAN
# ============================================================

def registreer_onderzoeker(
    naam,
    gebruikersnaam,
    wachtwoord,
    afdeling,
    email
):
    """
    Maakt in één transactie aan:
    1. person
    2. gebruiker
    3. profiel_data

    Als één stap mislukt, wordt alles teruggedraaid.
    """

    conn = get_connection()

    try:
        cursor = conn.cursor()

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
                naam.strip(),
                afdeling.strip()
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
            VALUES (
                ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP
            )
            """,
            (
                naam.strip(),
                gebruikersnaam.strip(),
                wachtwoord_hash,
                afdeling.strip(),
                "gebruiker",
                person_id
            )
        )

        # ----------------------------------------------------
        # 4. PROFIEL AANMAKEN
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
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                person_id,
                gebruikersnaam.strip(),
                email.strip(),
                "",
                "",
                "",
                ""
            )
        )

        # ----------------------------------------------------
        # ALLES OPSLAAN
        # ----------------------------------------------------

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

st.markdown(
    """
    <div style="
        max-width: 760px;
        margin: 0 auto;
        padding-top: 30px;
    ">
        <p style="
            color: #F07814;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin-bottom: 4px;
        ">
            ONDERZOEKERSACCOUNT
        </p>

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
    </div>
    """,
    unsafe_allow_html=True
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

    st.subheader("Persoonsgegevens")

    naam = st.text_input(
        "Volledige naam *",
        placeholder="Bijvoorbeeld: Robert de Jonge"
    )

    afdeling = st.text_input(
        "Afdeling *",
        placeholder="Bijvoorbeeld: Division 9"
    )

    email = st.text_input(
        "E-mailadres *",
        placeholder="naam@amsterdamumc.nl"
    )

    st.divider()

    st.subheader("Accountgegevens")

    gebruikersnaam = st.text_input(
        "Gebruikersnaam *",
        placeholder="Kies een gebruikersnaam"
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
    afdeling = afdeling.strip()
    email = email.strip()
    gebruikersnaam = gebruikersnaam.strip()

    # --------------------------------------------------------
    # VERPLICHTE VELDEN
    # --------------------------------------------------------

    if not naam:
        fouten.append(
            "Vul je volledige naam in."
        )

    if not afdeling:
        fouten.append(
            "Vul je afdeling in."
        )

    if not email:
        fouten.append(
            "Vul je e-mailadres in."
        )

    if not gebruikersnaam:
        fouten.append(
            "Kies een gebruikersnaam."
        )

    if not wachtwoord:
        fouten.append(
            "Vul een wachtwoord in."
        )

    # --------------------------------------------------------
    # EMAIL EENVOUDIG CONTROLEREN
    # --------------------------------------------------------

    if email and (
        "@" not in email
        or "." not in email.split("@")[-1]
    ):
        fouten.append(
            "Vul een geldig e-mailadres in."
        )

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

    if (
        gebruikersnaam
        and gebruikersnaam_bestaat(
            gebruikersnaam
        )
    ):
        fouten.append(
            "Deze gebruikersnaam bestaat al."
        )

    # --------------------------------------------------------
    # FOUTEN TONEN
    # --------------------------------------------------------

    if fouten:

        for fout in fouten:
            st.error(fout)

    else:

        gelukt, resultaat = registreer_onderzoeker(
            naam=naam,
            gebruikersnaam=gebruikersnaam,
            wachtwoord=wachtwoord,
            afdeling=afdeling,
            email=email
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