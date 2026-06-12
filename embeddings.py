import sqlite3
import pandas as pd
from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Verbinding met database
conn = sqlite3.connect("spider.db")

print("Model laden...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Model geladen!")

# Laad publicaties
publicaties = pd.read_sql("SELECT pmid, title, abstract, keywords FROM publications", conn)
print(f"{len(publicaties)} publicaties gevonden")

# Maak embeddings voor elke publicatie
print("Embeddings maken...")
teksten = (publicaties["title"].fillna("") + " " + publicaties["abstract"].fillna("")).tolist()
embeddings = model.encode(teksten, show_progress_bar=True)

# Sla embeddings op in database
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS publication_embeddings (
        pmid INTEGER,
        embedding TEXT
    )
""")

cursor.execute("DELETE FROM publication_embeddings")

for i, row in publicaties.iterrows():
    embedding_json = json.dumps(embeddings[i].tolist())
    cursor.execute("INSERT INTO publication_embeddings (pmid, embedding) VALUES (?, ?)",
                   (row["pmid"], embedding_json))

conn.commit()
print("Embeddings opgeslagen!")
conn.close()