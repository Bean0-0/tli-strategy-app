# TLi Trading Tool - Quick Start Guide

## Installation & Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the application:**
   ```bash
   python app.py
   ```

3. **Access the web interface:**
   Open your browser and go to: `http://localhost:5000`

## Features Overview

### 1. Dashboard (Home Page)
- **Strategy Reminders**: Visual cues to help you follow the TLi strategy
  - Large Cap Strategy: Let them run (AMD, NVDA, etc.)
  - Small Cap Strategy: Trade aggressively (OSCR, HIMS, etc.)
- Recent TLi notes and comments
- Open positions summary
- Active price alerts

### 2. Positions Management
- Add new positions with symbol, entry price, shares
- Mark positions as "Large Cap" or "Small Cap"
- Track P&L on closed positions
- View all positions history

### 3. Position Sizing Calculator
- **Risk-Based Calculator**: Calculate exact position size based on:
  - Account size
  - Risk percentage (typically 1-2%)
  - Entry price
  - Stop loss price
- **Fibonacci Calculator**: Calculate retracement and extension levels
  - Enter swing high and swing low
  - Get all key Fib levels instantly

### 4. Email Parser
- **How to use:**
  1. Forward TLi emails to your app email
  2. Copy the email content
  3. Paste into the Email Parser page
  4. Click "Parse Email"
  5. All symbols, price levels, and targets are automatically extracted
  6. Data is saved to the database

- **What it extracts:**
  - Stock symbols (e.g., $SE, $ZETA, $TGT)
  - Price targets (PT)
  - Wave targets (Wave 3, Wave 5)
  - Fibonacci levels (0.5 Fib, 0.38 Fib, 1.618 Fib)
  - Moving averages (50 Day MA, 200 WMA)
  - Buy zones and ranges
  - Breakout levels
  - Support and resistance levels
  - Strategic notes

### 5. Price Alerts
- Set alerts for specific price levels
- Alert types:
  - Buy Level
  - Sell Level
  - Fib Extension
- View all active alerts
- Track triggered alerts history

### 6. TLi Notes & Comments
- Store TLi's strategy comments
- Note types:
  - Long Term Plan
  - Short Term Expected Move
  - Expected Pullback
  - General Market Comment
- Reference these notes when making trading decisions

### 7. Price Levels
- View all extracted price levels by symbol
- Organized by type (support, resistance, fib, target, etc.)
- Shows creation date for each level

## Example Workflow

### Adding a Position
1. Go to **Positions** → **Add Position**
2. Enter: Symbol (AMD), Entry Price ($150), Shares (100)
3. Check "Large Cap" box
4. Add notes: "Stop at $145, target $200"
5. Click "Add Position"

### Parsing TLi Email
1. Forward TLi email to your dedicated email
2. Go to **Email Parser**
3. Paste the email content
4. Click "Parse Email"
5. Review extracted symbols and levels
6. Go to **Price Levels** to see all extracted data

### Setting Up Alerts
1. Go to **Alerts**
2. Enter symbol, price, and type
3. Optionally add notes
4. Click "Add Alert"
5. Alerts appear on dashboard

### Using the Calculator
1. Go to **Calculator**
2. **For Position Sizing:**
   - Enter your account size ($10,000)
   - Enter risk percentage (1%)
   - Enter entry price ($150)
   - Enter stop loss ($145)
   - Click "Calculate"
   - See exact shares to buy (20 shares)

3. **For Fibonacci Levels:**
   - Enter swing high ($200)
   - Enter swing low ($150)
   - Click "Calculate Fibs"
   - See all retracement and extension levels

### Recording TLi Strategy Notes
1. Go to **TLi Notes**
2. Select note type
3. Optionally add symbol
4. Enter the comment/strategy note
5. Click "Add Note"
6. View all notes on dashboard and notes page

## Tips for Success

1. **Use the Email Parser regularly** - Parse every TLi email to build your database of levels
2. **Check Dashboard daily** - Review your strategy reminders before trading
3. **Reference TLi Notes** - Look at long-term plans before exiting positions
4. **Set Alerts liberally** - Don't rely on memory, set alerts for all key levels
5. **Mark Large Caps correctly** - This triggers the right strategy reminders
6. **Use the Calculator** - Always size positions properly based on risk
7. **Track Everything** - Record all positions, even small ones, for analysis

## Strategy Reminders

### Large Cap (AMD, NVDA, MSFT, AAPL, etc.)
- **LET THEM RUN**
- Be patient
- Focus on Wave 3 and Wave 5 targets
- Don't exit early just because of small pullbacks
- Reference TLi's long-term notes

### Small Cap (OSCR, HIMS, etc.)
- **TRADE AGGRESSIVELY**
- Take profits more frequently
- Manage risk tightly
- React quickly to price action
- Use tighter stops

## Technical Details

- **Database**: SQLite (trading.db)
- **Backend**: Flask (Python)
- **Frontend**: HTML/CSS/JavaScript
- **Port**: 5000 (default)

## Troubleshooting

**App won't start:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version (3.7+ required)

**Database issues:**
- Delete trading.db and restart app to reinitialize

**Email parser not extracting correctly:**
- Make sure to paste the full email content
- Include the symbol in the email (preferably with $ prefix)

## Data Backup

Your trading data is stored in `trading.db`. To backup:
```bash
cp trading.db trading_backup_$(date +%Y%m%d).db
```

## Support

For issues or questions, refer to the README.md file or check the code comments.