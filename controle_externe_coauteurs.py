import sqlite3
import re
from collections import defaultdict
from itertools import combinations


conn = sqlite3.connect("spider.db")
conn.row_factory = sqlite3.Row


# ============================================================
# HULPFUNCTIES
# ============================================================

def normaliseer_naam(naam):
    if not naam:
        return ""

    naam = str(naam).lower().strip()

    naam = re.sub(
        r"[^a-z0-9\s]",
        " ",
        naam
    )

    naam = re.sub(
        r"\s+",
        " ",
        naam
    )

    return naam.strip()


def splits_auteurs(auteurs):
    if not auteurs:
        return []

    auteurs = str(auteurs).strip()

    if ";" in auteurs:
        delen = auteurs.split(";")

    elif "|" in auteurs:
        delen = auteurs.split("|")

    else:
        delen = auteurs.split(",")

    return [
        deel.strip()
        for deel in delen
        if deel.strip()
    ]


def betrouwbare_tussenpersoon(naam):
    """
    Voorlopige veiligheidsfilter.

    Namen zoals:
    'wu y'
    'li f'
    'zhang x'

    zijn te ambigu om betrouwbaar als unieke
    tussenpersoon te gebruiken.

    We eisen daarom minimaal 3 naamdelen.
    Voorbeelden die wel doorgaan:
    'charlotte e teunissen'
    'wiesje m van der flier'
    'martijn w heymans'
    """

    delen = naam.split()

    return len(delen) >= 3


# ============================================================
# SPIDER-ONDERZOEKERS + ALIASSEN
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


namen_per_persoon = defaultdict(set)


for persoon in personen:

    naam = normaliseer_naam(
        persoon["name"]
    )

    if naam:
        namen_per_persoon[
            persoon["id"]
        ].add(naam)


for alias in aliases:

    naam = normaliseer_naam(
        alias["author_name"]
    )

    if naam:
        namen_per_persoon[
            alias["person_id"]
        ].add(naam)


naam_per_id = {
    persoon["id"]: persoon["name"]
    for persoon in personen
}


alle_spider_namen = set()

for namen in namen_per_persoon.values():
    alle_spider_namen.update(namen)


# ============================================================
# PUBLICATIES
# ============================================================

publicaties = conn.execute(
    """
    SELECT pmid, title, authors
    FROM publications
    WHERE authors IS NOT NULL
      AND TRIM(authors) != ''
    """
).fetchall()


# externe auteur
# -> Spider-persoon
# -> PMIDs
extern_naar_spider = defaultdict(
    lambda: defaultdict(set)
)


# Directe Spider <-> Spider relaties.
#
# Hiermee voorkomen we dat een gedeelde mede-auteur
# op dezelfde publicatie ten onrechte als indirecte
# verbinding wordt gepresenteerd.
directe_relaties = defaultdict(set)


# ============================================================
# PUBLICATIES ANALYSEREN
# ============================================================

for publicatie in publicaties:

    pmid = str(
        publicatie["pmid"]
    )

    losse_auteurs = splits_auteurs(
        publicatie["authors"]
    )

    genormaliseerde_auteurs = {
        normaliseer_naam(auteur)
        for auteur in losse_auteurs
        if normaliseer_naam(auteur)
    }


    gevonden_spider_ids = set()


    for persoon_id, bekende_namen in (
        namen_per_persoon.items()
    ):

        if (
            genormaliseerde_auteurs
            & bekende_namen
        ):
            gevonden_spider_ids.add(
                persoon_id
            )


    if not gevonden_spider_ids:
        continue


    # --------------------------------------------------------
    # DIRECTE RELATIES
    # --------------------------------------------------------

    if len(gevonden_spider_ids) >= 2:

        for persoon_1, persoon_2 in combinations(
            sorted(gevonden_spider_ids),
            2
        ):
            directe_relaties[
                (persoon_1, persoon_2)
            ].add(pmid)


    # --------------------------------------------------------
    # EXTERNE CO-AUTEURS
    # --------------------------------------------------------

    externe_auteurs = (
        genormaliseerde_auteurs
        - alle_spider_namen
    )


    for externe_auteur in externe_auteurs:

        if not betrouwbare_tussenpersoon(
            externe_auteur
        ):
            continue

        for persoon_id in gevonden_spider_ids:

            extern_naar_spider[
                externe_auteur
            ][persoon_id].add(
                pmid
            )


