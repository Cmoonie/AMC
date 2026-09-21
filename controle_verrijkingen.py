import sqlite3

conn = sqlite3.connect("spider.db")

print("\nEERSTE 30 KOPPELINGEN")
print("=" * 80)

rows = conn.execute(
    """
    SELECT pmid, categorie, waarde, bron
    FROM publicatie_verrijkingen
    WHERE categorie = ?
    ORDER BY waarde, pmid
    LIMIT 30
    """,
    ("Onderzoeksmethode",)
).fetchall()

for row in rows:
    print(row)


print("\nAANTAL PER ONDERZOEKSMETHODE")
print("=" * 80)

rows = conn.execute(
    """
    SELECT waarde, COUNT(*) AS aantal
    FROM publicatie_verrijkingen
    WHERE categorie = ?
    GROUP BY waarde
    ORDER BY aantal DESC, waarde
    """,
    ("Onderzoeksmethode",)
).fetchall()

for row in rows:
    print(row)

conn.close()