# 🕷️ Spider — AMC Kenniscentrum

Een AI-gestuurde zoektool voor onderzoeksexpertise binnen Division 9 van Amsterdam UMC.

## Wat doet deze app?

- Zoek op naam, expertise of project via keyword search én semantisch zoeken
- Vind onderzoekers en hun verbindingen via de kennisgraaf
- Bekijk profielpagina's met publicaties, expertise en lopende projecten
- AI genereert automatisch een samenvatting van de zoekresultaten
- Beheerpaneel voor het toevoegen en beheren van data

## Technologie

- Python 3.14+
- Streamlit
- SQLite
- Sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- Groq AI (llama-3.3-70b)
- Pandas

## Installatie

1. Clone de repository:
   git clone https://github.com/Cmoonie/AMC
   cd AMC

2. Installeer de dependencies:
   pip install -r requirements.txt

3. Maak een .env bestand aan:
   GROQ_API_KEY=jouw_sleutel_hier

4. Maak de database aan:
   python database.py

5. Laad de PubMed data:
   python pubmed_parser.py
   python keywords_to_expertise.py
   python embeddings.py

6. Start de app:
   py -m streamlit run app.py

## Projectstructuur

- app.py — Zoekpagina (home)
- login.py — Login functie
- database.py — Database setup
- embeddings.py — Semantisch zoeken embeddings
- keywords_to_expertise.py — Keywords naar expertise tags
- pubmed_parser.py — PubMed data inladen
- tests.py — Unit testen
- pages/ — Alle subpagina's

## Testen

python tests.py

## Status

Proof of Concept — ontwikkeld als afstudeerproject bij Amsterdam UMC Division 9
Student: Cecilia Anim | Windesheim 2026
