# 🚀 DaLohyn-SpeedWatch

Ein Tool zur automatischen Überwachung der Internetgeschwindigkeit mit Python-Backend und Svelte-Web-Frontend.

## ✨ Features

- Automatische Speedtests in konfigurierbaren Intervallen (Python)
- E-Mail-Warnungen bei langsamer Verbindung (optional)
- CSV-Export für Datenanalyse
- Web-Frontend zur Visualisierung und Auswertung
- Grafische Statistiken & Messhistorie
- Server- und Standortinformationen
- Paketverlust- und IP-Erfassung

## 📋 Voraussetzungen

- Python 3.6+
- Ookla Speedtest CLI
- Node.js & npm (für das Web-Frontend)

## 📦 Installation

### 1. Repository klonen

```bash
git clone https://github.com/DaLohyn/DaLohyn-SpeedWatch.git
cd DaLohyn-SpeedWatch
```

### 2. Ookla Speedtest CLI installieren

**macOS:**
```bash
brew tap teamookla/speedtest
brew install speedtest
```
**Linux:**
```bash
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest
```
**Windows:**  
Download von https://www.speedtest.net/apps/cli und zum PATH hinzufügen.

### 3. Lizenz akzeptieren

```bash
speedtest --accept-license
```

### 4. Python-Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### 5. Web-Frontend installieren

```bash
cd frontend
npm install
```

## ▶️ Verwendung

### Backend starten

```bash
python3 py/Main.py
```

### Web-Frontend starten

```bash
cd frontend
npm run dev
```
Frontend erreichbar unter [http://localhost:5173](http://localhost:5173)

## 📝 Konfiguration & Ablauf

- Beim ersten Start: Datenschutz bestätigen, E-Mail-Warnungen konfigurieren (optional), Intervall festlegen.
- Messungen werden automatisch durchgeführt und in `Speedtest_log.csv` gespeichert.
- Web-Frontend zeigt aktuelle Werte, Statistiken und Grafiken.

## 📧 E-Mail-Warnungen

Automatische Benachrichtigung, wenn die Geschwindigkeit unter einen Grenzwert fällt.  
Unterstützte Provider: Gmail, Outlook, Yahoo, all-inkl, Web.de, GMX  
**Hinweis:** Für Gmail App-Passwort nutzen!

## 📊 CSV-Ausgabe

Spalten: time, download_Mbps, upload_Mbps, ping_ms, server, server_location, server_country, ip, packet_loss

## 📁 Projektstruktur

```
DaLohyn-SpeedWatch/
├── py/                # Python Backend
│   ├── Main.py
│   └── email_alert.py
├── frontend/          # Svelte Web-Frontend
│   ├── src/
│   └── ...
├── Speedtest_log.csv  # Messergebnisse
├── README.md
├── LICENSE
└── .gitignore
```

## 🛑 Programm beenden

Mit `Ctrl+C` im Terminal.

## ⚠️ Hinweise

- Ookla erlaubt ca. 10-15 Tests pro Stunde (Intervall min. 5 Minuten)
- E-Mail-Zugangsdaten niemals committen!
- Passwort-Eingabe ist nicht sichtbar.

## 👨‍💻 Entwickler

**DaLohyn**  
GitHub: https://github.com/DaLohyn  
Website: https://dalohyn.de

## 📜 Lizenz

MIT License

## 🤝 Mitwirken

Contributions willkommen! Issues & Pull Requests gerne öffnen.

## 💬 Support

Probleme? Issue auf GitHub öffnen:  
https://github.com/DaLohyn/DaLohyn-SpeedWatch/issues
└── .gitignore



## 🛑 Programm beenden 🛑

Drücke `Ctrl+C` im Terminal, um das Programm zu stoppen.

## ⚠️ Wichtige Hinweise ⚠️

**⏱️ Rate Limits:** Ookla erlaubt ca. 10-15 Tests pro Stunde. Nutze mindestens 5 Minuten Intervall (empfohlen: 15-60 Minuten)

**🔒 Sicherheit:** 
- 🔐 Nutze für E-Mails App-Passwörter, niemals dein echtes Passwort
- 🚫 Committe niemals deine E-Mail-Zugangsdaten zu Git
- 👁️ Die Eingabe des Passworts ist nicht sichtbar (getpass)

**⚡ Performance:**
- ⏳ Die erste Messung kann etwas länger dauern
- 🔄 Bei Netzwerkproblemen wird die Messung übersprungen
- ✅ Die CSV-Datei wird automatisch erstellt

## 👨‍💻 Entwickelt von 👨‍💻

**DaLohyn** - Version 1.0.0

🔗 GitHub: https://github.com/DaLohyn
🌐 Website: https://dalohyn.de

## 📜 Lizenz 📜

MIT License - siehe LICENSE Datei für Details.

## 🤝 Mitwirken 🤝

Contributions sind willkommen! Öffne gerne Issues oder Pull Requests.

## 💬 Support 💬

Bei Problemen öffne ein Issue auf GitHub:
https://github.com/DaLohyn/DaLohyn-SpeedWatch/issues
