import streamlit as st

st.set_page_config(
    page_title="Lopend project - Spider",
    layout="wide"
)

import pandas as pd
import sqlite3
import os
from datetime import datetime

from sidebar import toon_sidebar
from styling import apply_styling


# ============================================================
# DATABASE
# ============================================================

db_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "spider.db"
)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS project_media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        titel TEXT NOT NULL,
        url TEXT NOT NULL,
        media_type TEXT,
        toegevoegd_door INTEGER,
        toegevoegd_op TEXT
    )
    """
)

conn.commit()

# ============================================================
# AUTHENTICATIE
# ============================================================

# if (
#     "ingelogd" not in st.session_state
#     or not st.session_state.ingelogd
# ):
#     st.warning("Je moet eerst inloggen!")
#     st.switch_page("app.py")
#     st.stop()


# ============================================================
# CENTRALE STYLING + SIDEBAR
# ============================================================

apply_styling("projecten")
toon_sidebar()


# ============================================================
# DATA
# ============================================================

personen = pd.read_sql("SELECT * FROM persons", conn)
projecten = pd.read_sql("SELECT * FROM lopende_projecten", conn)
deelnemers = pd.read_sql("SELECT * FROM project_deelnemers", conn)


# ============================================================
# PAGINA
# ============================================================

with st.container(border=True):

    st.markdown(
        '<div class="spider-paper-label">LOPEND PROJECT</div>',
        unsafe_allow_html=True
    )

    if (
        "geselecteerd_lopend_project" not in st.session_state
        or st.session_state.geselecteerd_lopend_project is None
    ):
        st.title("🔬 Lopend project")
        st.warning("Geen project geselecteerd.")

        if st.button(
            "← Terug naar zoeken",
            key=f"terug_naar_zoeken_{project_id}"
        ):
            st.switch_page("app.py")

    else:
        project_id = int(
            st.session_state.geselecteerd_lopend_project
        )

        project_selectie = projecten[
            projecten["id"] == project_id
        ]

        if project_selectie.empty:
            st.title("🔬 Lopend project")
            st.warning("Dit project kon niet worden gevonden.")

        else:
            project = project_selectie.iloc[0]

            leider_selectie = personen[
                personen["id"] == project["leider_id"]
            ]

            leider_naam = (
                leider_selectie.iloc[0]["name"]
                if not leider_selectie.empty
                else "Onbekend"
            )

            st.title(project["naam"])

            st.caption(
                "Lopend onderzoeksproject binnen Amsterdam UMC"
            )

            st.markdown("**Projectleider:**")

            if not leider_selectie.empty:
                leider_id = int(project["leider_id"])

                if st.button(
                    f"👤 {leider_naam}",
                    key=f"projectleider_{leider_id}"
                ):
                    st.session_state.geselecteerde_persoon = leider_id
                    st.switch_page("pages/onderzoeker.py")
            else:
                st.write("Onbekend")

            st.write(f"**Gestart:** {project['datum']}")

            einddatum = project.get("einddatum")

            if pd.notna(einddatum) and str(einddatum).strip():
                st.write(f"**Einddatum:** {einddatum}")

            st.write(project["beschrijving"])

            st.divider()

            # Ingelogde gebruiker ophalen
            gebruikersnaam = st.session_state.get(
                "gebruikersnaam",
                ""
            )

            cursor.execute(
                "SELECT id FROM persons WHERE name = ?",
                (gebruikersnaam,)
            )

            result = cursor.fetchone()
            eigen_id = result[0] if result else None

            # Deelnemers
            st.subheader("👥 Deelnemers")
            
            deelnemer_ids = deelnemers[
                deelnemers["project_id"] == project_id
            ]["persoon_id"].tolist()

            betrokken = personen[
                personen["id"].isin(deelnemer_ids)
            ]

            aantal_deelnemers = len(betrokken)

            with st.expander(
                f"👥 Deelnemers ({aantal_deelnemers})",
                expanded=False
            ):
                if betrokken.empty:
                    st.write("Nog geen deelnemers gekoppeld.")
                else:
                    for _, persoon in betrokken.iterrows():
                        st.write(f"👤 {persoon['name']}")

         
# ============================================================
# PROJECTBESTANDEN
# ============================================================

st.subheader("📎 Projectbestanden")

mag_bestanden_beheren = (
    eigen_id is not None
    and (
        eigen_id == project["leider_id"]
        or eigen_id in deelnemer_ids
    )
)

# Tabel aanmaken indien nodig
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS project_bestanden (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER NOT NULL,
        naam TEXT NOT NULL,
        bestandspad TEXT NOT NULL,
        uploader_id INTEGER
    )
    """
)

