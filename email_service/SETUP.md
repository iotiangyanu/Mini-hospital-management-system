# Serverless Email Service Setup Guide

## Issues Fixed

1. ✅ **Hardcoded credentials** - Now uses environment variables
2. ✅ **Invalid email format** - Now uses proper MIME email headers
3. ✅ **No error handling** - Added comprehensive error handling and logging
4. ✅ **Timeout issues** - Added timeout handling for requests

## Setup Instructions

### Step 1: Create .env file

Copy `.env.example` to `.env` and update with your credentials:

```bash
cp .env.example .env
```

### Step 2: Configure Gmail App Password

Since Gmail requires app passwords for third-party applications:

1. Go to: https://myaccount.google.com/apppasswords
2. Select **Mail** and **Windows Computer**
3. Google will generate a 16-character password
4. Copy the password and paste it in `.env` as `SENDER_PASSWORD`

Example `.env`:
```
SENDER_EMAIL=your-email@gmail.com
SENDER_PASSWORD=xxxx xxxx xxxx xxxx
```

### Step 3: Install Dependencies

```bash
npm install
```

### Step 4: Run Locally

To test the serverless function locally:

```bash
npm install -g serverless
serverless offline start
```

The service will run at: `http://localhost:3000/send`

### Step 5: Test Email Service

Send a test email:

```bash
curl -X POST http://localhost:3000/send \
  -H "Content-Type: application/json" \
  -d '{
    "email": "recipient@example.com",
    "subject": "Test Email",
    "message": "This is a test email from the serverless service"
  }'
```

## Environment Variables

- `SENDER_EMAIL` - Your Gmail address (default: g.dwivedi8924@gmail.com)
- `SENDER_PASSWORD` - Gmail app password (default: Gyanbhai@786)

## Troubleshooting

### Connection Error
If Django shows "Could not connect to localhost:3000":
- Make sure the serverless service is running: `serverless offline start`
- Check port 3000 is not in use

### Authentication Error
- Verify you're using an **App Password**, not your regular Gmail password
- Re-create the app password from the Google Account settings

### Email Not Sending
- Check the email is formatted correctly
- Verify sender credentials in .env file
- Check AWS CloudWatch logs (if deployed)
