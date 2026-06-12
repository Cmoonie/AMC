import sqlite3
import pandas as pd

# Verbinding maken met de database
# Als het bestand niet bestaat, maakt Python het automatisch aan
conn = sqlite3.connect("spider.db")

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
    ("Alberto Miranda Bedate", "Division 9"),
    ("Andrew Li Yim", "Division 9"),
    ("Bas Voermans", "Division 9"),
    ("Costa Bachas", "Division 9"),
    ("Eric Reits", "Division 9"),
    ("Sarper Okuyan", "Division 9"),
    ("Febe van Maldegem", "Division 9"),
    ("Sjors In 't Veld", "Division 9"),
    ("Helena Chon", "Division 9"),
    ("Hung Jen Chen", "Division 9"),
    ("Hessel Peters-Sengers", "Division 9"),
    ("Jaap van Buul", "Division 9"),
    ("Jens Seidel", "Division 9"),
    ("Jan Koster", "Division 9"),
    ("Katy Wolstencroft", "Division 9"),
    ("Marten Hoeksema", "Division 9"),
    ("Martijn C Schut", "Division 9"),
    ("Mark Davids", "Division 9"),
    ("Mike de Kok", "Division 9"),
    ("Miranda Houtman", "Division 9"),
    ("Matthijs Welkers", "Division 9"),
    ("Marco Haselager", "Division 9"),
    ("Nynke Kooistra", "Division 9"),
    ("Patrick de Jonge", "Division 9"),
    ("Przemek Krawczyk", "Division 9"),
    ("Richard Schoonhoven", "Division 9"),
    ("Rogier Postma", "Division 9"),
    ("Rogier Schade", "Division 9"),
    ("Sanjat Kanjilal", "Division 9"),
    ("Azam Nurmohamed", "Division 9"),
    ("Tom Stirrop", "Division 9"),
    ("Thang Pham", "Division 9"),
    ("Wietske Pieters", "Division 9"),
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
    


# Sluit verbinding
conn.close()
print("Klaar!")