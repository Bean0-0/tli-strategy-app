# Authentication Setup Guide

This guide explains how to set up and use the authentication system in the TLi Trading Strategy Management Tool.

## Overview

The app provides **two login options**:
1. **Username/Password** - Simple, works anywhere (including HTTP)
2. **Google OAuth** (Optional) - Sign in with Google account

## How It Works

### Email Flow
1. Trading emails are **forwarded TO** the shared Gmail account: `tli.strategy.app@gmail.com`
2. The app fetches forwarded emails from this shared account using Gmail API
3. Users log in to see **their own** analyzed data from those forwarded emails
4. Each user has their own positions, alerts, and notes

**Note**: The app does NOT access individual users' Gmail accounts. All emails come through the shared forwarding address.

## Setup Options

### Option 1: Username/Password Only (Recommended for HTTP)

This is the simplest option and works without HTTPS.

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env and set:
# - SECRET_KEY (generate with: python3 -c "import secrets; print(secrets.token_hex(32))")
# Leave GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET empty
```

3. Create first user:
```bash
python3 << 'EOF'
from app import app, db
from models import User

with app.app_context():
    db.create_all()
    user = User(username='admin', email='admin@example.com')
    user.set_password('yourpassword')  # Change this!
    db.session.add(user)
    db.session.commit()
    print(f"Created user: {user.username}")
EOF
```

4. Run the app:
```bash
python app.py
```

5. Login at `http://localhost:5000` with username/password

### Option 2: Username/Password + Google OAuth

Add Google login as an additional option. **Requires HTTPS** for Google OAuth (but username/password still works on HTTP).

1. Follow Option 1 steps above

2. Set up Google OAuth:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a project
   - Enable "People API" (not Gmail API - that's for forwarded emails)
   - Create OAuth 2.0 credentials (Web application type)
   - Add authorized redirect URI: `https://yourdomain.com/login/callback` (or `http://localhost:5000/login/callback` for local testing)
   - Copy Client ID and Client Secret

3. Add to `.env`:
```bash
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

4. Restart the app - Google login button will now appear on login page

## Creating Users

### Via Command Line

```bash
python3 << 'EOF'
from app import app, db
from models import User

with app.app_context():
    username = input("Username: ")
    password = input("Password: ")
    email = input("Email (optional): ") or None
    
    if User.query.filter_by(username=username).first():
        print("Username already exists!")
    else:
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"✓ Created user: {username}")
EOF
```

### Via Google OAuth

Users can create accounts automatically by signing in with Google (if OAuth is configured).

## Gmail API Setup (For Forwarded Emails)

The app needs Gmail API access to fetch forwarded emails from `tli.strategy.app@gmail.com`.

1. Follow [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed instructions

2. Key points:
   - This is separate from user authentication
   - Only the app needs Gmail access (to read forwarded emails)
   - Users do NOT need their own Gmail API access

## User Management

### List Users

```bash
python3 << 'EOF'
from app import app
from models import User

with app.app_context():
    users = User.query.all()
    for user in users:
        auth_type = "Google" if user.google_id else "Password"
        print(f"{user.id}: {user.username} ({user.email}) - {auth_type}")
EOF
```

### Reset Password

```bash
python3 << 'EOF'
from app import app, db
from models import User

with app.app_context():
    username = input("Username: ")
    user = User.query.filter_by(username=username).first()
    
    if user:
        new_password = input("New password: ")
        user.set_password(new_password)
        db.session.commit()
        print(f"✓ Password reset for {username}")
    else:
        print("User not found")
EOF
```

### Delete User

```bash
python3 << 'EOF'
from app import app, db
from models import User

with app.app_context():
    username = input("Username to delete: ")
    user = User.query.filter_by(username=username).first()
    
    if user:
        confirm = input(f"Delete {username}? (yes/no): ")
        if confirm.lower() == 'yes':
            db.session.delete(user)
            db.session.commit()
            print(f"✓ Deleted user: {username}")
    else:
        print("User not found")
EOF
```

## Security Notes

### For HTTP Deployments (No HTTPS)
- ✅ Username/password login works fine
- ✅ Data is user-isolated
- ⚠️  Passwords transmitted in plain text (use strong passwords)
- ⚠️  Session cookies not encrypted
- ❌ Google OAuth won't work (requires HTTPS)

**Recommendation**: Use behind a VPN or local network only

### For HTTPS Deployments (Recommended)
- ✅ Both login methods work
- ✅ Encrypted communication
- ✅ Secure cookies
- ✅ Production-ready

**Recommendation**: Always use HTTPS in production

### Best Practices
1. Use strong SECRET_KEY (generate randomly)
2. Use strong passwords (12+ characters)
3. Don't share accounts
4. Enable HTTPS in production
5. Regular backups of `trading.db`

## Troubleshooting

### "Please log in to access this page"
- You're not logged in
- Go to `/login` and sign in

### "Invalid username or password"
- Check username and password
- Try resetting password (see above)

### Google login button doesn't appear
- `GOOGLE_CLIENT_ID` is not set in `.env`
- This is normal if you only want password login

### Google login fails
- Check Client ID and Secret are correct
- Verify redirect URI matches exactly (including http/https)
- Make sure you're using HTTPS (Google requirement)

### "Gmail connection successful" but no emails
- Emails need to be forwarded TO tli.strategy.app@gmail.com
- Check the Gmail account has forwarded emails
- Try increasing `days_back` parameter

## Architecture

```
Users forward emails → tli.strategy.app@gmail.com (shared inbox)
                                  ↓
                           Gmail API fetches
                                  ↓
                          App parses emails
                                  ↓
                         Each user sees their
                          own data/analysis
```

**Key Point**: The Gmail account is shared for receiving forwarded emails. User authentication is separate and controls who can access the app.

## Next Steps

1. Create user accounts (password or Google)
2. Set up Gmail API for fetching forwarded emails
3. Start using the app!
4. Forward trading emails to tli.strategy.app@gmail.com
5. Log in and analyze your trades

## Support

- Check environment variables in `.env`
- Make sure database is created (`trading.db`)
- Check Gmail API setup for email fetching
- Review Flask logs for errors
