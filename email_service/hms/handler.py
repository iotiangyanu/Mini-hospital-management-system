import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def send_email(event, context):
    try:
        body = json.loads(event["body"])

        email = body.get("email")
        subject = body.get("subject")
        message = body.get("message")

        # Get credentials from environment variables
        sender = os.environ.get("SENDER_EMAIL")
        password = os.environ.get("SENDER_PASSWORD")

        # Validate inputs
        if not email or not subject or not message:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing email, subject, or message"})
            }

        if not sender or not password:
            return {
                "statusCode": 500,
                "body": json.dumps({
                    "error": "Email service not configured. Missing SENDER_EMAIL or SENDER_PASSWORD in environment variables."
                })
            }

        # Create message with proper headers
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = email
        msg["Subject"] = subject

        msg.attach(MIMEText(message, "plain"))

        # Connect to Gmail SMTP server with detailed error handling
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, email, msg.as_string())
            server.quit()

            return {
                "statusCode": 200,
                "body": json.dumps({"message": "Email sent successfully"})
            }

        except smtplib.SMTPAuthenticationError as auth_error:
            error_msg = f"Gmail authentication failed. This usually means:\n"
            error_msg += "1. Email/password is incorrect\n"
            error_msg += "2. If 2FA is enabled, use an App Password (16-char) instead of regular password\n"
            error_msg += "3. Less secure app access is turned off\n"
            error_msg += f"Error details: {str(auth_error)}"
            return {
                "statusCode": 401,
                "body": json.dumps({"error": error_msg})
            }

        except smtplib.SMTPException as smtp_error:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"SMTP server error: {str(smtp_error)}"})
            }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON in request body"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Unexpected error: {str(e)}"})
        }