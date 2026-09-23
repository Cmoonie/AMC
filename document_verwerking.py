from pypdf import PdfReader
import pandas as pd


def lees_pdf(bestandspad):
    """
    Leest tekst uit een PDF-bestand.
    """

    reader = PdfReader(bestandspad)

    pagina_teksten = []

    for pagina in reader.pages:
        tekst = pagina.extract_text()

        if tekst:
            pagina_teksten.append(tekst)

    return "\n\n".join(pagina_teksten)


def lees_csv(bestandspad):
    """
    Leest een CSV-bestand.

    PubMed exports kunnen tab-gescheiden zijn.
    Daarom probeert Spider eerst tab-gescheiden
    en daarna een normale komma-CSV.
    """

    try:
        dataframe = pd.read_csv(
            bestandspad,
            sep="\t",
            encoding="utf-8"
        )

        # Als alles toch in één kolom terechtkomt,
        # proberen we een normale CSV.
        if len(dataframe.columns) == 1:
            dataframe = pd.read_csv(
                bestandspad,
                encoding="utf-8"
            )

        return dataframe

    except Exception:
        dataframe = pd.read_csv(
            bestandspad,
            encoding="utf-8"
        )

        return dataframe

def verwerk_document(bestandspad):
    """
    Bepaalt automatisch welk type bestand is geüpload
    en gebruikt daarna de juiste verwerking.
    """

    bestandspad_lower = bestandspad.lower()

    if bestandspad_lower.endswith(".pdf"):
        return {
            "type": "pdf",
            "inhoud": lees_pdf(bestandspad)
        }

    elif bestandspad_lower.endswith(".csv"):
        return {
            "type": "csv",
            "inhoud": lees_csv(bestandspad)
        }

    else:
        return {
            "type": "onbekend",
            "inhoud": None
        }
