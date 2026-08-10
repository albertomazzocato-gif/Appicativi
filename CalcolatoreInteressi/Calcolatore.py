# --- Modifica nel FORM ---
  col1, col2 = st.columns(2)
  with col1:
    data_inizio_str = st.text_input(
        "Data Inizio (GG/MM/AAAA):", value="01/01/2022"
    )
  with col2:
    data_fine_str = st.text_input(
        "Data Fine (GG/MM/AAAA):",
        value=datetime.now().strftime("%d/%m/%Y"),
    )

  # ... (resto del codice fino al submit_btn) ...

if submit_btn:
  # ... (controlli precedenti) ...
    try:
      capitale = float(cap_str.replace(",", "."))
      tasso = float(tasso_str.replace(",", "."))
      # --- Modifica qui: usa %d/%m/%Y ---
      d_inizio = datetime.strptime(data_inizio_str, "%d/%m/%Y")
      d_fine = datetime.strptime(data_fine_str, "%d/%m/%Y")
    except ValueError:
      st.error(
          "Controlla che i numeri siano validi e le date siano nel formato"
          " GG/MM/AAAA (es: 01/01/2022)."
      )
      st.stop()