import smtplib
import logging
import os
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables from .env file in project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

logger = logging.getLogger(__name__)

def send_email(email, subject, message):
    """
    Send email using Gmail SMTP
    Returns: True if successful, False otherwise
    """
    try:
        # Get credentials from environment variables
        sender = os.environ.get("SENDER_EMAIL")
        password = os.environ.get("SENDER_PASSWORD")

        if not sender or not password:
            logger.error("Email service not configured. Missing SENDER_EMAIL or SENDER_PASSWORD in environment variables.")
            return False

        # Create message with proper headers
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message, "plain"))

        # Connect to Gmail SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, email, msg.as_string())
        server.quit()

        logger.info(f"Email sent successfully to {email}")
        return True

    except smtplib.SMTPAuthenticationError as auth_error:
        logger.error(f"Gmail authentication failed for {email}. Check SENDER_EMAIL and SENDER_PASSWORD. Error: {str(auth_error)}")
        return False
    except smtplib.SMTPException as smtp_error:
        logger.error(f"SMTP server error when sending to {email}: {str(smtp_error)}")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        return False