# ============================================================
# INDIRECTE VERBINDINGEN
# ============================================================

indirecte_paden = defaultdict(list)


for externe_auteur, verbindingen in (
    extern_naar_spider.items()
):

    spider_ids = sorted(
        verbindingen.keys()
    )

    if len(spider_ids) < 2:
        continue


    for persoon_1, persoon_2 in combinations(
        spider_ids,
        2
    ):

        pmids_1 = verbindingen[
            persoon_1
        ]

        pmids_2 = verbindingen[
            persoon_2
        ]


        # ----------------------------------------------------
        # BELANGRIJKE REGEL
        #
        # Voor een echte indirecte route moeten er
        # TWEE VERSCHILLENDE publicaties bestaan:
        #
        # Spider A -> externe auteur
        # externe auteur -> Spider B
        #
        # Wanneer exact dezelfde PMID beide verbindingen
        # veroorzaakt, is dat geen interessante indirecte
        # route.
        # ----------------------------------------------------

        geldige_combinaties = []


        for pmid_1 in pmids_1:

            for pmid_2 in pmids_2:

                if pmid_1 == pmid_2:
                    continue

                geldige_combinaties.append(
                    (pmid_1, pmid_2)
                )


        if not geldige_combinaties:
            continue


        indirecte_paden[
            (persoon_1, persoon_2)
        ].append(
            {
                "via": externe_auteur,
                "combinaties": geldige_combinaties
            }
        )


# ============================================================
# RESULTATEN
# ============================================================

print()
print("=" * 80)
print("BETROUWBAAR CO-AUTEURSNETWERK SPIDER")
print("=" * 80)

print(
    f"Spider-onderzoekers: {len(personen)}"
)

print(
    f"Publicaties gecontroleerd: {len(publicaties)}"
)

print(
    "Directe Spider-paren: "
    f"{len(directe_relaties)}"
)

print(
    "Betrouwbare externe co-auteurs: "
    f"{len(extern_naar_spider)}"
)

print(
    "Spider-paren met minimaal één geldige "
    f"indirecte verbinding: {len(indirecte_paden)}"
)


print()
print("=" * 80)
print("GELDIGE INDIRECTE VERBINDINGEN")
print("=" * 80)


gesorteerde_paden = sorted(
    indirecte_paden.items(),
    key=lambda item: len(item[1]),
    reverse=True
)


if not gesorteerde_paden:

    print()
    print(
        "Geen geldige indirecte verbindingen gevonden."
    )


for (
    persoon_1,
    persoon_2
), paden in gesorteerde_paden:

    print()
    print("-" * 80)

    print(
        f"{naam_per_id[persoon_1]}"
        f" <-> "
        f"{naam_per_id[persoon_2]}"
    )

    direct = (
        (persoon_1, persoon_2)
        in directe_relaties
    )

    print(
        "Hebben ook directe gezamenlijke publicatie: "
        + ("JA" if direct else "NEE")
    )

    print(
        "Geldige tussenpersonen: "
        f"{len(paden)}"
    )


    for pad in paden[:10]:

        print()

        print(
            f"  via: {pad['via']}"
        )


        # Voor de controle tonen we alleen de eerste
        # geldige combinatie van twee publicaties.
        pmid_1, pmid_2 = (
            pad["combinaties"][0]
        )

        print(
            "    "
            f"{naam_per_id[persoon_1]}"
            f" -> PMID {pmid_1}"
        )

        print(
            "    "
            f"{naam_per_id[persoon_2]}"
            f" -> PMID {pmid_2}"
        )


conn.close()
