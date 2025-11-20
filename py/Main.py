"""
DaLohyn-SpeedWatch - Automatische Internetgeschwindigkeits-Überwachung
Hauptprogramm - Developed by DaLohyn - Version 1.0.0
"""

import time
import getpass
import sys
import os
import csv
import json
import subprocess
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import threading
import webbrowser

from config import *
from email_alert import EmailAlert
from macos_notification import MacOSNotification
from speedtest_runner import SpeedtestRunner
from csv_logger import CSVLogger
from visualize_data import SpeedwatchVisualizer


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

# Flask App Setup
app = Flask(__name__)
CORS(app)

# Globale Variablen für API
monitoring_active = False
monitoring_thread = None
current_settings = {
    'interval': 30,
    'threshold': 25.0,
    'email_enabled': False
}
latest_measurement = None

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
            
            # macOS Benachrichtigung
            try:
                mac_notifier.send_speed_alert(avg_speed, THRESHOLD_MBPS, recent_downloads.copy())
            except Exception:
                pass
            
            
            # E-Mail
            if email_alert is not None:
                email_alert.send_alert(avg_speed, recent_downloads.copy(), 
                                      THRESHOLD_MBPS, MEASUREMENTS_TO_CHECK)
            return True
    return False

def update_graphs():
    """Aktualisiert alle Grafiken (Thread-safe)"""
    try:
        print("📊 Aktualisiere Grafiken...")
        success = visualizer.generate_all_graphs()
        if not success:
            print("⚠️  Grafiken konnten nicht erstellt werden")
        return success
    except Exception as e:
        print(f"⚠️  Fehler beim Aktualisieren der Grafiken: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# API ENDPOINTS
# ============================================================================
@app.route('/measurements', methods=['GET'])
def api_get_measurements():
    limit = request.args.get('limit', default=None, type=int)
    measurements = []
    
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_measurements = list(reader)
                
                # Wenn limit angegeben, limitiere die Anzahl
                if limit:
                    measurements = all_measurements[-limit:]
                else:
                    measurements = all_measurements
                
                measurements.reverse()
        except Exception as e:
            print(f"❌ Fehler beim Lesen der CSV: {e}")
    
    return jsonify({'measurements': measurements})

@app.route('/statistics', methods=['GET'])
def api_get_statistics():
    measurements = []
    
    if os.path.exists(CSV_FILE):
        try:
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                measurements = list(reader)
        except Exception as e:
            print(f"❌ Fehler: {e}")
    
    if not measurements:
        return jsonify({
            'avgDownload': 0,
            'avgUpload': 0,
            'avgPing': 0,
            'totalTests': 0
        })
    
    avg_download = sum(float(m['download_Mbps']) for m in measurements) / len(measurements)
    avg_upload = sum(float(m['upload_Mbps']) for m in measurements) / len(measurements)
    avg_ping = sum(float(m['ping_ms']) for m in measurements) / len(measurements)
    
    return jsonify({
        'avgDownload': round(avg_download, 2),
        'avgUpload': round(avg_upload, 2),
        'avgPing': round(avg_ping, 2),
        'totalTests': len(measurements)
    })

@app.route('/export/csv', methods=['GET'])
def api_export_csv():
    if os.path.exists(CSV_FILE):
        return send_file(CSV_FILE, as_attachment=True, download_name='Speedtest_log.csv')
    return jsonify({'error': 'No data available'}), 404

@app.route('/status', methods=['GET'])
def api_status():
    exists = os.path.exists(CSV_FILE)
    count = 0
    
    if exists:
        with open(CSV_FILE, 'r') as f:
            count = sum(1 for line in f) - 1  # -1 für Header
    
    return jsonify({
        'csv_exists': exists,
        'csv_path': CSV_FILE,
        'measurement_count': count,
        'monitoring_active': monitoring_active
    })

@app.route('/start', methods=['POST'])
def api_start_monitoring():
    global monitoring_active, monitoring_thread, current_settings
    
    data = request.json or {}
    current_settings['interval'] = data.get('interval', 30)
    current_settings['threshold'] = data.get('threshold', 25.0)
    current_settings['email_enabled'] = data.get('email_settings') is not None
    
    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=run_monitoring_loop, daemon=True)
        monitoring_thread.start()
    
    return jsonify({'status': 'started', 'active': True})

@app.route('/stop', methods=['POST'])
def api_stop_monitoring():
    global monitoring_active
    monitoring_active = False
    return jsonify({'status': 'stopped', 'active': False})

@app.route('/test', methods=['POST'])
def api_run_single_test():
    global latest_measurement
    try:
        print("🔄 Starte manuellen Speedtest...")
        result = speedtest.run()
        
        if result:
            # CSV speichern
            csv_logger.write(result)
            latest_measurement = result
            
            # Grafiken aktualisieren
            if AUTO_UPDATE_GRAPHS:
                update_graphs()
            
            return jsonify(result)
        else:
            return jsonify({'error': 'Speedtest fehlgeschlagen'}), 500
    except Exception as e:
        print(f"❌ Fehler beim Test: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/settings', methods=['GET', 'POST'])
def api_settings():
    global current_settings
    
    if request.method == 'POST':
        data = request.json
        current_settings.update(data)
        return jsonify(current_settings)
    
    return jsonify(current_settings)

def get_graph_path(filename):
    # Holt den absoluten Pfad zur Grafik
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'graphs', filename)

