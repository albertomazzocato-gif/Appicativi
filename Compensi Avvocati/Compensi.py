import io
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def calcola_parametri_forensi(valore_causa, fasi_attive):
  if valore_causa <= 1100:
    valori_base = [300, 350, 450, 450]
  elif valore_causa <= 5200:
    valori_base = [600, 700, 900, 900]
  elif valore_causa <= 25000:
    valori_base = [1200, 1400, 1800, 1800]
  elif valore_causa <= 50000:
    valori_base = [2200, 2500, 3200, 3200]
  elif valore_causa <= 250000:
    valori_base = [3500, 4000, 5500, 5500]
  else:
    valori_base = [5000, 6000, 8000, 8000]

  nomi_fasi = [
      "Fase di studio della controversia",
      "Fase introduttiva del giudizio",
      "Fase istruttoria e/o di trattazione",
      "Fase decisionale",
  ]

  dettaglio_fasi = []
  totale_min = 0
  totale_med = 0
  totale_max = 0

  for i, attiva in enumerate(fasi_attive):
    if attiva:
      base = valori_base[i]
      p_min = round(base * 0.55, 2)
      p_med = round(base, 2)
      p_max = round(base * 1.65, 2)

      dettaglio_fasi.append(
          {"fase": nomi_fasi[i], "min": p_min, "med": p_med, "max": p_max}
      )
      totale_min += p_min
      totale_med += p_med
      totale_max += p_max

  return dettaglio_fasi, totale_min, totale_med, totale_max


def valuta_scaglione(valore):
  if valore <= 1100:
    return "Fino a € 1.100"
  elif valore <= 5200:
    return "Da € 1.101 a € 5.200"
  elif valore <= 25000:
    return "Da € 5.201 a € 25.000"
  elif valore <= 50000:
    return "Da € 25.001 a € 50.000"
  elif valore <= 250000:
    return "Da € 50.001 a € 250.000"
  else:
    return "Oltre € 250.000"


