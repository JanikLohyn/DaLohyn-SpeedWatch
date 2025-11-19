"""
DaLohyn-SpeedWatch - Automatische Internetgeschwindigkeits-Überwachung
Hauptprogramm - Developed by DaLohyn - Version 1.0.0
"""

import time
import getpass
from config import *
from email_alert import EmailAlert
from macos_notification import MacOSNotification
from speedtest_runner import SpeedtestRunner
from csv_logger import CSVLogger


# ============================================================================
# INITIALISIERUNG
# ============================================================================
print(WELCOME_TEXT)
print("=" * 88)

# Initialisiere Komponenten
speedtest = SpeedtestRunner()
csv_logger = CSVLogger(CSV_FILE)
mac_notifier = MacOSNotification()
email_alert = None
recent_downloads = []

# ============================================================================
# DATENSCHUTZ-EINWILLIGUNG
# ============================================================================
while True:
    consent = input("Mit der Nutzung dieses Tools erklärst du dich damit einverstanden, dass deine "
                   "Internetgeschwindigkeitsdaten lokal gespeichert werden. Fortfahren? (ja/nein): ")
    
    if consent.lower() == "ja":
        print("✅ Einwilligung erteilt. Programm wird fortgesetzt.")
        break
    elif consent.lower() == "nein":
        print("❌ Nutzung abgelehnt. Beende das Programm.")
        exit()
    else:
        print("⚠️  Bitte 'ja' oder 'nein' eingeben.")

print("=" * 88)

# ============================================================================
# E-MAIL-KONFIGURATION (OPTIONAL)
# ============================================================================
consent_email = input("Möchtest du E-Mail-Warnungen bei langsamer Verbindung erhalten? (ja/nein): ")

if consent_email.lower() == "ja":
    EMAIL_FROM = input("E-Mail Absender: ")
    EMAIL_PASSWORD = getpass.getpass("E-Mail Passwort (wird nicht angezeigt): ")
    EMAIL_TO = input("E-Mail Empfänger: ")
    SMTP_SERVER = input("SMTP Server (ohne http://): ")
    SMTP_PORT = int(input("SMTP Port (z.B. 587): "))
    
    # Grenzwert
    threshold_input = float(input(f"Download-Grenzwert in Mbps (Standard: {DEFAULT_THRESHOLD_MBPS}): "))
    THRESHOLD_MBPS = threshold_input
    
    email_alert = EmailAlert(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)
    print("✅ E-Mail-Warnungen aktiviert.")
else:
    THRESHOLD_MBPS = DEFAULT_THRESHOLD_MBPS
    print("📧 E-Mail-Warnungen deaktiviert.")

print("=" * 88)

# ============================================================================
# macOS BENACHRICHTIGUNGEN
# ============================================================================
mac_notifier.send_notification("🚀 SpeedWatch gestartet", 
                               "Internetgeschwindigkeits-Überwachung läuft...", 
                               sound=True)

# ============================================================================
# MESSINTERVALL
# ============================================================================
while True:
    try:
        interval_input = int(input(f"Intervall (Minuten, min. {MIN_INTERVAL_MINUTES}): "))
        
        if interval_input < MIN_INTERVAL_MINUTES:
            print(f"⚠️  Warnung: Intervall unter {MIN_INTERVAL_MINUTES} Minuten kann zu Rate-Limits führen!")
            if input("Trotzdem fortfahren? (ja/nein): ").lower() != "ja":
                continue
        
        print(f"✅ Messintervall gesetzt auf {interval_input} Minuten.")
        check_intervall = interval_input * 60
        break
    except ValueError:
        print("❌ Ungültige Eingabe. Bitte eine Zahl eingeben.")

# ============================================================================
# FUNKTIONEN
# ============================================================================
def check_speed_threshold(download_speed):
    """Prüft ob Durchschnitt unter Grenzwert liegt"""
    recent_downloads.append(download_speed)
    
    if len(recent_downloads) > MEASUREMENTS_TO_CHECK:
        recent_downloads.pop(0)
    
    if len(recent_downloads) == MEASUREMENTS_TO_CHECK:
        avg_speed = sum(recent_downloads) / len(recent_downloads)
        
        if avg_speed < THRESHOLD_MBPS:
            print(f"⚠️  WARNUNG: Durchschnitt unter {THRESHOLD_MBPS} Mbps!")
            mac_notifier.send_speed_alert(avg_speed, THRESHOLD_MBPS, recent_downloads.copy())
            
            if email_alert is not None:
                email_alert.send_alert(avg_speed, recent_downloads.copy(), 
                                      THRESHOLD_MBPS, MEASUREMENTS_TO_CHECK)
            return True
    return False

# ============================================================================
# HAUPTSCHLEIFE
# ============================================================================
print("=" * 88)
print("🚀 SpeedWatch läuft! Drücke Ctrl+C zum Beenden.")
print("=" * 88)

while True:
    result = speedtest.run()
    
    if result:
        print(speedtest.format_result(result))
        csv_logger.write(result)
        mac_notifier.send_test_complete(result['download_Mbps'], 
                                       result['upload_Mbps'], 
                                       result['ping_ms'])
        check_speed_threshold(result['download_Mbps'])
    
    print(f"⏳ Nächster Test in {interval_input} Minuten...")
    time.sleep(check_intervall)
