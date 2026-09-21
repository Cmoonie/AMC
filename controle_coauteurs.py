import sqlite3
from collections import defaultdict
from itertools import combinations


conn = sqlite3.connect("spider.db")
conn.row_factory = sqlite3.Row


# ============================================================
# ONDERZOEKERS + AUTEURSALIASSEN
# ============================================================

personen = conn.execute(
    """
    SELECT id, name
    FROM persons
    ORDER BY name
    """
).fetchall()

aliases = conn.execute(
    """
    SELECT person_id, author_name
    FROM person_author_aliases
    """
).fetchall()


namen_per_persoon = defaultdict(list)

for persoon in personen:
    namen_per_persoon[persoon["id"]].append(
        persoon["name"]
    )

for alias in aliases:
    namen_per_persoon[alias["person_id"]].append(
        alias["author_name"]
    )


# ============================================================
# FUNCTIE: ONDERZOEKER HERKENNEN IN AUTEURSVELD
# ============================================================

def onderzoeker_in_auteurs(auteurs, namen):

    if not auteurs:
        return False

    auteurs_lower = str(auteurs).lower()

    for naam in namen:

        if not naam:
            continue

        naam_lower = str(naam).strip().lower()

        if naam_lower and naam_lower in auteurs_lower:
            return True

    return False


# ============================================================
# PUBLICATIES CONTROLEREN
# ============================================================

publicaties = conn.execute(
    """
    SELECT pmid, title, authors
    FROM publications
    WHERE authors IS NOT NULL
      AND TRIM(authors) != ''
    """
).fetchall()


# (persoon_1, persoon_2) -> set met PMIDs
coauteur_publicaties = defaultdict(set)


for publicatie in publicaties:

    gevonden_personen = []

    for persoon in personen:

        persoon_id = persoon["id"]

        if onderzoeker_in_auteurs(
            publicatie["authors"],
            namen_per_persoon[persoon_id]
        ):
            gevonden_personen.append(
                persoon_id
            )

    # Een co-auteursrelatie bestaat pas wanneer minimaal
    # twee bekende Spider-onderzoekers op dezelfde publicatie staan.
    if len(gevonden_personen) >= 2:

        gevonden_personen = sorted(
            set(gevonden_personen)
        )

        for persoon_1, persoon_2 in combinations(
            gevonden_personen,
            2
        ):
            coauteur_publicaties[
                (persoon_1, persoon_2)
            ].add(
                str(publicatie["pmid"])
            )


# ============================================================
# RESULTATEN
# ============================================================

naam_per_id = {
    persoon["id"]: persoon["name"]
    for persoon in personen
}

print()
print("=" * 80)
print("CO-AUTEURSNETWERK SPIDER")
print("=" * 80)

print(
    f"Onderzoekers gecontroleerd: {len(personen)}"
)

print(
    f"Publicaties gecontroleerd: {len(publicaties)}"
)

print(
    f"Unieke co-auteursrelaties: {len(coauteur_publicaties)}"
)


print()
print("=" * 80)
print("CO-AUTEURSRELATIES")
print("=" * 80)


gesorteerde_relaties = sorted(
    coauteur_publicaties.items(),
    key=lambda item: len(item[1]),
    reverse=True
)


for (persoon_1, persoon_2), pmids in gesorteerde_relaties:

    print()
    print(
        f"{naam_per_id[persoon_1]} "
        f"<-> "
        f"{naam_per_id[persoon_2]}"
    )

    print(
        f"Gezamenlijke publicaties: {len(pmids)}"
    )

    print(
        "PMIDs: "
        + ", ".join(
            sorted(pmids)[:10]
        )
    )


conn.close()
