import os
import subprocess

class MacOSNotification:
    """Sendet native macOS Benachrichtigungen"""
    
    def __init__(self, app_name="DaLohyn-SpeedWatch"):
        self.app_name = app_name
    
    def send_notification(self, title, message, subtitle=None, sound=True):
        """
        Sendet eine macOS Notification
        
        Args:
            title: Titel der Benachrichtigung
            message: Hauptnachricht
            subtitle: Optional - Untertitel
            sound: Bool - Soll ein Sound abgespielt werden?
        """
        # Escape Anführungszeichen in Strings
        title = title.replace('"', '\\"')
        message = message.replace('"', '\\"')
        
        # AppleScript zusammenbauen
        script = f'display notification "{message}" with title "{title}"'
        
        if subtitle:
            subtitle = subtitle.replace('"', '\\"')
            script = f'display notification "{message}" with title "{title}" subtitle "{subtitle}"'
        
        if sound:
            script += ' sound name "Glass"'
        
        # Notification senden
        try:
            os.system(f"osascript -e '{script}'")
            return True
        except Exception as e:
            print(f"Fehler beim Senden der Notification: {e}")
            return False
    
    def send_speed_alert(self, avg_speed, threshold, measurements):
        """Spezielle Warnung für langsame Verbindung"""
        title = "⚠️ Langsame Internetverbindung!"
        message = f"Durchschnitt: {avg_speed:.2f} Mbps (unter {threshold} Mbps)"
        subtitle = f"Letzte 3 Messungen: {', '.join([f'{m:.1f}' for m in measurements])} Mbps"
        
        self.send_notification(title, message, subtitle, sound=True)
    
    def send_test_complete(self, download, upload, ping):
        """Notification nach erfolgreichem Test"""
        title = "✅ Speedtest abgeschlossen"
        message = f"↓ {download} Mbps | ↑ {upload} Mbps | Ping: {ping} ms"
        
        self.send_notification(title, message, sound=False)
