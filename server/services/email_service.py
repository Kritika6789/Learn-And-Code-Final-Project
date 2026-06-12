import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, body: str):
        """
        Mock email service that logs the email content to the console.
        In a production environment, this would integrate with an SMTP server or email API like SendGrid.
        """
        email_content = f"""
==================================================
EMAIL NOTIFICATION
--------------------------------------------------
To:      {to_email}
Subject: {subject}
--------------------------------------------------
{body}
==================================================
"""
        # Print to console for easy visibility during development/testing
        print(email_content)
        # Log to application logs as well
        logger.info(f"Mock email sent to {to_email} with subject: {subject}")
