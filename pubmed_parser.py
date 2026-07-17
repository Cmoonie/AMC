import sqlite3
import os

def parse_pubmed_file(bestandsnaam):
    with open(bestandsnaam, encoding='utf-8') as f:
        inhoud = f.read()
    
    records = []
    for blok in inhoud.strip().split('\n\n'):
        record = {}
        for regel in blok.split('\n'):
            if regel.startswith('PMID-'):
                record['pmid'] = regel.replace('PMID-', '').strip()
            elif regel.startswith('TI  -'):
                record['title'] = regel.replace('TI  -', '').strip()
            elif regel.startswith('AB  -'):
                record['abstract'] = regel.replace('AB  -', '').strip()
            elif regel.startswith('AU  -'):
                record.setdefault('authors', []).append(regel.replace('AU  -', '').strip())
            elif regel.startswith('DP  -'):
                record['year'] = regel.replace('DP  -', '').strip()[:4]
            elif regel.startswith('OT  -'):
                record.setdefault('keywords', []).append(regel.replace('OT  -', '').strip())
            elif regel.startswith('MH  -'):
                record.setdefault('mesh_terms', []).append(regel.replace('MH  -', '').strip())
        
        if 'pmid' in record:
            record['authors'] = '; '.join(record.get('authors', []))
            record['keywords'] = '; '.join(record.get('keywords', []))
            record['mesh_terms'] = '; '.join(record.get('mesh_terms', []))
            records.append(record)
    
    return records

# Importeer alle bestanden
conn = sqlite3.connect("spider.db")
cursor = conn.cursor()

data_map = 'Data'
bestanden = [f for f in os.listdir(data_map) if f.startswith('csv-') and f.endswith('.csv')]

totaal = 0
for bestand in bestanden:
    pad = os.path.join(data_map, bestand)
    records = parse_pubmed_file(pad)
    for r in records:
        cursor.execute("""
            INSERT OR IGNORE INTO publications (pmid, year, title, authors, abstract, keywords, mesh_terms)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (r.get('pmid'), r.get('year'), r.get('title'), r.get('authors'),
              r.get('abstract'), r.get('keywords'), r.get('mesh_terms')))
    totaal += len(records)
    print(f"{bestand}: {len(records)} publicaties")

conn.commit()
conn.close()
print(f"\nTotaal: {totaal} publicaties geïmporteerd!")