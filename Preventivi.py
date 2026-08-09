import os
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# --- GESTIONE DATABASE ---
def inizializza_db():
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    
    # Tabella Preventivi
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS preventivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            cliente TEXT,
            data TEXT,
            descrizione TEXT,
            totale REAL
        )
    """
    )
    
    # Tabella Clienti (con campi completi)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS clienti (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            piva_cf TEXT,
            indirizzo TEXT,
            localita TEXT,
            telefono TEXT,
            email TEXT
        )
    """
    )
    conn.commit()
    conn.close()


def ottieni_clienti():
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    cursor.execute("SELECT nome FROM clienti ORDER BY nome ASC")
    clienti = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clienti


def ottieni_dati_cliente(nome_cliente):
    """Estrae tutti i dati anagrafici di un cliente specifico dal database."""
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT piva_cf, indirizzo, localita, telefono, email FROM clienti WHERE nome = ?",
        (nome_cliente,)
    )
    risultato = cursor.fetchone()
    conn.close()
    
    if risultato:
        return {
            "piva_cf": risultato[0] or "",
            "indirizzo": risultato[1] or "",
            "localita": risultato[2] or "",
            "telefono": risultato[3] or "",
            "email": risultato[4] or ""
        }
    return {"piva_cf": "", "indirizzo": "", "localita": "", "telefono": "", "email": ""}


def genera_prossimo_numero():
    anno_corrente = datetime.date.today().strftime("%Y")
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT numero FROM preventivi WHERE numero LIKE ? ORDER BY id DESC LIMIT 1", (f"{anno_corrente}/%",))
    risultato = cursor.fetchone()
    conn.close()
    
    if risultato:
        ultimo_num = risultato[0]
        try:
            parte_prog = int(ultimo_num.split("/")[1])
            prossimo = parte_prog + 1
        except ValueError:
            prossimo = 1
    else:
        prossimo = 1
        
    return f"{anno_corrente}/{prossimo:02d}"


def salva_cliente_completo_db(nome, piva_cf, indirizzo, localita, telefono, email):
    if not nome.strip():
        return False, "Il campo Cliente è obbligatorio."
    
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO clienti (nome, piva_cf, indirizzo, localita, telefono, email) 
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome.strip(), piva_cf.strip(), indirizzo.strip(), localita.strip(), telefono.strip(), email.strip())
        )
        conn.commit()
        return True, "Cliente salvato con successo!"
    except sqlite3.IntegrityError:
        return False, f"Il cliente '{nome}' è già presente in archivio."
    except Exception as e:
        return False, f"Errore: {e}"
    finally:
        conn.close()


