import streamlit as st

st.set_page_config(
    page_title="Mijn profiel - Spider",
    layout="wide"
)

import pandas as pd
import sqlite3
import os
from datetime import date
import time
from sidebar import toon_sidebar
from pubmed_sync import synchroniseer_onderzoeker
from document_verwerking import (
    verwerk_document,
    importeer_publicatiebestand
)
from embeddings import (
    maak_embeddings_voor_nieuwe_publicaties
)

from keywords_to_expertise import (
    werk_expertise_bij
)




db_path = os.path.join(os.path.dirname(__file__), "..", "spider.db")
conn = sqlite3.connect(db_path)


# Login check
if "ingelogd" not in st.session_state or not st.session_state.ingelogd:
    st.warning("Je moet eerst inloggen!")
    st.switch_page("app.py")
    st.stop()

# Styling
from styling import apply_styling
apply_styling("profiel")

# Centrale sidebar
toon_sidebar()


# ============================================================
# INGELOGDE ONDERZOEKER OPHALEN VIA PERSON_ID
# ============================================================

rol = st.session_state.get("rol", "")
persoon_id = st.session_state.get("person_id")

if persoon_id is None:
    st.error(
        "Er is geen onderzoekersprofiel aan dit account gekoppeld."
    )
    st.stop()


cursor = conn.cursor()

# ============================================================
# TABEL VOOR PERSOONLIJKE BESTANDEN
# ============================================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS onderzoeker_bestanden (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        bestandsnaam TEXT NOT NULL,
        bestandspad TEXT NOT NULL,
        bestandstype TEXT,
        toegevoegd_op TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (person_id) REFERENCES persons(id)
    )
""")

conn.commit()

# ============================================================
# PUBMED AUTEURSNAMEN
# ============================================================

cursor.execute("""
    CREATE TABLE IF NOT EXISTS person_author_aliases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER NOT NULL,
        author_name TEXT NOT NULL,
        FOREIGN KEY (person_id) REFERENCES persons(id)
    )
