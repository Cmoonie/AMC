import re
import sqlite3

import pandas as pd


def normaliseer_auteursnaam(tekst):
    """
    Maakt auteursnamen vergelijkbaar zonder hoofdletters,
    spaties en leestekens.

    Voorbeelden:
    Wolstencroft.K  -> wolstencroftk
    Wolstencroft K  -> wolstencroftk
    Wolstencroft, K -> wolstencroftk
    """
    if tekst is None:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(tekst).lower()
    )

def werk_expertise_bij(conn):
    """
    Werkt expertise bij op basis van publicaties.

    Voor iedere onderzoeker:
    - gebruikt de normale naam + PubMed-auteursaliassen
    - zoekt bijbehorende publicaties
    - gebruikt keywords als die aanwezig zijn
    - gebruikt MeSH-termen als keywords ontbreken
    - bepaalt de top 10 onderwerpen
    - maakt expertise en koppelingen opnieuw aan
    """

    cursor = conn.cursor()

    personen = pd.read_sql(
        """
        SELECT id, name
        FROM persons
        """,
        conn
    )

    totaal_nieuwe_expertise = 0
    totaal_nieuwe_koppelingen = 0

    # Algemene MeSH-termen die geen echte expertise zijn
    mesh_stopwoorden = {
        "humans",
        "animals",
        "male",
        "female",
        "adult",
        "child",
        "infant",
        "adolescent",
        "aged",
        "middle aged",
        "young adult",
        "mice",
        "rats",
        "cell line",
    }

    for _, persoon in personen.iterrows():

        naam = persoon["name"]
        persoon_id = persoon["id"]

        # --------------------------------------------------------
        # OUDE KOPPELINGEN VERWIJDEREN
        # --------------------------------------------------------

        cursor.execute(
            """
            DELETE FROM persons_expertise
            WHERE person_id = ?
            """,
            (
                persoon_id,
            )
        )

        # --------------------------------------------------------
        # AUTEURSNAMEN + ALIASSEN
        # --------------------------------------------------------

        aliases_df = pd.read_sql(
            """
            SELECT author_name
            FROM person_author_aliases
            WHERE person_id = ?
            """,
            conn,
            params=(
                persoon_id,
            )
        )

        auteursnamen = [
            str(naam).strip()
        ]

        for alias in aliases_df["author_name"].dropna():

            alias = str(alias).strip()

            if alias and alias not in auteursnamen:
                auteursnamen.append(alias)

        # --------------------------------------------------------
        # PUBLICATIES VAN DEZE ONDERZOEKER
        # --------------------------------------------------------

        publicaties = pd.read_sql(
            """
            SELECT
                authors,
                keywords,
                mesh_terms
            FROM publications
            """,
            conn
        )

        genormaliseerde_auteursnamen = [
            normaliseer_auteursnaam(auteursnaam)
            for auteursnaam in auteursnamen
            if auteursnaam
        ]

        publicaties = publicaties[
            publicaties["authors"].fillna("").apply(
                lambda authors: any(
                    auteursnaam
                    in normaliseer_auteursnaam(authors)
                    for auteursnaam
                    in genormaliseerde_auteursnamen
                )
            )
        ]

        if publicaties.empty:
            continue

        # --------------------------------------------------------
        # KEYWORDS / MESH VERZAMELEN
        # --------------------------------------------------------

        keyword_tellingen = {}

        for _, pub in publicaties.iterrows():

            keywords_tekst = pub["keywords"]

            mesh_tekst = pub["mesh_terms"]

            # Eerst normale keywords proberen
            if (
                keywords_tekst
                and str(keywords_tekst).strip()
            ):

                termen = str(
                    keywords_tekst
                ).split(";")

                gebruik_mesh = False

            # Geen keywords?
            # Dan MeSH gebruiken als fallback
            elif (
                mesh_tekst
                and str(mesh_tekst).strip()
            ):

                termen = str(
                    mesh_tekst
                ).split(";")

                gebruik_mesh = True

            else:
                continue

            for term in termen:

                term = term.strip()

                if not term:
                    continue

                # Bij MeSH alleen het hoofdonderwerp gebruiken.
                #
                # Bijvoorbeeld:
                # Autoimmune Diseases/genetics/*immunology
                #
                # wordt:
                # autoimmune diseases
                if gebruik_mesh:

                    term = term.split("/")[0]

                    term = term.replace(
                        "*",
                        ""
                    )

                term = term.strip().lower()

                # Eventuele foutieve tekencodering herstellen
                try:
                    term = (
                        term
                        .encode("latin-1")
                        .decode("utf-8")
                    )
                except Exception:
                    pass

                if not term:
                    continue

                if len(term) <= 2:
                    continue

                if term in {"nan", "none", "null"}:
                    continue

                if (
                    gebruik_mesh
                    and term in mesh_stopwoorden
                ):
                    continue

                if term not in keyword_tellingen:
                    keyword_tellingen[term] = 0

                keyword_tellingen[term] += 1

        # --------------------------------------------------------
        # TOP 10 BEPALEN
        # --------------------------------------------------------

        gesorteerde_keywords = sorted(
            keyword_tellingen.items(),
            key=lambda item: (
                -item[1],
                item[0]
            )
        )

        keywords = [
            keyword
            for keyword, aantal
            in gesorteerde_keywords[:10]
        ]

        # --------------------------------------------------------
        # EXPERTISE OPSLAAN
        # --------------------------------------------------------

        for keyword in keywords:

            cursor.execute(
                """
                SELECT id
                FROM expertise
                WHERE LOWER(label) = ?
                """,
                (
                    keyword,
                )
            )

            bestaand = cursor.fetchone()

            if bestaand:

                expertise_id = bestaand[0]

            else:

                cursor.execute(
                    """
                    INSERT INTO expertise (
                        label
                    )
                    VALUES (?)
                    """,
                    (
                        keyword,
                    )
                )

                expertise_id = cursor.lastrowid

                totaal_nieuwe_expertise += 1

            # ----------------------------------------------------
            # KOPPELING ONDERZOEKER ↔ EXPERTISE
            # ----------------------------------------------------

            cursor.execute(
                """
                SELECT 1
                FROM persons_expertise
                WHERE person_id = ?
                AND expertise_id = ?
                """,
                (
                    persoon_id,
                    expertise_id
                )
            )

            koppeling = cursor.fetchone()

            if not koppeling:

                cursor.execute(
                    """
                    INSERT INTO persons_expertise (
                        person_id,
                        expertise_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        persoon_id,
                        expertise_id
                    )
                )

                totaal_nieuwe_koppelingen += 1

    conn.commit()

    return {
        "nieuwe_expertise": totaal_nieuwe_expertise,
        "nieuwe_koppelingen": totaal_nieuwe_koppelingen
    }


if __name__ == "__main__":

    conn = sqlite3.connect(
        "spider.db"
    )

    print(
        "Expertise bijwerken..."
    )

    resultaat = werk_expertise_bij(
        conn
    )

    print(
        f"{resultaat['nieuwe_expertise']} "
        "nieuwe expertise-termen toegevoegd."
    )

    print(
        f"{resultaat['nieuwe_koppelingen']} "
        "nieuwe onderzoeker-expertise koppelingen toegevoegd."
    )

    conn.close()

    print(
        "Klaar!"
    )