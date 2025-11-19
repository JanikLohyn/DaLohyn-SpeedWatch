# 🚀 DaLohyn-SpeedWatch 🚀

Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit. Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.

## ✨ Features ✨

🚀 Automatische Speedtests in konfigurierbaren Intervallen
📧 E-Mail-Warnungen bei langsamer Verbindung (optional)
📊 CSV-Export für einfache Datenanalyse
🌍 Erfasst Server-Informationen (Name, Standort, Land)
🔍 Zeigt deine externe IP-Adresse
📉 Misst Paketverlust (Packet Loss)
⚡ Nutzt die offizielle Ookla Speedtest CLI
🔒 Sichere Passworteingabe (nicht sichtbar)
💾 Speichert: Download, Upload, Ping, Packet Loss, Zeit, Server, Land und IP

## 📋 Voraussetzungen 📋

✅ Python 3.6 oder höher
✅ Ookla Speedtest CLI

## 📦 Installation 📦

### 1️⃣ Repository klonen

git clone https://github.com/DaLohyn/DaLohyn-SpeedWatch.git
cd DaLohyn-SpeedWatch



### 2️⃣ Ookla Speedtest CLI installieren

#### 🍎 macOS (mit Homebrew):
brew tap teamookla/speedtest
brew install speedtest



#### 🐧 Linux (Debian/Ubuntu):
curl -s https://packagecloud.io/install/repositories/ookla/speedtest-cli/script.deb.sh | sudo bash
sudo apt-get install speedtest



#### 🪟 Windows:
Lade die CLI von https://www.speedtest.net/apps/cli herunter und füge sie zu deinem PATH hinzu.

### 3️⃣ Lizenz akzeptieren

Beim ersten Start musst du die Lizenz akzeptieren:
speedtest --accept-license



## ▶️ Verwendung ▶️

Starte das Programm:
python3 py/Main.py



### 📝 Schritt-für-Schritt:

1️⃣ Datenschutz-Einwilligung: Bestätige, dass du mit der lokalen Speicherung einverstanden bist

2️⃣ E-Mail-Warnungen (optional):
   - ✉️ Wähle "ja" für E-Mail-Benachrichtigungen bei langsamer Verbindung
   - 🔧 Gib deine SMTP-Daten ein (Gmail, Outlook, all-inkl, etc.)
   - ⚙️ Lege den Geschwindigkeits-Grenzwert fest (Standard: 25 Mbps)

3️⃣ Messintervall: Gib das Intervall in Minuten an (empfohlen: 15-60 Minuten)

### 🖥️ Beispiel-Ausgabe:

welcome to DaLohyn-SpeedWatch
Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit.
Developed by DaLohyn
Version 1.0.0

Mit der Nutzung dieses Tools erklärst du dich damit einverstanden, dass deine
Internetgeschwindigkeitsdaten lokal gespeichert werden. Fortfahren? (ja/nein): ja

Möchtest du E-Mail-Warnungen bei langsamer Verbindung erhalten? (ja/nein): ja
E-Mail Absender: speedwatch@example.com
E-Mail Passwort: [verborgen]
E-Mail Empfänger: ich@example.com
SMTP Server (ohne http://): smtp.gmail.com
SMTP Port (z.B. 587): 587
Gib den Download-Geschwindigkeits-Grenzwert in Mbps an (Standard: 25.0 Mbps): 25
Grenzwert gesetzt auf 25.0 Mbps.

Intervall (Minuten, min. 5): 30
Messintervall gesetzt auf 30 Minuten.
Starte Speedtest...
Zeit: 2025-11-19 09:00:00 | Download: 125.43 Mbps | Upload: 45.21 Mbps |
Ping: 12.5 ms | Server: Telekom (Stuttgart, Germany) | IP: 123.45.67.89 | Packet Loss: 0.0%



## 📧 E-Mail-Warnungen 📧

Das Tool kann automatisch E-Mails senden, wenn der Durchschnitt der letzten 3 Messungen unter deinen Grenzwert fällt.

### 🌐 Unterstützte E-Mail-Provider:

| Provider | SMTP Server | Port |
|----------|-------------|------|
| 📮 Gmail | smtp.gmail.com | 587 |
| 📮 Outlook/Hotmail | smtp.office365.com | 587 |
| 📮 Yahoo | smtp.mail.yahoo.com | 587 |
| 📮 all-inkl | deinedomain.kasserver.com | 587 |
| 📮 Web.de | smtp.web.de | 587 |
| 📮 GMX | smtp.gmx.net | 587 |

⚠️ **Wichtig für Gmail:** Nutze ein App-Passwort (https://myaccount.google.com/apppasswords), nicht dein normales Passwort!

## 📊 CSV-Ausgabe 📊

Die Daten werden in `Speedtest_log.csv` gespeichert mit folgenden Spalten:

- ⏰ **time** - Zeitstempel der Messung (Format: YYYY-MM-DD HH:MM:SS)
- 📥 **download_Mbps** - Download-Geschwindigkeit in Mbps
- 📤 **upload_Mbps** - Upload-Geschwindigkeit in Mbps
- 🏓 **ping_ms** - Ping in Millisekunden
- 🖥️ **server** - Name des Speedtest-Servers
- 📍 **server_location** - Standort des Servers (Stadt)
- 🌍 **server_country** - Land des Servers
- 🌐 **ip** - Deine externe IP-Adresse
- 📉 **packet_loss** - Paketverlust in Prozent

## 📁 Projektstruktur 📁

DaLohyn-SpeedWatch/
├── py/
│ ├── Main.py # Hauptprogramm
│ └── email_alert.py # E-Mail-Benachrichtigungen
├── Speedtest_log.csv # Messergebnisse (wird erstellt)
├── README.md
├── LICENSE
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
