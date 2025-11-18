import subprocess
import json
import csv 
import os
import time 
from datetime import datetime


CSV_FILE = 'Speedtest_log.csv'
print("welcome to DaLohyn-SpeedWatch")
print("Ein Python-Tool zur automatischen Überwachung der Internetgeschwindigkeit. ")
print("Misst in konfigurierbaren Intervallen Download, Upload und Ping via Ookla Speedtest CLI und speichert die Ergebnisse in einer CSV-Datei zur späteren Auswertung.")
print("Developed by DaLohyn")
print("Version 1.0.0")
print("----------------------------------------------------------------------------------------")
print("Gib die Messintervalle in Minuten an (Standard: 60 Minuten): ")

while True:
    try:
        interval_input = int(input("Intervall (Minuten): "))
        print("Messintervall gesetzt auf " + str(interval_input) + " Minuten.")
        check_intervall = interval_input * 60
        break
    except ValueError:
        print("Ungültige Eingabe. Bitte eine Zahl eingeben.")


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
            'ip': data['interface']['externalIp']
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
        print(f"Zeit: {result['time']} | Download: {result['download_Mbps']} Mbps | Upload: {result['upload_Mbps']} Mbps | Ping: {result['ping_ms']} ms | Server: {result['server']} ({result['server_location']}, {result['server_country']}) | IP: {result['ip']}")
        write_to_csv(result)
    time.sleep(check_intervall)
