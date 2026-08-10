import sqlite3
import streamlit as st


# --- GESTIONE DATABASE ---
def inizializza_db():
  conn = sqlite3.connect("magazzino.db")
  cursor = conn.cursor()
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS ricambi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codice TEXT UNIQUE,
            nome TEXT,
            quantita INTEGER,
            soglia_minima INTEGER
        )
    """)
  conn.commit()
  conn.close()


def esegui_query(query, parametri=()):
  conn = sqlite3.connect("magazzino.db")
  cursor = conn.cursor()
  cursor.execute(query, parametri)
  conn.commit()
  conn.close()


def ottieni_dati(query, parametri=()):
  conn = sqlite3.connect("magazzino.db")
  cursor = conn.cursor()
  cursor.execute(query, parametri)
  righe = cursor.fetchall()
  conn.close()
  return righe


# --- CONFIGURAZIONE PAGINA STREAMLIT ---
st.set_page_config(page_title="Magazzino Ricambi", layout="wide")

# Inizializza il database all'avvio
inizializza_db()

# --- INTESTAZIONE CON LOGO ---
col_logo, col_titolo = st.columns([1, 4])

with col_titolo:
  st.title("Gestione Magazzino Ricambi")
  st.write(
      "   Portale ufficiale per il controllo e lo scarico di ricambi."
  )

st.markdown("---")

# --- SEZIONE RICERCA E FILTRI ---
st.subheader("🔍 Cerca in Magazzino")
col_ricerca, col_reset = st.columns([4, 1])

with col_ricerca:
  filtro = st.text_input(
      "Cerca per nome o codice ricambio:",
      placeholder="Digita qui...",
      label_visibility="collapsed",
  )

# --- QUERY DATI ---
if filtro:
  query = "SELECT id, codice, nome, quantita, soglia_minima FROM ricambi WHERE nome LIKE ? OR codice LIKE ?"
  parametro = f"%{filtro}%"
  righe = ottieni_dati(query, (parametro, parametro))
else:
  righe = ottieni_dati(
      "SELECT id, codice, nome, quantita, soglia_minima FROM ricambi"
  )

# --- VISUALIZZAZIONE TABELLA ---
st.subheader("📦 Elenco Ricambi")

if righe:
  # Creiamo una visualizzazione pulita in tabella
  dati_tabella = []
  for riga in righe:
    id_r, codice, nome, qta, soglia = riga
    # Evidenziamo se è sotto soglia
    stato = "⚠️ Sotto soglia!" if qta <= soglia else "✅ OK"
    dati_tabella.append({
        "ID": id_r,
        "Codice": codice,
        "Nome Ricambio": nome,
        "Quantità": qta,
        "Soglia Minima": soglia,
        "Stato": stato,
    })

  st.dataframe(dati_tabella, use_container_width=True, hide_index=True)
else:
  st.info(
      "Nessun ricambio trovato nel magazzino. Aggiungine uno qui sotto!"
  )

st.markdown("---")

# --- SEZIONE AZIONI: SCARICA O ELIMINA ---
if righe:
  st.subheader("⚡ Azioni Rapide su Articolo")
  # Creiamo un selettore basato sui ricambi presenti
  opzioni_articoli = {
      f"{r[1]} - {r[2]} (Disponibili: {r[3]})": r for r in righe
  }
  articolo_selezionato_str = st.selectbox(
      "Seleziona un articolo per gestirlo:", list(opzioni_articoli.keys())
  )

  if articolo_selezionato_str:
    art = opzioni_articoli[articolo_selezionato_str]
    art_id, art_codice, art_nome, art_qta, art_soglia = art

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
      if st.button("🔽 Scarica 1 pezzo (-)", use_container_width=True):
        if art_qta > 0:
          nuova_qta = art_qta - 1
          esegui_query(
              "UPDATE ricambi SET quantita = ? WHERE id = ?",
              (nuova_qta, art_id),
          )
          st.success(f"Scaricato 1 pezzo di '{art_nome}'. Nuova quantità: {nuova_qta}")
          if nuova_qta <= art_soglia:
            st.warning(
                f"⚠️ ATTENZIONE: Il ricambio è sceso sotto la soglia minima"
                f" ({art_soglia})!"
            )
          st.rerun()
        else:
          st.error("La quantità è già a zero!")

    with col_btn2:
      if st.button("🗑️ Elimina Articolo", use_container_width=True):
        esegui_query("DELETE FROM ricambi WHERE id = ?", (art_id,))
        st.success(f"Articolo '{art_nome}' eliminato con successo.")
        st.rerun()

st.markdown("---")

# --- SEZIONE INSERIMENTO / AGGIORNAMENTO ---
st.subheader("➕ Inserisci o Aggiorna Ricambio")
with st.form("form_inserimento"):
  col1, col2 = st.columns(2)
  with col1:
    codice_input = st.text_input("Codice Ricambio (es. Codice OEM)")
    nome_input = st.text_input("Nome Ricambio")
  with col2:
    qta_input = st.number_input("Quantità", min_value=0, step=1, value=1)
    soglia_input = st.number_input(
        "Soglia Minima (Allarme)", min_value=0, step=1, value=2
    )

  submit_button = st.form_submit_button(
      label="Salva / Aggiorna Articolo nel Magazzino"
  )

  if submit_button:
    if not codice_input or not nome_input:
      st.error("Il Codice e il Nome del ricambio sono obbligatori!")
    else:
      try:
        esegui_query(
            """
                    INSERT INTO ricambi (codice, nome, quantita, soglia_minima) 
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(codice) DO UPDATE SET 
                    nome=excluded.nome, 
                    quantita=excluded.quantita, 
                    soglia_minima=excluded.soglia_minima
                """,
            (codice_input, nome_input, qta_input, soglia_input),
        )
        st.success(
            f"Articolo '{nome_input}' salvato/aggiornato correttamente!"
        )
        st.rerun()
      except Exception as e:
        st.error(f"Errore durante il salvataggio: {e}")
