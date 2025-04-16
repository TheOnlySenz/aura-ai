import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.service = os.getenv('EMAIL_SERVICE', 'SMTP')
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.use_tls = os.getenv('SMTP_USE_TLS', 'True').lower() == 'true'
        self.username = os.getenv('SMTP_USERNAME')
        self.password = os.getenv('SMTP_PASSWORD')
        
    def send_email(self, to_email: str, subject: str, body: str, html: Optional[str] = None) -> Dict:
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.username
            message['To'] = to_email
            message['Subject'] = subject
            
            # Add body
            if html:
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html, 'html'))
            else:
                message.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.username, self.password)
                server.send_message(message)
            
            logger.info(f"Email sent successfully to {to_email}")
            return {
                'status': 'success',
                'message': 'Email sent successfully',
                'to': to_email,
                'subject': subject
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }

def get_email_service():
    return EmailService()
