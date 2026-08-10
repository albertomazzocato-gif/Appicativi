with st.form("form_calcolatore_legale"):
    st.subheader("📋 Dati della Pratica")

    cliente = st.text_input("Nome Cliente / Pratica:", value="Mario Rossi")
    cap_str = st.text_input("Capitale Iniziale (€):", value="10000")

    col1, col2 = st.columns(2)
    with col1:
        data_inizio_str = st.text_input("Data Inizio (GG/MM/AAAA):", value="01/01/2022")
    with col2:
        data_fine_str = st.text_input("Data Fine (GG/MM/AAAA):", value=datetime.now().strftime("%d/%m/%Y"))

    tasso_str = st.text_input("Tasso Interesse Legale Annuo (%):", value="2.5")

    submit_btn = st.form_submit_button(label="Esegui Calcolo Istantaneo", use_container_width=True)