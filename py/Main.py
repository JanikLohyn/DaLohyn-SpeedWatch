"""
DaLohyn-SpeedWatch - Automatische Internetgeschwindigkeits-Überwachung
Hauptprogramm - Developed by DaLohyn - Version 1.0.0
"""

import time
import getpass
import sys
from config import *
from email_alert import EmailAlert
from macos_notification import MacOSNotification
from speedtest_runner import SpeedtestRunner
from csv_logger import CSVLogger
from visualize_data import SpeedwatchVisualizer  # NEU!


# ============================================================================
# INITIALISIERUNG
# ============================================================================
print(WELCOME_TEXT)
print("=" * 88)

# Initialisiere Komponenten
speedtest = SpeedtestRunner()
csv_logger = CSVLogger(CSV_FILE)
mac_notifier = MacOSNotification()
visualizer = SpeedwatchVisualizer(CSV_FILE)  # NEU: Visualizer hinzufügen
email_alert = None
recent_downloads = []
THRESHOLD_MBPS = DEFAULT_THRESHOLD_MBPS

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
        sys.exit(0)
    else:
        print("⚠️  Bitte 'ja' oder 'nein' eingeben.")

print("=" * 88)

# ============================================================================
# E-MAIL-KONFIGURATION (OPTIONAL)
# ============================================================================
while True:
    consent_email = input("Möchtest du E-Mail-Warnungen bei langsamer Verbindung erhalten? (ja/nein): ")
    
    if consent_email.lower() == "ja":
        try:
            EMAIL_FROM = input("E-Mail Absender: ")
            EMAIL_PASSWORD = getpass.getpass("E-Mail Passwort (wird nicht angezeigt): ")
            EMAIL_TO = input("E-Mail Empfänger: ")
            SMTP_SERVER = input("SMTP Server (ohne http://): ")
            SMTP_PORT = int(input("SMTP Port (z.B. 587): "))
            
            threshold_input = float(input(f"Download-Grenzwert in Mbps (Standard: {DEFAULT_THRESHOLD_MBPS}): "))
            THRESHOLD_MBPS = threshold_input
            
            email_alert = EmailAlert(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)
            print("✅ E-Mail-Warnungen aktiviert.")
            break
        except ValueError:
            print("❌ Ungültige Eingabe. Bitte versuche es erneut.")
    elif consent_email.lower() == "nein":
        print("📧 E-Mail-Warnungen deaktiviert.")
        break
    else:
        print("⚠️  Bitte 'ja' oder 'nein' eingeben.")

print("=" * 88)

# ============================================================================
# GRAFIK-AKTUALISIERUNG (NEU!)
# ============================================================================
while True:
    auto_graph = input("Möchtest du Grafiken nach jedem Test automatisch aktualisieren? (ja/nein): ")
    if auto_graph.lower() in ["ja", "nein"]:
        AUTO_UPDATE_GRAPHS = (auto_graph.lower() == "ja")
        if AUTO_UPDATE_GRAPHS:
            print("📊 Grafiken werden automatisch aktualisiert.")
        else:
            print("📊 Grafiken werden nicht automatisch aktualisiert.")
        break
    else:
        print("⚠️  Bitte 'ja' oder 'nein' eingeben.")

print("=" * 88)

# ============================================================================
# macOS BENACHRICHTIGUNGEN
# ============================================================================
try:
    mac_notifier.send_notification("🚀 SpeedWatch gestartet", 
                                   "Internetgeschwindigkeits-Überwachung läuft...", 
                                   sound=True)
except Exception as e:
    print(f"⚠️  macOS-Benachrichtigung fehlgeschlagen: {e}")

# ============================================================================
# MESSINTERVALL
# ============================================================================
while True:
    try:
        interval_input = int(input(f"Intervall (Minuten, min. {MIN_INTERVAL_MINUTES}): "))
        
        if interval_input < MIN_INTERVAL_MINUTES:
            print(f"⚠️  Warnung: Intervall unter {MIN_INTERVAL_MINUTES} Minuten kann zu Rate-Limits führen!")
            confirm = input("Trotzdem fortfahren? (ja/nein): ")
            if confirm.lower() != "ja":
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
            print(f"⚠️  WARNUNG: Durchschnitt der letzten {MEASUREMENTS_TO_CHECK} Messungen "
                  f"liegt bei {avg_speed:.2f} Mbps (unter {THRESHOLD_MBPS} Mbps)!")
            
            try:
                mac_notifier.send_speed_alert(avg_speed, THRESHOLD_MBPS, recent_downloads.copy())
            except Exception:
                pass
            
            if email_alert is not None:
                email_alert.send_alert(avg_speed, recent_downloads.copy(), 
                                      THRESHOLD_MBPS, MEASUREMENTS_TO_CHECK)
            return True
    return False

def update_graphs():
    """Aktualisiert alle Grafiken"""
    try:
        print("📊 Aktualisiere Grafiken...")
        visualizer.generate_all_graphs()
    except Exception as e:
        print(f"⚠️  Fehler beim Aktualisieren der Grafiken: {e}")

# ============================================================================
# HAUPTSCHLEIFE
# ============================================================================
print("=" * 88)
print("🚀 SpeedWatch läuft! Drücke Ctrl+C zum Beenden.")
if AUTO_UPDATE_GRAPHS:
    print("📊 Grafiken werden nach jedem Test aktualisiert.")
print("=" * 88)

test_count = 0

try:
    while True:
        result = speedtest.run()
        
        if result:
            test_count += 1
            print(f"\n[Test #{test_count}]")
            print(speedtest.format_result(result))
            
            # CSV speichern
            if csv_logger.write(result):
                print("💾 Daten in CSV gespeichert")
            
            # macOS-Benachrichtigung
            try:
                mac_notifier.send_test_complete(result['download_Mbps'], 
                                               result['upload_Mbps'], 
                                               result['ping_ms'])
            except Exception:
                pass
            
            # Geschwindigkeit prüfen
            check_speed_threshold(result['download_Mbps'])
            
            # NEU: Grafiken aktualisieren (falls aktiviert)
            if AUTO_UPDATE_GRAPHS:
                update_graphs()
        else:
            print("❌ Speedtest fehlgeschlagen. Überspringe diese Messung.")
        
        print(f"\n⏳ Nächster Test in {interval_input} Minuten...")
        print("=" * 88)
        time.sleep(check_intervall)

except KeyboardInterrupt:
    print("\n\n🛑 Programm durch Benutzer beendet (Ctrl+C)")
    print(f"📊 Insgesamt {test_count} Tests durchgeführt")
    print("💾 Alle Daten wurden in der CSV-Datei gespeichert")
    
    # Finale Grafik-Aktualisierung
    if test_count > 0:
        print("\n📊 Erstelle finale Grafiken...")
        update_graphs()
    
    print("\n👋 Auf Wiedersehen!")
    sys.exit(0)

except Exception as e:
    print(f"\n❌ Unerwarteter Fehler: {e}")
    print("💾 Bisherige Daten wurden in der CSV-Datei gespeichert")
    sys.exit(1)
