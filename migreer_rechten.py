from database import get_connection

conn = get_connection()

try:
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS gebruikers_rechten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER NOT NULL,
            recht TEXT NOT NULL,

            UNIQUE(person_id, recht),

            FOREIGN KEY (person_id)
                REFERENCES persons(id)
                ON DELETE CASCADE
        )
        """
    )

    conn.commit()

    print("Gebruikersrechten succesvol aangemaakt.")

except Exception as fout:
    conn.rollback()
    print("FOUT:", fout)

finally:
    conn.close()