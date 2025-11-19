"""
CSV-Logger für DaLohyn-SpeedWatch
Speichert Speedtest-Ergebnisse in CSV-Datei
"""

import csv
import os


class CSVLogger:
    """Verwaltet das Schreiben von Speedtest-Ergebnissen in CSV"""
    
    def __init__(self, filename):
        self.filename = filename
    
    def write(self, data):
        """
        Schreibt Messergebnisse in die CSV-Datei.
        Erstellt automatisch Header, falls Datei neu ist.
        
        Args:
            data: Dictionary mit Messergebnissen
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        try:
            # Prüfe ob Datei existiert und nicht leer ist
            file_exists = os.path.exists(self.filename) and os.path.getsize(self.filename) > 0
            
            # Öffne Datei im Append-Modus (anhängen)
            with open(self.filename, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                
                # Schreibe Header nur wenn Datei neu ist
                if not file_exists:
                    writer.writeheader()
                
                # Schreibe Datenzeile
                writer.writerow(data)
            
            return True
        except Exception as e:
            print(f"❌ Fehler beim Schreiben in CSV: {e}")
            return False
    
    def get_recent_measurements(self, count=10):
        """
        Liest die letzten N Messungen aus der CSV
        
        Args:
            count: Anzahl der zu lesenden Messungen
            
        Returns:
            Liste von Dictionaries mit Messungen
        """
        try:
            if not os.path.exists(self.filename):
                return []
            
            with open(self.filename, 'r') as f:
                reader = csv.DictReader(f)
                measurements = list(reader)
                return measurements[-count:] if len(measurements) > count else measurements
        except Exception as e:
            print(f"❌ Fehler beim Lesen der CSV: {e}")
            return []
