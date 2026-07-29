import streamlit as st
import sqlite3
import os

# Database verbinding
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"..", "spider.db")
conn = sqlite3.connect(db_path)

def registreer_pagina():
    st.title("📝 Registreren")
    st.subheader("Maak een nieuw account aan")
    
    naam = st.text_input("Volledige naam")
    gebruikersnaam = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    wachtwoord2 = st.text_input("Herhaal wachtwoord", type="password")
    afdeling = st.text_input("Afdeling", value="Division 9")
    
    if st.button("Registreren"):
        if not naam or not gebruikersnaam or not wachtwoord:
            st.error("Vul alle velden in!")
        elif wachtwoord != wachtwoord2:
            st.error("Wachtwoorden komen niet overeen!")
        else:
            cursor = conn.cursor()
            
            # Check of gebruikersnaam al bestaat
            cursor.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = ?", (gebruikersnaam,))
            if cursor.fetchone():
                st.error("Gebruikersnaam al in gebruik!")
            else:
                # Voeg gebruiker toe
                cursor.execute("""
                    INSERT INTO gebruikers (naam, gebruikersnaam, wachtwoord, afdeling, rol)
                    VALUES (?, ?, ?, ?, ?)
                """, (naam, gebruikersnaam, wachtwoord, afdeling, "gebruiker"))
                
                # Voeg ook toe aan persons tabel
                cursor.execute("INSERT INTO persons (name, department) VALUES (?, ?)",
                               (naam, afdeling))


                
                conn.commit()
                st.success(f"✅ Account aangemaakt! Je kan nu inloggen als {gebruikersnaam}.")
                st.switch_page("app.py")

# Roep de functie aan
registreer_pagina()