def importeer_publicaties_csv(bestandspad, conn):
    """
    Importeert publicaties uit een PubMed CSV/TSV-bestand.

    Bestaande PMID's worden niet opnieuw toegevoegd.

    Geeft terug:
    {
        "toegevoegd": aantal,
        "overgeslagen": aantal
    }
    """

    dataframe = lees_csv(bestandspad)

    # Kolomnamen opschonen
    dataframe.columns = [
        str(kolom).strip().lower()
        for kolom in dataframe.columns
    ]

    # Veel voorkomende alternatieve PubMed-kolomnamen
    kolom_mapping = {
        "publication year": "year",
        "publication_year": "year",
        "title": "title",
        "journal/book": "journal",
        "journal": "journal",
        "authors": "authors",
        "abstract": "abstract",
        "keywords": "keywords",
        "mesh terms": "mesh_terms",
        "mesh_terms": "mesh_terms",
        "doi": "doi",
        "pmid": "pmid",
        "pubmed_url": "pubmed_url"
    }

    dataframe = dataframe.rename(
        columns=kolom_mapping
    )

    if "pmid" not in dataframe.columns:
        raise ValueError(
            "Geen PMID-kolom gevonden. "
            "Dit lijkt geen ondersteund PubMed CSV-bestand te zijn."
        )

    cursor = conn.cursor()

    toegevoegd = 0
    overgeslagen = 0

    for _, rij in dataframe.iterrows():

        # ----------------------------------------------------
        # PMID
        # ----------------------------------------------------

        pmid = rij.get("pmid")

        if pd.isna(pmid):
            overgeslagen += 1
            continue

        pmid = str(pmid).strip()

        # Excel/pandas kan bijvoorbeeld 12345678.0 maken
        if pmid.endswith(".0"):
            pmid = pmid[:-2]

        if not pmid:
            overgeslagen += 1
            continue

        # ----------------------------------------------------
        # CONTROLEREN OF PUBLICATIE AL BESTAAT
        # ----------------------------------------------------

        bestaand = cursor.execute(
            """
            SELECT pmid
            FROM publications
            WHERE pmid = ?
            """,
            (pmid,)
        ).fetchone()

        if bestaand:
            overgeslagen += 1
            continue

        # ----------------------------------------------------
        # HULPFUNCTIE VOOR LEGE WAARDEN
        # ----------------------------------------------------

        def waarde(kolom):
            if kolom not in dataframe.columns:
                return ""

            inhoud = rij.get(kolom)

            if pd.isna(inhoud):
                return ""

            return str(inhoud).strip()

        # ----------------------------------------------------
        # PUBMED URL
        # ----------------------------------------------------

        pubmed_url = waarde("pubmed_url")

        if not pubmed_url:
            pubmed_url = (
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            )

        # ----------------------------------------------------
        # PUBLICATIE TOEVOEGEN
        # ----------------------------------------------------

        cursor.execute(
            """
            INSERT OR IGNORE INTO publications (
                pmid,
                year,
                title,
                journal,
                authors,
                abstract,
                keywords,
                mesh_terms,
                doi,
                pubmed_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pmid,
                waarde("year"),
                waarde("title"),
                waarde("journal"),
                waarde("authors"),
                waarde("abstract"),
                waarde("keywords"),
                waarde("mesh_terms"),
                waarde("doi"),
                pubmed_url
            )
        )

        toegevoegd += 1

    conn.commit()

    return {
        "gevonden": len(dataframe),
        "toegevoegd": toegevoegd,
        "overgeslagen": overgeslagen
    }    
def parse_pubmed_formaat(bestandspad):
    """
    Leest het PubMed/MEDLINE tekstformaat.

    Ondersteunt onder andere:
    PMID - PubMed ID
    TI   - titel
    AB   - abstract
    AU   - auteurs
    DP   - publicatiedatum
    OT   - keywords
    MH   - MeSH-termen
    JT   - tijdschrift
    LID  - DOI
    """

    with open(
        bestandspad,
        "r",
        encoding="utf-8"
    ) as bestand:
        regels = bestand.readlines()

    records = []
    record = {}

    huidig_veld = None

    for regel in regels:

        regel = regel.rstrip("\n")

        # --------------------------------------------------
        # LEEG REGEL = EINDE VAN RECORD
        # --------------------------------------------------

        if not regel.strip():

            if "pmid" in record:

                record["authors"] = "; ".join(
                    record.get("authors", [])
                )

                record["keywords"] = "; ".join(
                    record.get("keywords", [])
                )

                record["mesh_terms"] = "; ".join(
                    record.get("mesh_terms", [])
                )

                records.append(record)

            record = {}
            huidig_veld = None
            continue

        # --------------------------------------------------
        # NIEUW PUBMED VELD
        # --------------------------------------------------

        if len(regel) >= 6 and regel[4:6] == "- ":

            code = regel[:4].strip()
            waarde = regel[6:].strip()

            huidig_veld = code

            if code == "PMID":
                record["pmid"] = waarde

            elif code == "TI":
                record["title"] = waarde

            elif code == "AB":
                record["abstract"] = waarde

            elif code == "AU":
                record.setdefault(
                    "authors",
                    []
                ).append(waarde)

            elif code == "DP":
                record["year"] = waarde[:4]

            elif code == "OT":
                record.setdefault(
                    "keywords",
                    []
                ).append(waarde)

            elif code == "MH":
                record.setdefault(
                    "mesh_terms",
                    []
                ).append(waarde)

            elif code == "JT":
                record["journal"] = waarde

            elif code in ("LID", "AID"):

                if "[doi]" in waarde.lower():
                    doi = waarde.split()[0]

                    if not record.get("doi"):
                        record["doi"] = doi

        # --------------------------------------------------
        # VERVOLGREGEL
        # PubMed verdeelt lange titels en abstracts
        # over meerdere regels.
        # --------------------------------------------------

        elif regel.startswith("      "):

            vervolg = regel.strip()

            if not vervolg:
                continue

            if huidig_veld == "TI":
                record["title"] = (
                    record.get("title", "")
                    + " "
                    + vervolg
                ).strip()

            elif huidig_veld == "AB":
                record["abstract"] = (
                    record.get("abstract", "")
                    + " "
                    + vervolg
                ).strip()

            elif huidig_veld == "OT":

                if record.get("keywords"):
                    record["keywords"][-1] += (
                        " " + vervolg
                    )

            elif huidig_veld == "MH":

                if record.get("mesh_terms"):
                    record["mesh_terms"][-1] += (
                        " " + vervolg
                    )

    # ------------------------------------------------------
    # LAATSTE RECORD
    # ------------------------------------------------------

    if "pmid" in record:

        record["authors"] = "; ".join(
            record.get("authors", [])
        )

        record["keywords"] = "; ".join(
            record.get("keywords", [])
        )

        record["mesh_terms"] = "; ".join(
            record.get("mesh_terms", [])
        )

        records.append(record)

    # ------------------------------------------------------
    # PUBMED URL TOEVOEGEN
    # ------------------------------------------------------

    for record in records:

        pmid = record.get("pmid", "")

        if pmid:
            record["pubmed_url"] = (
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
            )

    return records

def importeer_pubmed_formaat(
    bestandspad,
    conn
):
    """
    Importeert een PubMed/MEDLINE bestand
    naar de publications tabel.

    Bestaande PMID's worden overgeslagen.
    """

    records = parse_pubmed_formaat(
        bestandspad
    )

    cursor = conn.cursor()

    toegevoegd = 0
    overgeslagen = 0

    for record in records:

        pmid = record.get("pmid", "").strip()

        if not pmid:
            overgeslagen += 1
            continue

        bestaand = cursor.execute(
            """
            SELECT pmid
            FROM publications
            WHERE pmid = ?
            """,
            (pmid,)
        ).fetchone()

        if bestaand:
            overgeslagen += 1
            continue

        cursor.execute(
            """
            INSERT INTO publications (
                pmid,
                year,
                title,
                journal,
                authors,
                abstract,
                keywords,
                mesh_terms,
                doi,
                pubmed_url
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                pmid,
                record.get("year", ""),
                record.get("title", ""),
                record.get("journal", ""),
                record.get("authors", ""),
                record.get("abstract", ""),
                record.get("keywords", ""),
                record.get("mesh_terms", ""),
                record.get("doi", ""),
                record.get("pubmed_url", "")
            )
        )

        toegevoegd += 1

    conn.commit()

    return {
        "gevonden": len(records),
        "toegevoegd": toegevoegd,
        "overgeslagen": overgeslagen
    }