conn.commit()


# ------------------------------------------------------------
# Upload
# ------------------------------------------------------------

if mag_bestanden_beheren:

    upload = st.file_uploader(
        "Bestand toevoegen",
        type=[
            "pdf",
            "docx",
            "txt",
            "xlsx",
            "csv",
            "pptx",
            "png",
            "jpg",
            "jpeg",
            "mp3",
            "wav",
            "m4a",
            "mp4",
            "mov",
            "webm",
        ],
        key=f"project_bestand_{project_id}"
    )

    if upload is not None:

        if st.button(
            "💾 Bestand opslaan",
            key=f"opslaan_project_bestand_{project_id}",
            type="primary"
        ):

            project_map = os.path.join(
                os.path.dirname(
                    os.path.abspath(__file__)
                ),
                "..",
                "uploads",
                "projecten",
                str(project_id)
            )

            os.makedirs(
                project_map,
                exist_ok=True
            )

            bestandsnaam = os.path.basename(
                upload.name
            )

            bestandspad = os.path.join(
                project_map,
                bestandsnaam
            )

            basisnaam, extensie = os.path.splitext(
                bestandsnaam
            )

            teller = 1

            while os.path.exists(bestandspad):

                bestandspad = os.path.join(
                    project_map,
                    f"{basisnaam}_{teller}{extensie}"
                )

                teller += 1

            with open(
                bestandspad,
                "wb"
            ) as bestand:

                bestand.write(
                    upload.getbuffer()
                )

            cursor.execute(
                """
                INSERT INTO project_bestanden (
                    project_id,
                    naam,
                    bestandspad,
                    uploader_id
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    project_id,
                    os.path.basename(bestandspad),
                    bestandspad,
                    eigen_id,
                )
            )

            conn.commit()

            st.success(
                "✅ Bestand opgeslagen."
            )

            st.rerun()


# ------------------------------------------------------------
# Bestanden tonen
# ------------------------------------------------------------

project_bestanden = pd.read_sql(
    """
    SELECT *
    FROM project_bestanden
    WHERE project_id = ?
    ORDER BY id DESC
    """,
    conn,
    params=(project_id,)
)

if project_bestanden.empty:

    st.info(
        "Er zijn nog geen projectbestanden toegevoegd."
    )

else:

    for _, bestand in project_bestanden.iterrows():

        pad = bestand["bestandspad"]

        with st.container(border=True):

            st.markdown(
                f"📄 **{bestand['naam']}**"
            )

            if os.path.exists(pad):

                with open(pad, "rb") as bestand_data:

                    st.download_button(
                        "⬇️ Download",
                        data=bestand_data.read(),
                        file_name=bestand["naam"],
                        key=f"download_{bestand['id']}",
                        use_container_width=True
                    )

            else:

                st.warning(
                    "Bestand kon niet worden gevonden."
                )

            if (
                eigen_id is not None
                and eigen_id == project["leider_id"]
            ):

                if st.button(
                    "🗑️ Verwijderen",
                    key=f"verwijder_bestand_{bestand['id']}"
                ):

                    if os.path.exists(pad):
                        os.remove(pad)

                    cursor.execute(
                        """
                        DELETE FROM project_bestanden
                        WHERE id = ?
                        """,
                        (int(bestand["id"]),)
                    )

                    conn.commit()

                    st.rerun()

st.divider()

            # ============================================================
# AUDIO / VIDEO
# ============================================================

st.subheader("🎥 Audio & Video")

# Projectleider of deelnemer mag media toevoegen
mag_media_toevoegen = (
    eigen_id is not None
    and (
        eigen_id == project["leider_id"]
        or eigen_id in deelnemer_ids
    )
)

if mag_media_toevoegen:

    with st.expander(
        "➕ Recording of mediakoppeling toevoegen"
    ):

        media_titel = st.text_input(
            "Titel",
            placeholder="Bijvoorbeeld: Projectpresentatie",
            key=f"media_titel_{project_id}"
        )

        media_type = st.selectbox(
            "Type",
            [
                "Microsoft Teams",
                "YouTube",
                "Podcast",
                "Seminar",
                "Anders"
            ],
            key=f"media_type_{project_id}"
        )

        media_url = st.text_input(
            "Link",
            placeholder="https://...",
            key=f"media_url_{project_id}"
        )

        if st.button(
            "💾 Recording opslaan",
            key=f"media_opslaan_{project_id}",
            type="primary"
        ):

            titel_schoon = media_titel.strip()
            url_schoon = media_url.strip()

            if not titel_schoon:
                st.warning(
                    "Vul eerst een titel in."
                )

            elif not url_schoon:
                st.warning(
                    "Vul eerst een link in."
                )

            elif not (
                url_schoon.startswith("https://")
                or url_schoon.startswith("http://")
            ):
                st.warning(
                    "Vul een geldige http- of https-link in."
                )

            else:
                cursor.execute(
                    """
                    INSERT INTO project_media (
                        project_id,
                        titel,
                        url,
                        media_type,
                        toegevoegd_door,
                        toegevoegd_op
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        titel_schoon,
                        url_schoon,
                        media_type,
                        eigen_id,
                        datetime.now().isoformat(
                            timespec="seconds"
                        )
                    )
                )

                conn.commit()

                st.success(
                    "Recording opgeslagen."
                )

                st.rerun()


