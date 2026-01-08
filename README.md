# TLi Trading Strategy Management Tool

A web application for managing the TLi trading strategy, with features to help prevent common trading mistakes and enforce disciplined position management.

## 🔐 Authentication

The app now includes a user login system with two options:
- ✅ **Username/Password** - Simple login (works without HTTPS)
- ✅ **Google OAuth** (Optional) - Sign in with Google account

Each user has their own isolated data (positions, alerts, notes). See [AUTHENTICATION.md](AUTHENTICATION.md) for setup guide.

## Features

### 🎯 Core Functionality

1. **User Authentication**
   - Username/password login (works on HTTP)
   - Optional Google OAuth (requires HTTPS)
   - User-specific data isolation
   - Session management

2. **Position Sizing Calculator**
   - Risk-based position sizing
   - Account size management
   - Fibonacci retracement and extension calculator

3. **Email Parser & Gmail Integration**
   - **Forwarded Email System**: Forward trading emails to tli.strategy.app@gmail.com
   - **Gmail API Integration**: App fetches from shared inbox
   - **Manual Input**: Paste email content directly
   - **Auto-parsing**: Extract symbols, levels, and targets
   - Each user sees their own analyzed data

4. **Price Alerts System**
   - Set alerts for buy levels
   - Fibonacci extension alerts
   - Sell target notifications
   - Personal alert management

5. **TLi Comments & Notes**
   - Store long-term strategy plans
   - Track short-term expected moves
   - Document pullback expectations
   - Personal notes per user

6. **Position Management**
   - Track all positions (open and closed)
   - Separate large cap vs small cap tracking
   - P&L calculation
   - User-specific position tracking

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

3. Set up environment:
```bash
cp .env.example .env
# Edit .env and set SECRET_KEY
```

4. Create first user:
```bash
python3 << 'EOF'
from app import app, db
from models import User

with app.app_context():
    db.create_all()
    user = User(username='admin', email='admin@example.com')
    user.set_password('changeme')  # Change this!
    db.session.add(user)
    db.session.commit()
    print(f"Created user: {user.username}")
EOF
```

5. Run the app:
```bash
python app.py
```

6. Login at `http://localhost:5000`

## Authentication Setup

See [AUTHENTICATION.md](AUTHENTICATION.md) for detailed setup guide including:
- Creating users
- Configuring Google OAuth (optional)
- Password management
- Security best practices

## Gmail API Setup (For Forwarded Emails)

For automatic email fetching from tli.strategy.app@gmail.com:

1. **Quick Setup**: See [GMAIL_SETUP.md](GMAIL_SETUP.md) for detailed step-by-step instructions
2. **Enable Gmail API** in Google Cloud Console
3. **Download credentials.json** and place in project root
4. **Run authentication**: `python gmail_client.py`
5. **Grant access** when browser opens

**Without Gmail API setup**, you can still manually paste email content in the Email Parser interface.

## Usage

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

3. The application includes:
   - **Dashboard**: Overview of positions, alerts, and recent notes
   - **Positions**: Manage all trading positions
   - **Calculator**: Position sizing and fibonacci tools
   - **Alerts**: Set and manage price alerts
   - **TLi Notes**: Store strategy comments and plans
   - **Email Parser**: Extract levels from emails (manual paste or Gmail fetch)
   - **Price Levels**: View all extracted price levels

## Workflow

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
5. Symbols and price levels are automatically saved

**Option 2: Manual Paste**
1. Navigate to Email Parser
2. Paste the forwarded email content
3. Click "Parse Email"
4. Review extracted symbols and price levels
5. Data is automatically saved to the database

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

**Gmail API Security:**

- **Never commit** `credentials.json` or `token.pickle` to Git (already in .gitignore)
- Store Gmail credentials securely - they provide access to your email
- The app uses **read-only** Gmail access (cannot send or modify emails)
- OAuth tokens are stored locally in `token.pickle`
- Tokens automatically refresh when expired
- To revoke access: Delete `token.pickle` and remove app from [Google Account Security](https://myaccount.google.com/security)
- See [GMAIL_SETUP.md](GMAIL_SETUP.md) for complete security guidelines

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