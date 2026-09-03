"""
tests.py — Unit testen voor Spider
Voer uit met: python tests.py
"""

import unittest
import sqlite3
import os
import pandas as pd
import numpy as np
import json

# Database pad
DB_PAD = "spider.db"

class TestDatabaseVerbinding(unittest.TestCase):
    """Test of de database correct verbinding maakt"""

    def test_database_bestaat(self):
        """Controleert of spider.db bestaat"""
        self.assertTrue(os.path.exists(DB_PAD), "spider.db niet gevonden!")

    def test_verbinding_werkt(self):
        """Controleert of verbinding gemaakt kan worden"""
        conn = sqlite3.connect(DB_PAD)
        self.assertIsNotNone(conn)
        conn.close()

    def test_tabellen_bestaan(self):
        """Controleert of alle verplichte tabellen bestaan"""
        conn = sqlite3.connect(DB_PAD)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tabellen = [rij[0] for rij in cursor.fetchall()]
        conn.close()

        verplichte_tabellen = [
            "persons",
            "expertise",
            "persons_expertise",
            "publications",
            "publication_embeddings",
            "profiel_data",
            "wijzigingen",
            "lopende_projecten",
            "project_documenten",
        ]
        for tabel in verplichte_tabellen:
            self.assertIn(tabel, tabellen, f"Tabel '{tabel}' ontbreekt!")


class TestPersonenData(unittest.TestCase):
    """Test of de onderzoekers correct in de database staan"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_drie_onderzoekers(self):
        """Controleert of er precies 3 onderzoekers zijn"""
        df = pd.read_sql("SELECT * FROM persons", self.conn)
        self.assertEqual(len(df), 3, f"Verwacht 3 onderzoekers, gevonden: {len(df)}")

    def test_robert_aanwezig(self):
        """Controleert of Robert de Jonge aanwezig is"""
        df = pd.read_sql("SELECT * FROM persons WHERE name = 'Robert de Jonge'", self.conn)
        self.assertFalse(df.empty, "Robert de Jonge niet gevonden!")

    def test_sjors_aanwezig(self):
        """Controleert of Sjors In 't Veld aanwezig is"""
        df = pd.read_sql("SELECT * FROM persons WHERE name LIKE '%Sjors%'", self.conn)
        self.assertFalse(df.empty, "Sjors In 't Veld niet gevonden!")

    def test_martijn_aanwezig(self):
        """Controleert of Martijn C Schut aanwezig is"""
        df = pd.read_sql("SELECT * FROM persons WHERE name = 'Martijn C Schut'", self.conn)
        self.assertFalse(df.empty, "Martijn C Schut niet gevonden!")


class TestPublicatiesData(unittest.TestCase):
    """Test of publicaties correct zijn geladen"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_publicaties_aanwezig(self):
        """Controleert of er publicaties zijn"""
        df = pd.read_sql("SELECT * FROM publications", self.conn)
        self.assertGreater(len(df), 0, "Geen publicaties gevonden!")

    def test_minimaal_300_publicaties(self):
        """Controleert of er minimaal 300 publicaties zijn"""
        df = pd.read_sql("SELECT * FROM publications", self.conn)
        self.assertGreaterEqual(len(df), 300, f"Te weinig publicaties: {len(df)}")

    def test_publicaties_hebben_titel(self):
        """Controleert of publicaties een titel hebben"""
        df = pd.read_sql("SELECT * FROM publications WHERE title IS NULL", self.conn)
        self.assertEqual(len(df), 0, f"{len(df)} publicaties zonder titel!")

    def test_robert_heeft_publicaties(self):
        """Controleert of Robert publicaties heeft"""
        df = pd.read_sql("SELECT * FROM publications WHERE authors LIKE '%Robert de Jonge%'", self.conn)
        self.assertGreater(len(df), 0, "Geen publicaties van Robert de Jonge!")


class TestExpertiseData(unittest.TestCase):
    """Test of expertise tags correct zijn gekoppeld"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_expertise_aanwezig(self):
        """Controleert of er expertise tags zijn"""
        df = pd.read_sql("SELECT * FROM expertise", self.conn)
        self.assertGreater(len(df), 0, "Geen expertise tags gevonden!")

    def test_robert_heeft_expertise(self):
        """Controleert of Robert expertise tags heeft"""
        df = pd.read_sql("""
            SELECT e.label FROM expertise e
            JOIN persons_expertise pe ON e.id = pe.expertise_id
            JOIN persons p ON pe.person_id = p.id
            WHERE p.name = 'Robert de Jonge'
        """, self.conn)
        self.assertGreater(len(df), 0, "Robert heeft geen expertise tags!")

    def test_methotrexate_gekoppeld(self):
        """Controleert of methotrexate tag aanwezig is"""
        df = pd.read_sql("SELECT * FROM expertise WHERE LOWER(label) LIKE '%methotrexate%'", self.conn)
        self.assertFalse(df.empty, "Methotrexate tag niet gevonden!")

    def test_neurofilament_gekoppeld(self):
        """Controleert of neurofilament tag aanwezig is"""
        df = pd.read_sql("SELECT * FROM expertise WHERE LOWER(label) LIKE '%neurofilament%'", self.conn)
        self.assertFalse(df.empty, "Neurofilament tag niet gevonden!")


