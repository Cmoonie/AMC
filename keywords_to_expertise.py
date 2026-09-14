import sqlite3
import pandas as pd


def werk_expertise_bij(conn):
    """
    Werkt expertise bij op basis van keywords
    uit publicaties.

    Voor iedere onderzoeker:
    - zoekt publicaties waarin de naam voorkomt
    - verzamelt keywords
    - maakt ontbrekende expertise aan
    - maakt ontbrekende persons_expertise koppelingen aan

    Geeft terug hoeveel nieuwe koppelingen zijn gemaakt.
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

    for _, persoon in personen.iterrows():

        naam = persoon["name"]
        persoon_id = persoon["id"]
        
    # Oude expertise-koppelingen van deze onderzoeker verwijderen
    # zodat de nieuwe top 10 opnieuw opgebouwd kan worden
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
        # PUBLICATIES VAN DEZE ONDERZOEKER
        # --------------------------------------------------------

        publicaties = pd.read_sql(
            """
            SELECT keywords
            FROM publications
            WHERE authors LIKE ?
            AND keywords IS NOT NULL
            AND TRIM(keywords) != ''
            """,
            conn,
            params=(
                f"%{naam}%",
            )
        )

        if publicaties.empty:
            continue

        # --------------------------------------------------------
        # KEYWORDS VERZAMELEN
        # --------------------------------------------------------

        keyword_tellingen = {}

        for _, pub in publicaties.iterrows():

            keywords_tekst = pub["keywords"]

            if not keywords_tekst:
                continue

            for keyword in keywords_tekst.split(";"):

                keyword = keyword.strip().lower()

                try:
                    keyword = (
                        keyword
                        .encode("latin-1")
                        .decode("utf-8")
                    )
                except Exception:
                    pass

                if keyword and len(keyword) > 2:

                    if keyword not in keyword_tellingen:
                        keyword_tellingen[keyword] = 0

                    keyword_tellingen[keyword] += 1


            # Sorteer op aantal keer voorkomen:
            # meest voorkomende eerst
            gesorteerde_keywords = sorted(
                keyword_tellingen.items(),
                key=lambda item: (
                    -item[1],
                    item[0]
                )
            )


            # Alleen de keyword-tekst bewaren
            keywords = [
                keyword
                for keyword, aantal in gesorteerde_keywords[:10]
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

                expertise_id = (
                    cursor.lastrowid
                )

                totaal_nieuwe_expertise += 1

            # ----------------------------------------------------
            # KOPPELING PERSON ↔ EXPERTISE
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
  