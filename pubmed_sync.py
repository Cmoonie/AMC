import os
import tempfile
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

from document_verwerking import importeer_pubmed_formaat


EUTILS_BASE = (
    "https://eutils.ncbi.nlm.nih.gov/"
    "entrez/eutils/"
)

TOOL_NAME = "SpiderResearchSearch"


def _request(url, params):
    """
    Voert een request uit naar de officiële
    NCBI E-utilities API.
    """

    query = urllib.parse.urlencode(params)

    volledige_url = (
        url
        + "?"
        + query
    )

    request = urllib.request.Request(
        volledige_url,
        headers={
            "User-Agent": "SpiderResearchSearch/1.0"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=30
    ) as response:

        return response.read()


def zoek_pubmed_pmids(
    auteursnaam,
    maximaal=100
):
    """
    Zoekt PubMed-publicaties voor één auteursnaam.

    Geeft een lijst met PMID's terug.
    """

    auteursnaam = auteursnaam.strip()

    if not auteursnaam:
        return []

    zoekterm = (
        f'"{auteursnaam}"[Author]'
    )

    data = _request(
        EUTILS_BASE + "esearch.fcgi",
        {
            "db": "pubmed",
            "term": zoekterm,
            "retmode": "xml",
            "retmax": maximaal,
            "tool": TOOL_NAME,
        }
    )

    root = ET.fromstring(data)

    pmids = []

    for element in root.findall(
        ".//IdList/Id"
    ):
        if element.text:
            pmids.append(
                element.text.strip()
            )

    return pmids


def haal_pubmed_records_op(pmids):
    """
    Haalt volledige PubMed-records op
    voor een lijst met PMID's.

    PubMed levert MEDLINE-tekst terug.
    """

    if not pmids:
        return ""

    data = _request(
        EUTILS_BASE + "efetch.fcgi",
        {
            "db": "pubmed",
            "id": ",".join(pmids),
            "rettype": "medline",
            "retmode": "text",
            "tool": TOOL_NAME,
        }
    )

    return data.decode(
        "utf-8",
        errors="replace"
    )


def synchroniseer_auteursnaam(
    auteursnaam,
    conn,
    maximaal=100
):
    """
    Zoekt publicaties voor één PubMed-auteursnaam,
    haalt de MEDLINE-records op en importeert
    nieuwe publicaties in Spider.

    Bestaande PMID's worden door de bestaande
    importfunctie automatisch overgeslagen.
    """

    pmids = zoek_pubmed_pmids(
        auteursnaam,
        maximaal=maximaal
    )

    if not pmids:
        return {
            "auteursnaam": auteursnaam,
            "gevonden": 0,
            "toegevoegd": 0,
            "overgeslagen": 0
        }

    medline_tekst = haal_pubmed_records_op(
        pmids
    )

    if not medline_tekst.strip():
        return {
            "auteursnaam": auteursnaam,
            "gevonden": len(pmids),
            "toegevoegd": 0,
            "overgeslagen": 0
        }

    tijdelijk_pad = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            encoding="utf-8",
            delete=False
        ) as tijdelijk_bestand:

            tijdelijk_bestand.write(
                medline_tekst
            )

            tijdelijk_pad = (
                tijdelijk_bestand.name
            )

        resultaat = importeer_pubmed_formaat(
            tijdelijk_pad,
            conn
        )

        resultaat["auteursnaam"] = (
            auteursnaam
        )

        return resultaat

    finally:
        if (
            tijdelijk_pad
            and os.path.exists(tijdelijk_pad)
        ):
            os.remove(tijdelijk_pad)


def synchroniseer_onderzoeker(
    person_id,
    conn,
    maximaal_per_alias=100
):
    """
    Synchroniseert alle PubMed-auteursnamen
    van één onderzoeker.

    De normale onderzoekersnaam wordt ook
    meegenomen.
    """

    cursor = conn.cursor()

    persoon = cursor.execute(
        """
        SELECT name
        FROM persons
        WHERE id = ?
        """,
        (person_id,)
    ).fetchone()

    if persoon is None:
        raise ValueError(
            "Onderzoeker bestaat niet."
        )

    volledige_naam = persoon[0]

    alias_rijen = cursor.execute(
        """
        SELECT author_name
        FROM person_author_aliases
        WHERE person_id = ?
        ORDER BY author_name
        """,
        (person_id,)
    ).fetchall()

    auteursnamen = [
        volledige_naam
    ]

    for rij in alias_rijen:
        alias = str(rij[0]).strip()

        if (
            alias
            and alias.lower()
            not in [
                naam.lower()
                for naam in auteursnamen
            ]
        ):
            auteursnamen.append(alias)

    totaal_gevonden = 0
    totaal_toegevoegd = 0
    totaal_overgeslagen = 0

    resultaten = []

    for auteursnaam in auteursnamen:

        resultaat = synchroniseer_auteursnaam(
            auteursnaam,
            conn,
            maximaal=maximaal_per_alias
        )

        resultaten.append(
            resultaat
        )

        totaal_gevonden += (
            resultaat.get(
                "gevonden",
                0
            )
        )

        totaal_toegevoegd += (
            resultaat.get(
                "toegevoegd",
                0
            )
        )

        totaal_overgeslagen += (
            resultaat.get(
                "overgeslagen",
                0
            )
        )

    return {
        "auteursnamen": auteursnamen,
        "gevonden": totaal_gevonden,
        "toegevoegd": totaal_toegevoegd,
        "overgeslagen": totaal_overgeslagen,
        "resultaten": resultaten
    }