def genera_pdf_in_memoria(nome_cliente, tipo_procedimento, valore_causa, fasi_attive):
  buffer = io.BytesIO()
  try:
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    colore_primario = colors.HexColor("#1A365D")
    colore_secondario = colors.HexColor("#2B6CB0")
    colore_testo = colors.HexColor("#2D3748")
    colore_sfondo_tabella = colors.HexColor("#EDF2F7")

    stile_titolo = ParagraphStyle(
        "Titolo",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colore_primario,
        spaceAfter=4,
    )
    stile_sottotitolo = ParagraphStyle(
        "Sub",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#718096"),
        spaceAfter=15,
    )
    stile_h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colore_secondario,
        spaceBefore=10,
        spaceAfter=6,
    )
    stile_testo = ParagraphStyle(
        "Txt", parent=styles["Normal"], fontSize=10, textColor=colore_testo, leading=14
    )
    stile_testo_bold = ParagraphStyle("TxtBold", parent=stile_testo, fontName="Helvetica-Bold")
    stile_cellabu = ParagraphStyle(
        "CellB", parent=styles["Normal"], fontSize=9, textColor=colore_testo, leading=12
    )
    stile_cellath = ParagraphStyle(
        "CellH",
        parent=styles["Normal"],
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=colors.white,
        leading=12,
    )

    # Intestazione
    story.append(Paragraph("STUDIO LEGALE ASSOCIATO", stile_titolo))
    story.append(
        Paragraph(
            "Diritto Civile - Commerciale - Contenzioso e ADR<br/>Via Roma 42, 31040"
            " Montebelluna (TV) | Tel. 0423 000000",
            stile_sottotitolo,
        )
    )
    story.append(
        Paragraph(
            "<b>PROSPETTO INFORMATIVO E PREVENTIVO COMPENSI</b><br/><i>(Art. 4, comma"
            " 5, Decreto Ministeriale n. 55/2014 e ss.mm.ii.)</i>",
            stile_testo,
        )
    )
    story.append(Spacer(1, 10))

    dati_pratica_data = [
        [
            Paragraph("<b>Cliente:</b>", stile_testo),
            Paragraph(nome_cliente, stile_testo),
            Paragraph("<b>Data:</b>", stile_testo),
            Paragraph("Oggi", stile_testo),
        ],
        [
            Paragraph("<b>Tipo Procedimento:</b>", stile_testo),
            Paragraph(tipo_procedimento, stile_testo),
            Paragraph("<b>Valore Controversia:</b>", stile_testo),
            Paragraph(
                f"€ {valore_causa:,.2f} ({valuta_scaglione(valore_causa)})",
                stile_testo,
            ),
        ],
    ]
    t_pratica = Table(dati_pratica_data, colWidths=[110, 180, 100, 150])
    t_pratica.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colore_sfondo_tabella),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ])
    )
    story.append(t_pratica)
    story.append(Spacer(1, 15))

    fasi_dettaglio, t_min, t_med, t_max = calcola_parametri_forensi(
        valore_causa, fasi_attive
    )

    story.append(Paragraph("1. Dettaglio dei Compensi per Fase Processuale", stile_h2))

    tab_fasi_data = [[
        Paragraph("Fase Attività", stile_cellath),
        Paragraph("Compenso Minimo (€)", stile_cellath),
        Paragraph("Compenso Medio (€)", stile_cellath),
        Paragraph("Compenso Massimo (€)", stile_cellath),
    ]]

    for f in fasi_dettaglio:
      tab_fasi_data.append([
          Paragraph(f["fase"], stile_cellabu),
          Paragraph(f"€ {f['min']:,.2f}", stile_cellabu),
          Paragraph(f"€ {f['med']:,.2f}", stile_cellabu),
          Paragraph(f"€ {f['max']:,.2f}", stile_cellabu),
      ])

    tab_fasi_data.append([
        Paragraph("<b>TOTALE COMPENSI</b>", stile_cellabu),
        Paragraph(f"<b>€ {t_min:,.2f}</b>", stile_cellabu),
        Paragraph(f"<b>€ {t_med:,.2f}</b>", stile_cellabu),
        Paragraph(f"<b>€ {t_max:,.2f}</b>", stile_cellabu),
    ])

    t_fasi = Table(tab_fasi_data, colWidths=[200, 95, 95, 150])
    t_fasi.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colore_primario),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -2), 0.5, colors.HexColor("#CBD5E0")),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#E2E8F0")),
            ("LINEABOVE", (0, -1), (-1, -1), 1, colore_primario),
        ])
    )
    story.append(t_fasi)
    story.append(Spacer(1, 15))

    spese_generali = t_med * 0.15
    imponibile_cpa = t_med + spese_generali
    cpa = imponibile_cpa * 0.04
    imponibile_iva = imponibile_cpa + cpa
    iva = imponibile_iva * 0.22
    totale_preventivo = imponibile_iva + iva

    story.append(
        Paragraph(
            "2. Riepilogo Preventivo di Spesa (Parametro Medio di Riferimento)", stile_h2
        )
    )

    riepilogo_data = [
        [
            Paragraph("Compensi Professionali (Valore Medio)", stile_testo),
            Paragraph(f"€ {t_med:,.2f}", stile_testo),
        ],
        [
            Paragraph(
                "Rimborso spese generali forfettarie (15% ex art. 2 D.M. 55/14)", stile_testo
            ),
            Paragraph(f"€ {spese_generali:,.2f}", stile_testo),
        ],
        [
            Paragraph("CPA 4% (Contributo Previdenziale)", stile_testo),
            Paragraph(f"€ {cpa:,.2f}", stile_testo),
        ],
        [
            Paragraph("IVA 22% (sul totale imponibile)", stile_testo),
            Paragraph(f"€ {iva:,.2f}", stile_testo),
        ],
        [
            Paragraph("<b>TOTALE STIMATO COMPLESSIVO</b>", stile_testo_bold),
            Paragraph(f"<b>€ {totale_preventivo:,.2f}</b>", stile_testo_bold),
        ],
    ]

    t_riepilogo = Table(riepilogo_data, colWidths=[350, 190])
    t_riepilogo.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -2), colore_sfondo_tabella),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#FEFCBF")),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
            ("LINEABOVE", (0, -1), (-1, -1), 1.5, colore_primario),
        ])
    )
    story.append(t_riepilogo)
    story.append(Spacer(1, 20))

    note_testo = (
        "<b>Note informative:</b> Il presente preventivo ha carattere puramente indicativo e"
        " viene formulato sulla base delle fasi processuali attualmente prevedibili, ai"
        " sensi della Legge n. 124/2017 sulla concorrenza e trasparenza."
    )
    story.append(
        Paragraph(
            note_testo,
            ParagraphStyle(
                "Note",
                parent=stile_testo,
                fontSize=8,
                leading=11,
                textColor=colors.HexColor("#4A5568"),
            ),
        )
    )
    story.append(Spacer(1, 30))

    firme_data = [[
        Paragraph(
            "<b>Firma per accettazione del"
            " cliente</b><br/><br/><br/>___________________________",
            stile_testo,
        ),
        Paragraph(
            "<b>L'Avvocato</b><br/><br/><br/>___________________________", stile_testo
        ),
    ]]
    t_firme = Table(firme_data, colWidths=[270, 270])
    t_firme.setStyle(
        TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (1, 0), (1, -1), "RIGHT")])
    )
    story.append(KeepTogether(t_firme))

    doc.build(story)
    buffer.seek(0)
    return buffer
  except Exception as e:
    st.error(f"Errore durante la generazione del PDF: {str(e)}")
    return None


