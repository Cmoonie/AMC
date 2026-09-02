"""
check_expertise.py — Controleer welke expertise-tags gekoppeld zijn aan een onderzoeker.

Gebruik:
    python check_expertise.py
    (pas NAAM hieronder aan, of geef de naam mee als argument)

    python check_expertise.py "Robert de Jonge"
"""

import sqlite3
import sys

NAAM = "Robert de Jonge"  # <-- pas dit aan als je geen argument meegeeft

def main():
    naam = sys.argv[1] if len(sys.argv) > 1 else NAAM

    conn = sqlite3.connect("spider.db")
    cur = conn.cursor()

    # 1. Bestaat deze persoon uberhaupt?
    cur.execute("SELECT id, name FROM persons WHERE name = ?", (naam,))
    persoon = cur.fetchone()

    if not persoon:
        print(f"❌ Geen persoon gevonden met naam '{naam}'.")
        print("   Beschikbare namen in de database:")
        cur.execute("SELECT id, name FROM persons")
        for row in cur.fetchall():
            print(f"   - id={row[0]}: {row[1]}")
        conn.close()
        return

    person_id, person_name = persoon
    print(f"✅ Persoon gevonden: id={person_id}, naam='{person_name}'")

    # 2. Toon eerst de kolomnamen van de expertise-tabel, zodat we de juiste
    #    kolom gebruiken (dit kan per database-versie verschillen)
    cur.execute("PRAGMA table_info(expertise)")
    kolommen = [row[1] for row in cur.fetchall()]
    print(f"ℹ️  Kolommen in tabel 'expertise': {kolommen}")

    # Kies de eerste tekstkolom die niet 'id' heet als vermoedelijke naam-kolom
    naam_kolom = next((k for k in kolommen if k != "id"), None)

    if not naam_kolom:
        print("❌ Kon geen naamkolom bepalen in de expertise-tabel.")
        conn.close()
        return

    print(f"ℹ️  Gebruik kolom '{naam_kolom}' als expertise-naam")

    # 3. Welke expertise is gekoppeld?
    cur.execute(
        f"""
        SELECT e.id, e.{naam_kolom}
        FROM expertise e
        JOIN persons_expertise pe ON e.id = pe.expertise_id
        WHERE pe.person_id = ?
        """,
        (person_id,),
    )
    resultaten = cur.fetchall()

    if not resultaten:
        print(f"❌ Geen expertise-koppelingen gevonden voor '{person_name}' in persons_expertise.")
    else:
        print(f"✅ {len(resultaten)} expertise-koppeling(en) gevonden:")
        for exp_id, exp_naam in resultaten:
            print(f"   - id={exp_id}: {exp_naam}")

    conn.close()


if __name__ == "__main__":
    main()