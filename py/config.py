"""
Konfigurationsdatei für DaLohyn-SpeedWatch
Alle Konstanten und Einstellungen
"""

# CSV-Konfiguration
CSV_FILE = 'Speedtest_log.csv'

# Geschwindigkeits-Konfiguration
DEFAULT_THRESHOLD_MBPS = 25
MEASUREMENTS_TO_CHECK = 3

# Intervall-Konfiguration
MIN_INTERVAL_MINUTES = 5
DEFAULT_INTERVAL_MINUTES = 60

# Programm-Information
APP_NAME = "DaLohyn-SpeedWatch"
VERSION = "1.0.0"
DEVELOPER = "DaLohyn"

# Willkommenstext
WELCOME_TEXT = f"""welcome to {APP_NAME}
Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit.
Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI
und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.
Developed by {DEVELOPER}
Version {VERSION}"""