# ------------------------------------------------------------
# OPGESLAGEN RECORDINGS TONEN
# ------------------------------------------------------------

media_items = pd.read_sql(
    """
    SELECT *
    FROM project_media
    WHERE project_id = ?
    ORDER BY id DESC
    """,
    conn,
    params=(project_id,)
)

if media_items.empty:

    st.info(
        "Er zijn nog geen recordings of mediakoppelingen toegevoegd."
    )

else:

    for _, media in media_items.iterrows():

        with st.container(border=True):

            st.markdown(
                f"### 🎬 {media['titel']}"
            )

            if (
                pd.notna(media["media_type"])
                and str(media["media_type"]).strip()
            ):
                st.caption(
                    str(media["media_type"])
                )

            st.link_button(
                "▶️ Open recording",
                media["url"],
                use_container_width=True
            )

            # Alleen projectleider mag verwijderen
            if (
                eigen_id is not None
                and eigen_id == project["leider_id"]
            ):

                if st.button(
                    "🗑️ Recording verwijderen",
                    key=f"verwijder_media_{media['id']}"
                ):

                    cursor.execute(
                        """
                        DELETE FROM project_media
                        WHERE id = ?
                        """,
                        (int(media["id"]),)
                    )

                    conn.commit()

                    st.success(
                        "Recording verwijderd."
                    )

                    st.rerun()

            st.divider()

            # Rol van ingelogde gebruiker
            if eigen_id == project["leider_id"]:
                st.info("✅ Jij bent de projectleider.")

            elif eigen_id in deelnemer_ids:
                st.info(
                    "✅ Je bent aangemeld voor dit project."
                )

                if st.button(
                    "❌ Afmelden",
                    key="afmelden_project"
                ):
                    cursor.execute(
                        """
                        DELETE FROM project_deelnemers
                        WHERE project_id = ?
                        AND persoon_id = ?
                        """,
                        (project_id, eigen_id)
                    )

                    conn.commit()
                    st.success("✅ Je bent afgemeld!")
                    st.rerun()

            conn.commit()
            st.success("✅ Je bent afgemeld!")
            st.rerun()
