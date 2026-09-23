import sqlite3

conn = sqlite3.connect("spider.db")

try:
    conn.execute("BEGIN")

    # Elke PMID mag maar één keer voorkomen
    # in de publicatietabel.
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_publications_unique_pmid
        ON publications(pmid)
        """
    )

    # Elke PMID mag ook maar één embedding hebben.
    conn.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_publication_embeddings_unique_pmid
        ON publication_embeddings(pmid)
        """
    )

    conn.commit()

    print("UNIQUE-indexen succesvol aangemaakt.")

except Exception:
    conn.rollback()
    raise


print("\nINDEXEN PUBLICATIONS:")
for rij in conn.execute(
    "PRAGMA index_list(publications)"
).fetchall():
    print(rij)


print("\nINDEXEN PUBLICATION_EMBEDDINGS:")
for rij in conn.execute(
    "PRAGMA index_list(publication_embeddings)"
).fetchall():
    print(rij)

conn.close()