def detecteer_publicatieformaat(bestandspad):
    """
    Probeert automatisch te herkennen of een bestand:

    - PubMed/MEDLINE-formaat bevat
    - een CSV/TSV tabel bevat
    - geen ondersteund publicatieformaat is
    """

    try:
        with open(
            bestandspad,
            "r",
            encoding="utf-8"
        ) as bestand:
            eerste_tekst = bestand.read(10000)

    except UnicodeDecodeError:
        return "onbekend"

    tekst = eerste_tekst.lstrip()

    # PubMed / MEDLINE formaat herkennen
    if (
        tekst.startswith("PMID-")
        or "\nPMID-" in tekst
    ):
        return "pubmed"

    # CSV/TSV herkennen aan bekende kolommen
    eerste_regel = tekst.splitlines()[0].lower()

    bekende_kolommen = [
        "pmid",
        "title",
        "authors",
        "abstract"
    ]

    aantal_gevonden = sum(
        kolom in eerste_regel
        for kolom in bekende_kolommen
    )

    if aantal_gevonden >= 2:
        return "csv"

    return "onbekend" 

def importeer_publicatiebestand(
    bestandspad,
    conn
):
    """
    Centrale publicatie-import voor Spider.

    Spider herkent automatisch of het bestand
    een PubMed/MEDLINE-bestand of CSV/TSV is.
    """

    formaat = detecteer_publicatieformaat(
        bestandspad
    )

    if formaat == "pubmed":

        resultaat = importeer_pubmed_formaat(
            bestandspad,
            conn
        )

        resultaat["formaat"] = "PubMed/MEDLINE"

        return resultaat

    elif formaat == "csv":

        resultaat = importeer_publicaties_csv(
            bestandspad,
            conn
        )

        resultaat["formaat"] = "CSV/TSV"

        return resultaat

    else:
        return {
            "formaat": "onbekend",
            "toegevoegd": 0,
            "overgeslagen": 0
        }