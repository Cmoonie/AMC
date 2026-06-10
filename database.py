import sqlite3
import pandas as pd

# Verbinding maken met de database
# Als het bestand niet bestaat, maakt Python het automatisch aan
conn = sqlite3.connect("spider.db")

print("Database verbinding gemaakt!")

# Laad CSV bestanden en importeer in database
personen = pd.read_csv("Data/persons.csv")
expertise = pd.read_csv("Data/expertise.csv")
personen_expertise = pd.read_csv("Data/persons_expertise.csv")
projecten = pd.read_csv("Data/projects.csv")
personen_projecten = pd.read_csv("Data/persons_projects.csv")

# Zet data in database
personen.to_sql("persons", conn, if_exists="replace", index=False)
expertise.to_sql("expertise", conn, if_exists="replace", index=False)
personen_expertise.to_sql("persons_expertise", conn, if_exists="replace", index=False)
projecten.to_sql("projects", conn, if_exists="replace", index=False)
personen_projecten.to_sql("persons_projects", conn, if_exists="replace", index=False)

print("Data geïmporteerd!")

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
    

# Controleer of data goed is opgeslagen
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM publications")
print(f"Aantal publicaties in database: {cursor.fetchone()[0]}")

cursor.execute("SELECT * FROM persons")
print("\nPersonen in database:")
for rij in cursor.fetchall():
    print(rij)

# Sluit verbinding
conn.close()
print("Klaar!")