@app.route('/graphs/speed-over-time', methods=['GET'])
def api_graph_speed():
    graph_path = get_graph_path('speed_over_time.png')
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    return jsonify({'error': 'Grafik nicht verfügbar'}), 404

@app.route('/graphs/ping-over-time', methods=['GET'])
def api_graph_ping():
    graph_path = get_graph_path('ping_over_time.png')
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    return jsonify({'error': 'Grafik nicht verfügbar'}), 404

@app.route('/graphs/statistics', methods=['GET'])
def api_graph_statistics():
    graph_path = get_graph_path('statistics.png')
    if os.path.exists(graph_path):
        return send_file(graph_path, mimetype='image/png')
    return jsonify({'error': 'Grafik nicht verfügbar'}), 404

@app.route('/graphs/list', methods=['GET'])
def api_list_graphs():
    graphs = []
    graph_files = {
        'speed_over_time.png': ('Geschwindigkeit über Zeit', '/graphs/speed-over-time'),
        'ping_over_time.png': ('Ping über Zeit', '/graphs/ping-over-time'),
        'statistics.png': ('Statistik-Übersicht', '/graphs/statistics')
    }
    for filename, (name, url) in graph_files.items():
        graph_path = get_graph_path(filename)
        if os.path.exists(graph_path):
            graphs.append({
                'name': name,
                'filename': filename,
                'url': url
            })
    return jsonify({'graphs': graphs})

def run_monitoring_loop():
    """Hauptschleife für kontinuierliche Überwachung"""
    global monitoring_active, latest_measurement
    
    while monitoring_active:
        try:
            print(f"\n🔄 Automatischer Test läuft...")
            result = speedtest.run()
            
            if result:
                latest_measurement = result
                print(f"Zeit: {result['time']} | Download: {result['download_Mbps']} Mbps | "
                      f"Upload: {result['upload_Mbps']} Mbps | Ping: {result['ping_ms']} ms")
                
                # CSV speichern
                csv_logger.write(result)
                
                # Geschwindigkeit prüfen
                check_speed_threshold(result['download_Mbps'])
                
                # Grafiken aktualisieren
                if AUTO_UPDATE_GRAPHS:
                    update_graphs()
            
            # Warte für das nächste Intervall
            time.sleep(current_settings['interval'] * 60)
            
        except Exception as e:
            print(f"❌ Fehler in Monitoring-Loop: {e}")
            time.sleep(60)

def start_api_server():
    """Startet den Flask API-Server"""
    print("\n" + "="*50)
    print("🌐 API-Server startet...")
    print(f"📁 CSV-Datei: {CSV_FILE}")
    print(f"📊 CSV existiert: {os.path.exists(CSV_FILE)}")
    print(f"🔧 API: http://localhost:5001")
    print(f"🎨 Frontend: http://localhost:5173")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5001, debug=False, use_reloader=False)

def start_frontend():
    """Startet das Svelte Frontend automatisch"""
    frontend_path = os.path.join(os.path.dirname(__file__), '..', 'frontend')
    
    if os.path.exists(frontend_path):
        print("🎨 Starte Frontend...")
        try:
            # Wechsle zum Frontend-Verzeichnis und starte npm
            os.chdir(frontend_path)
            
            # Starte npm run dev im Hintergrund
            if sys.platform == 'darwin' or sys.platform == 'linux':
                subprocess.Popen(['npm', 'run', 'dev'], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            else:  # Windows
                subprocess.Popen(['npm', 'run', 'dev'], 
                               shell=True,
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
            
            # Warte kurz und öffne Browser
            time.sleep(5)
            webbrowser.open('http://localhost:5173')
            print("✅ Frontend gestartet und Browser geöffnet")
            
            # Zurück zum ursprünglichen Verzeichnis
            os.chdir(os.path.join(os.path.dirname(__file__), '..'))
            
        except Exception as e:
            print(f"⚠️  Frontend konnte nicht gestartet werden: {e}")
            print("💡 Starte manuell mit: cd frontend && npm run dev")
    else:
        print("⚠️  Frontend-Verzeichnis nicht gefunden")

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
    # Starte API-Server in separatem Thread
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    
    print("\n✅ DaLohyn SpeedWatch läuft!")
    print("🌐 Frontend: http://localhost:5173")
    print("🔧 API: http://localhost:5001")
    print("💡 Teste die API: http://localhost:5001/status")
    
    # Gebe dem API-Server Zeit zum Starten
    time.sleep(2)
    
    # Starte Frontend automatisch
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    print("\nDrücke Ctrl+C zum Beenden\n")
    
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