""")

conn.commit()
# ============================================================
# PERSOONSGEGEVENS
# ============================================================

cursor.execute(
    """
    SELECT
        id,
        name,
        department
    FROM persons
    WHERE id = ?
    """,
    (persoon_id,)
)

persoon = cursor.fetchone()


if persoon is None:
    st.error(
        "Het gekoppelde onderzoekersprofiel bestaat niet."
    )
    st.stop()


gebruikersnaam = persoon[1]
afdeling = persoon[2] or ""


# ============================================================
# PROFIELGEGEVENS
# ============================================================

cursor.execute(
    """
    SELECT *
    FROM profiel_data
    WHERE person_id = ?
    """,
    (persoon_id,)
)

profiel = cursor.fetchone()


# ============================================================
# PROFIEL AUTOMATISCH AANMAKEN ALS HET NOG NIET BESTAAT
# ============================================================

if profiel is None:

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
            persoon_id,
            "",
            "",
            "",
            "",
            "",
            ""
        )
    )

    conn.commit()

    cursor.execute(
        """
        SELECT *
        FROM profiel_data
        WHERE person_id = ?
        """,
        (persoon_id,)
    )

    profiel = cursor.fetchone()





# ============================================================
# PAGINA INHOUD - ÉÉN GROOT "PAPIER"
# ============================================================

bio_tekst = (
    profiel[3]
    if profiel and profiel[3]
    else "Geen bio beschikbaar."
)

email_tekst = (
    profiel[2]
    if profiel and profiel[2]
    else "Geen email beschikbaar."
)

initialen = "".join(
    [
        naam[0]
        for naam in gebruikersnaam.split()
        if naam
    ]
)[:2].upper()


with st.container(border=True):

    # ========================================================
    # PROFIEL HEADER
    # ========================================================

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(
            '<div class="spider-paper-label">MIJN PROFIEL</div>',
            unsafe_allow_html=True
        )

        st.title(f"👤 {gebruikersnaam}")
        st.subheader(rol.capitalize())
        st.write(bio_tekst)

    with col2:
        st.markdown(
            f"""<div style="width:160px;height:160px;border-radius:50%;background-color:#003741;display:flex;align-items:center;justify-content:center;margin:10px auto;border:5px solid #FFFFFF;box-shadow:0 4px 14px rgba(0,55,65,0.12);">
            <span style="color:white;font-size:52px;font-weight:700;">{initialen}</span>
            </div>""",
            unsafe_allow_html=True
        )

    st.divider()

    # ========================================================
    # CONTACT
    # ========================================================

    st.subheader("📧 Contact")
    st.write(f"📧 {email_tekst}")

    with st.expander("Klik om aan te passen"):

        nieuwe_naam = st.text_input(
            "Naam",
            value=gebruikersnaam
        )

        nieuw_email = st.text_input(
            "Email",
            value=(
                email_tekst
                if email_tekst != "Geen email beschikbaar."
                else ""
            )
        )

        nieuwe_bio = st.text_area(
            "Bio",
            value=(
                ""
                if bio_tekst == "Geen bio beschikbaar."
                else bio_tekst
            )
        )

        if st.button(
            "💾 Opslaan",
            type="primary",
            key="profiel_opslaan"
        ):

            nieuwe_naam = nieuwe_naam.strip()
            nieuw_email = nieuw_email.strip()
            nieuwe_bio = nieuwe_bio.strip()

            try:

                # Naam wijzigen in persons
                cursor.execute(
                    """
                    UPDATE persons
                    SET name = ?
                    WHERE id = ?
                    """,
                    (
                        nieuwe_naam,
                        persoon_id
                    )
                )

                # Naam ook wijzigen in gebruikers
                cursor.execute(
                    """
                    UPDATE gebruikers
                    SET naam = ?
                    WHERE person_id = ?
                    """,
                    (
                        nieuwe_naam,
                        persoon_id
                    )
                )

                # Profielgegevens wijzigen
                cursor.execute(
                    """
                    UPDATE profiel_data
                    SET
                        email = ?,
                        bio = ?
                    WHERE person_id = ?
                    """,
                    (
                        nieuw_email,
                        nieuwe_bio,
                        persoon_id
                    )
                )

                conn.commit()


                st.success(
                    "✅ Profiel opgeslagen!"
                )

                st.rerun()

            except Exception as e:

                conn.rollback()

                st.error(
                    "Het profiel kon niet worden opgeslagen."
                )

                st.caption(
                    f"Technische melding: {e}"
                )

    
    # ============================================================
    # EXPERTISE
    # ============================================================

    st.divider()

    st.subheader("🔬 Expertise")

    st.caption(
        "Onderwerpen die automatisch uit je publicaties zijn gekoppeld."
    )

    if persoon_id is None:

        st.info(
            "Geen gekoppeld onderzoekersprofiel gevonden."
        )

    else:

        expertise_df = pd.read_sql(
            """
            SELECT DISTINCT
                e.id,
                e.label
            FROM expertise e
            INNER JOIN persons_expertise pe
                ON pe.expertise_id = e.id
            WHERE pe.person_id = ?
            ORDER BY e.label
            """,
            conn,
            params=(persoon_id,)
        )

        if expertise_df.empty:

            st.info(
                "Er is nog geen expertise gekoppeld aan je profiel."
            )

        else:

            for start in range(
                0,
                len(expertise_df),
                3
            ):

                rij = expertise_df.iloc[
                    start:start + 3
                ]

                kolommen = st.columns(3)

                for kolom, (_, exp) in zip(
                    kolommen,
                    rij.iterrows()
                ):

                    with kolom:

                        if st.button(
                            f"🔬 {exp['label']}",
                            key=f"eigen_exp_{exp['id']}",
                            use_container_width=True
                        ):

                            st.session_state[
                                "geselecteerde_expertise_id"
                            ] = int(
                                exp["id"]
                            )

                            st.switch_page(
                                "pages/expertise.py"
                            )
    # ============================================================
    # PUBMED AUTEURSNAMEN
    # ============================================================

    st.divider()

    st.subheader("📚 Mijn PubMed-auteursnamen")

    st.caption(
        "Voeg hier de namen toe waaronder je in PubMed-publicaties voorkomt. "
        "Spider gebruikt deze namen om publicaties aan jouw profiel te koppelen."
    )

    auteur_aliases = pd.read_sql(
        """
        SELECT *
        FROM person_author_aliases
        WHERE person_id = ?
        ORDER BY author_name
        """,
        conn,
        params=(persoon_id,)
    )

    if auteur_aliases.empty:

        st.info(
            "Je hebt nog geen PubMed-auteursnamen toegevoegd."
        )

    else:

        for _, alias in auteur_aliases.iterrows():

            col_naam, col_verwijder = st.columns(
                [5, 1]
            )

            with col_naam:

                st.write(
                    f"👤 {alias['author_name']}"
                )

            with col_verwijder:

                if st.button(
                    "🗑️",
                    key=f"verwijder_author_alias_{alias['id']}"
                ):

                    cursor.execute(
                        """
                        DELETE FROM person_author_aliases
                        WHERE id = ?
                        AND person_id = ?
                        """,
                        (
                            int(alias["id"]),
                            persoon_id
                        )
                    )

                    conn.commit()

                    st.rerun()


    with st.expander(
        "➕ PubMed-auteursnaam toevoegen"
    ):

        nieuwe_author_alias = st.text_input(
            "Auteursnaam",
            placeholder="Bijvoorbeeld: Anim C",
            key="nieuwe_author_alias"
        )

        st.caption(
            "Voor Cecilia Anim kunnen PubMed-auteursnamen "
            "bijvoorbeeld zijn: Anim C, C Anim of Cecilia Anim."
        )

        if st.button(
            "💾 Auteursnaam toevoegen",
            type="primary",
            key="author_alias_opslaan"
        ):

            nieuwe_author_alias = (
                nieuwe_author_alias.strip()
            )

            if not nieuwe_author_alias:

                st.warning(
                    "Vul eerst een auteursnaam in."
                )

            else:

                cursor.execute(
                    """
                    SELECT id
                    FROM person_author_aliases
                    WHERE person_id = ?
                    AND LOWER(author_name) = LOWER(?)
                    """,
                    (
                        persoon_id,
                        nieuwe_author_alias
                    )
                )

                bestaand_alias = (
                    cursor.fetchone()
                )

                if bestaand_alias:

                    st.info(
                        "Deze auteursnaam staat al bij je profiel."
                    )

                else:

                    cursor.execute(
                        """
                        INSERT INTO person_author_aliases (
                            person_id,
                            author_name
                        )
                        VALUES (?, ?)
                        """,
                        (
                            persoon_id,
                            nieuwe_author_alias
                        )
                    )

                    conn.commit()

                    st.success(
                        "✅ PubMed-auteursnaam toegevoegd."
                    )

                    st.rerun()

        # ============================================================
    # PUBMED SYNCHRONISEREN
    # ============================================================

    st.markdown("#### 🔄 Publicaties synchroniseren")

    st.caption(
        "Spider kan je publicaties rechtstreeks vanuit PubMed "
        "ophalen op basis van je PubMed-auteursnamen."
    )

    if auteur_aliases.empty:

        st.info(
            "Voeg eerst minimaal één PubMed-auteursnaam toe "
            "om publicaties te kunnen synchroniseren."
        )

    else:

        if st.button(
            "🔄 Synchroniseren met PubMed",
            type="primary",
            key="pubmed_sync"
        ):

            try:

                with st.spinner(
                    "Spider zoekt je publicaties in PubMed..."
                ):

                    sync_resultaat = (
                        synchroniseer_onderzoeker(
                            persoon_id,
                            conn
                        )
                    )

                gevonden = sync_resultaat.get(
                    "gevonden",
                    0
                )

                toegevoegd = sync_resultaat.get(
                    "toegevoegd",
                    0
                )

                overgeslagen = sync_resultaat.get(
                    "overgeslagen",
                    0
                )

                st.success(
                    f"PubMed-synchronisatie voltooid. "
                    f"{gevonden} publicaties gevonden, "
                    f"{toegevoegd} nieuw toegevoegd."
                )

                if overgeslagen > 0:
                    st.caption(
                        f"{overgeslagen} gevonden publicaties "
                        "stonden al in Spider."
                    )

            except Exception as fout:

                st.error(
                    "Het synchroniseren met PubMed is niet gelukt."
                )

                st.exception(fout)                


    st.divider()
    st.subheader("📁 Mijn bestanden")
    st.caption(
        "Upload publicaties en onderzoeksdocumenten naar je profiel."
    )

    uploaded_file = st.file_uploader(
        "Kies een bestand",
        type=["pdf", "csv", "docx", "txt"],
        key="profiel_bestand_upload"
    )

    if uploaded_file is not None:

        if st.button(
            "📤 Bestand opslaan",
            type="primary",
            key="bestand_opslaan"
        ):

            try:
                # ====================================================
                # MAP VAN DEZE ONDERZOEKER
                # ====================================================

                upload_map = os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    "uploads",
                    str(persoon_id)
                )

                os.makedirs(
                    upload_map,
                    exist_ok=True
                )

                # ====================================================
                # BESTANDSNAAM EN PAD
                # ====================================================

                veilige_bestandsnaam = os.path.basename(
                    uploaded_file.name
                )

                bestandspad = os.path.join(
                    upload_map,
                    veilige_bestandsnaam
                )

                # ====================================================
                # BESTAND OPSLAAN
                # ====================================================

                with open(bestandspad, "wb") as bestand:
                    bestand.write(
                        uploaded_file.getbuffer()
                    )

                # ====================================================
                # BESTAND OPSLAAN IN DATABASE
                # ====================================================

                cursor.execute(
                    """
                    SELECT id
                    FROM onderzoeker_bestanden
                    WHERE person_id = ?
                    AND bestandsnaam = ?
                    """,
                    (
                        persoon_id,
                        veilige_bestandsnaam
                    )
                )

                bestaand_bestand = cursor.fetchone()

                if bestaand_bestand:

                    cursor.execute(
                        """
                        UPDATE onderzoeker_bestanden
                        SET
                            bestandspad = ?,
                            bestandstype = ?,
                            toegevoegd_op = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            bestandspad,
                            uploaded_file.type,
                            bestaand_bestand[0]
                        )
                    )

                else:

                    cursor.execute(
                        """
                        INSERT INTO onderzoeker_bestanden (
                            person_id,
                            bestandsnaam,
                            bestandspad,
                            bestandstype
                        )
                        VALUES (?, ?, ?, ?)
                        """,
                        (
                            persoon_id,
                            veilige_bestandsnaam,
                            bestandspad,
                            uploaded_file.type
                        )
                    )

                conn.commit()

                st.success(
                    f"✅ {veilige_bestandsnaam} is permanent opgeslagen!"
                )

                # ====================================================
                # DOCUMENT CONTROLEREN / UITLEZEN
                # ====================================================

                resultaat = verwerk_document(bestandspad)

                # ----------------------------------------------------
                # PDF
                # ----------------------------------------------------

                if resultaat["type"] == "pdf":

                    tekst = resultaat["inhoud"]

                    if tekst:
                        st.success(
                            f"📄 Spider heeft {len(tekst)} tekens "
                            "uit de PDF gelezen."
                        )
                    else:
                        st.warning(
                            "De PDF is opgeslagen, maar Spider kon "
                            "geen tekst uitlezen."
                        )

                # ----------------------------------------------------
                # CSV / TXT / PUBMED
                # ----------------------------------------------------

                elif bestandspad.lower().endswith(
                    (".csv", ".txt")
                ):

                    import_resultaat = importeer_publicatiebestand(
                        bestandspad,
                        conn
                    )

                    if import_resultaat["formaat"] == "onbekend":

                        st.info(
                            "Het bestand is opgeslagen, maar Spider "
                            "herkent het niet als een ondersteund "
                            "publicatiebestand."
                        )

                    else:

                        st.success(
                            f"🔎 Spider herkende dit bestand als "
                            f"{import_resultaat['formaat']}."
                        )

                        st.write(
                            f"**Gevonden publicaties:** "
                            f"{import_resultaat['gevonden']}"
                        )

                        st.write(
                            f"**Nieuwe publicaties toegevoegd:** "
                            f"{import_resultaat['toegevoegd']}"
                        )

                        if import_resultaat["toegevoegd"] > 0:

                            with st.spinner(
                                "Spider verwerkt de nieuwe publicaties..."
                            ):
                                maak_embeddings_voor_nieuwe_publicaties(
                                    conn
                                )

                        if import_resultaat["overgeslagen"] > 0:
                            with st.spinner(
                                    "Spider werkt expertise bij..."
                                ):

                                    expertise_resultaat = (
                                        werk_expertise_bij(
                                            conn
                                        )
                                    )

                            st.success(
                                    f"🔬 "
                                    f"{expertise_resultaat['nieuwe_koppelingen']} "
                                    "nieuwe expertise-koppelingen toegevoegd."
                                )

                            st.info(
                                f"ℹ️ "
                                f"{import_resultaat['overgeslagen']} "
                                "publicaties zijn overgeslagen omdat "
                                "ze al bestonden of geen geldig PMID hadden."
                            )
                    

                # ----------------------------------------------------
                # OVERIGE BESTANDEN
                # ----------------------------------------------------

                else:

                    st.info(
                        "Het bestand is opgeslagen. Automatische "
                        "publicatie-import ondersteunen we op dit moment "
                        "voor CSV, TXT en PubMed/MEDLINE-bestanden."
                    )

            except Exception as e:

                conn.rollback()

                st.error(
                    "Het bestand kon niet worden opgeslagen."
                )

                st.caption(
                    f"Technische melding: {e}"
                )


    # ============================================================
    # OPGESLAGEN BESTANDEN TONEN
    # ============================================================

    mijn_bestanden = pd.read_sql(
        """
        SELECT *
        FROM onderzoeker_bestanden
        WHERE person_id = ?
        ORDER BY toegevoegd_op DESC
        """,
        conn,
        params=(persoon_id,)
    )

    if mijn_bestanden.empty:

        st.info(
            "Je hebt nog geen bestanden toegevoegd."
        )

    else:

        st.markdown("#### Opgeslagen bestanden")

        for _, bestand in mijn_bestanden.iterrows():

            col_bestand, col_download, col_verwijder = st.columns(
                [4, 1, 1]
            )

            with col_bestand:

                st.write(
                    f"📄 **{bestand['bestandsnaam']}**"
                )

                st.caption(
                    f"Toegevoegd: {bestand['toegevoegd_op']}"
                )

            with col_download:

                bestandspad = bestand["bestandspad"]

                if os.path.exists(bestandspad):

                    with open(
                        bestandspad,
                        "rb"
                    ) as opgeslagen_bestand:

                        bestand_bytes = opgeslagen_bestand.read()

                    st.download_button(
                        "⬇️",
                        data=bestand_bytes,
                        file_name=bestand["bestandsnaam"],
                        mime=(
                            bestand["bestandstype"]
                            or "application/octet-stream"
                        ),
                        key=f"download_bestand_{bestand['id']}"
                    )

                else:

                    st.caption("Bestand ontbreekt")

            with col_verwijder:

                if st.button(
                    "🗑️",
                    key=f"verwijder_bestand_{bestand['id']}"
                ):

                    try:

                        if os.path.exists(
                            bestand["bestandspad"]
                        ):

                            os.remove(
                                bestand["bestandspad"]
                            )

                        cursor.execute(
                            """
                            DELETE FROM onderzoeker_bestanden
                            WHERE id = ?
                            AND person_id = ?
                            """,
                            (
                                int(bestand["id"]),
                                persoon_id
                            )
                        )

                        conn.commit()

                        st.success(
                            "✅ Bestand verwijderd."
                        )

                        st.rerun()

                    except Exception as e:

                        conn.rollback()

                        st.error(
                            "Het bestand kon niet worden verwijderd."
                        )

                        st.caption(
                            f"Technische melding: {e}"
                        )


    # ============================================================
    # EXTERNE LINKS
    # ============================================================

    st.divider()

    opgeslagen_links = (
        profiel[6]
        if profiel
        and len(profiel) > 6
        and profiel[6]
        else ""
    )

    links_dict = {}

    if opgeslagen_links:

        import json

        try:

            links_dict = json.loads(
                opgeslagen_links
            )

        except Exception:

            links_dict = {}


    if links_dict:

        st.subheader("🔗 Mijn links")

        st.caption(
            "Opgeslagen externe bronnen die bij jouw profiel horen."
        )

        for key, emoji, label in [
            ("google", "📄", "Google Docs"),
            ("teams", "📹", "Teams Recording"),
            ("podcast", "🎙️", "Podcast"),
            ("opname", "📺", "Seminar opname"),
        ]:

            if links_dict.get(key):

                col1, col2 = st.columns(
                    [4, 1]
                )

                with col1:

                    st.markdown(
                        f"{emoji} [{label}]"
                        f"({links_dict[key]})"
                    )

                with col2:

                    if st.button(
                        "🗑️",
                        key=f"verwijder_{key}"
                    ):

                        links_dict[key] = ""

                        cursor.execute(
                            """
                            UPDATE profiel_data
                            SET links = ?
                            WHERE person_id = ?
                            """,
                            (
                                __import__(
                                    "json"
                                ).dumps(
                                    links_dict
                                ),
                                persoon_id
                            )
                        )

                        conn.commit()

                        st.rerun()


    # ============================================================
    # EXTERNE LINKS TOEVOEGEN
    # ============================================================

    st.divider()

    st.subheader(
        "🔗 Externe links toevoegen"
    )

    st.caption(
        "Beheer hier links naar documenten, "
        "opnames, podcasts en seminars."
    )

    with st.expander(
        "➕ Externe links beheren"
    ):

        google_link = st.text_input(
            "📄 Google Docs link",
            value=links_dict.get(
                "google",
                ""
            ),
            key="google_link"
        )

        teams_link = st.text_input(
            "📹 Teams Recording link",
            value=links_dict.get(
                "teams",
                ""
            ),
            key="teams_link"
        )

        podcast_link = st.text_input(
            "🎙️ Podcast link",
            value=links_dict.get(
                "podcast",
                ""
            ),
            key="podcast_link"
        )

        opname_link = st.text_input(
            "📺 Seminar opname link",
            value=links_dict.get(
                "opname",
                ""
            ),
            key="opname_link"
        )

        if st.button(
            "💾 Links opslaan",
            key="save_links",
            type="primary"
        ):

            import json

            nieuwe_links = {
                "google": google_link,
                "teams": teams_link,
                "podcast": podcast_link,
                "opname": opname_link,
            }

            cursor.execute(
                """
                UPDATE profiel_data
                SET links = ?
                WHERE person_id = ?
                """,
                (
                    json.dumps(
                        nieuwe_links
                    ),
                    persoon_id
                )
            )

            conn.commit()

            st.success(
                "✅ Links opgeslagen!"
            )

            st.rerun()


    # ============================================================
    # LOPEND PROJECT STARTEN
    # ============================================================

    st.divider()

    st.subheader(
        "🔬 Lopend project starten"
    )

    st.caption(
        "Start een nieuw onderzoek en voeg later deelnemers toe."
    )

    with st.expander(
        "➕ Nieuw project starten"
    ):

        project_naam = st.text_input(
            "Projectnaam",
            key="nieuw_project_naam"
        )

        project_beschrijving = st.text_area(
            "Beschrijving",
            key="nieuw_project_beschrijving"
        )

        project_begindatum = st.date_input(
            "Begindatum",
            key="nieuw_project_begindatum"
        )

        project_einddatum = st.date_input(
            "Einddatum",
            key="nieuw_project_einddatum"
        )

        if st.button(
            "💾 Project starten",
            key="start_project",
            type="primary"
        ):

            if project_naam:

                cursor.execute(
                    """
                    INSERT INTO lopende_projecten (
                        naam,
                        beschrijving,
                        leider_id,
                        datum,
                        einddatum
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        project_naam,
                        project_beschrijving,
                        persoon_id,
                        str(
                            project_begindatum
                        ),
                        str(
                            project_einddatum
                        )
                    )
                )

                conn.commit()

                st.success(
                    f"✅ Project "
                    f"'{project_naam}' gestart!"
                )

                time.sleep(1.5)

                st.rerun()

            else:

                st.error(
                    "Vul een projectnaam in!"
                )


    # ============================================================
    # MIJN LOPENDE PROJECTEN
    # ============================================================

    st.divider()

    st.subheader(
        "📋 Mijn lopende projecten"
    )

    st.caption(
        "Projecten waarvan jij de leider bent."
    )

    if persoon_id:

        mijn_projecten = pd.read_sql(
            """
            SELECT *
            FROM lopende_projecten
            WHERE leider_id = ?
            """,
            conn,
            params=(persoon_id,)
        )

    else:

        mijn_projecten = pd.DataFrame()


    if mijn_projecten.empty:

        st.info(
            "Je hebt nog geen lopende projecten."
        )

    else:

        for _, project in mijn_projecten.iterrows():

            beschrijving = (
                project["beschrijving"]
                or ""
            )

            st.write(
                f"🔬 **{project['naam']}** — "
                f"{beschrijving[:50]}..."
            )

            col1, col2, col3 = st.columns(
                [2, 1, 1]
            )

            with col1:

                if st.button(
                    "🔗 Bekijk project",
                    key=f"bekijk_{project['id']}"
                ):

                    st.session_state.geselecteerd_lopend_project = int(
                        project["id"]
                    )

                    st.switch_page(
                        "pages/lopend_project.py"
                    )

            with col2:

                if st.button(
                    "✏️ Aanpassen",
                    key=f"aanpas_{project['id']}"
                ):

                    st.session_state.aanpassen_project_id = (
                        project["id"]
                    )

            with col3:

                if st.button(
                    "🗑️ Verwijderen",
                    key=f"verwijder_{project['id']}"
                ):

                    cursor.execute(
                        """
                        DELETE FROM project_deelnemers
                        WHERE project_id = ?
                        """,
                        (
                            project["id"],
                        )
                    )

                    cursor.execute(
                        """
                        DELETE FROM lopende_projecten
                        WHERE id = ?
                        """,
                        (
                            project["id"],
                        )
                    )

                    conn.commit()

                    st.success(
                        "✅ Project verwijderd!"
                    )

                    st.rerun()


    # ============================================================
    # PROJECTEN WAAR IK AAN DEELNEEM
    # ============================================================

    st.divider()

    st.subheader(
        "📋 Projecten waar ik aan deelneem"
    )

    st.caption(
        "Onderzoeken waarin je als deelnemer bent gekoppeld."
    )

    if persoon_id:

        deelname_projecten = pd.read_sql(
            """
            SELECT lp.*
            FROM lopende_projecten lp
            JOIN project_deelnemers pd
                ON lp.id = pd.project_id
            WHERE pd.persoon_id = ?
            AND lp.leider_id != ?
            """,
            conn,
            params=(
                persoon_id,
                persoon_id
            )
        )

        if deelname_projecten.empty:

            st.info(
                "Je neemt nog niet deel aan projecten van anderen."
            )

        else:

            for _, project in deelname_projecten.iterrows():

                if st.button(
                    f"🔬 {project['naam']}",
                    key=f"deelname_{project['id']}"
                ):

                    st.session_state.geselecteerd_lopend_project = int(
                        project["id"]
                    )

                    st.switch_page(
                        "pages/lopend_project.py"
                    )

    else:

        st.info(
            "Log in als onderzoeker om je deelname te zien."
        )


    # ============================================================
    # PROJECT AANPASSEN
    # ============================================================

    if (
        "aanpassen_project_id" in st.session_state
        and st.session_state.aanpassen_project_id
    ):

        project_id = (
            st.session_state.aanpassen_project_id
        )

        huidig_df = pd.read_sql(
            """
            SELECT *
            FROM lopende_projecten
            WHERE id = ?
            """,
            conn,
            params=(
                project_id,
            )
        )

        if not huidig_df.empty:

            huidig = huidig_df.iloc[0]

            st.divider()

            st.subheader(
                "✏️ Project aanpassen"
            )

            nieuwe_naam = st.text_input(
                "Naam",
                value=huidig["naam"],
                key="aanpas_naam"
            )

            nieuwe_beschrijving = st.text_area(
                "Beschrijving",
                value=huidig["beschrijving"],
                key="aanpas_beschrijving"
            )

            if st.button(
                "💾 Opslaan",
                key="opslaan_project",
                type="primary"
            ):

                cursor.execute(
                    """
                    UPDATE lopende_projecten
                    SET
                        naam = ?,
                        beschrijving = ?
                    WHERE id = ?
                    """,
                    (
                        nieuwe_naam,
                        nieuwe_beschrijving,
                        project_id
                    )
                )

                conn.commit()

                st.session_state.aanpassen_project_id = None

                st.success(
                    "✅ Project bijgewerkt!"
                )

                st.rerun()


    # ============================================================
    # TERUG
    # ============================================================

    st.divider()

    if st.button(
        "← Terug naar zoeken",
        key="terug_onder"
    ):

        st.switch_page(
            "app.py"
        )


# # ============================================================
# # OPGESLAGEN BESTANDEN TONEN
# # ============================================================

# mijn_bestanden = pd.read_sql(
#     """
#     SELECT *
#     FROM onderzoeker_bestanden
#     WHERE person_id = ?
#     ORDER BY toegevoegd_op DESC
#     """,
#     conn,
#     params=(persoon_id,)
# )

# if mijn_bestanden.empty:

#     st.info(
#         "Je hebt nog geen bestanden toegevoegd."
#     )

# else:

#     st.markdown("#### Opgeslagen bestanden")

# for _, bestand in mijn_bestanden.iterrows():

#     col_bestand, col_download, col_verwijder = st.columns(
#         [4, 1, 1]
#     )

#     with col_bestand:

#         st.write(
#             f"📄 **{bestand['bestandsnaam']}**"
#         )

#         st.caption(
#             f"Toegevoegd: {bestand['toegevoegd_op']}"
#         )

#     with col_download:

#         bestandspad = bestand["bestandspad"]

#         if os.path.exists(bestandspad):

#             with open(bestandspad, "rb") as opgeslagen_bestand:

#                 bestand_bytes = opgeslagen_bestand.read()

#             st.download_button(
#                 "⬇️",
#                 data=bestand_bytes,
#                 file_name=bestand["bestandsnaam"],
#                 mime=bestand["bestandstype"] or "application/octet-stream",
#                 key=f"download_bestand_{bestand['id']}"
#             )

#         else:

#             st.caption("Bestand ontbreekt")

#     with col_verwijder:

#         if st.button(
#             "🗑️",
#             key=f"verwijder_bestand_{bestand['id']}"
#         ):

#                 try:
#                     # Bestand van schijf verwijderen
#                     if os.path.exists(
#                         bestand["bestandspad"]
#                     ):
#                         os.remove(
#                             bestand["bestandspad"]
#                         )

#                     # Database-record verwijderen
#                     cursor.execute(
#                         """
#                         DELETE FROM onderzoeker_bestanden
#                         WHERE id = ?
#                         AND person_id = ?
#                         """,
#                         (
#                             int(bestand["id"]),
#                             persoon_id
#                         )
#                     )

#                     conn.commit()

#                     st.success(
#                         "✅ Bestand verwijderd."
#                     )

#                     st.rerun()

#                 except Exception as e:

#                     conn.rollback()

#                     st.error(
#                         "Het bestand kon niet worden verwijderd."
#                     )

#                     st.caption(
#                         f"Technische melding: {e}"
#                     )

#     # Laad opgeslagen links
#     opgeslagen_links = profiel[6] if profiel and len(profiel) > 6 and profiel[6] else ""
#     links_dict = {}
#     if opgeslagen_links:
#         import json
#         try:
#             links_dict = json.loads(opgeslagen_links)
#         except:
#             links_dict = {}

#     # Toon opgeslagen links
#     if links_dict:
#         st.divider()
#         st.subheader("🔗 Mijn links")
#         st.caption("Opgeslagen externe bronnen die bij jouw profiel horen.")
    
#         for key, emoji, label in [
#             ("google", "📄", "Google Docs"),
#             ("teams", "📹", "Teams Recording"),
#             ("podcast", "🎙️", "Podcast"),
#             ("opname", "📺", "Seminar opname"),
#         ]:
#             if links_dict.get(key):
#                 col1, col2 = st.columns([4, 1])
#                 with col1:
#                     st.markdown(f"{emoji} [{label}]({links_dict[key]})")
#                 with col2:
#                     if st.button("🗑️", key=f"verwijder_{key}"):
#                         links_dict[key] = ""
#                         cursor.execute(
#                             """
#                             UPDATE profiel_data
#                             SET links = ?
#                             WHERE person_id = ?
#                             """,
#                             (
#                                 __import__("json").dumps(links_dict),
#                                 persoon_id
#                             )
#                         )
#                         conn.commit()
#                         st.rerun()

#     # Links invoeren
#     st.divider()
#     st.subheader("🔗 Externe links toevoegen")
#     st.caption("Beheer hier links naar documenten, opnames, podcasts en seminars.")

#     with st.expander("➕ Externe links beheren"):
#         google_link = st.text_input("📄 Google Docs link", value=links_dict.get("google", ""), key="google_link")
#         teams_link = st.text_input("📹 Teams Recording link", value=links_dict.get("teams", ""), key="teams_link")
#         podcast_link = st.text_input("🎙️ Podcast link", value=links_dict.get("podcast", ""), key="podcast_link")
#         opname_link = st.text_input("📺 Seminar opname link", value=links_dict.get("opname", ""), key="opname_link")

#         if st.button("💾 Links opslaan", key="save_links", type="primary"):
#             import json
#             nieuwe_links = {
#                 "google": google_link,
#                 "teams": teams_link,
#                 "podcast": podcast_link,
#                 "opname": opname_link,
#             }
#             cursor.execute(
#                 """
#                 UPDATE profiel_data
#                 SET links = ?
#                 WHERE person_id = ?
#                 """,
#                 (
#                     json.dumps(nieuwe_links),
#                     persoon_id
#                 )
#             )
#             conn.commit()
#             st.success("✅ Links opgeslagen!")
#             st.rerun()

#     st.divider()
#     st.subheader("🔬 Lopend project starten")
#     st.caption("Start een nieuw onderzoek en voeg later deelnemers toe.")

#     with st.expander("➕ Nieuw project starten"):
#         project_naam = st.text_input("Projectnaam", key="nieuw_project_naam")
#         project_beschrijving = st.text_area("Beschrijving", key="nieuw_project_beschrijving")
#         project_begindatum = st.date_input("Begindatum", key="nieuw_project_begindatum")
#         project_einddatum = st.date_input("Einddatum", key="nieuw_project_einddatum")


#         if st.button("💾 Project starten", key="start_project", type="primary"):
#             if project_naam:
#                 cursor = conn.cursor()
#                 cursor.execute("""
#                     INSERT INTO lopende_projecten (
#                         naam,
#                         beschrijving,
#                         leider_id,
#                         datum,
#                         einddatum
#                     )
#                     VALUES (?, ?, ?, ?, ?)
#                 """, (
#                     project_naam,
#                     project_beschrijving,
#                     persoon_id,
#                     str(project_begindatum),
#                     str(project_einddatum)
# ))

#                 conn.commit()
#                 st.success(f"✅ Project '{project_naam}' gestart!")
#                 time.sleep(1.5)
#                 st.rerun()
#             else:
#                 st.error("Vul een projectnaam in!")

#     # Toon eigen lopende projecten
#     st.divider()
#     st.subheader("📋 Mijn lopende projecten")
#     st.caption("Projecten waarvan jij de leider bent.")

#     mijn_projecten = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE leider_id = {persoon_id}", conn) if persoon_id else pd.DataFrame()

#     if mijn_projecten.empty:
#         st.info("Je hebt nog geen lopende projecten.")
#     else:
#         for _, project in mijn_projecten.iterrows():
#             st.write(f"🔬 **{project['naam']}** — {project['beschrijving'][:50]}...")

#             col1, col2, col3 = st.columns([2, 1, 1])
#             with col1:
#                 if st.button("🔗 Bekijk project", key=f"bekijk_{project['id']}"):
#                     st.session_state.geselecteerd_lopend_project = int(project["id"])
#                     st.switch_page("pages/lopend_project.py")
#             with col2:
#                 if st.button("✏️ Aanpassen", key=f"aanpas_{project['id']}"):
#                     st.session_state.aanpassen_project_id = project["id"]
#             with col3:
#                 if st.button("🗑️ Verwijderen", key=f"verwijder_{project['id']}"):
#                     cursor.execute("DELETE FROM lopende_projecten WHERE id = ?", (project["id"],))
#                     cursor.execute("DELETE FROM project_deelnemers WHERE project_id = ?", (project["id"],))
#                     conn.commit()
#                     st.success("✅ Project verwijderd!")
#                     st.rerun()

#                     # Projecten waar je deelnemer van bent
#     st.divider()
#     st.subheader("📋 Projecten waar ik aan deelneem")
#     st.caption("Onderzoeken waarin je als deelnemer bent gekoppeld.")

#     if persoon_id:
#         deelname_projecten = pd.read_sql(f"""
#             SELECT lp.* FROM lopende_projecten lp
#             JOIN project_deelnemers pd ON lp.id = pd.project_id
#             WHERE pd.persoon_id = {persoon_id}
#             AND lp.leider_id != {persoon_id}
#         """, conn)
    
#         if deelname_projecten.empty:
#             st.info("Je neemt nog niet deel aan projecten van anderen.")
#         else:
#             for _, project in deelname_projecten.iterrows():
#                 if st.button(f"🔬 {project['naam']}", key=f"deelname_{project['id']}"):
#                     st.session_state.geselecteerd_lopend_project = int(project["id"])
#                     st.switch_page("pages/lopend_project.py")
#     else:
#         st.info("Log in als onderzoeker om je deelname te zien.")

#     # Aanpassen formulier
#     if "aanpassen_project_id" in st.session_state and st.session_state.aanpassen_project_id:
#         project_id = st.session_state.aanpassen_project_id
#         huidig_df = pd.read_sql(f"SELECT * FROM lopende_projecten WHERE id = {project_id}", conn)
#         if not huidig_df.empty:
#             huidig = huidig_df.iloc[0]
#             st.divider()
#             st.subheader("✏️ Project aanpassen")
#             nieuwe_naam = st.text_input("Naam", value=huidig["naam"], key="aanpas_naam")
#             nieuwe_beschrijving = st.text_area("Beschrijving", value=huidig["beschrijving"], key="aanpas_beschrijving")
#             if st.button("💾 Opslaan", key="opslaan_project", type="primary"):
#                 cursor.execute("UPDATE lopende_projecten SET naam = ?, beschrijving = ? WHERE id = ?",
#                                (nieuwe_naam, nieuwe_beschrijving, project_id))
#                 conn.commit()
#                 st.session_state.aanpassen_project_id = None
#                 st.success("✅ Project bijgewerkt!")
#                 st.rerun()

#     st.divider()
#     if st.button("← Terug naar zoeken", key="terug_onder"):
#         st.switch_page("app.py")