def salva_preventivo_db(numero, cliente, data, descrizione, totale):
    conn = sqlite3.connect("preventivi.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO preventivi (numero, cliente, data, descrizione, totale)
        VALUES (?, ?, ?, ?, ?)
    """,
        (numero, cliente, data, descrizione, totale),
    )
    conn.commit()
    conn.close()


# --- CREAZIONE PDF ---
def genera_pdf(numero, cliente_nome, data, descrizione, imponibile, iva, totale):
    # Recupera tutti i dati del cliente dal database
    dati_cli = ottieni_dati_cliente(cliente_nome)
    
    cliente_pulito = "".join(c for c in cliente_nome if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')
    num_pulito = numero.replace('/', '_')
    nome_file = f"Preventivo_{num_pulito}_{cliente_pulito}.pdf"
    
    c = canvas.Canvas(nome_file, pagesize=A4)
    width, height = A4

    # Intestazione Azienda
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "OFFICINA MECCANICA / ARTIGIANO")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 65, "Via Artigiana, 10 - Caerano / Montebelluna (TV)")
    c.drawString(50, height - 80, "P.IVA: 01234567890 - Tel: 333 1234567")

    # Linea divisoria
    c.setLineWidth(1)
    c.line(50, height - 95, width - 50, height - 95)

    # Dati Preventivo
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, height - 125, f"PREVENTIVO N. {numero}")
    c.setFont("Helvetica", 10)
    c.drawString(50, height - 145, f"Data: {data}")

    # Blocco Dati Cliente Completo sul PDF
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - 175, "Spettabile Cliente:")
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, height - 190, cliente_nome)
    
    c.setFont("Helvetica", 10)
    y_offset = 205
    if dati_cli["piva_cf"]:
        c.drawString(50, height - y_offset, f"P.IVA / C.F.: {dati_cli['piva_cf']}")
        y_offset += 15
    if dati_cli["indirizzo"] or dati_cli["localita"]:
        c.drawString(50, height - y_offset, f"Indirizzo: {dati_cli['indirizzo']} - {dati_cli['localita']}")
        y_offset += 15
    if dati_cli["telefono"]:
        c.drawString(50, height - y_offset, f"Telefono: {dati_cli['telefono']}")
        y_offset += 15
    if dati_cli["email"]:
        c.drawString(50, height - y_offset, f"Email: {dati_cli['email']}")
        y_offset += 15

    # Tabella Voci (spostata leggermente più in basso per fare spazio ai dati del cliente)
    y_tabella = max(260, y_offset + 25)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, height - y_tabella, "Descrizione Lavori / Ricambi")
    c.drawRightString(width - 50, height - y_tabella, "Importo (€)")
    c.line(50, height - (y_tabella + 5), width - 50, height - (y_tabella + 5))

    # Multilinea per la descrizione
    c.setFont("Helvetica", 10)
    text_object = c.beginText(50, height - (y_tabella + 25))
    text_object.setLeading(15)
    for riga in descrizione.split("\n"):
        text_object.textLine(riga)
    c.drawText(text_object)

    # Totali in basso
    c.line(50, height - 440, width - 50, height - 440)
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 150, height - 460, "Imponibile:")
    c.drawRightString(width - 50, height - 460, f"€ {imponibile:.2f}")

    c.drawRightString(width - 150, height - 480, "IVA (22%):")
    c.drawRightString(width - 50, height - 480, f"€ {iva:.2f}")

    c.setFont("Helvetica-Bold", 12)
    c.drawRightString(width - 150, height - 505, "TOTALE:")
    c.drawRightString(width - 50, height - 505, f"€ {totale:.2f}")

    c.save()
    return nome_file


# --- FINESTRA POPUP NUOVO CLIENTE ---
class FinestraNuovoCliente:
    def __init__(self, parent, callback_aggiorna):
        self.top = tk.Toplevel(parent)
        self.top.title("Inserisci Nuovo Cliente")
        self.top.geometry("450x380")
        self.top.grab_set()
        self.callback_aggiorna = callback_aggiorna

        frame = tk.LabelFrame(self.top, text=" Dati Anagrafici Cliente ")
        frame.pack(fill="both", expand=True, padx=15, pady=15)
        frame.columnconfigure(1, weight=1)

        # Campi
        tk.Label(frame, text="Cliente / Ragione Sociale *").grid(row=0, column=0, padx=10, pady=6, sticky="w")
        self.e_nome = tk.Entry(frame, width=28)
        self.e_nome.grid(row=0, column=1, padx=10, pady=6, sticky="w")

        tk.Label(frame, text="P.IVA o Codice Fiscale").grid(row=1, column=0, padx=10, pady=6, sticky="w")
        self.e_piva = tk.Entry(frame, width=28)
        self.e_piva.grid(row=1, column=1, padx=10, pady=6, sticky="w")

        tk.Label(frame, text="Indirizzo").grid(row=2, column=0, padx=10, pady=6, sticky="w")
        self.e_indirizzo = tk.Entry(frame, width=28)
        self.e_indirizzo.grid(row=2, column=1, padx=10, pady=6, sticky="w")

        tk.Label(frame, text="Località").grid(row=3, column=0, padx=10, pady=6, sticky="w")
        self.e_localita = tk.Entry(frame, width=28)
        self.e_localita.grid(row=3, column=1, padx=10, pady=6, sticky="w")

        tk.Label(frame, text="Telefono").grid(row=4, column=0, padx=10, pady=6, sticky="w")
        self.e_tel = tk.Entry(frame, width=28)
        self.e_tel.grid(row=4, column=1, padx=10, pady=6, sticky="w")

        tk.Label(frame, text="Email").grid(row=5, column=0, padx=10, pady=6, sticky="w")
        self.e_email = tk.Entry(frame, width=28)
        self.e_email.grid(row=5, column=1, padx=10, pady=6, sticky="w")

        btn_salva = tk.Button(
            self.top,
            text="Salva Cliente",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold"),
            command=self.salva_e_chiudi
        )
        btn_salva.pack(pady=10)

    def salva_e_chiudi(self):
        nome = self.e_nome.get()
        piva = self.e_piva.get()
        indirizzo = self.e_indirizzo.get()
        localita = self.e_localita.get()
        tel = self.e_tel.get()
        email = self.e_email.get()

        successo, messaggio = salva_cliente_completo_db(nome, piva, indirizzo, localita, tel, email)
        if successo:
            messagebox.showinfo("Successo", messaggio, parent=self.top)
            self.callback_aggiorna(nome.strip())
            self.top.destroy()
        else:
            messagebox.showerror("Errore", messaggio, parent=self.top)


# --- INTERFACCIA GRAFICA PRINCIPALE ---
class PreventiviApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Generatore Preventivi Light - Officina")
        self.root.geometry("680x680")

        titolo = tk.Label(
            root, text="Generatore Rapido Preventivi con Archivio Clienti", font=("Arial", 15, "bold")
        )
        titolo.pack(pady=10)

        frame = tk.LabelFrame(root, text=" Dati Preventivo e Cliente ")
        frame.pack(fill="both", expand=True, padx=15, pady=5)

        frame.columnconfigure(1, weight=1)

        # Numero Preventivo
        tk.Label(frame, text="Numero Preventivo:").grid(
            row=0, column=0, padx=10, pady=8, sticky="w"
        )
        self.entry_num = tk.Entry(frame, width=25)
        self.entry_num.grid(row=0, column=1, padx=10, pady=8, sticky="w")
        self.entry_num.insert(0, genera_prossimo_numero())

        # Data
        tk.Label(frame, text="Data:").grid(
            row=1, column=0, padx=10, pady=8, sticky="w"
        )
        self.entry_data = tk.Entry(frame, width=25)
        self.entry_data.grid(row=1, column=1, padx=10, pady=8, sticky="w")
        self.entry_data.insert(0, datetime.date.today().strftime("%d/%m/%Y"))

        # Selezione Cliente da Archivio
        tk.Label(frame, text="Seleziona Cliente:").grid(
            row=2, column=0, padx=10, pady=8, sticky="w"
        )
        
        sub_cli_frame = tk.Frame(frame)
        sub_cli_frame.grid(row=2, column=1, padx=0, pady=5, sticky="w")
        
        self.combo_clienti = ttk.Combobox(sub_cli_frame, width=30, state="readonly")
        self.combo_clienti.pack(side="left", padx=(0, 10))
        self.aggiorna_lista_clienti()
        self.combo_clienti.bind("<<ComboboxSelected>>", self.seleziona_cliente_combo)

        btn_nuovo_cli = tk.Button(
            sub_cli_frame,
            text="Inserisci nuovo cliente",
            bg="#4CAF50",
            fg="white",
            font=("Arial", 9, "bold"),
            command=self.apri_finestra_nuovo_cliente
        )
        btn_nuovo_cli.pack(side="left")

        self.cliente_selezionato = ""

        # Descrizione / Voci
        tk.Label(frame, text="Descrizione Lavori / Costi:\n(es. Ricambi + Ore)").grid(
            row=3, column=0, padx=10, pady=8, sticky="nw"
        )
        self.text_desc = tk.Text(frame, width=40, height=7)
        self.text_desc.grid(row=3, column=1, padx=10, pady=8, sticky="w")
        self.text_desc.insert(
            "1.0", "- Sostituzione Mozzo Ruota: € 120.00\n- Manodopera (2 ore): € 80.00"
        )

        # Totale Imponibile
        tk.Label(frame, text="Importo Totale (Imponibile €):").grid(
            row=4, column=0, padx=10, pady=8, sticky="w"
        )
        self.entry_totale = tk.Entry(frame, width=25)
        self.entry_totale.grid(row=4, column=1, padx=10, pady=8, sticky="w")
        self.entry_totale.insert(0, "200.00")

        # Pulsante Genera in basso
        btn_genera = tk.Button(
            root,
            text="Genera Preventivo",
            bg="#2196F3",
            fg="white",
            font=("Arial", 11, "bold"),
            command=self.crea_preventivo_pdf,
        )
        btn_genera.pack(pady=15)

    def aggiorna_lista_clienti(self, seleziona_questo=None):
        clienti = ottieni_clienti()
        self.combo_clienti["values"] = clienti
        if clienti:
            if seleziona_questo and seleziona_questo in clienti:
                self.combo_clienti.set(seleziona_questo)
                self.cliente_selezionato = seleziona_questo
            else:
                self.combo_clienti.set("--- Scegli dall'archivio ---")
        else:
            self.combo_clienti.set("Nessun cliente in archivio")

    def seleziona_cliente_combo(self, event):
        cliente_scelto = self.combo_clienti.get()
        if cliente_scelto and cliente_scelto != "--- Scegli dall'archivio ---" and cliente_scelto != "Nessun cliente in archivio":
            self.cliente_selezionato = cliente_scelto

    def apri_finestra_nuovo_cliente(self):
        FinestraNuovoCliente(self.root, self.aggiorna_lista_clienti)

    def crea_preventivo_pdf(self):
        numero = self.entry_num.get().strip()
        data = self.entry_data.get().strip()
        cliente = self.cliente_selezionato.strip()
        descrizione = self.text_desc.get("1.0", tk.END).strip()
        str_totale = self.entry_totale.get().strip()

        if not cliente or cliente == "--- Scegli dall'archivio ---" or cliente == "Nessun cliente in archivio":
            messagebox.showerror("Errore", "Seleziona un cliente valido dall'archivio (o inseriscine uno nuovo)!")
            return

        if not numero or not str_totale:
            messagebox.showerror("Errore", "Compila i campi obbligatori (Numero e Importo)!")
            return

        try:
            imponibile = float(str_totale.replace(",", "."))
        except ValueError:
            messagebox.showerror("Errore", "L'importo deve essere un numero valido.")
            return

        iva = imponibile * 0.22
        totale_finito = imponibile + iva

        try:
            file_pdf = genera_pdf(
                numero, cliente, data, descrizione, imponibile, iva, totale_finito
            )
            salva_preventivo_db(numero, cliente, data, descrizione, totale_finito)
            
            messagebox.showinfo(
                "Successo",
                f"Preventivo generato con successo!\nSalvato come: {file_pdf}",
            )
            
            self.entry_num.delete(0, tk.END)
            self.entry_num.insert(0, genera_prossimo_numero())
            
        except Exception as e:
            messagebox.showerror("Errore", f"Errore nella creazione del PDF: {e}")


if __name__ == "__main__":
    inizializza_db()
    root = tk.Tk()
    app = PreventiviApp(root)
    root.mainloop()