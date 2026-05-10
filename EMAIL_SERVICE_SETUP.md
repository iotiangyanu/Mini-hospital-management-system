# Mini HMS Email Service - Configuration Guide

## 🚀 Status
✅ Email service is now running on `http://localhost:3000`

## 📋 Issues Fixed
1. **Port Mismatch** - Updated from 6001 to 3000
2. **Hardcoded Credentials** - Removed from `serverless.yml` 
3. **Environment Variables** - Now properly configured via `.env`

## 🔧 Complete Setup Steps

### Step 1: Get Gmail App Password
1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Windows Computer** from the dropdowns
3. Click **Generate**
4. Google will show a 16-character password (with spaces)
5. Copy this password

### Step 2: Configure .env File
Edit `email_service/hms/.env` and replace with your credentials:

```env
SENDER_EMAIL=your-gmail-account@gmail.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx
```

**Example:**
```env
SENDER_EMAIL=john.doe@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
```

### Step 3: Restart Email Service
If the service is already running, kill it and restart:

```bash
# Kill the running service
taskkill /F /IM node.exe

# Navigate to email service directory
cd email_service/hms

# Start the service
serverless offline start
```

### Step 4: Test Email Service
Send a test email by running the registration flow or use this Python test:

```python
import requests

response = requests.post(
    'http://localhost:3000/dev/send',
    json={
        'email': 'test@example.com',
        'subject': 'HMS Test Email',
        'message': 'This is a test email'
    },
    timeout=10
)

print(response.status_code)
print(response.json())
```

## 📧 What Happens During Registration
1. User fills registration form
2. System generates a random 5-digit OTP
3. OTP is saved in `TemporaryRegistration` table
4. Email is sent via serverless function to the user's email
5. User enters OTP to complete registration

## 🐛 Troubleshooting

### "Failed to send OTP email"
- **Check 1:** Is serverless service running? → `http://localhost:3000/dev/send` should be accessible
- **Check 2:** Is `.env` configured with valid Gmail credentials?
- **Check 3:** Have you enabled 2FA on Gmail? → Use App Password, not regular password
- **Check 4:** Is firewall blocking port 3000?

### "Email service request timed out"
- Increase timeout in `utils/email_service.py` (currently 10 seconds)
- Check internet connection
- Verify Gmail SMTP server is accessible

### "Authentication failed"
- Gmail password is incorrect or expired
- 2FA enabled but using regular password instead of App Password
- Go back to Step 1 and get a new App Password

## 📝 Important Notes
- OTP is valid for **42 seconds**
- Do NOT commit `.env` file to Git (it has credentials)
- The `.env` file is in `.gitignore` by default
- Keep your Gmail App Password secure - don't share it
