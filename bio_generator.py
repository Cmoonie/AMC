import os
import re

import pandas as pd
from dotenv import load_dotenv
from groq import Groq


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)
def normaliseer_auteursnaam(tekst):
    """
    Maakt auteursnamen vergelijkbaar zonder hoofdletters,
    spaties en leestekens.
    """
    if tekst is None:
        return ""

    return re.sub(
        r"[^a-z0-9]",
        "",
        str(tekst).lower()
    )

def genereer_bio(naam, persoon_id, conn):
    """
    Genereert een onderzoeksbio op basis van publicaties
    die in Spider aan de onderzoeker gekoppeld kunnen worden.

    De normale naam en PubMed-auteursaliassen worden gebruikt.
    """

    # --------------------------------------------------------
    # 1. Auteursnamen verzamelen
    # --------------------------------------------------------

    auteursnamen = [naam]

    aliases = pd.read_sql(
        """
        SELECT author_name
        FROM person_author_aliases
        WHERE person_id = ?
        """,
        conn,
        params=(persoon_id,)
    )

    for alias in aliases["author_name"].dropna().tolist():
        alias = str(alias).strip()

        if (
            alias
            and alias.lower()
            not in [auteur.lower() for auteur in auteursnamen]
        ):
            auteursnamen.append(alias)

    # --------------------------------------------------------
    # 2. Publicaties zoeken
    # --------------------------------------------------------

        publicaties = pd.read_sql(
        """
        SELECT
            pmid,
            year,
            title,
            abstract,
            keywords,
            mesh_terms,
            authors
        FROM publications
        ORDER BY year DESC
        """,
        conn
    )

    genormaliseerde_auteursnamen = [
        normaliseer_auteursnaam(auteursnaam)
        for auteursnaam in auteursnamen
        if auteursnaam
    ]

    publicaties = publicaties[
        publicaties["authors"].fillna("").apply(
            lambda authors: any(
                auteursnaam
                in normaliseer_auteursnaam(authors)
                for auteursnaam
                in genormaliseerde_auteursnamen
            )
        )
    ].head(10)

    if publicaties.empty:
        return None

    # --------------------------------------------------------
    # 3. Publicatiegegevens voorbereiden
    # --------------------------------------------------------

    def veilige_tekst(waarde):
        if waarde is None or pd.isna(waarde):
            return ""

        return str(waarde).strip()

    context_delen = []

    for _, publicatie in publicaties.iterrows():

        titel = veilige_tekst(
            publicatie.get("title")
        )

        abstract = veilige_tekst(
            publicatie.get("abstract")
        )

        keywords = veilige_tekst(
            publicatie.get("keywords")
        )

        mesh = veilige_tekst(
            publicatie.get("mesh_terms")
        )

        jaar = veilige_tekst(
            publicatie.get("year")
        )

        onderdeel = (
            f"Publicatie:\n"
            f"Jaar: {jaar}\n"
            f"Titel: {titel}\n"
            f"Abstract: {abstract[:2500]}\n"
            f"Keywords: {keywords}\n"
            f"MeSH-termen: {mesh}"
        )

        context_delen.append(
            onderdeel
        )

    publicatie_context = (
        "\n\n---\n\n".join(context_delen)
    )

    # --------------------------------------------------------
    # 4. Bio genereren
    # --------------------------------------------------------

    prompt = f"""
Schrijf een korte professionele onderzoeksbio in het Nederlands
voor onderzoeker {naam}.

Gebruik UITSLUITEND de onderstaande publicatiegegevens.

Regels:
- Beschrijf alleen onderzoeksthema's die uit de publicaties blijken.
- Verzin geen functie, beroep, academische titel of opleiding.
- Verzin geen werkgever, afdeling of instelling.
- Verzin geen prijzen, prestaties of persoonlijke informatie.
- Beweer niet dat de onderzoeker hoofdonderzoeker of specialist is
  als dat niet uit de gegevens blijkt.
- Formuleer voorzichtig wanneer meerdere publicaties verschillende
  onderzoeksgebieden laten zien.
- Noem geen informatie die niet uit de aangeleverde gegevens blijkt.
- Schrijf ongeveer 3 tot 5 zinnen.
- Schrijf in helder en professioneel Nederlands.

PUBLICATIEGEGEVENS:

{publicatie_context}
"""

    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    bio = response.choices[0].message.content

    if not bio:
        return None

    return bio.strip()