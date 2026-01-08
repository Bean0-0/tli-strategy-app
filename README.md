# TLi Trading Strategy Management Tool

A web application for managing the TLi trading strategy, with features to help prevent common trading mistakes and enforce disciplined position management.

## 🔐 NEW: Google OAuth Login System

The app now includes a secure Google OAuth login system that:
- ✅ Authenticates users with their Google accounts
- ✅ Automatically syncs with users' forwarded Gmail emails
- ✅ Provides user-specific data isolation and privacy
- ✅ Eliminates the need for password management
- ✅ Enables secure, automatic email fetching

See [OAUTH_SETUP.md](OAUTH_SETUP.md) for detailed setup instructions.

## Features

### 🎯 Core Functionality

1. **Position Sizing Calculator**
   - Risk-based position sizing
   - Account size management
   - Fibonacci retracement and extension calculator

2. **Email Parser & Gmail Integration**
   - **Gmail API Integration**: Automatically fetch forwarded emails using OAuth
   - **User-Specific Syncing**: Each user's emails are synced to their account
   - **Manual Input**: Paste email content directly
   - Extract trading levels from forwarded emails
   - Automatically parse symbols, support/resistance levels
   - Extract fibonacci levels and price targets
   - OAuth 2.0 secure authentication

3. **Price Alerts System**
   - Set alerts for buy levels
   - Fibonacci extension alerts
   - Sell target notifications

4. **TLi Comments & Notes**
   - Store long-term strategy plans
   - Track short-term expected moves
   - Document pullback expectations

5. **Position Management**
   - Track all positions (open and closed)
   - Separate large cap vs small cap tracking
   - P&L calculation

6. **User Authentication & Data Privacy**
   - Secure Google OAuth login
   - User-specific data isolation
   - Each user has their own positions, alerts, and notes

### 🛡️ Strategy Enforcement

**Large Cap Strategy (AMD, NVDA, etc.)**
- Visual reminders to LET THEM RUN
- Designed to prevent premature exits
- Emphasizes patience with high-quality names

**Small Cap Strategy (OSCR, HIMS, etc.)**
- Reminders to TRADE AGGRESSIVELY
- Take profits more actively
- Manage risk more tightly

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Bean0-0/tli-strategy-app.git
cd tli-strategy-app
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Google OAuth for login and Gmail integration:
```bash
# Copy environment template
cp .env.example .env

# Follow the OAuth setup guide for detailed instructions
# See OAUTH_SETUP.md for complete setup instructions
```

4. Configure your Google OAuth credentials in `.env`:
   - Get OAuth credentials from Google Cloud Console
   - Add `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
   - See [OAUTH_SETUP.md](OAUTH_SETUP.md) for step-by-step instructions

5. Initialize the database:
```bash
python app.py
```

The database will be automatically created on first run.

## Usage

### First Time Setup

1. Start the application:
```bash
# Development mode (with debug)
FLASK_DEBUG=true python app.py

# Production mode (recommended)
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. **Sign in with Google**:
   - Click "Sign in with Google" on the login page
   - Choose your Google account
   - Grant the requested permissions (email, profile, Gmail read access)
   - You'll be redirected to your personal dashboard

4. The application includes:
   - **Dashboard**: Overview of your positions, alerts, and recent notes
   - **Positions**: Manage all your trading positions
   - **Calculator**: Position sizing and fibonacci tools
   - **Alerts**: Set and manage price alerts
   - **TLi Notes**: Store strategy comments and plans
   - **Email Parser**: Extract levels from emails (syncs with your Gmail)
   - **Price Levels**: View all extracted price levels

### Email Syncing

The app automatically syncs with forwarded emails in your Gmail account:
1. Forward trading emails to your Gmail account
2. Use the "Fetch from Gmail" feature in Email Parser
3. The app fetches and parses emails using your OAuth credentials
4. All data is saved to your personal account

## Workflow

### First Login

1. Click "Sign in with Google"
2. Authorize the app to access your Gmail
3. Start adding positions and tracking your trades

### Adding a Position

1. Navigate to Positions → Add Position
2. Enter symbol, entry price, and shares
3. Mark as "Large Cap" for stocks you should let run (AMD, NVDA)
4. Leave unchecked for small caps you should trade aggressively (OSCR, HIMS)
5. Add notes about stop loss, targets, or strategy

### Parsing Trading Emails

**Option 1: Fetch from Gmail (Automatic)**
1. Navigate to Email Parser
2. Click "Fetch from Gmail" button
3. Select emails from the list
4. Click "Parse Selected" to extract data
5. Symbols and price levels are automatically saved to your account

**Option 2: Manual Paste**
1. Navigate to Email Parser
2. Paste the forwarded email content
3. Click "Parse Email"
4. Review extracted symbols and price levels
5. Data is automatically saved to your account

### Setting Alerts

1. Navigate to Alerts
2. Add alert with symbol, price, and type
3. Types: Buy Level, Sell Level, or Fib Extension
4. View active alerts on dashboard

### Recording TLi Strategy Notes

1. Navigate to TLi Notes
2. Select note type:
   - Long Term Plan: Overall strategy direction
   - Short Term Expected Move: Near-term expectations
   - Expected Pullback: Where to look for entries
   - General Market Comment: Overall market thoughts
3. Add notes and reference them when making decisions

## Security

**⚠️ Important Security Notes:**

### OAuth & Authentication

- **Google OAuth**: Secure authentication with Google accounts
- **User Isolation**: Each user's data is completely isolated
- **Automatic Token Management**: OAuth tokens are securely stored and automatically refreshed
- **Read-Only Gmail Access**: The app can only read emails, not send or delete them
- See [OAUTH_SETUP.md](OAUTH_SETUP.md) for complete security guidelines

### Application Security

- The app uses a default development secret key. **Change this in production!**
- Set `SECRET_KEY` environment variable:
  ```bash
  export SECRET_KEY='your-secure-random-key-here'
  python app.py
  ```
- Debug mode is **disabled by default** for security
- Only enable debug in development with `FLASK_DEBUG=true`
- Database file contains sensitive trading data - protect it appropriately
- Consider running behind a reverse proxy (nginx) in production
- **Never commit** `.env` file to Git (already in .gitignore)
- Store OAuth credentials securely

### Environment Variables

Required environment variables (in `.env`):
- `SECRET_KEY`: Application secret key (generate with `python3 -c "import secrets; print(secrets.token_hex(32))"`)
- `GOOGLE_CLIENT_ID`: OAuth client ID from Google Cloud Console
- `GOOGLE_CLIENT_SECRET`: OAuth client secret from Google Cloud Console

## Key Trading Principles

The tool is designed to help enforce these key principles:

1. **Let Large Caps Run**: AMD, NVDA, and similar high-quality names have room to grow
2. **Trade Small Caps Aggressively**: Take profits and manage risk actively on smaller names
3. **Follow the Plan**: Reference TLi's comments to stay aligned with the strategy
4. **Proper Position Sizing**: Use the calculator to ensure appropriate risk per trade
5. **Watch Key Levels**: Set alerts at important support, resistance, and fib levels

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, CSS, JavaScript
- **Styling**: Custom CSS with modern design

## Documentation

- **QUICKSTART.md**: Step-by-step usage guide
- **IMPLEMENTATION.md**: Technical details and architecture

## License

MIT License