class TestEmbeddings(unittest.TestCase):
    """Test of embeddings correct zijn opgeslagen"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_embeddings_aanwezig(self):
        """Controleert of embeddings zijn opgeslagen"""
        df = pd.read_sql("SELECT * FROM publication_embeddings", self.conn)
        self.assertGreater(len(df), 0, "Geen embeddings gevonden!")

    def test_embedding_is_geldig_json(self):
        """Controleert of embeddings geldig JSON zijn"""
        df = pd.read_sql("SELECT embedding FROM publication_embeddings LIMIT 5", self.conn)
        for _, rij in df.iterrows():
            try:
                embedding = json.loads(rij["embedding"])
                self.assertIsInstance(embedding, list, "Embedding is geen lijst!")
                self.assertGreater(len(embedding), 0, "Embedding is leeg!")
            except json.JSONDecodeError:
                self.fail("Embedding is geen geldig JSON!")

    def test_embeddings_zijn_floats(self):
        """Controleert of embeddings numerieke waarden bevatten"""
        df = pd.read_sql("SELECT embedding FROM publication_embeddings LIMIT 1", self.conn)
        embedding = json.loads(df.iloc[0]["embedding"])
        for waarde in embedding[:5]:
            self.assertIsInstance(waarde, float, "Embedding bevat geen floats!")


class TestLopendProjecten(unittest.TestCase):
    """Test of lopende projecten correct zijn ingevoerd"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_drie_projecten(self):
        """Controleert of er 3 lopende projecten zijn"""
        df = pd.read_sql("SELECT * FROM lopende_projecten", self.conn)
        self.assertGreaterEqual(len(df), 3, f"Verwacht minimaal 3 projecten, gevonden: {len(df)}")

    def test_projecten_hebben_naam(self):
        """Controleert of alle projecten een naam hebben"""
        df = pd.read_sql("SELECT * FROM lopende_projecten WHERE naam IS NULL OR naam = ''", self.conn)
        self.assertEqual(len(df), 0, f"{len(df)} projecten zonder naam!")

    def test_documenten_aanwezig(self):
        """Controleert of er documenten zijn gekoppeld"""
        df = pd.read_sql("SELECT * FROM project_documenten", self.conn)
        self.assertGreater(len(df), 0, "Geen documenten gevonden!")


class TestProfielData(unittest.TestCase):
    """Test of profieldata correct is ingevoerd"""

    def setUp(self):
        self.conn = sqlite3.connect(DB_PAD)

    def tearDown(self):
        self.conn.close()

    def test_robert_heeft_bio(self):
        """Controleert of Robert een bio heeft"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT bio FROM profiel_data WHERE gebruikersnaam = 'Robert de Jonge'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "Robert heeft geen profieldata!")
        self.assertGreater(len(result[0]), 0, "Roberts bio is leeg!")

    def test_robert_heeft_email(self):
        """Controleert of Robert een email heeft"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT email FROM profiel_data WHERE gebruikersnaam = 'Robert de Jonge'")
        result = cursor.fetchone()
        self.assertIsNotNone(result, "Robert heeft geen email!")
        self.assertIn("amsterdamumc", result[0], "Email lijkt niet van AMC!")


if __name__ == "__main__":
    print("🕷️ Spider — Unit Testen")
    print("=" * 50)
    unittest.main(verbosity=2)