# OAuth Login System Setup Guide

This guide explains how to set up the Google OAuth login system for the TLi Trading Strategy Management Tool.

## Overview

The application now uses Google OAuth 2.0 for user authentication. This provides:
- Secure login with Google accounts
- Automatic Gmail API access for email syncing
- User-specific data isolation
- No need for separate password management

## Prerequisites

1. A Google Cloud Platform account
2. Python 3.7 or higher installed
3. The application dependencies installed (`pip install -r requirements.txt`)

## Step 1: Create Google OAuth Credentials

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top of the page
4. Click "New Project"
5. Name your project (e.g., "TLi Trading Tool")
6. Click "Create"

### 1.2 Enable Required APIs

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Gmail API** (for email access)
   - You may also want to enable "Google+ API" for profile information

### 1.3 Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select user type:
   - **External**: For personal use or public applications
   - **Internal**: If using Google Workspace (only for your organization)
3. Click "Create"
4. Fill in the required information:
   - **App name**: TLi Trading Tool
   - **User support email**: Your email address
   - **Developer contact email**: Your email address
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add the following scopes:
   - `openid`
   - `email`
   - `profile`
   - `https://www.googleapis.com/auth/gmail.readonly`
8. Click "Update" and then "Save and Continue"
9. On the "Test users" page (for External apps):
   - Click "Add Users"
   - Add the email addresses that will use the app during testing
10. Review the summary and click "Back to Dashboard"

### 1.4 Create OAuth 2.0 Client ID

1. Go to "APIs & Services" > "Credentials"
2. Click "+ Create Credentials" at the top
3. Select "OAuth client ID"
4. Choose "Web application" as the application type
5. Name it "TLi Trading Tool Web Client"
6. Under "Authorized redirect URIs", add:
   - `http://localhost:5000/login/callback` (for local development)
   - Add your production URL if deploying (e.g., `https://yourdomain.com/login/callback`)
7. Click "Create"
8. A dialog will appear with your client ID and client secret
9. **IMPORTANT**: Copy both values - you'll need them in the next step

## Step 2: Configure the Application

### 2.1 Create Environment File

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OAuth credentials:
```bash
# Flask Configuration
SECRET_KEY=your-secure-random-secret-key-here-change-this
FLASK_DEBUG=False

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Gmail API Configuration (optional for backward compatibility)
GMAIL_USER_EMAIL=tli.strategy.app@gmail.com
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.pickle
```

3. Generate a secure secret key:
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```
   Replace `your-secure-random-secret-key-here-change-this` with the generated key.

### 2.2 Set File Permissions

Make sure your `.env` file is secure:
```bash
chmod 600 .env
```

## Step 3: Initialize the Database

The application will automatically create the database on first run, but you can initialize it manually:

```bash
python3 app.py
# Press Ctrl+C after it starts
```

Or use the Flask CLI:
```bash
flask --app app init-db
```

## Step 4: Run the Application

### Development Mode

```bash
FLASK_DEBUG=true python3 app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
python3 app.py
```

## Step 5: First Login

1. Open your browser and navigate to `http://localhost:5000`
2. You'll be redirected to the login page
3. Click "Sign in with Google"
4. Choose your Google account
5. Review the permissions:
   - Read your email address and basic profile info
   - Read emails from Gmail
6. Click "Allow"
7. You'll be redirected back to the application
8. You're now logged in!

## How It Works

### User Authentication Flow

1. User clicks "Sign in with Google"
2. App redirects to Google's OAuth page
3. User authorizes the app
4. Google redirects back with an authorization code
5. App exchanges code for access tokens
6. App verifies the user's identity
7. App creates or updates user record in database
8. User is logged in and redirected to dashboard

### Email Syncing

When you use the Gmail integration features:
1. The app uses the OAuth tokens stored in your user profile
2. It authenticates with Gmail API using your credentials
3. It fetches emails from your authorized Gmail account
4. All data is linked to your user account

### Data Isolation

- Each user has their own isolated data
- Positions, alerts, price levels, and comments are user-specific
- You can only see and modify your own data
- Multiple users can use the app simultaneously

## Security Best Practices

### 1. Protect Your Credentials

- **Never commit** `.env` file to Git (it's already in `.gitignore`)
- **Never share** your OAuth client secret
- Store `.env` securely with restricted file permissions

### 2. Use Strong Secret Keys

- Generate random secret keys (don't use the example)
- Use different keys for development and production
- Rotate keys periodically

### 3. Secure Your Environment

- Use HTTPS in production (OAuth requires it)
- Set `FLASK_DEBUG=False` in production
- Use environment variables, not hardcoded values
- Consider using a secrets management service for production

### 4. OAuth Scope Management

- The app requests minimal required scopes
- Gmail access is read-only (cannot send or delete emails)
- Users must explicitly grant permissions

### 5. Token Security

- OAuth tokens are stored securely in the database
- Tokens are encrypted at rest (use database encryption in production)
- Tokens automatically refresh when expired

## Troubleshooting

### Problem: "Redirect URI Mismatch"

**Solution:**
- Verify the redirect URI in Google Cloud Console matches exactly
- Include the protocol (`http://` or `https://`)
- Include the port if not standard (`:5000` for local development)

### Problem: "Invalid Client"

**Solution:**
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are correct
- Ensure there are no extra spaces or quotes in the `.env` file
- Verify the credentials are from the correct Google Cloud project

### Problem: "Access Blocked"

**Solution:**
- Make sure you've added your email as a test user (for External apps)
- Verify the OAuth consent screen is configured correctly
- Check that all required scopes are added

### Problem: "User Not Authenticated for Gmail"

**Solution:**
- Log out and log back in to refresh OAuth tokens
- Make sure Gmail API is enabled in Google Cloud Console
- Verify the Gmail scope is included in the OAuth consent screen

### Problem: Database Errors After Update

**Solution:**
If upgrading from a version without authentication:
1. Backup your existing database: `cp trading.db trading.db.backup`
2. The app will automatically migrate on startup
3. All existing data will be accessible to the first user who logs in

## Production Deployment

### Environment Configuration

1. Use a production-grade secret key
2. Set `FLASK_DEBUG=False`
3. Use HTTPS (required for OAuth)
4. Update redirect URIs to your production domain

### OAuth Configuration

1. Add production redirect URI to Google Cloud Console
2. Move OAuth consent screen from Testing to Production (if needed)
3. Consider adding a custom domain to the consent screen

### Database

1. Consider using PostgreSQL or MySQL instead of SQLite
2. Enable database backups
3. Implement database encryption for sensitive data

### Reverse Proxy

Use nginx or another reverse proxy:
```nginx
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Migration from Previous Version

If you're upgrading from a version without authentication:

1. **Backup your data**: 
   ```bash
   cp trading.db trading.db.backup
   ```

2. **Update dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up OAuth credentials** (follow steps above)

4. **Run the application**:
   - The database will automatically update
   - Existing data will have `user_id = NULL`

5. **First login**:
   - Log in with Google
   - Your user account is created
   - You'll need to manually assign existing data to your user if needed

## Support

For issues:
- Check this guide's troubleshooting section
- Review [Google OAuth 2.0 documentation](https://developers.google.com/identity/protocols/oauth2)
- Check [Flask-Login documentation](https://flask-login.readthedocs.io/)

## Summary

You now have:
- ✅ Secure Google OAuth login
- ✅ Automatic Gmail integration
- ✅ User-specific data isolation
- ✅ No password management needed
- ✅ Enhanced security and privacy

Happy Trading! 🚀
