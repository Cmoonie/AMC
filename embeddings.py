import sqlite3
import pandas as pd
from sentence_transformers import SentenceTransformer
import json


MODEL_NAAM = "paraphrase-multilingual-MiniLM-L12-v2"


def maak_embeddings_voor_nieuwe_publicaties(conn):
    """
    Maakt alleen embeddings voor publicaties
    die nog niet in publication_embeddings staan.

    Geeft terug:
    {
        "gevonden": aantal publicaties zonder embedding,
        "toegevoegd": aantal nieuwe embeddings
    }
    """

    cursor = conn.cursor()

    # --------------------------------------------------------
    # TABEL CONTROLEREN / AANMAKEN
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS publication_embeddings (
            pmid TEXT,
            embedding TEXT
        )
    """)

    # --------------------------------------------------------
    # PUBLICATIES ZONDER EMBEDDING OPHALEN
    # --------------------------------------------------------

    publicaties = pd.read_sql(
        """
        SELECT
            p.pmid,
            p.title,
            p.abstract
        FROM publications p
        LEFT JOIN publication_embeddings pe
            ON CAST(p.pmid AS TEXT) = CAST(pe.pmid AS TEXT)
        WHERE pe.pmid IS NULL
        """,
        conn
    )

    if publicaties.empty:

        return {
            "gevonden": 0,
            "toegevoegd": 0
        }

    # --------------------------------------------------------
    # MODEL LADEN
    # --------------------------------------------------------

    model = SentenceTransformer(
        MODEL_NAAM
    )

    # --------------------------------------------------------
    # TEKST VOOR EMBEDDING
    # --------------------------------------------------------

    teksten = (
        publicaties["title"].fillna("")
        + " "
        + publicaties["abstract"].fillna("")
    ).tolist()

    # --------------------------------------------------------
    # EMBEDDINGS MAKEN
    # --------------------------------------------------------

    embeddings = model.encode(
        teksten,
        show_progress_bar=False
    )

    # --------------------------------------------------------
    # OPSLAAN
    # --------------------------------------------------------

    toegevoegd = 0

    for i, row in publicaties.iterrows():

        embedding_json = json.dumps(
            embeddings[i].tolist()
        )

        cursor.execute(
            """
            INSERT INTO publication_embeddings (
                pmid,
                embedding
            )
            VALUES (?, ?)
            """,
            (
                str(row["pmid"]),
                embedding_json
            )
        )

        toegevoegd += 1

    conn.commit()

    return {
        "gevonden": len(publicaties),
        "toegevoegd": toegevoegd
    }


# ============================================================
# HANDMATIG UITVOEREN VIA TERMINAL
# ============================================================

if __name__ == "__main__":

    conn = sqlite3.connect("spider.db")

    print("Nieuwe publicaties zoeken...")

    resultaat = maak_embeddings_voor_nieuwe_publicaties(
        conn
    )

    print(
        f"{resultaat['gevonden']} publicaties "
        "zonder embedding gevonden."
    )

    print(
        f"{resultaat['toegevoegd']} embeddings toegevoegd."
    )

    conn.close()
# import sqlite3
# import pandas as pd
# from sentence_transformers import SentenceTransformer
# import numpy as np
# import json

# # Verbinding met database
# conn = sqlite3.connect("spider.db")

# print("Model laden...")
# model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
# print("Model geladen!")

# # Laad publicaties
# publicaties = pd.read_sql("SELECT pmid, title, abstract, keywords FROM publications", conn)
# print(f"{len(publicaties)} publicaties gevonden")

# # Maak embeddings voor elke publicatie
# print("Embeddings maken...")
# teksten = (publicaties["title"].fillna("") + " " + publicaties["abstract"].fillna("")).tolist()
# embeddings = model.encode(teksten, show_progress_bar=True)

# # Sla embeddings op in database
# cursor = conn.cursor()
# cursor.execute("""
#     CREATE TABLE IF NOT EXISTS publication_embeddings (
#         pmid INTEGER,
#         embedding TEXT
#     )
# """)

# cursor.execute("DELETE FROM publication_embeddings")

# for i, row in publicaties.iterrows():
#     embedding_json = json.dumps(embeddings[i].tolist())
#     cursor.execute("INSERT INTO publication_embeddings (pmid, embedding) VALUES (?, ?)",
#                    (row["pmid"], embedding_json))

# conn.commit()
# print("Embeddings opgeslagen!")
# conn.close()