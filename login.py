import streamlit as st

st.set_page_config(layout="centered")

def login_pagina():
    st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)
    st.title("🔐 Spider — Inloggen")
    st.subheader("Voer je gegevens in om toegang te krijgen")
    
    gebruikersnaam = st.text_input("Gebruikersnaam")
    wachtwoord = st.text_input("Wachtwoord", type="password")
    
    if st.button("Inloggen"):
        if gebruikersnaam == "admin" and wachtwoord == "spider2026":
            st.session_state.ingelogd = True
            st.session_state.rol = "beheerder"
            st.session_state.gebruikersnaam = "Admin"

            st.switch_page("pages/beheer.py")
        elif gebruikersnaam == "user" and wachtwoord == "spider123":
            st.session_state.ingelogd = True
            st.session_state.rol = "gebruiker"
            st.session_state.gebruikersnaam = "Gebruiker"

            st.rerun()    
        else:
            st.error("Onjuiste gebruikersnaam of wachtwoord!")