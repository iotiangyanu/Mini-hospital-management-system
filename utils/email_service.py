import requests
import logging

logger = logging.getLogger(__name__)

def send_email(email, subject, message):
    """
    Send email using serverless email service
    Returns: True if successful, False otherwise
    """
    try:
        # Use /dev/send for serverless-offline development
        url = "http://localhost:3000/dev/send"

        data = {
            "email": email,
            "subject": subject,
            "message": message
        }

        response = requests.post(url, json=data, timeout=10)

        if response.status_code == 200:
            logger.info(f"Email sent successfully to {email}")
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            logger.error(f"Failed to send email to {email}: {error_msg}")
            return False

    except requests.exceptions.ConnectionError:
        logger.error("Could not connect to email service. Make sure serverless service is running on port 3000.")
        return False
    except requests.exceptions.Timeout:
        logger.error("Email service request timed out")
        return False
    except Exception as e:
        logger.error(f"Error sending email to {email}: {str(e)}")
        return False