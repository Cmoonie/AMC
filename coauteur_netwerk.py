import re
from collections import defaultdict
from itertools import combinations

from database import get_connection


# ============================================================
# NAAMVERWERKING
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
    Korte auteursnamen zoals 'Wu Y' zijn te ambigu
    om betrouwbaar als tussenpersoon te gebruiken.

    Daarom gebruiken we voorlopig alleen namen met
    minimaal drie naamdelen.
    """

    if not naam:
        return False

    return len(
        naam.split()
    ) >= 3


# ============================================================
# NETWERK OPBOUWEN
# ============================================================

def bouw_coauteur_netwerk():
    """
    Bouwt het publicatienetwerk op basis van:
    - persons
    - person_author_aliases
    - publications

    Geeft directe en indirecte relaties terug.
    """

    conn = get_connection()

    try:
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

        publicaties = conn.execute(
            """
            SELECT pmid, title, authors
            FROM publications
            WHERE authors IS NOT NULL
              AND TRIM(authors) != ''
            """
        ).fetchall()

    finally:
        conn.close()


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


    directe_relaties = defaultdict(set)

    extern_naar_spider = defaultdict(
        lambda: defaultdict(set)
    )


    # ========================================================
    # PUBLICATIES ANALYSEREN
    # ========================================================

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


        # ----------------------------------------------------
        # DIRECTE SPIDER ↔ SPIDER RELATIES
        # ----------------------------------------------------

        if len(gevonden_spider_ids) >= 2:

            for persoon_1, persoon_2 in combinations(
                sorted(gevonden_spider_ids),
                2
            ):
                directe_relaties[
                    (persoon_1, persoon_2)
                ].add(pmid)


        # ----------------------------------------------------
        # EXTERNE CO-AUTEURS
        # ----------------------------------------------------

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


    # ========================================================
    # INDIRECTE RELATIES
    # ========================================================

    indirecte_relaties = defaultdict(list)


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


            indirecte_relaties[
                (persoon_1, persoon_2)
            ].append(
                {
                    "via": externe_auteur,
                    "combinaties": geldige_combinaties
                }
            )


    return {
        "namen": naam_per_id,
        "direct": directe_relaties,
        "indirect": indirecte_relaties
    }


# ============================================================
# VERBINDING TUSSEN TWEE ONDERZOEKERS
# ============================================================

def vind_publicatieconnectie(
    persoon_id_1,
    persoon_id_2,
    netwerk=None
):
    """
    Geeft de beste bekende publicatieconnectie terug.

    Voorrang:
    1. directe gezamenlijke publicatie
    2. indirect via externe co-auteur
    3. geen bekende connectie
    """

    if persoon_id_1 == persoon_id_2:
        return {
            "type": "zelfde_persoon"
        }


    if netwerk is None:
        netwerk = bouw_coauteur_netwerk()


    sleutel = tuple(
        sorted(
            [
                int(persoon_id_1),
                int(persoon_id_2)
            ]
        )
    )


    # ========================================================
    # DIRECT
    # ========================================================

    directe_pmids = netwerk[
        "direct"
    ].get(
        sleutel,
        set()
    )


    if directe_pmids:

        return {
            "type": "direct",
            "aantal_publicaties": len(
                directe_pmids
            ),
            "pmids": sorted(
                directe_pmids
            )
        }


    # ========================================================
    # INDIRECT
    # ========================================================

    indirecte_paden = netwerk[
        "indirect"
    ].get(
        sleutel,
        []
    )


    if indirecte_paden:

        # Voorlopig kiezen we de tussenpersoon met
        # de meeste geldige publicatiecombinaties.
        beste_pad = max(
            indirecte_paden,
            key=lambda pad: len(
                pad["combinaties"]
            )
        )

        pmid_1, pmid_2 = (
            beste_pad[
                "combinaties"
            ][0]
        )

        return {
            "type": "indirect",
            "via": beste_pad["via"],
            "pmid_1": pmid_1,
            "pmid_2": pmid_2,
            "aantal_mogelijke_tussenpersonen": len(
                indirecte_paden
            )
        }


    # ========================================================
    # GEEN VERBINDING
    # ========================================================

    return {
        "type": "geen"
    }