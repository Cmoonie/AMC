from pathlib import Path
import sqlite3


# ============================================================
# PADEN
# ============================================================

# database.py staat in de hoofdmap van Spider.
# Daardoor gebruiken alle pagina's ALTIJD dezelfde database.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "spider.db"


# ============================================================
# DATABASE VERBINDING
# ============================================================

def get_connection():
    """
    Geeft een verbinding met de centrale Spider database terug.
    """

    conn = sqlite3.connect(DB_PATH)

    # Hiermee kunnen we later bijvoorbeeld:
    # persoon["name"]
    # gebruiken in plaats van persoon[1]
    conn.row_factory = sqlite3.Row

    # SQLite foreign keys inschakelen
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ============================================================
# HULPFUNCTIE VOOR MIGRATIES
# ============================================================

def kolom_bestaat(conn, tabel, kolom):
    """
    Controleert of een kolom al in een tabel bestaat.
    """

    kolommen = conn.execute(
        f"PRAGMA table_info({tabel})"
    ).fetchall()

    return any(
        rij["name"] == kolom
        for rij in kolommen
    )


# ============================================================
# DATABASE INITIALISEREN
# ============================================================

def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    # --------------------------------------------------------
    # PERSONS
    # Onderzoekers die zichtbaar zijn in Spider
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department TEXT
        )
    """)

    # --------------------------------------------------------
    # GEBRUIKERS
    # Accounts waarmee onderzoekers kunnen inloggen
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gebruikers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL,
            gebruikersnaam TEXT NOT NULL UNIQUE,
            wachtwoord TEXT NOT NULL,
            afdeling TEXT,
            rol TEXT NOT NULL DEFAULT 'gebruiker',
            person_id INTEGER,
            aangemaakt_op TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Bestaande database veilig upgraden
    if not kolom_bestaat(
        conn,
        "gebruikers",
        "person_id"
    ):
        cursor.execute("""
            ALTER TABLE gebruikers
            ADD COLUMN person_id INTEGER
        """)

    if not kolom_bestaat(
        conn,
        "gebruikers",
        "aangemaakt_op"
    ):
        cursor.execute("""
            ALTER TABLE gebruikers
            ADD COLUMN aangemaakt_op TEXT
        """)

    # --------------------------------------------------------
    # PROFIELDATA
    # Aanvullende gegevens van een onderzoeker
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profiel_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            person_id INTEGER
            gebruikersnaam TEXT,
            email TEXT,
            bio TEXT,
            expertise TEXT,
            projecten TEXT,
            links TEXT
        )
    """)

    if not kolom_bestaat(
        conn,
        "profiel_data",
        "person_id"
    ):
        cursor.execute("""
            ALTER TABLE profiel_data
            ADD COLUMN person_id TEXT
        """)
    if not kolom_bestaat(
        conn,
        "profiel_data",
        "links"
):
     cursor.execute("""
        ALTER TABLE profiel_data
        ADD COLUMN links TEXT
    """)
# ============================================================
# BESTAANDE PROFIELEN KOPPELEN AAN PERSON_ID
# ============================================================

    cursor.execute("""
        UPDATE profiel_data
        SET person_id = (
            SELECT persons.id
            FROM persons
            WHERE persons.name = profiel_data.gebruikersnaam
        )
        WHERE person_id IS NULL
    """)

    cursor.execute("""
        UPDATE profiel_data
        SET person_id = (
            SELECT gebruikers.person_id
            FROM gebruikers
            WHERE LOWER(gebruikers.gebruikersnaam)
                = LOWER(profiel_data.gebruikersnaam)
        )
        WHERE person_id IS NULL
    """)

    # --------------------------------------------------------
    # EXPERTISE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expertise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL UNIQUE
        )
    """)

    # --------------------------------------------------------
    # # PERSONS ↔ EXPERTISE
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS persons_expertise (
            person_id INTEGER NOT NULL,
            expertise_id INTEGER NOT NULL,

            UNIQUE(person_id, expertise_id)
        )
    """)

    # --------------------------------------------------------
    # PUBLICATIES
    #
    # Deze tabel bestaat al.
    # We verwijderen of overschrijven hem hier NIET.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # PUBLICATION EMBEDDINGS
    #
    # Bestaat al en blijft behouden.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # LOPENDE PROJECTEN
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lopende_projecten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naam TEXT NOT NULL,
            beschrijving TEXT,
            leider_id INTEGER,
            datum TEXT
        )
    """)

    # --------------------------------------------------------
    # PROJECT DEELNEMERS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_deelnemers (
            project_id INTEGER NOT NULL,
            persoon_id INTEGER NOT NULL,

            UNIQUE(project_id, persoon_id)
        )
    """)

    # --------------------------------------------------------
    # PROJECT DOCUMENTEN
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_documenten (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            naam TEXT NOT NULL,
            url TEXT,
            type TEXT
        )
    """)

    # --------------------------------------------------------
    # INDEXEN
    #
    # Worden belangrijk wanneer Spider duizenden records krijgt.
    # --------------------------------------------------------

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_persons_name
        ON persons(name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_persons_department
        ON persons(department)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_gebruikers_gebruikersnaam
        ON gebruikers(gebruikersnaam)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_gebruikers_person_id
        ON gebruikers(person_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_persons_expertise_person
        ON persons_expertise(person_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_persons_expertise_expertise
        ON persons_expertise(expertise_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_deelnemers_project
        ON project_deelnemers(project_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_deelnemers_persoon
        ON project_deelnemers(persoon_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_project_documenten_project
        ON project_documenten(project_id)
    """)

    conn.commit()
    conn.close()

    print(f"Spider database gecontroleerd: {DB_PATH}")


# ============================================================
# ALLEEN UITVOEREN WANNEER DIT BESTAND DIRECT WORDT GESTART
# ============================================================

if __name__ == "__main__":
    initialize_database()
