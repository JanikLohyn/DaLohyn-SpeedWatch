import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class EmailAlert:
    def __init__(self, smtp_server, smtp_port, email_from, email_password, email_to):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email_from = email_from
        self.email_password = email_password
        self.email_to = email_to
    
    def send_alert(self, avg_speed, measurements, threshold, num_measurements):
        """Sendet eine E-Mail-Warnung bei langsamer Verbindung"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_from
            msg['To'] = self.email_to
            msg['Subject'] = '⚠️ DaLohyn-SpeedWatch: Langsame Verbindung erkannt!'
            
            body = f"""
Warnung: Deine Internetverbindung ist langsam!

Durchschnittliche Download-Geschwindigkeit der letzten {num_measurements} Messungen:
{avg_speed:.2f} Mbps (Grenzwert: {threshold} Mbps)

Details der letzten Messungen:
"""
            for i, speed in enumerate(measurements, 1):
                body += f"\nMessung {i}: {speed:.2f} Mbps"
            
            body += f"\n\nZeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            body += "\n\n-- DaLohyn-SpeedWatch"
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_from, self.email_password)
            server.send_message(msg)
            server.quit()
            
            print("✉️  Warn-E-Mail erfolgreich gesendet!")
            return True
        except Exception as e:
            print(f"Fehler beim E-Mail-Versand: {e}")
            return False
