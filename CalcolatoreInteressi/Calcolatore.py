from datetime import datetime
import os
import openpyxl
import streamlit as st

EXCEL_STORICO = "storico_calcoli_legali.xlsx"


def inizializza_storico():
  if not os.path.exists(EXCEL_STORICO):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Calcoli Legali"
    ws.append([
        "Data Calcolo",
        "Cliente",
        "Capitale Iniziale (€)",
        "Data Inizio",
        "Data Fine",
        "Totale Interessi (€)",
        "Totale Rivalutato (€)",
    ])
    wb.save(EXCEL_STORICO)


# Inizializza il file Excel dello storico all'avvio
inizializza_storico()

# Configurazione pagina Streamlit
st.set_page_config(
    page_title="Calcolatore Legale - Interessi e Rivalutazione",
    layout="centered",
)

# Header personalizzato
st.markdown(
    "<h2 style='color: #1b4f72; text-align: center;'>CALCOLATORE LEGALE: INTERESSI"
    " & RIVALUTAZIONE</h2>",
    unsafe_allow_html=True,
)
st.write("")

# Form di inserimento dati
with st.form("form_calcolatore_legale"):
  st.subheader("📋 Dati della Pratica")

  cliente = st.text_input("Nome Cliente / Pratica:", value="Mario Rossi")
  cap_str = st.text_input("Capitale Iniziale (€):", value="10000")

  col1, col2 = st.columns(2)
  with col1:
    data_inizio_str = st.text_input(
        "Data Inizio (AAAA-MM-GG):", value="2022-01-01"
    )
  with col2:
    data_fine_str = st.text_input(
        "Data Fine (AAAA-MM-GG):",
        value=datetime.now().strftime("%Y-%m-%d"),
    )

  tasso_str = st.text_input("Tasso Interesse Legale Annuo (%):", value="2.5")

  submit_btn = st.form_submit_button(
      label="Esegui Calcolo Istantaneo", use_container_width=True
  )

if submit_btn:
  if not cliente or not cap_str or not data_inizio_str or not data_fine_str or not tasso_str:
    st.error("Tutti i campi sono obbligatori!")
  else:
    try:
      capitale = float(cap_str.replace(",", "."))
      tasso = float(tasso_str.replace(",", "."))
      d_inizio = datetime.strptime(data_inizio_str, "%Y-%m-%d")
      d_fine = datetime.strptime(data_fine_str, "%Y-%m-%d")
    except ValueError:
      st.error(
          "Controlla che i numeri siano validi e le date siano nel formato"
          " AAAA-MM-GG."
      )
      st.stop()

    if d_inizio >= d_fine:
      st.error("La 'Data Inizio' deve essere precedente alla 'Data Fine'.")
    else:
      giorni = (d_fine - d_inizio).days
      anni = giorni / 365.25

      interessi = capitale * (tasso / 100.0) * anni
      coefficiente_rivalutazione_stimato = 1.025 ** anni
      capitale_rivalutato = capitale * coefficiente_rivalutazione_stimato
      maggior_valore_rivalutazione = capitale_rivalutato - capitale

      totale_dovuto = capitale + interessi + maggior_valore_rivalutazione

      # Salvataggio nel file Excel storico
      try:
        wb = openpyxl.load_workbook(EXCEL_STORICO)
        ws = wb.active
        ws.append([
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            cliente,
            capitale,
            data_inizio_str,
            data_fine_str,
            round(interessi, 2),
            round(totale_dovuto, 2),
        ])
        wb.save(EXCEL_STORICO)
      except Exception as e:
        st.warning(f"Errore durante il salvataggio su Excel: {e}")

      # Visualizzazione dei risultati in stile report pulito
      st.success("Calcolo eseguito e salvato nello storico con successo!")

      st.markdown("### Report Risultati")
      report_markdown = f"""
--------------------------------------------------
**PRATICA / CLIENTE:** {cliente.upper()}
--------------------------------------------------
* **Capitale Storico:** € {capitale:,.2f}
* **Periodo considerato:** {giorni} giorni ({anni:.2f} anni)
* **Interessi Legali maturati:** € {interessi:,.2f}
* **Rivalutazione Monetaria:** € {maggior_valore_rivalutazione:,.2f}
--------------------------------------------------
### **TOTALE COMPLESSIVO DOVUTO:** € {totale_dovuto:,.2f}
--------------------------------------------------
"""
      st.markdown(report_markdown)