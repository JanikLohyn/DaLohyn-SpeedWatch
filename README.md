# DaLohyn-SpeedWatch
Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit. Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.

## Features

- 🚀 Automatische Speedtests in konfigurierbaren Intervallen
- 📊 CSV-Export für einfache Datenanalyse
- 🌍 Erfasst Server-Informationen (Name, Standort, Land)
- 🔍 Zeigt deine externe IP-Adresse
- ⚡ Nutzt die offizielle Ookla Speedtest CLI
- 💾 Speichert: Download, Upload, Ping, Zeit, Server und IP

## Voraussetzungen

- Python 3.6 oder höher
- Ookla Speedtest CLI

## Installation

### 1. Repository klonen
git clone https://github.com/deinusername/DaLohyn-SpeedWatch.git
cd DaLohyn-SpeedWatch

### 2. Ookla Speedtest CLI installieren

#### macOS (mit Homebrew):
ew tap teamookla/speedtest
brew install speedtest


#### Oder direkt von Ookla:
Lade die CLI von [speedtest.net/apps/cli](https://www.speedtest.net/apps/cli) herunter und füge sie zu deinem PATH hinzu.

### 3. Lizenz akzeptieren

Beim ersten Start musst du die Lizenz akzeptieren:
speedtest --accept-license

## Verwendung

Starte das Programm:
python3 Main.py

Das Programm fragt dich nach dem Messintervall in Minuten. Danach führt es automatisch Speedtests durch und speichert die Ergebnisse.

### Beispiel-Ausgabe:
welcome to DaLohyn-SpeedWatch
Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit.
Developed by DaLohyn
Version 1.0.0

Intervall (Minuten): 30
Messintervall gesetzt auf 30 Minuten.
Starte Speedtest...
Zeit: 2025-11-18 20:00:00 | Download: 125.43 Mbps | Upload: 45.21 Mbps | Ping: 12.5 ms | Server: Telekom (Stuttgart, Germany) | IP: 123.45.67.89

## CSV-Ausgabe

Die Daten werden in `Speedtest_log.csv` gespeichert mit folgenden Spalten:

- `time` - Zeitstempel der Messung
- `download_Mbps` - Download-Geschwindigkeit in Mbps
- `upload_Mbps` - Upload-Geschwindigkeit in Mbps
- `ping_ms` - Ping in Millisekunden
- `server` - Name des Speedtest-Servers
- `server_location` - Standort des Servers
- `server_country` - Land des Servers
- `ip` - Deine externe IP-Adresse

## Programm beenden

Drücke `Ctrl+C` im Terminal, um das Programm zu stoppen.

## Entwickelt von

**DaLohyn** - Version 1.0.0

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Hinweise

- Die erste Messung kann etwas länger dauern
- Bei Netzwerkproblemen wird die Messung übersprungen und beim nächsten Intervall fortgesetzt
- Die CSV-Datei wird automatisch erstellt, falls sie nicht existiert