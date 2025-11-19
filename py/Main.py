"""
DaLohyn-SpeedWatch - Automatische Internetgeschwindigkeits-Überwachung
Developed by DaLohyn - Version 1.0.0

Dieses Tool misst regelmäßig die Internetgeschwindigkeit und speichert die Ergebnisse.
Optional können E-Mail-Warnungen und macOS-Benachrichtigungen aktiviert werden.
"""

# ============================================================================
# IMPORTS - Benötigte Module
# ============================================================================
import subprocess      # Für das Ausführen von externen Befehlen (speedtest)
import json           # Für das Parsen von JSON-Daten
import csv            # Für das Schreiben von CSV-Dateien
import os             # Für Dateisystem-Operationen
import time           # Für Pausen zwischen Messungen
import getpass        # Für sichere Passworteingabe (nicht sichtbar)
from datetime import datetime  # Für Zeitstempel

# Eigene Module
from email_alert import EmailAlert              # E-Mail-Benachrichtigungen
from macos_notification import MacOSNotification  # macOS-Benachrichtigungen

# ============================================================================
# KONFIGURATION - Grundeinstellungen
# ============================================================================
CSV_FILE = 'Speedtest_log.csv'  # Name der CSV-Datei für die Messergebnisse
THRESHOLD_MBPS = 25             # Standard-Grenzwert für Warnungen (in Mbps)
MEASUREMENTS_TO_CHECK = 3       # Anzahl der Messungen für Durchschnittsberechnung

# ============================================================================
# WILLKOMMENSTEXT
# ============================================================================
print("welcome to DaLohyn-SpeedWatch")
print("Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit.")
print("Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI")
print("und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.")
print("Developed by DaLohyn")
print("Version 1.0.0")
print("----------------------------------------------------------------------------------------")

# ============================================================================
# DATENSCHUTZ-EINWILLIGUNG
# ============================================================================
while True:
    try:
        consent = input("Mit der Nutzung dieses Tools erklärst du dich damit einverstanden, dass deine "
                       "Internetgeschwindigkeitsdaten lokal gespeichert werden. Fortfahren? (ja/nein): ")
        
        if consent.lower() == "ja":
            print("✅ Einwilligung erteilt. Programm wird fortgesetzt.")
            break
        elif consent.lower() == "nein":
            print("❌ Nutzung abgelehnt. Beende das Programm.")
            exit()  # Beendet das Programm
        else:
            print("⚠️  Bitte 'ja' oder 'nein' eingeben.")
    except ValueError:
        print("❌ Ungültige Eingabe. Bitte 'ja' oder 'nein' eingeben.")

print("----------------------------------------------------------------------------------------")

# ============================================================================
# E-MAIL-KONFIGURATION (OPTIONAL)
# ============================================================================
while True:
    try:
        consent_email = input("Möchtest du E-Mail-Warnungen bei langsamer Verbindung erhalten? (ja/nein): ")
        
        if consent_email.lower() == "ja":
            # Sammle E-Mail-Zugangsdaten vom Benutzer
            EMAIL_FROM = input("E-Mail Absender: ")
            EMAIL_PASSWORD = getpass.getpass("E-Mail Passwort (wird nicht angezeigt): ")
            EMAIL_TO = input("E-Mail Empfänger: ")
            SMTP_SERVER = input("SMTP Server (ohne http://): ")
            SMTP_PORT = int(input("SMTP Port (z.B. 587): "))
            
            # Frage nach individuellem Grenzwert
            while True:
                try:
                    threshold_input = float(input(f"Gib den Download-Geschwindigkeits-Grenzwert in Mbps an "
                                                 f"(Standard: {THRESHOLD_MBPS} Mbps): "))
                    THRESHOLD_MBPS = threshold_input
                    print(f"✅ Grenzwert gesetzt auf {THRESHOLD_MBPS} Mbps.")
                    break
                except ValueError:
                    print("❌ Ungültige Eingabe. Bitte eine Zahl eingeben.")
            
            # Erstelle das E-Mail-Alert-Objekt mit den eingegebenen Daten
            email_alert = EmailAlert(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)
            print("✅ E-Mail-Warnungen aktiviert.")
            break
            
        elif consent_email.lower() == "nein":
            # Keine E-Mails gewünscht - setze email_alert auf None
            email_alert = None
            print("📧 E-Mail-Warnungen deaktiviert.")
            break
            
        else:
            print("⚠️  Bitte 'ja' oder 'nein' eingeben.")
            
    except ValueError:
        print("❌ Ungültige Eingabe.")

print("----------------------------------------------------------------------------------------")

# ============================================================================
# macOS BENACHRICHTIGUNGEN INITIALISIEREN
# ============================================================================
# Erstelle macOS-Notification-Handler (funktioniert nur auf macOS)
mac_notifier = MacOSNotification()
mac_notifier.send_notification("🚀 SpeedWatch gestartet", 
                               "Internetgeschwindigkeits-Überwachung läuft...", 
                               sound=True)

print("----------------------------------------------------------------------------------------")

# ============================================================================
# MESSINTERVALL KONFIGURIEREN
# ============================================================================
print("Gib die Messintervalle in Minuten an (Standard: 60 Minuten): ")

while True:
    try:
        interval_input = int(input("Intervall (Minuten, min. 5): "))
        
        # Warnung bei zu kurzen Intervallen (Rate-Limit-Gefahr)
        if interval_input < 5:
            print("⚠️  Warnung: Intervall unter 5 Minuten kann zu Rate-Limits von Ookla führen!")
            confirm = input("Trotzdem fortfahren? (ja/nein): ")
            if confirm.lower() != "ja":
                continue  # Frage nochmal nach Intervall
        
        print(f"✅ Messintervall gesetzt auf {interval_input} Minuten.")
        check_intervall = interval_input * 60  # Umrechnung in Sekunden
        break
    except ValueError:
        print("❌ Ungültige Eingabe. Bitte eine Zahl eingeben.")

