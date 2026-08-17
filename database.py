import sqlite3
import pandas as pd

# Verbinding maken met de database
# Als het bestand niet bestaat, maakt Python het automatisch aan
conn = sqlite3.connect("spider.db")

cursor = conn.cursor()

# Reset alle tabellen
cursor.execute("DROP TABLE IF EXISTS persons_expertise")
cursor.execute("DROP TABLE IF EXISTS expertise")
cursor.execute("""
    CREATE TABLE expertise (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT UNIQUE
    )
""")
cursor.execute("""
    CREATE TABLE persons_expertise (
        person_id INTEGER,
        expertise_id INTEGER
    )
""")
conn.commit()
print("Tabellen gereset!")

print("Database verbinding gemaakt!")


# Importeer PubMed publicaties
try:
    pubmed_robert = pd.read_csv("Data/pubmed_publications_Robert_de_Jonge.csv", sep="\t", encoding="utf-8")
    pubmed_sjors = pd.read_csv("Data/pubmed_publications_Sjors_G_J_G_In_t_Veld.csv", sep="\t", encoding="utf-8")
    
    pubmed_robert.to_sql("publications", conn, if_exists="replace", index=False)
    pubmed_sjors.to_sql("publications", conn, if_exists="append", index=False)

    print("Publicaties geïmporteerd!")
except Exception as e:
    print(f"Publicaties niet gevonden: {e}")

    # Wijzigingen importeren 
wijzigingen = pd.read_csv("Data/wijzigingen.csv")
wijzigingen.to_sql("wijzigingen", conn, if_exists="replace", index=False)
print("Wijzigingen geïmporteerd!")
    

# Profiel data tabel aanmaken
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS profiel_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        gebruikersnaam TEXT,
        email TEXT,
        bio TEXT,
        expertise TEXT,
        projecten TEXT
    )
""")
conn.commit()
print("Profiel tabel aangemaakt!") 

# Voeg echte onderzoekers toe
onderzoekers = [
    ("Robert de Jonge", "Division 9"),
    ("Sjors In 't Veld", "Division 9"),
    ("Martijn C Schut", "Division 9"),
]

# Verwijder dummy personen en voeg echte toe
cursor = conn.cursor()
# Maak persons tabel opnieuw aan met auto-increment id
cursor.execute("DROP TABLE IF EXISTS persons")
cursor.execute("""
    CREATE TABLE persons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT
    )
""")
conn.commit()
cursor.execute("DELETE FROM persons")
for naam, dept in onderzoekers:
    cursor.execute("INSERT INTO persons (name, department) VALUES (?, ?)", (naam, dept))
conn.commit()
print(f"{len(onderzoekers)} echte onderzoekers toegevoegd!")

# Voeg Martijn Schut publicaties toe
try:
    pubmed_martijn = pd.read_csv("Data/pubmed_publications_Martijn_C_Schut.csv", sep="\t", encoding="utf-8")
    pubmed_martijn.to_sql("publications", conn, if_exists="append", index=False)
    print("Martijn Schut publicaties geïmporteerd!")
except Exception as e:
    print(f"Fout: {e}")

 # Verwijder lege expertise koppelingen
cursor.execute("DELETE FROM persons_expertise WHERE expertise_id IS NULL")
conn.commit()
print("Lege expertise koppelingen verwijderd!")   

# Verwijder ook persons_expertise helemaal en maak opnieuw aan
cursor.execute("DROP TABLE IF EXISTS persons_expertise")
cursor.execute("""
    CREATE TABLE persons_expertise (
        person_id INTEGER,
        expertise_id INTEGER
    )
""")
conn.commit()
print("Persons expertise tabel opnieuw aangemaakt!")
# Lopende projecten tabel aanmaken
cursor.execute("""
    CREATE TABLE IF NOT EXISTS lopende_projecten (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naam TEXT,
        beschrijving TEXT,
        leider_id INTEGER,
        datum TEXT
    )
""")

# Deelnemers tabel aanmaken
cursor.execute("""
    CREATE TABLE IF NOT EXISTS project_deelnemers (
        project_id INTEGER,
        persoon_id INTEGER
    )
""")
conn.commit()
print("Lopende projecten tabel aangemaakt!")

# Gebruikers tabel aanmaken
cursor.execute("""
    CREATE TABLE IF NOT EXISTS gebruikers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        naam TEXT,
        gebruikersnaam TEXT UNIQUE,
        wachtwoord TEXT,
        afdeling TEXT,
        rol TEXT DEFAULT 'gebruiker'
    )
""")
conn.commit()
print("Gebruikers tabel aangemaakt!")

# Sluit verbinding
conn.close()
print("Klaar!")