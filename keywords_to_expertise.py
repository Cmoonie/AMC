import sqlite3
import pandas as pd

conn = sqlite3.connect("spider.db")
cursor = conn.cursor()

# Haal alle personen op
personen = pd.read_sql("SELECT id, name FROM persons", conn)

for _, persoon in personen.iterrows():
    naam = persoon["name"]
    persoon_id = persoon["id"]

    # Vervang apostrof in naam voor SQL
    naam_sql = naam.replace("'", "''")
    
    # Haal keywords op uit publicaties van deze persoon
    publicaties = pd.read_sql(f"""
        SELECT keywords FROM publications 
        WHERE authors LIKE '%{naam_sql}%'
        AND keywords IS NOT NULL
    """, conn)
    
    if publicaties.empty:
        print(f"{naam}: geen keywords gevonden")
        continue
    
    # Verzamel alle unieke keywords
    alle_keywords = set()
    for _, pub in publicaties.iterrows():
        if pub["keywords"]:
            for keyword in pub["keywords"].split(";"):
               keyword = keyword.strip().lower()
                # Fix encoding problemen zoals â€™ → '
               try:
                    keyword = keyword.encode('latin-1').decode('utf-8')
               except:
                    pass
               if keyword and len(keyword) > 2:
                    alle_keywords.add(keyword)
    
    # Voeg top 10 keywords toe als expertise
    top_keywords = list(alle_keywords)[:10]
    
    for keyword in top_keywords:
        # Check of expertise al bestaat
        cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (keyword,))
        bestaand = cursor.fetchone()
        
        if not bestaand:
            cursor.execute("INSERT INTO expertise (label) VALUES (?)", (keyword,))
            conn.commit()
        
        cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (keyword,))
        expertise_id = cursor.fetchone()[0]
        
        # Koppel aan persoon
        cursor.execute("SELECT * FROM persons_expertise WHERE person_id = ? AND expertise_id = ?", 
                       (persoon_id, expertise_id))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO persons_expertise (person_id, expertise_id) VALUES (?, ?)",
                           (persoon_id, expertise_id))
    
    conn.commit()
    print(f"{naam}: {len(top_keywords)} expertise tags toegevoegd")

conn.close()
print("Klaar!")
