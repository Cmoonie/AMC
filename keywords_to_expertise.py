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

        alle_keywords = set()

        for _, pub in publicaties.iterrows():

            keywords_tekst = pub["keywords"]

            if not keywords_tekst:
                continue

            for keyword in keywords_tekst.split(";"):

                keyword = keyword.strip().lower()

                # Eventuele oude encodingproblemen proberen
                # te herstellen.
                try:
                    keyword = (
                        keyword
                        .encode("latin-1")
                        .decode("utf-8")
                    )
                except Exception:
                    pass

                if keyword and len(keyword) > 2:
                    alle_keywords.add(keyword)

        # --------------------------------------------------------
        # CONSISTENTE VOLGORDE
        # --------------------------------------------------------

        keywords = sorted(
            alle_keywords
        )

        # Voorlopig maximaal 10 expertise-termen
        keywords = keywords[:10]

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
    # import sqlite3
# import pandas as pd

# conn = sqlite3.connect("spider.db")
# cursor = conn.cursor()

# # Haal alle personen op
# personen = pd.read_sql("SELECT id, name FROM persons", conn)

# for _, persoon in personen.iterrows():
#     naam = persoon["name"]
#     persoon_id = persoon["id"]

#     # Vervang apostrof in naam voor SQL
#     naam_sql = naam.replace("'", "''")
    
#     # Haal keywords op uit publicaties van deze persoon
#     publicaties = pd.read_sql(f"""
#         SELECT keywords FROM publications 
#         WHERE authors LIKE '%{naam_sql}%'
#         AND keywords IS NOT NULL
#     """, conn)
    
#     if publicaties.empty:
#         print(f"{naam}: geen keywords gevonden")
#         continue
    
#     # Verzamel alle unieke keywords
#     alle_keywords = set()
#     for _, pub in publicaties.iterrows():
#         if pub["keywords"]:
#             for keyword in pub["keywords"].split(";"):
#                keyword = keyword.strip().lower()
#                 # Fix encoding problemen zoals â€™ → '
#                try:
#                     keyword = keyword.encode('latin-1').decode('utf-8')
#                except:
#                     pass
#                if keyword and len(keyword) > 2:
#                     alle_keywords.add(keyword)
    
#     # Voeg top 10 keywords toe als expertise
#     top_keywords = list(alle_keywords)[:10]
    
#     for keyword in top_keywords:
#         # Check of expertise al bestaat
#         cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (keyword,))
#         bestaand = cursor.fetchone()
        
#         if not bestaand:
#             cursor.execute("INSERT INTO expertise (label) VALUES (?)", (keyword,))
#             conn.commit()
        
#         cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (keyword,))
#         expertise_id = cursor.fetchone()[0]
        
#         # Koppel aan persoon
#         cursor.execute("SELECT * FROM persons_expertise WHERE person_id = ? AND expertise_id = ?", 
#                        (persoon_id, expertise_id))
#         if not cursor.fetchone():
#             cursor.execute("INSERT INTO persons_expertise (person_id, expertise_id) VALUES (?, ?)",
#                            (persoon_id, expertise_id))
    
#     conn.commit()
#     print(f"{naam}: {len(top_keywords)} expertise tags toegevoegd")

# conn.close()
# print("Klaar!")
