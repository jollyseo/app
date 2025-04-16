import json
import os
import re
import requests
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from tkinter import Tk, Label, Button, Text, END, messagebox, filedialog, ttk, StringVar

# Configurazione
CONFIG = {
    "max_workers": 10,
    "timeout": 15,
    "input_file": "backlink.json",
    "sites_file": "siti.txt",
    "output_dir": "reports",
    "placeholder": "vostroportale.com",
    "log_file": "backlink_checker.log",
    "log_level": "DEBUG"  # DEBUG, INFO, WARNING, ERROR
}

class BacklinkChecker:
    def __init__(self):
        self.setup_logging()
        self.verify_directories()
        
    def setup_logging(self):
        """Configura il sistema di logging con verifica scrivibilità"""
        try:
            logging.basicConfig(
                filename=CONFIG["log_file"],
                level=CONFIG["log_level"],
                format='%(asctime)s - %(levelname)s - %(message)s',
                force=True
            )
            # Test scrittura log
            logging.info("=== SESSIONE INIZIATA ===")
            logging.info(f"Backlink Checker avviato in: {os.getcwd()}")
            logging.info(f"Percorso log: {os.path.abspath(CONFIG['log_file'])}")
        except Exception as e:
            print(f"CRITICAL: Impossibile scrivere log: {str(e)}")
            raise

    def verify_directories(self):
        """Verifica/Crea cartelle con controllo permessi"""
        try:
            os.makedirs(CONFIG["output_dir"], exist_ok=True)
            # Test scrivibilità
            test_file = os.path.join(CONFIG["output_dir"], "test_write.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            logging.info(f"Cartella {CONFIG['output_dir']} verificata")
        except Exception as e:
            logging.critical(f"Errore cartella report: {str(e)}")
            raise

    def get_file_path(self, filename):
        """Restituisce il percorso assoluto con verifica"""
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        logging.debug(f"Resolved path for {filename}: {path}")
        return path

    def load_file(self, filename, file_type="text"):
        """Carica file con gestione errori avanzata"""
        try:
            path = self.get_file_path(filename)
            if not os.path.exists(path):
                raise FileNotFoundError(f"File {filename} non trovato in {path}")
                
            with open(path, "r", encoding="utf-8") as f:
                if file_type == "json":
                    data = json.load(f)
                    logging.info(f"Caricati {len(data)} elementi da {filename}")
                else:
                    data = [line.strip() for line in f if line.strip()]
                    logging.info(f"Caricate {len(data)} righe da {filename}")
                return data
        except Exception as e:
            logging.error(f"Errore caricamento {filename}: {str(e)}")
            raise

    def check_url(self, url):
        """Verifica URL con ritentativi e timeout"""
        for attempt in range(3):
            try:
                start_time = time.time()
                response = requests.get(
                    url,
                    timeout=CONFIG["timeout"],
                    headers={'User-Agent': 'Mozilla/5.0'}
                )
                elapsed = time.time() - start_time
                logging.debug(f"URL {url} verificato in {elapsed:.2f}s (Status: {response.status_code})")
                return response.status_code
            except requests.exceptions.RequestException as e:
                logging.warning(f"Tentativo {attempt+1} fallito per {url}: {str(e)}")
                if attempt == 2:
                    return str(e)
                time.sleep(1)

    def generate_report(self, domain, results):
        """Genera report HTML con verifica scrivibilità"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{domain}_{timestamp}.html"
            report_path = os.path.join(CONFIG["output_dir"], filename)
            
            # Verifica finale percorso
            if not os.path.exists(CONFIG["output_dir"]):
                raise FileNotFoundError(f"Cartella {CONFIG['output_dir']} non esiste")
                
            # Dati report
            working = [r for r in results if isinstance(r[1], int) and r[1] == 200]
            failed = [r for r in results if r not in working]
            
            # Generazione HTML
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Report {domain}</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #2c3e50; }}
        .success {{ color: #27ae60; }}
        .failed {{ color: #e74c3c; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; }}
        th {{ background-color: #f2f2f2; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <h1>Backlink Report: {domain}</h1>
    <p><strong>Data generazione:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <h2 class="success">Backlink Funzionanti: {len(working)}</h2>
    <table>
        <tr><th>URL</th><th>Status</th></tr>
"""
            for url, status in working:
                html_content += f'        <tr><td><a href="{url}" target="_blank">{url}</a></td><td>{status}</td></tr>\n'
            
            html_content += f"""
    </table>
    
    <h2 class="failed">Backlink Non Funzionanti: {len(failed)}</h2>
    <table>
        <tr><th>URL</th><th>Errore</th></tr>
"""
            for url, error in failed:
                html_content += f'        <tr><td>{url}</td><td>{error}</td></tr>\n'
            
            html_content += """
    </table>
</body>
</html>"""

            # Scrittura file con verifica
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            
            logging.info(f"Generato report: {report_path}")
            return report_path
            
        except Exception as e:
            logging.error(f"Errore generazione report per {domain}: {str(e)}")
            raise

class ApplicationUI(Tk):
    def __init__(self, checker):
        super().__init__()
        self.checker = checker
        self.title("Backlink Checker Pro v2.0")
        self.geometry("1000x800")
        self.minsize(800, 600)
        
        # Variabili di stato
        self.running = False
        self.current_domain = StringVar(value="")
        self.progress_value = 0
        
        self.setup_ui()
        self.check_environment()

    def setup_ui(self):
        """Configura l'interfaccia grafica"""
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5")
        self.style.configure("TButton", padding=6)
        self.style.configure("Accent.TButton", foreground="white", background="#3498db")
        self.style.map("Accent.TButton",
                      background=[("active", "#2980b9"), ("disabled", "#bdc3c7")])
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Label(header_frame, text="Backlink Checker Professional", font=("Arial", 16)).pack(side="left")
        
        # Toolbar
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill="x", pady=5)
        
        self.btn_start = ttk.Button(
            toolbar_frame,
            text="Avvia Verifica",
            command=self.start_process,
            style="Accent.TButton"
        )
        self.btn_start.pack(side="left", padx=5)
        
        self.btn_open_reports = ttk.Button(
            toolbar_frame,
            text="Apri Cartella Report",
            command=self.open_reports_folder
        )
        self.btn_open_reports.pack(side="left", padx=5)
        
        self.btn_show_logs = ttk.Button(
            toolbar_frame,
            text="Mostra Log",
            command=self.show_logs
        )
        self.btn_show_logs.pack(side="left", padx=5)
        
        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill="x", pady=5)
        
        ttk.Label(status_frame, text="Stato:").pack(side="left")
        self.lbl_status = ttk.Label(status_frame, text="Pronto", foreground="#2c3e50")
        self.lbl_status.pack(side="left", padx=5)
        
        ttk.Label(status_frame, text="Dominio corrente:").pack(side="left", padx=(20,5))
        self.lbl_domain = ttk.Label(status_frame, textvariable=self.current_domain, foreground="#e67e22")
        self.lbl_domain.pack(side="left")
        
        # Progress bar
        self.progress = ttk.Progressbar(
            main_frame,
            orient="horizontal",
            length=100,
            mode="determinate"
        )
        self.progress.pack(fill="x", pady=5)
        
        # Console output
        console_frame = ttk.Frame(main_frame)
        console_frame.pack(fill="both", expand=True)
        
        self.console = Text(
            console_frame,
            wrap="word",
            font=("Consolas", 10),
            bg="white",
            padx=10,
            pady=10
        )
        self.console.pack(fill="both", expand=True, side="left")
        
        scrollbar = ttk.Scrollbar(console_frame)
        scrollbar.pack(side="right", fill="y")
        self.console.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.console.yview)
        
        # Footer
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=(10,0))
        
        ttk.Label(footer_frame, text=f"Versione 2.0 | Cartella report: {os.path.abspath(CONFIG['output_dir'])}").pack(side="left")

    def check_environment(self):
        """Verifica l'ambiente all'avvio"""
        try:
            # Verifica cartella report
            if not os.path.exists(CONFIG["output_dir"]):
                os.makedirs(CONFIG["output_dir"])
                self.log("Cartella report creata")
            
            # Verifica scrivibilità
            test_file = os.path.join(CONFIG["output_dir"], "test.tmp")
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            
            self.log("Ambiente verificato con successo")
        except Exception as e:
            self.log(f"ERRORE AMBIENTE: {str(e)}", "error")
            messagebox.showerror("Errore Ambiente", 
                               f"Impossibile scrivere nella cartella report:\n{str(e)}")

    def log(self, message, level="info"):
        """Scrive nel log e nella console UI"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_msg = f"[{timestamp}] {message}"
        
        # Colori in base al livello
        if level == "error":
            tag = "error"
            self.console.tag_config(tag, foreground="red")
        elif level == "warning":
            tag = "warning"
            self.console.tag_config(tag, foreground="orange")
        else:
            tag = "info"
        
        self.console.insert(END, formatted_msg + "\n", tag)
        self.console.see(END)
        self.update_idletasks()

    def open_reports_folder(self):
        """Apre la cartella dei report"""
        report_path = os.path.abspath(CONFIG["output_dir"])
        try:
            if os.path.exists(report_path):
                os.startfile(report_path)
            else:
                self.log(f"Cartella non trovata: {report_path}", "error")
        except Exception as e:
            self.log(f"Errore apertura cartella: {str(e)}", "error")

    def show_logs(self):
        """Mostra il contenuto del file di log"""
        log_path = os.path.abspath(CONFIG["log_file"])
        try:
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    content = f.read()
                
                log_window = Tk()
                log_window.title("Log dell'applicazione")
                log_window.geometry("800x600")
                
                text = Text(log_window, wrap="word", font=("Consolas", 10))
                text.pack(fill="both", expand=True, padx=10, pady=10)
                text.insert(END, content)
                
                scrollbar = ttk.Scrollbar(log_window)
                scrollbar.pack(side="right", fill="y")
                text.config(yscrollcommand=scrollbar.set)
                scrollbar.config(command=text.yview)
            else:
                self.log("File log non trovato", "error")
        except Exception as e:
            self.log(f"Errore lettura log: {str(e)}", "error")

    def start_process(self):
        """Avvia il processo principale"""
        if self.running:
            return
            
        self.running = True
        self.btn_start["state"] = "disabled"
        self.console.delete(1.0, END)
        self.progress["value"] = 0
        
        try:
            # Caricamento dati
            self.log("Caricamento siti...")
            domains = self.checker.load_file(CONFIG["sites_file"])
            
            self.log("Caricamento backlink...")
            backlinks = self.checker.load_file(CONFIG["input_file"], "json")
            
            if not domains or not backlinks:
                self.log("Dati insufficienti per avviare", "error")
                return
                
            self.log(f"Inizio verifica per {len(domains)} domini")
            
            # Processamento
            for i, domain in enumerate(domains, 1):
                self.current_domain.set(domain)
                self.log(f"\nElaborazione dominio {i}/{len(domains)}: {domain}")
                
                # Processa dominio
                results = []
                total = len(backlinks)
                
                with ThreadPoolExecutor(max_workers=CONFIG["max_workers"]) as executor:
                    futures = []
                    for j, backlink in enumerate(backlinks):
                        url = backlink['url'].replace(CONFIG["placeholder"], domain)
                        futures.append(executor.submit(self.checker.check_url, url))
                        
                        # Aggiorna progresso ogni 5 elementi
                        if j % 5 == 0:
                            progress = (j/total)*100
                            self.progress["value"] = progress
                            self.update_idletasks()
                    
                    for j, future in enumerate(as_completed(futures)):
                        try:
                            result = future.result()
                            url = backlinks[j]['url'].replace(CONFIG["placeholder"], domain)
                            results.append((url, result))
                            
                            if j % 5 == 0:
                                progress = ((j+1)/total)*100
                                self.progress["value"] = progress
                                self.update_idletasks()
                        except Exception as e:
                            self.log(f"Errore verifica URL: {str(e)}", "error")
                
                # Genera report
                try:
                    report_path = self.checker.generate_report(domain, results)
                    if report_path:
                        self.log(f"Report generato: {os.path.basename(report_path)}")
                    
                    # Statistiche
                    working = len([r for r in results if isinstance(r[1], int) and r[1] == 200])
                    failed = len(results) - working
                    self.log(f"Risultati: {working} funzionanti, {failed} falliti")
                except Exception as e:
                    self.log(f"Errore generazione report: {str(e)}", "error")
            
            self.log("\nProcesso completato con successo!", "info")
            messagebox.showinfo("Completato", "Elaborazione terminata")
            
        except Exception as e:
            self.log(f"\nERRORE: {str(e)}", "error")
            messagebox.showerror("Errore", f"Si è verificato un errore:\n{str(e)}")
            
        finally:
            self.running = False
            self.btn_start["state"] = "normal"
            self.progress["value"] = 100
            self.current_domain.set("")

if __name__ == "__main__":
    try:
        checker = BacklinkChecker()
        app = ApplicationUI(checker)
        app.mainloop()
    except Exception as e:
        with open("crash_report.txt", "w") as f:
            f.write(f"CRASH REPORT {datetime.now()}\n")
            f.write(f"Error: {str(e)}\n\n")
            f.write("Traceback:\n")
            import traceback
            traceback.print_exc(file=f)
        
        messagebox.showerror("Errore Critico", 
                           f"L'applicazione si è arrestata:\n{str(e)}\n\n"
                           "Vedere crash_report.txt per dettagli.")