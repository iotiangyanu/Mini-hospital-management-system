#!/usr/bin/env python3
"""
Gmail App Password Setup Script for Mini HMS Email Service
This script helps configure Gmail authentication for the email service.
"""

import os
import subprocess
import webbrowser
import time
import sys
import requests
from pathlib import Path

# Colors for terminal output
BLUE = '\033[94m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{text.center(60)}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")

def print_error(text):
    print(f"{RED}✗ {text}{RESET}")

def print_warning(text):
    print(f"{YELLOW}⚠ {text}{RESET}")

def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")

def check_env_file():
    """Check if .env file exists"""
    env_path = Path("c:\\Users\\hp\\Desktop\\pythondjango\\email_service\\hms\\.env")
    return env_path.exists()

def get_app_password():
    """Prompt user for Gmail app password"""
    print_info("Opening Google App Passwords page in your browser...")
    print("(You will need to be logged into your Gmail account)\n")
    
    webbrowser.open("https://myaccount.google.com/apppasswords")
    
    print_warning("Steps in Google Account:")
    print("  1. Select 'Mail' from the dropdown")
    print("  2. Select 'Windows Computer'")
    print("  3. Click 'Generate'")
    print("  4. Copy the 16-character password (with spaces)")
    print()
    
    app_password = input(f"{YELLOW}Paste your 16-character app password here: {RESET}").strip()
    
    if len(app_password.replace(" ", "")) != 16:
        print_error("Invalid app password format. Should be 16 characters (with spaces).")
        return None
    
    return app_password

def update_env_file(email, app_password):
    """Update .env file with new credentials"""
    env_path = Path("c:\\Users\\hp\\Desktop\\pythondjango\\email_service\\hms\\.env")
    
    env_content = f"""SENDER_EMAIL={email}
SENDER_PASSWORD={app_password}
"""
    
    try:
        with open(env_path, 'w') as f:
            f.write(env_content)
        print_success(f"Updated .env file with email: {email}")
        return True
    except Exception as e:
        print_error(f"Could not update .env file: {str(e)}")
        return False

def stop_serverless():
    """Stop running serverless service"""
    print_info("Stopping existing serverless service...")
    try:
        os.system("taskkill /F /IM node.exe > nul 2>&1")
        time.sleep(2)
        print_success("Serverless service stopped")
        return True
    except:
        print_warning("Could not stop serverless service (may not be running)")
        return True

def start_serverless():
    """Start serverless offline service"""
    print_info("Starting serverless email service...")
    os.chdir("c:\\Users\\hp\\Desktop\\pythondjango\\email_service\\hms")
    
    # Start in background
    subprocess.Popen(["serverless", "offline", "start"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL)
    
    print_info("Waiting for service to start...")
    time.sleep(5)
    
    # Check if running
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 3000))
        sock.close()
        
        if result == 0:
            print_success("Serverless service started on port 3000")
            return True
        else:
            print_error("Service failed to start on port 3000")
            return False
    except:
        print_error("Could not verify service status")
        return False

def test_email_service(test_email):
    """Test if email service is working"""
    print_info("Testing email service...")
    
    try:
        response = requests.post(
            'http://localhost:3000/dev/send',
            json={
                'email': test_email,
                'subject': 'Mini HMS - Email Service Test',
                'message': 'This is a test email from your Mini Hospital Management System.\n\nIf you received this, the email service is working correctly!'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            print_success("Email service test successful!")
            print_info(f"A test email has been sent to {test_email}")
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            print_error(f"Email service error: {error_msg}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_error("Could not connect to email service. Make sure serverless is running.")
        return False
    except Exception as e:
        print_error(f"Error testing email service: {str(e)}")
        return False

def main():
    print_header("Mini HMS Email Service Setup")
    
    print_info("This script will help you configure Gmail authentication for the email service.\n")
    
    # Get email
    email = input(f"{YELLOW}Enter your Gmail address: {RESET}").strip()
    
    # Get app password
    app_password = get_app_password()
    if not app_password:
        print_error("Setup cancelled.")
        return False
    
    # Update .env file
    if not update_env_file(email, app_password):
        return False
    
    # Stop existing service
    stop_serverless()
    
    # Start serverless service
    if not start_serverless():
        print_error("Could not start serverless service")
        print_warning("Try running manually: cd c:\\Users\\hp\\Desktop\\pythondjango\\email_service\\hms && serverless offline start")
        return False
    
    # Test email service
    test_email = input(f"\n{YELLOW}Enter an email to test the service: {RESET}").strip()
    if not test_email_service(test_email):
        print_warning("Email service test failed. Check the error message above.")
        return False
    
    print_header("Setup Complete! ✓")
    print_success("Your email service is now configured and running!")
    print_info("You can now:")
    print("  • Register as a doctor or patient (welcome email will be sent)")
    print("  • Book appointments (confirmation emails will be sent)")
    print("  • All emails go to the configured Gmail address")
    print()
    print_warning("Keep the serverless service running in the background!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)
