import sqlite3
import pandas as pd

conn = sqlite3.connect("spider.db")

# Check projecten zonder naam
print("=== Projecten zonder naam ===")
df = pd.read_sql("SELECT * FROM lopende_projecten WHERE naam IS NULL OR naam = '' OR naam = ' '", conn)
print(df)

# Check publicaties zonder titel
print("\n=== Publicaties zonder titel ===")
df = pd.read_sql("SELECT pmid, authors FROM publications WHERE title IS NULL OR title = ''", conn)
print(df)

conn.close()