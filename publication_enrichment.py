import sqlite3
from pathlib import Path


# ============================================================
# DATABASE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "spider.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# ONDERZOEKSMETHODEN
# ============================================================

# Eerste gecontroleerde lijst.
# Later kunnen we deze uitbreiden of AI gebruiken voor gevallen
# die niet met voldoende zekerheid herkend kunnen worden.
ONDERZOEKSMETHODEN = {
    "linear regression": [
        "linear regression",
        "linear regression modelling",
        "linear regression modeling",
        "multivariate linear regression",
        "multivariable linear regression",
    ],

    "logistic regression": [
        "logistic regression",
        "multivariable logistic regression",
        "multivariate logistic regression",
    ],

    "machine learning": [
        "machine learning",
        "deep learning",
        "neural network",
        "neural networks",
    ],

    "randomized controlled trial": [
        "randomized controlled trial",
        "randomised controlled trial",
        "randomized clinical trial",
        "randomised clinical trial",
        "rct",
    ],

    "cohort study": [
        "cohort study",
        "cohort studies",
        "prospective cohort",
        "retrospective cohort",
    ],

    "case-control study": [
        "case-control study",
        "case control study",
    ],

    "cross-sectional study": [
        "cross-sectional study",
        "cross sectional study",
    ],

    "systematic review": [
        "systematic review",
        "systematic literature review",
    ],

    "meta-analysis": [
        "meta-analysis",
        "meta analysis",
    ],

    "qualitative research": [
        "qualitative study",
        "qualitative research",
        "qualitative analysis",
    ],

    "mass spectrometry": [
        "mass spectrometry",
        "tandem mass spectrometry",
    ],

    "chromatography": [
        "chromatography",
        "liquid chromatography",
    ],
}


# ============================================================
# METHODEN HERKENNEN
# ============================================================

def herken_onderzoeksmethoden(publicatie):
    """
    Zoekt onderzoeksmethoden in titel, keywords en MeSH-termen.

    Geeft per gevonden methode ook terug uit welke bron
    de herkenning afkomstig is.
    """

    bronnen = {
        "title": publicatie["title"] or "",
        "keyword": publicatie["keywords"] or "",
        "mesh": publicatie["mesh_terms"] or "",
    }

    gevonden = {}

    for methode, zoektermen in ONDERZOEKSMETHODEN.items():

        gevonden_bronnen = set()

        for bron, tekst in bronnen.items():

            tekst_lower = str(tekst).lower()

            for zoekterm in zoektermen:

                if zoekterm.lower() in tekst_lower:
                    gevonden_bronnen.add(bron)
                    break

        if gevonden_bronnen:
            gevonden[methode] = sorted(gevonden_bronnen)

    return gevonden


# ============================================================
# TESTEN
# ============================================================

def test_onderzoeksmethoden(limiet=20):

    conn = get_connection()

    publicaties = conn.execute(
        """
        SELECT
            pmid,
            year,
            title,
            keywords,
            mesh_terms
        FROM publications
        WHERE
            keywords IS NOT NULL
            OR mesh_terms IS NOT NULL
        ORDER BY year DESC
        LIMIT ?
        """,
        (limiet,)
    ).fetchall()

    aantal_met_methode = 0

    for publicatie in publicaties:

        methoden = herken_onderzoeksmethoden(
            publicatie
        )

        if not methoden:
            continue

        aantal_met_methode += 1

        print()
        print("=" * 80)
        print(f"PMID: {publicatie['pmid']}")
        print(f"JAAR: {publicatie['year']}")
        print(f"TITEL: {publicatie['title']}")
        print()

        for methode, bronnen in methoden.items():

            print(
                f"  Methode: {methode}"
            )

            print(
                f"  Bron: {', '.join(bronnen)}"
            )

            print()

    print("=" * 80)

    print(
        f"{aantal_met_methode} van de "
        f"{len(publicaties)} publicaties "
        "hadden minimaal één herkende onderzoeksmethode."
    )

    conn.close()



# ============================================================
# ONDERZOEKSMETHODEN OPSLAAN
# ============================================================

def sla_onderzoeksmethoden_op():

    conn = get_connection()

    publicaties = conn.execute(
        """
        SELECT
            pmid,
            year,
            title,
            keywords,
            mesh_terms
        FROM publications
        """
    ).fetchall()

    aantal_toegevoegd = 0
    aantal_gevonden = 0

    for publicatie in publicaties:

        methoden = herken_onderzoeksmethoden(
            publicatie
        )

        for methode, bronnen in methoden.items():

            aantal_gevonden += 1

            # Bijvoorbeeld:
            # keyword
            # mesh
            # keyword, mesh, title
            bron = ", ".join(bronnen)

            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO publicatie_verrijkingen (
                    pmid,
                    categorie,
                    waarde,
                    bron
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(publicatie["pmid"]),
                    "Onderzoeksmethode",
                    methode,
                    bron
                )
            )

            if cursor.rowcount > 0:
                aantal_toegevoegd += 1

    conn.commit()
    conn.close()

    print()
    print("=" * 80)
    print(
        f"{aantal_gevonden} methode-koppelingen gevonden."
    )
    print(
        f"{aantal_toegevoegd} nieuwe koppelingen opgeslagen."
    )
    print("=" * 80)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    sla_onderzoeksmethoden_op()    