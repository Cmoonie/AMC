import streamlit as st

st.set_page_config(layout="centered")

def login_pagina():
    st.set_page_config(layout="centered")
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔐 Spider — Inloggen")
    st.subheader("Voer je gegevens in om toegang te krijgen")
    
    gebruikersnaam = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Inloggen"):
            # Check hardcoded admin
            if gebruikersnaam == "admin" and wachtwoord == "spider2026":
                st.session_state.ingelogd = True
                st.session_state.rol = "beheerder"
                st.session_state.gebruikersnaam = "Admin"
                st.switch_page("pages/beheer.py")
            else:
                # Check database gebruikers
                import sqlite3
                import os
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spider.db")
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM gebruikers WHERE gebruikersnaam = ? AND wachtwoord = ?",
                               (gebruikersnaam, wachtwoord))
                gebruiker = cursor.fetchone()
                
                if gebruiker:
                    st.session_state.ingelogd = True
                    st.session_state.rol = gebruiker[5]
                    st.session_state.gebruikersnaam = gebruiker[1]
                    st.rerun()
                else:
                    st.error("Onjuiste gebruikersnaam of wachtwoord!")
    
    with col2:
        if st.button("📝 Registreren"):
            st.switch_page("pages/registreren.py")