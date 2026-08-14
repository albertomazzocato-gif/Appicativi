import streamlit as st
import pandas as pd
import os
from datetime import datetime, timezone

# Configurazione Pagina
st.set_page_config(page_title="Logbook Radioamatori", page_icon="📻", layout="wide")
st.title("📻 Logbook Radioamatori")

LOG_FILE = "radio_log.csv"

# --- FUNZIONI LOGBOOK ---
def salva_qso(nominativo, banda, modo, rst_in, rst_out, note):
    data = {
        "Data/Ora (UTC)": [datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")],
        "Nominativo": [nominativo.upper()],
        "Banda": [banda],
        "Modo": [modo],
        "RST In": [rst_in],
        "RST Out": [rst_out],
        "Note": [note]
    }
    nuovo_qso = pd.DataFrame(data)
    
    if os.path.exists(LOG_FILE):
        log = pd.read_csv(LOG_FILE)
        log = pd.concat([log, nuovo_qso], ignore_index=True)
    else:
        log = nuovo_qso
        
    log.to_csv(LOG_FILE, index=False)

# --- SIDEBAR: INSERIMENTO QSO ---
with st.sidebar:
    st.header("➕ Nuovo QSO")
    
    call = st.text_input("Nominativo")
    
    col1, col2 = st.columns(2)
    with col1:
        band = st.selectbox("Banda", ["160m", "80m", "40m", "30m", "20m", "17m", "15m", "12m", "10m", "6m", "2m", "70cm"])
    with col2:
        mode = st.selectbox("Modo", ["SSB", "CW", "FT8", "FT4", "FM", "AM", "RTTY"])
        
    col3, col4 = st.columns(2)
    with col3:
        rst_in = st.text_input("RST In", "59")
    with col4:
        rst_out = st.text_input("RST Out", "59")
        
    note = st.text_input("Note (es. QTH, Nome, Apparati)")
    
    if st.button("💾 Salva QSO", use_container_width=True):
        if call:
            salva_qso(call, band, mode, rst_in, rst_out, note)
            st.success(f"QSO con {call.upper()} salvato con successo!")
        else:
            st.error("⚠️ Il nominativo è obbligatorio!")

# --- INTERFACCIA PRINCIPALE ---
st.subheader("📜 I tuoi contatti radio")

if os.path.exists(LOG_FILE):
    df = pd.read_csv(LOG_FILE)
    
    # Mostra alcune statistiche rapide
    st.caption(f"Totale QSO a log: **{len(df)}**")
    
    # Mostra la tabella (invertita, per avere i QSO più recenti in alto)
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)
else:
    st.info("Il tuo Logbook è ancora vuoto. Inserisci il tuo primo QSO usando il modulo a sinistra!")