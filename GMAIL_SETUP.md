# Gmail API Setup Guide

This guide will walk you through setting up Gmail API access for the TLi Trading Strategy Management Tool.

## Overview

The application uses Google Gmail API to:
- Connect to tli.strategy.app@gmail.com
- Fetch forwarded emails automatically
- Parse trading levels and symbols from emails
- Store extracted data in the database

## Prerequisites

- Python 3.7 or higher
- A Google Account (tli.strategy.app@gmail.com)
- Access to Google Cloud Console

## Step 1: Enable Gmail API in Google Cloud Console

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with the Google account (tli.strategy.app@gmail.com)
3. Click on the project dropdown at the top of the page
4. Click "New Project"
5. Name your project (e.g., "TLi Trading Tool")
6. Click "Create"

### 1.2 Enable Gmail API

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click on "Gmail API" in the results
4. Click the "Enable" button
5. Wait for the API to be enabled (this may take a few seconds)

## Step 2: Create OAuth 2.0 Credentials

### 2.1 Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (or "Internal" if using Google Workspace)
3. Click "Create"
4. Fill in the required information:
   - **App name**: TLi Trading Tool
   - **User support email**: Your email address
   - **Developer contact email**: Your email address
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Filter for Gmail API and select:
   - `https://www.googleapis.com/auth/gmail.readonly` (Read-only access to Gmail)
8. Click "Update" and then "Save and Continue"
9. On the "Test users" page, click "Add Users"
10. Add tli.strategy.app@gmail.com as a test user
11. Click "Save and Continue"
12. Review the summary and click "Back to Dashboard"

### 2.2 Create OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "+ Create Credentials" at the top
3. Select "OAuth client ID"
4. Choose "Desktop app" as the application type
5. Name it "TLi Trading Tool Desktop Client"
6. Click "Create"
7. A dialog will appear with your client ID and client secret
8. Click "Download JSON"
9. Save the downloaded file as `credentials.json`

## Step 3: Install the Application

### 3.1 Install Dependencies

```bash
cd /path/to/Trading-tool-
pip install -r requirements.txt
```

### 3.2 Configure Environment Variables

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and configure:
```bash
# Flask Configuration
SECRET_KEY=your-secure-random-secret-key-here
FLASK_DEBUG=False

# Gmail API Configuration
GMAIL_USER_EMAIL=tli.strategy.app@gmail.com
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle
```

### 3.3 Place credentials.json

1. Copy the downloaded `credentials.json` file to the project root directory:
```bash
cp ~/Downloads/credentials.json /path/to/Trading-tool-/
```

2. Verify the file is in place:
```bash
ls -la credentials.json
```

## Step 4: Authenticate the Application

### 4.1 First-Time Authentication

1. Run the Gmail client test:
```bash
python gmail_client.py
```

2. A browser window will open automatically
3. Sign in with tli.strategy.app@gmail.com
4. Review the permissions requested:
   - "Read emails from Gmail"
5. Click "Allow" to grant access
6. You should see a success message in the browser
7. Return to the terminal - you should see:
```
✅ Gmail API connection successful!
```

8. A `token.pickle` file will be created automatically
   - This file stores your authentication token
   - It will be reused for future requests
   - The token will be automatically refreshed when needed

### 4.2 Verify Connection

After authentication, the test script will:
1. Connect to Gmail
2. Display your email address
3. Show total message count
4. Fetch recent forwarded emails
5. Display email subjects, senders, and dates

## Step 5: Use Gmail Integration in the App

### 5.1 Start the Application

```bash
python app.py
```

### 5.2 Access Gmail Features

1. Open your browser to `http://localhost:5000`
2. Navigate to "Email Parser"
3. Click "Fetch from Gmail" button (new feature)
4. The app will:
   - Connect to Gmail API
   - Fetch recent forwarded emails
   - Parse trading levels automatically
   - Save data to database

## Security Best Practices

### ⚠️ Important Security Notes

1. **Never commit credentials to Git**
   - `credentials.json` is in `.gitignore`
   - `token.pickle` is in `.gitignore`
   - Keep these files secure

2. **Protect your credentials**
   - Store `credentials.json` securely
   - Don't share it with anyone
   - Don't upload it to public repositories

3. **Use environment variables**
   - Sensitive configuration in `.env`
   - `.env` is excluded from Git
   - Use `.env.example` as a template only

4. **Token security**
   - `token.pickle` contains access tokens
   - Treat it like a password
   - If compromised, revoke access in Google Console

5. **Read-only access**
   - The app only requests read permission
   - It cannot send emails or modify your mailbox
   - This minimizes security risk

## Troubleshooting

### Problem: "credentials.json not found"

**Solution:**
- Verify `credentials.json` is in the project root directory
- Check the path in `.env` file matches the actual location
- Re-download from Google Cloud Console if needed

### Problem: "Invalid grant" or "Token expired"

**Solution:**
1. Delete the token file:
```bash
rm token.pickle
```
2. Run authentication again:
```bash
python gmail_client.py
```

### Problem: "Access blocked: This app's request is invalid"

**Solution:**
- Ensure OAuth consent screen is configured correctly
- Add tli.strategy.app@gmail.com as a test user
- Verify Gmail API is enabled in Google Cloud Console

### Problem: "The user has not granted the app..."

**Solution:**
- Complete the OAuth consent screen configuration
- Ensure all required scopes are selected
- Re-authenticate with the correct Google account

### Problem: No forwarded emails found

**Solution:**
- Check that emails are actually forwarded to tli.strategy.app@gmail.com
- Verify emails have "Fwd:" or "FW:" in the subject
- Increase `days_back` parameter to search further back
- Try searching with custom query: `client.search_emails("subject:Fwd")`

## API Quotas and Limits

Gmail API has usage limits:
- **Daily API calls**: 1,000,000,000 quota units per day
- **Read operations**: 250 quota units per request
- **Typical usage**: ~10,000 emails = 2,500 quota units

For this application, normal usage is well within limits.

## Advanced Configuration

### Custom Email Search

You can search emails with custom queries:

```python
from gmail_client import get_gmail_client

client = get_gmail_client()
client.authenticate()

# Search by sender
emails = client.search_emails("from:specific@email.com")

# Search by date range
emails = client.search_emails("after:2024/01/01 before:2024/12/31")

# Combine filters
emails = client.search_emails("from:sender@email.com subject:trading")
```

### Adjust Fetch Parameters

In the application code, you can modify:

```python
# Fetch more emails
emails = client.get_forwarded_emails(max_results=50)

# Look further back
emails = client.get_forwarded_emails(days_back=30)
```

## Revoking Access

To revoke the application's access to Gmail:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Navigate to "Third-party apps with account access"
3. Find "TLi Trading Tool"
4. Click "Remove Access"
5. Delete `token.pickle` from the project directory

## Next Steps

After setup:
1. ✅ Test the Gmail connection
2. ✅ Fetch recent forwarded emails
3. ✅ Parse trading levels automatically
4. ✅ Set up alerts for key price levels
5. ✅ Track positions systematically

## Support

For issues:
- Check this guide's troubleshooting section
- Review [Gmail API documentation](https://developers.google.com/gmail/api)
- Check [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)

## References

- [Gmail API Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Gmail API Reference](https://developers.google.com/gmail/api/reference/rest)
- [OAuth 2.0 Scopes for Google APIs](https://developers.google.com/identity/protocols/oauth2/scopes)