# --- INTERFACCIA GRAFICA STREAMLIT ---
st.set_page_config(page_title="Calcolatore Preventivi Legali", layout="centered")

st.markdown(
    "<h2 style='color: #1A365D; text-align: center;'>Generatore Preventivo"
    " Forense</h2>",
    unsafe_allow_html=True,
)
st.write("")

# Form di inserimento dati
with st.form("form_preventivo"):
  st.subheader("📋 Dati Pratica")

  cliente = st.text_input("Nome Cliente", value="Mario Rossi")
  tipo_procedimento = st.text_input(
      "Tipo Procedimento", value="Civile Ordinario di Cognizione"
  )
  valore_str = st.text_input("Valore Causa (€)", value="15000")

  st.subheader("⚙️ Fasi Processuali Previste")
  chk_studio = st.checkbox("Fase di Studio della controversia", value=True)
  chk_intro = st.checkbox("Fase Introduttiva del giudizio", value=True)
  chk_istr = st.checkbox("Fase Istruttoria e/o di trattazione", value=True)
  chk_dec = st.checkbox("Fase Decisionale", value=True)

  submit_btn = st.form_submit_button(
      label="Genera Preventivo PDF", use_container_width=True
  )

if submit_btn:
  if not cliente or not tipo_procedimento or not valore_str:
    st.warning("Tutti i campi devono essere compilati.")
  else:
    try:
      valore_causa = float(valore_str)
    except ValueError:
      st.error("Il valore della causa deve essere un numero valido.")
      st.stop()

    fasi = [chk_studio, chk_intro, chk_istr, chk_dec]

    if not any(fasi):
      st.warning("Seleziona almeno una fase processuale.")
    else:
      pdf_buffer = genera_pdf_in_memoria(
          cliente, tipo_procedimento, valore_causa, fasi
      )
      if pdf_buffer:
        st.success("Preventivo generato con successo!")
        nome_file_download = f"preventivo_{cliente.replace(' ', '_')}.pdf"
        st.download_button(
            label="📥 Clicca qui per scaricare il PDF",
            data=pdf_buffer,
            file_name=nome_file_download,
            mime="application/pdf",
            use_container_width=True,
        )