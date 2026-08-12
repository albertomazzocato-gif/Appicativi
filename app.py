import streamlit as str_app

# Configurazione della pagina principale
str_app.set_page_config(
    page_title="Hub Applicazioni",
    page_icon="🚀",
    layout="centered"
)

str_app.title("🚀 Le mie Applicazioni")
str_app.write("Benvenuto nel tuo pannello di controllo centrale. Seleziona l'applicazione che desideri avviare:")

str_app.markdown("---")

# Sezione App su Streamlit
str_app.subheader("📊 Applicazioni Web (Streamlit)")

# Sostituisci i link tra parentesi tonde con i tuoi veri link di Streamlit
str_app.page_link("https://applicativi-s3drpw6hdt6rqxzmwdpprz.streamlit.app/", label="Calcolatore di Interessi", icon="💰")
str_app.page_link("https://applicativi-uzkwbpzwvfc6gtbg8mtrsp.streamlit.app/", label="Compensi per Avvocati", icon="⚖️")
str_app.page_link("https://applicativi-ecihnvbseondgzcmlttcng.streamlit.app/", label="Gestionale di Magazzino", icon="📦")
str_app.page_link("https://applicativi-pzvnvsrqnwgqsxznbcaxre.streamlit.app/", label="Preventivi per Imbianchini", icon="🖌️")

str_app.markdown("---")

# Sezione Collegamenti a GitHub
str_app.subheader("📂 Codice Sorgente (GitHub)")
str_app.write("Se vuoi visualizzare i codici sorgente originali nel repository `Applicativi`:")

# Sostituisci con il link diretto alla cartella o al repository su GitHub
str_app.markdown("- [🔗 Visualizza il repository su GitHub](https://github.com/tuonome/Applicativi)")
str_app.markdown("- [🔗 Cartella Calcolatore Interessi](https://github.com/tuonome/Applicativi/tree/main/CalcolatoreInteressi)")
