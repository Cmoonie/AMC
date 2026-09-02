"""
voeg_expertise_toe.py — Koppel handmatig een expertise-tag aan een onderzoeker.

Nodig omdat keywords_to_expertise.py willekeurige top-10 keywords per persoon
pakt, waardoor sommige gewenste tags (die wel in publicaties voorkomen, maar
niet in de random top-10 vielen) niet automatisch gekoppeld worden.

Gebruik:
    python voeg_expertise_toe.py
"""

import sqlite3

# Pas dit aan per keer dat je een koppeling wilt toevoegen
# Dit zijn de "showcase"-tags die GEGARANDEERD gekoppeld moeten blijven,
# ongeacht wat keywords_to_expertise.py toevallig als willekeurige top-10 kiest.
# Draai dit script daarom altijd NA keywords_to_expertise.py.
KOPPELINGEN = [
    ("Robert de Jonge", "methotrexate polyglutamates"),
    ("Robert de Jonge", "laboratory medicine"),
    ("Sjors In 't Veld", "neurofilament light chain"),
    ("Sjors In 't Veld", "systemic amyloidosis"),
    ("Martijn C Schut", "clinical practice guidelines"),
]


def voeg_toe(cursor, naam, label):
    # Persoon opzoeken
    cursor.execute("SELECT id FROM persons WHERE name = ?", (naam,))
    persoon = cursor.fetchone()
    if not persoon:
        print(f"❌ Persoon '{naam}' niet gevonden.")
        return
    person_id = persoon[0]

    # Expertise-tag opzoeken of aanmaken
    cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (label.lower(),))
    expertise = cursor.fetchone()
    if not expertise:
        cursor.execute("INSERT INTO expertise (label) VALUES (?)", (label,))
        cursor.execute("SELECT id FROM expertise WHERE LOWER(label) = ?", (label.lower(),))
        expertise = cursor.fetchone()
        print(f"ℹ️  Nieuwe expertise-tag aangemaakt: '{label}'")
    expertise_id = expertise[0]

    # Koppeling checken/toevoegen
    cursor.execute(
        "SELECT * FROM persons_expertise WHERE person_id = ? AND expertise_id = ?",
        (person_id, expertise_id),
    )
    if cursor.fetchone():
        print(f"⚠️  '{naam}' was al gekoppeld aan '{label}', niks veranderd.")
    else:
        cursor.execute(
            "INSERT INTO persons_expertise (person_id, expertise_id) VALUES (?, ?)",
            (person_id, expertise_id),
        )
        print(f"✅ '{naam}' gekoppeld aan '{label}'.")


def main():
    conn = sqlite3.connect("spider.db")
    cursor = conn.cursor()

    for naam, label in KOPPELINGEN:
        voeg_toe(cursor, naam, label)

    conn.commit()
    conn.close()
    print("Klaar!")


if __name__ == "__main__":
    main()