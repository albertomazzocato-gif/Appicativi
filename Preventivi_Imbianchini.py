import streamlit as st
import sqlite3
import os
from datetime import datetime
from fpdf import FPDF

DB_FILE = "preventivi_imbianchino.db"

# --- GESTIONE DATABASE ---
def inizializza_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preventivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT,
            cliente TEXT,
            tipo_lavoro TEXT,
            mq REAL,
            materiale_desc TEXT,
            costo_materiale REAL,
            mano_opera REAL,
            costo_totale REAL
        )
    """)
    conn.commit()
    conn.close()

def salva_su_db(data, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO preventivi (data, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (data, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale))
    conn.commit()
    conn.close()

# --- GENERAZIONE PDF ---
class PDFPreventivo(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, 'PREVENTIVO LAVORI - IMBIANCHINO', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(127, 140, 141)
        self.cell(0, 5, 'Servizi di Tinteggiatura ed Edilizia Leggera', 0, 1, 'L')
        self.ln(10)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 9)
        self.set_text_color(127, 140, 141)
        self.cell(0, 5, 'Preventivo valido per 30 giorni dalla data di emissione.', 0, 1, 'C')
        self.cell(0, 5, 'Condizioni di pagamento da concordare a fine lavori.', 0, 1, 'C')

def genera_pdf(data, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale):
    pdf = PDFPreventivo()
    pdf.add_page()
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(240, 243, 244)
    pdf.cell(0, 8, ' Dettagli Intervento', 0, 1, 'L', fill=True)
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)
    
    pdf.cell(50, 8, 'Data Emissione:', 0, 0)
    pdf.cell(0, 8, f"{data}", 0, 1)
    pdf.cell(50, 8, 'Cliente:', 0, 0)
    pdf.cell(0, 8, f"{cliente}", 0, 1)
    pdf.cell(50, 8, 'Tipo di Lavoro:', 0, 0)
    pdf.cell(0, 8, f"{tipo_lavoro}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font('Arial', 'B', 12)
    pdf.set_fill_color(52, 73, 94)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(90, 8, ' Descrizione Voce', 1, 0, 'L', fill=True)
    pdf.cell(45, 8, ' Quantità / Unità', 1, 0, 'C', fill=True)
    pdf.cell(55, 8, ' Importo', 1, 1, 'R', fill=True)
    
    pdf.set_font('Arial', '', 11)
    pdf.set_text_color(50, 50, 50)
    
    pdf.cell(90, 8, f" Mano d'opera ({tipo_lavoro})", 1, 0, 'L')
    pdf.cell(45, 8, f"{mq} mq", 1, 0, 'C')
    pdf.cell(55, 8, f"EUR {mano_opera:.2f}", 1, 1, 'R')
    
    testo_materiale = f" Materiali ({materiale_desc})" if materiale_desc else " Materiali"
    lunghezza_testo = pdf.get_string_width(testo_materiale)
    
    if lunghezza_testo > 82:
        pdf.cell(135, 8, testo_materiale, 'LTB', 0, 'L')
        pdf.cell(0, 8, '', 'RTB', 0, 'R')
        pdf.set_x(145)
        pdf.cell(55, 8, f"EUR {costo_materiale:.2f}", 1, 1, 'R')
    else:
        pdf.cell(90, 8, testo_materiale, 1, 0, 'L')
        pdf.cell(45, 8, "Forfait", 1, 0, 'C')
        pdf.cell(55, 8, f"EUR {costo_materiale:.2f}", 1, 1, 'R')
    
    pdf.ln(10)
    
    pdf.set_font('Arial', 'B', 14)
    pdf.set_fill_color(232, 248, 245)
    pdf.set_text_color(17, 122, 101)
    pdf.cell(0, 12, f"  COSTO TOTALE PREVENTIVO: EUR {costo_totale:.2f}  ", 1, 1, 'C', fill=True)
    
    nome_file_safe = cliente.replace(" ", "_").lower()
    pdf_filename = f"preventivo_{nome_file_safe}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    pdf.output(pdf_filename)
    return pdf_filename

# --- INTERFACCIA STREAMLIT ---
def main():
    inizializza_db()
    
    st.title("🖌️ Gestionale Preventivi - Imbianchino")
    st.write("Compila i campi per generare il preventivo in PDF e salvarlo nel database.")

    cliente = st.text_input("Nome Cliente *")
    tipo_lavoro = st.text_input("Tipo Lavoro (es. Pareti, Soffitto) *", value="Tinteggiatura pareti interne")
    
    col1, col2 = st.columns(2)
    with col1:
        mq = st.number_input("Metri Quadri (mq)", min_value=0.0, value=120.0, step=1.0)
    with col2:
        prezzo_mq = st.number_input("Prezzo al mq (€)", min_value=0.0, value=5.0, step=0.5)
        
    materiale_desc = st.text_input("Descrizione Materiali Usati", value="Idropittura lavabile")
    costo_materiale = st.number_input("Costo Totale Materiali (€)", min_value=0.0, value=150.0, step=10.0)
    
    if st.button("Salva Preventivo & Genera PDF", type="primary"):
        if not cliente.strip() or not tipo_lavoro.strip():
            st.error("Compila almeno i campi Nome Cliente e Tipo Lavoro!")
            return
            
        mano_opera = mq * prezzo_mq
        costo_totale = mano_opera + costo_materiale
        data_oggi = datetime.now().strftime("%Y-%m-%d")
        
        try:
            salva_su_db(data_oggi, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale)
            pdf_path = genera_pdf(data_oggi, cliente, tipo_lavoro, mq, materiale_desc, costo_materiale, mano_opera, costo_totale)
            
            st.success("Preventivo completato e salvato nel database!")
            
            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Scarica il PDF del Preventivo",
                    data=pdf_file,
                    file_name=pdf_path,
                    mime="application/pdf"
                )
        except Exception as e:
            st.error(f"Errore durante la generazione: {e}")

if __name__ == "__main__":
    main()
