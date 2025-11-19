import subprocess
import json
import csv 
import os
import time 
import getpass
from datetime import datetime
from email_alert import EmailAlert

# Konfiguration
CSV_FILE = 'Speedtest_log.csv'
THRESHOLD_MBPS = 25
MEASUREMENTS_TO_CHECK = 3

print("welcome to DaLohyn-SpeedWatch")
print("Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit.")
print("Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.")
print("Developed by DaLohyn")
print("Version 1.0.0")
print("----------------------------------------------------------------------------------------")
while True:
    try:
        consent = input("Mit der Nutzung dieses Tools erklärst du dich damit einverstanden, dass deine Internetgeschwindigkeitsdaten lokal gespeichert werden. Fortfahren? (ja/nein): ")
        if consent.lower() == "ja":
            break
        elif consent.lower() == "nein":
            print("Nutzung abgelehnt. Beende das Programm.")
        exit()
    except ValueError:
        print("Ungültige Eingabe. Bitte 'ja' oder 'nein' eingeben.")
print("----------------------------------------------------------------------------------------")
while True:
    try:
        consent_email = input("Möchtest du E-Mail-Warnungen bei langsamer Verbindung erhalten? (ja/nein): ")
        if consent_email.lower() == "ja":
            # E-Mail Konfiguration
            EMAIL_FROM = input("E-Mail Absender: ")
            EMAIL_PASSWORD = getpass.getpass("E-Mail Passwort: ")
            EMAIL_TO = input("E-Mail Empfänger: ")
            SMTP_SERVER = input("SMTP Server (ohne http://): ")
            SMTP_PORT = int(input("SMTP Port (z.B. 587): "))
            
            # Threshold-Eingabe
            while True:
                try:
                    threshold_input = float(input(f"Gib den Download-Geschwindigkeits-Grenzwert in Mbps an (Standard: {THRESHOLD_MBPS} Mbps): "))
                    THRESHOLD_MBPS = threshold_input
                    print(f"Grenzwert gesetzt auf {THRESHOLD_MBPS} Mbps.")
                    break
                except ValueError:
                    print("Ungültige Eingabe. Bitte eine Zahl eingeben.")
            
            # Erstelle E-Mail-Alert-Objekt
            email_alert = EmailAlert(SMTP_SERVER, SMTP_PORT, EMAIL_FROM, EMAIL_PASSWORD, EMAIL_TO)
            break
            
        elif consent_email.lower() == "nein":
            email_alert = None
            print("E-Mail-Warnungen deaktiviert.")
            break
            
        else:
            print("Bitte 'ja' oder 'nein' eingeben.")
            
    except ValueError:
        print("Ungültige Eingabe.")

print("----------------------------------------------------------------------------------------")







print("----------------------------------------------------------------------------------------")
print("Gib die Messintervalle in Minuten an (Standard: 60 Minuten): ")

while True:
    try:
        interval_input = int(input("Intervall (Minuten, min. 5): "))
        if interval_input < 5:
            print("⚠️  Warnung: Intervall unter 5 Minuten kann zu Rate-Limits führen!")
            confirm = input("Trotzdem fortfahren? (ja/nein): ")
            if confirm.lower() != "ja":
                continue
        print("Messintervall gesetzt auf " + str(interval_input) + " Minuten.")
        check_intervall = interval_input * 60
        break
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")

# Liste für die letzten Messungen
recent_downloads = []

def check_speed_threshold(download_speed):
    """Prüft ob Durchschnitt unter Grenzwert liegt"""
    recent_downloads.append(download_speed)
    
    if len(recent_downloads) > MEASUREMENTS_TO_CHECK:
        recent_downloads.pop(0)
    
    if len(recent_downloads) == MEASUREMENTS_TO_CHECK:
        avg_speed = sum(recent_downloads) / len(recent_downloads)
        
        if avg_speed < THRESHOLD_MBPS:
            print(f"⚠️  WARNUNG: Durchschnitt der letzten {MEASUREMENTS_TO_CHECK} Messungen unter {THRESHOLD_MBPS} Mbps!")
            email_alert.send_alert(avg_speed, recent_downloads.copy(), THRESHOLD_MBPS, MEASUREMENTS_TO_CHECK)
            return True
    
    return False

def run_speedtest():
    print("Starte Speedtest...")
    result = subprocess.run(['speedtest', '--format=json', '--accept-license'], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Fehler beim Speedtest: {result.stderr}")
        return None
    
    try:
        data = json.loads(result.stdout)
        return {
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'download_Mbps': round(data['download']['bandwidth'] / 125000, 2),
            'upload_Mbps': round(data['upload']['bandwidth'] / 125000, 2),
            'ping_ms': round(data['ping']['latency'], 2),
            'server': data['server']['name'],
            'server_location': data['server']['location'],
            'server_country': data['server']['country'],
            'ip': data['interface']['externalIp'],
            'packet_loss': data.get('packetLoss', 0),
        }
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Fehler beim Parsen: {e}")
        return None

def write_to_csv(data):
    file_exists = os.path.exists(CSV_FILE) and os.path.getsize(CSV_FILE) > 0
    
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

while True:
    result = run_speedtest()
    if result:
        print(f"Zeit: {result['time']} | Download: {result['download_Mbps']} Mbps | Upload: {result['upload_Mbps']} Mbps | Ping: {result['ping_ms']} ms | Server: {result['server']} ({result['server_location']}, {result['server_country']}) | IP: {result['ip']} | Packet Loss: {result['packet_loss']}%")
        write_to_csv(result)
        check_speed_threshold(result['download_Mbps'])
    time.sleep(check_intervall)
