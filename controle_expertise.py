from database import get_connection

conn = get_connection()

print("\n=== STRUCTUUR EXPERTISE ===")

for kolom in conn.execute(
    'PRAGMA table_info("expertise")'
).fetchall():
    print(dict(kolom))

print("\n=== VOORBEELDEN ===")

for rij in conn.execute(
    "SELECT * FROM expertise LIMIT 5"
).fetchall():
    print(dict(rij))

conn.close()