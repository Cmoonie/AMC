from database import get_connection

conn = get_connection()

try:
    cursor = conn.cursor()

    # Oude experimentele koppeltabel verwijderen
    cursor.execute(
        """
        DROP TABLE IF EXISTS kennisgraaf_categorie_expertise
        """
    )

    # Categorieën blijven bestaan
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS kennisgraaf_categorieen (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL UNIQUE,
            beschrijving TEXT
        )
        """
    )

    # Vrije items binnen een categorie
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS kennisgraaf_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            categorie_id INTEGER NOT NULL,
            naam TEXT NOT NULL,

            FOREIGN KEY (categorie_id)
                REFERENCES kennisgraaf_categorieen(id)
                ON DELETE CASCADE,

            UNIQUE (categorie_id, naam)
        )
        """
    )

    conn.commit()

    print("Nieuwe categorie-structuur succesvol aangemaakt.")

except Exception as fout:
    conn.rollback()
    print("FOUT:", fout)

finally:
    conn.close()