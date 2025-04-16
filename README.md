# Automatic Backlink

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen)

Strumento avanzato per la creazione di backlink in modo automatico, di massa, per piu domini, generare report HTML dei risultati e gestire liste di proxy.

## 🚀 Funzionalità

- ✅ Verifica multipla di backlink per diversi domini
- ✅ Generazione report HTML con risultati dettagliati
- ✅ Supporto multi-threading per prestazioni elevate
- ✅ Interfaccia grafica intuitiva
- ✅ Logging dettagliato delle operazioni
- ✅ Gestione automatica dei proxy (opzionale)

## 📦 Installazione

1. **Prerequisiti**:
   - Python 3.8+
   - Pip (incluso in Python)

2. **Clona il repository**:
   ```bash
   git clone https://github.com/jollyseo/app.git

Installa le dipendenze:

bash
Copy
pip install -r requirements.txt

🛠 Configurazione
Prima dell'uso, prepara questi file nella cartella principale:

backlink.json - Template dei backlink da verificare:
siti.txt - Lista di domini da verificare (uno per riga):

Copy
miosito1.com
miosito2.net
proxy.txt (opzionale) - Lista di proxy da usare (formato ip:porta):

Copy
123.45.67.89:8080
98.76.54.32:3128

🖥 Uso
Metodo 1: Interfaccia Grafica
bash
Copy
python backlink_checker.py
Clicca "Avvia Verifica" per iniziare

Monitora lo stato nella console integrata

Usa "Apri Cartella Report" per accedere ai risultati

Metodo 2: Da riga di comando (senza GUI)
bash
Copy
python backlink_checker.py --cli --sites siti.txt --backlinks backlink.json
📊 Output
I report vengono salvati in:

reports/ - Cartella con report HTML per ogni dominio

backlink_checker.log - Log dettagliato delle operazioni

Esempio di struttura report:

Copy
reports/
├── report_miosito1.com_20230815_143022.html
├── report_miosito2.net_20230815_143045.html
🛠 Personalizzazione
Modifica config.py per:

Cambiare timeout delle richieste

Regolare il numero di thread

Modificare i percorsi dei file

❓ Domande Frequenti
❌ Non vengono generati i report
Verifica i permessi di scrittura nella cartella reports/

Controlla che backlink.json contenga il placeholder corretto

Cerca errori nel file backlink_checker.log

🐛 Come segnalare un bug?
Apri una issue su GitHub includendo:

Il log dell'errore

I passi per riprodurre il problema

Screenshot (se applicabile)

🤝 Contribuire
I contributi sono benvenuti! Ecco come aiutare:

Fai un fork del progetto

Crea un branch (git checkout -b feature/nuova-funzione)

Fai commit delle modifiche (git commit -am 'Aggiunta nuova funzionalità')

Pusha sul branch (git push origin feature/nuova-funzione)

Apri una Pull Request

📄 Licenza
Distribuito con licenza MIT. Vedi LICENSE per dettagli.

Nota: Per supporto o domande, contattami su GitHub o via email!

Copy

### Extra per GitHub:

1. **Aggiungi una cartella `.github`** con:
   - `ISSUE_TEMPLATE.md` per segnalazioni bug
   - `PULL_REQUEST_TEMPLATE.md` per contributi

2. **Struttura consigliata del repo**:
backlink-checker/
├── .github/
├── docs/ # Documentazione aggiuntiva
├── samples/ # File di esempio
├── backlink_checker.py # Script principale
├── config.py # File configurazione
├── requirements.txt # Dipendenze
├── README.md # Questa guida
└── LICENSE # Licenza MIT

Copy

3. **Badge aggiuntivi** (da aggiungere in README):
```markdown
![powered](https://www.anyweb.it) by Angelo Cosenza


