"""
Speedtest-Runner für DaLohyn-SpeedWatch
Führt Speedtests mit der Ookla CLI aus
"""

import subprocess
import json
from datetime import datetime


class SpeedtestRunner:
    """Führt Speedtests aus und verarbeitet die Ergebnisse"""
    
    def __init__(self):
        self.last_result = None
    
    def run(self):
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
            self.last_result = {
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'download_Mbps': round(data['download']['bandwidth'] / 125000, 2),
                'upload_Mbps': round(data['upload']['bandwidth'] / 125000, 2),
                'ping_ms': round(data['ping']['latency'], 2),
                'server': data['server']['name'],
                'server_location': data['server']['location'],
                'server_country': data['server']['country'],
                'ip': data['interface']['externalIp'],
                'packet_loss': data.get('packetLoss', 0),
            }  # <-- DIESE KLAMMER HAT GEFEHLT!
            
            return self.last_result
            
        except (json.JSONDecodeError, KeyError) as e:
            print(f"❌ Fehler beim Parsen der Speedtest-Daten: {e}")
            return None
    
    def format_result(self, result):
        """
        Formatiert Speedtest-Ergebnis für Terminal-Ausgabe
        
        Args:
            result: Dictionary mit Speedtest-Ergebnissen
            
        Returns:
            Formatierter String
        """
        return (f"⏰ Zeit: {result['time']} | "
                f"📥 Download: {result['download_Mbps']} Mbps | "
                f"📤 Upload: {result['upload_Mbps']} Mbps | "
                f"🏓 Ping: {result['ping_ms']} ms | "
                f"🖥️ Server: {result['server']} ({result['server_location']}, {result['server_country']}) | "
                f"🌐 IP: {result['ip']} | "
                f"📉 Packet Loss: {result['packet_loss']}%")
