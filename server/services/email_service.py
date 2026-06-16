import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        """
        Sends an email using Gmail SMTP if credentials are provided in environment variables.
        Otherwise, falls back to logging the email to the console (mock).
        """
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))
        
        if not smtp_user or not smtp_password:
            logger.warning("SMTP credentials not found in environment variables. Falling back to mock email.")
            EmailService._send_mock_email(to_email, subject, body)
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            
            server.sendmail(smtp_user, to_email, msg.as_string())
            server.quit()
            
            logger.info(f"Successfully sent email to {to_email} with subject: {subject}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email} via SMTP. Error: {str(e)}")
            logger.info("Falling back to mock email due to SMTP error.")
            EmailService._send_mock_email(to_email, subject, body)

    @staticmethod
    def _send_mock_email(to_email: str, subject: str, body: str):
        email_content = f"""
==================================================
EMAIL NOTIFICATION (MOCK)
--------------------------------------------------
To:      {to_email}
Subject: {subject}
--------------------------------------------------
{body}
==================================================
"""
        print(email_content)
        logger.info(f"Mock email sent to {to_email} with subject: {subject}")