# ============================================================================
# GLOBALE VARIABLEN
# ============================================================================
# Liste für die letzten Download-Messungen (für Durchschnittsberechnung)
recent_downloads = []

# ============================================================================
# FUNKTIONEN
# ============================================================================

def check_speed_threshold(download_speed):
    """
    Prüft ob der Durchschnitt der letzten Messungen unter dem Grenzwert liegt.
    
    Args:
        download_speed: Aktuelle Download-Geschwindigkeit in Mbps
        
    Returns:
        True wenn Warnung ausgelöst wurde, sonst False
    """
    # Füge aktuelle Messung zur Liste hinzu
    recent_downloads.append(download_speed)
    
    # Behalte nur die letzten X Messungen (MEASUREMENTS_TO_CHECK)
    if len(recent_downloads) > MEASUREMENTS_TO_CHECK:
        recent_downloads.pop(0)  # Entferne älteste Messung
    
    # Prüfe nur wenn genug Messungen vorhanden sind
    if len(recent_downloads) == MEASUREMENTS_TO_CHECK:
        # Berechne Durchschnitt der letzten Messungen
        avg_speed = sum(recent_downloads) / len(recent_downloads)
        
        # Ist der Durchschnitt unter dem Grenzwert?
        if avg_speed < THRESHOLD_MBPS:
            print(f"⚠️  WARNUNG: Durchschnitt der letzten {MEASUREMENTS_TO_CHECK} Messungen "
                  f"unter {THRESHOLD_MBPS} Mbps!")
            
            # Sende macOS-Benachrichtigung (immer aktiv)
            mac_notifier.send_speed_alert(avg_speed, THRESHOLD_MBPS, recent_downloads.copy())
            
            # Sende E-Mail nur wenn E-Mail-Warnungen aktiviert sind
            if email_alert is not None:
                email_alert.send_alert(avg_speed, recent_downloads.copy(), 
                                      THRESHOLD_MBPS, MEASUREMENTS_TO_CHECK)
            
            return True
    
    return False


def run_speedtest():
    """
    Führt einen Speedtest mit der Ookla CLI aus.
    
    Returns:
        Dictionary mit Messergebnissen oder None bei Fehler
    """
    print("⚡ Starte Speedtest...")
    
    # Führe speedtest-Befehl aus
    result = subprocess.run(['speedtest', '--format=json', '--accept-license'], 
                          capture_output=True, text=True)
    
    # Prüfe ob der Befehl erfolgreich war
    if result.returncode != 0:
        print(f"❌ Fehler beim Speedtest: {result.stderr}")
        return None
    
    try:
        # Parse JSON-Ausgabe von speedtest
        data = json.loads(result.stdout)
        
        # Erstelle Dictionary mit relevanten Daten
        return {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Zeitstempel
            'download_Mbps': round(data['download']['bandwidth'] / 125000, 2),  # Download in Mbps
            'upload_Mbps': round(data['upload']['bandwidth'] / 125000, 2),      # Upload in Mbps
            'ping_ms': round(data['ping']['latency'], 2),                       # Ping in ms
            'server': data['server']['name'],                                   # Server-Name
            'server_location': data['server']['location'],                      # Server-Standort
            'server_country': data['server']['country'],                        # Server-Land
            'ip': data['interface']['externalIp'],                              # Externe IP
            'packet_loss': data.get('packetLoss', 0),                          # Paketverlust
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"❌ Fehler beim Parsen der Speedtest-Daten: {e}")
        return None


def write_to_csv(data):
    """
    Schreibt Messergebnisse in die CSV-Datei.
    Erstellt automatisch Header, falls Datei neu ist.
    
    Args:
        data: Dictionary mit Messergebnissen
    """
    # Prüfe ob Datei existiert und nicht leer ist
    file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
    
    # Öffne Datei im Append-Modus (anhängen)
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        
        # Schreibe Header nur wenn Datei neu ist
        if not file_exists:
            writer.writeheader()
        
        # Schreibe Datenzeile
        writer.writerow(data)


# ============================================================================
# HAUPTSCHLEIFE - WIEDERHOLTE SPEEDTESTS
# ============================================================================
print("----------------------------------------------------------------------------------------")
print("🚀 SpeedWatch läuft! Drücke Ctrl+C zum Beenden.")
print("----------------------------------------------------------------------------------------")

while True:
    # Führe Speedtest aus
    result = run_speedtest()
    
    # Wenn Speedtest erfolgreich war
    if result:
        # Zeige Ergebnisse im Terminal
        print(f"⏰ Zeit: {result['time']} | "
              f"📥 Download: {result['download_Mbps']} Mbps | "
              f"📤 Upload: {result['upload_Mbps']} Mbps | "
              f"🏓 Ping: {result['ping_ms']} ms | "
              f"🖥️ Server: {result['server']} ({result['server_location']}, {result['server_country']}) | "
              f"🌐 IP: {result['ip']} | "
              f"📉 Packet Loss: {result['packet_loss']}%")
        
        # Speichere Ergebnisse in CSV
        write_to_csv(result)
        
        # Sende macOS-Benachrichtigung nach jedem erfolgreichen Test
        mac_notifier.send_test_complete(result['download_Mbps'], 
                                       result['upload_Mbps'], 
                                       result['ping_ms'])
        
        # Prüfe ob Geschwindigkeit zu langsam ist
        check_speed_threshold(result['download_Mbps'])
    
    # Warte bis zur nächsten Messung
    print(f"⏳ Nächster Test in {interval_input} Minuten...")
    time.sleep(check_intervall)

