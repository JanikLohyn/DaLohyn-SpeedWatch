"""
Daten-Visualisierung für DaLohyn-SpeedWatch
Erstellt Grafiken aus den CSV-Logs
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os

# Style setzen (modern und clean)
plt.style.use('seaborn-v0_8-darkgrid')

class SpeedwatchVisualizer:
    """Erstellt Visualisierungen aus Speedtest-Daten"""
    
    def __init__(self, csv_file='Speedtest_log.csv'):
        self.csv_file = csv_file
        self.data = None
        
    def load_data(self):
        """Lädt CSV-Daten und konvertiert Zeitstempel"""
        if not os.path.exists(self.csv_file):
            print(f"❌ Datei {self.csv_file} nicht gefunden!")
            return False
        
        try:
            self.data = pd.read_csv(self.csv_file)
            self.data['time'] = pd.to_datetime(self.data['time'])
            print(f"✅ {len(self.data)} Messungen geladen")
            return True
        except Exception as e:
            print(f"❌ Fehler beim Laden: {e}")
            return False
    
    def plot_speed_over_time(self, save_path='graphs/speed_over_time.png'):
        """Erstellt Liniendiagramm: Download & Upload über Zeit"""
        if self.data is None or len(self.data) == 0:
            print("⚠️  Keine Daten vorhanden")
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Download und Upload plotten
        ax.plot(self.data['time'], self.data['download_Mbps'], 
                label='Download', color='#00D9FF', linewidth=2, marker='o', markersize=4)
        ax.plot(self.data['time'], self.data['upload_Mbps'], 
                label='Upload', color='#FF6B35', linewidth=2, marker='s', markersize=4)
        
        # Durchschnittslinie
        avg_download = self.data['download_Mbps'].mean()
        avg_upload = self.data['upload_Mbps'].mean()
        ax.axhline(y=avg_download, color='#00D9FF', linestyle='--', 
                   alpha=0.5, label=f'Ø Download: {avg_download:.1f} Mbps')
        ax.axhline(y=avg_upload, color='#FF6B35', linestyle='--', 
                   alpha=0.5, label=f'Ø Upload: {avg_upload:.1f} Mbps')
        
        # Styling
        ax.set_xlabel('Zeit', fontsize=12, fontweight='bold')
        ax.set_ylabel('Geschwindigkeit (Mbps)', fontsize=12, fontweight='bold')
        ax.set_title('Internet-Geschwindigkeit über Zeit', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # X-Achse formatieren
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        # Ordner erstellen falls nicht vorhanden
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Grafik gespeichert: {save_path}")
        plt.close()
    
    def plot_ping_over_time(self, save_path='graphs/ping_over_time.png'):
        """Erstellt Liniendiagramm: Ping über Zeit"""
        if self.data is None or len(self.data) == 0:
            return
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        # Ping plotten
        ax.plot(self.data['time'], self.data['ping_ms'], 
                label='Ping', color='#9D4EDD', linewidth=2, marker='o', markersize=4)
        
        # Durchschnitt
        avg_ping = self.data['ping_ms'].mean()
        ax.axhline(y=avg_ping, color='#9D4EDD', linestyle='--', 
                   alpha=0.5, label=f'Ø Ping: {avg_ping:.1f} ms')
        
        # Styling
        ax.set_xlabel('Zeit', fontsize=12, fontweight='bold')
        ax.set_ylabel('Ping (ms)', fontsize=12, fontweight='bold')
        ax.set_title('Ping-Latenz über Zeit', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # X-Achse formatieren
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m %H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Grafik gespeichert: {save_path}")
        plt.close()
    
    def plot_statistics(self, save_path='graphs/statistics.png'):
        """Erstellt Statistik-Übersicht"""
        if self.data is None or len(self.data) == 0:
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle('Speedtest Statistiken', fontsize=18, fontweight='bold', y=0.995)
        
        # 1. Download Histogram
        axes[0, 0].hist(self.data['download_Mbps'], bins=20, color='#00D9FF', edgecolor='black', alpha=0.7)
        axes[0, 0].set_xlabel('Download (Mbps)', fontweight='bold')
        axes[0, 0].set_ylabel('Häufigkeit', fontweight='bold')
        axes[0, 0].set_title('Download-Verteilung')
        axes[0, 0].axvline(self.data['download_Mbps'].mean(), color='red', 
                           linestyle='--', linewidth=2, label=f"Ø {self.data['download_Mbps'].mean():.1f} Mbps")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Upload Histogram
        axes[0, 1].hist(self.data['upload_Mbps'], bins=20, color='#FF6B35', edgecolor='black', alpha=0.7)
        axes[0, 1].set_xlabel('Upload (Mbps)', fontweight='bold')
        axes[0, 1].set_ylabel('Häufigkeit', fontweight='bold')
        axes[0, 1].set_title('Upload-Verteilung')
        axes[0, 1].axvline(self.data['upload_Mbps'].mean(), color='red', 
                           linestyle='--', linewidth=2, label=f"Ø {self.data['upload_Mbps'].mean():.1f} Mbps")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Ping Histogram
        axes[1, 0].hist(self.data['ping_ms'], bins=20, color='#9D4EDD', edgecolor='black', alpha=0.7)
        axes[1, 0].set_xlabel('Ping (ms)', fontweight='bold')
        axes[1, 0].set_ylabel('Häufigkeit', fontweight='bold')
        axes[1, 0].set_title('Ping-Verteilung')
        axes[1, 0].axvline(self.data['ping_ms'].mean(), color='red', 
                           linestyle='--', linewidth=2, label=f"Ø {self.data['ping_ms'].mean():.1f} ms")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Server-Verteilung (Top 5)
        server_counts = self.data['server'].value_counts().head(5)
        axes[1, 1].barh(server_counts.index, server_counts.values, color='#06FFA5', edgecolor='black')
        axes[1, 1].set_xlabel('Anzahl Tests', fontweight='bold')
        axes[1, 1].set_ylabel('Server', fontweight='bold')
        axes[1, 1].set_title('Top 5 Speedtest-Server')
        axes[1, 1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✅ Grafik gespeichert: {save_path}")
        plt.close()
    
    def generate_all_graphs(self):
        """Erstellt alle Grafiken"""
        if not self.load_data():
            return
        
        print("\n📊 Erstelle Visualisierungen...")
        print("=" * 50)
        
        self.plot_speed_over_time()
        self.plot_ping_over_time()
        self.plot_statistics()
        
        print("=" * 50)
        print("✅ Alle Grafiken erfolgreich erstellt!")
        print(f"📁 Gespeichert in: graphs/")


# ============================================================================
# HAUPTPROGRAMM
# ============================================================================
if __name__ == "__main__":
    print("🎨 DaLohyn-SpeedWatch Visualizer")
    print("=" * 50)
    
    visualizer = SpeedwatchVisualizer()
    visualizer.generate_all_graphs()
