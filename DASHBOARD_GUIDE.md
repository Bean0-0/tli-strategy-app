# TLI Stock Evaluation Dashboard - Setup & Usage Guide

## Overview
This application has been transformed into a focused **Stock Evaluation Dashboard** that:
- Parses TLI subscription emails for stock recommendations
- Cross-validates with external market data and technical indicators
- Provides actionable BUY/SELL/HOLD recommendations
- Highlights areas of disagreement between TLI and market analysis
- Presents everything in an easy-to-consume dashboard format

## What Changed

### Removed Features
- ❌ Positions tracking (manual position entry)
- ❌ Position size calculator
- ❌ Manual alerts system
- ❌ TLI notes/comments section

### New Features
- ✅ **Automated Stock Evaluation Dashboard**
- ✅ **AI-Powered Email Parsing** (uses Google Gemini)
- ✅ **External Market Data Integration** (Alpha Vantage, Finnhub, Yahoo Finance)
- ✅ **Technical Indicators** (RSI, MACD, Moving Averages)
- ✅ **Cross-Validation Analysis** with agreement scoring
- ✅ **Risk/Reward Calculations**
- ✅ **Automated Flag System** for warnings and conflicts

## Architecture

### Core Components

1. **Email Parser** (`email_parser.py`)
   - Uses Google Gemini AI to extract stock symbols, price targets, and stop losses
   - Supports chart/image analysis from emails
   - Falls back to regex parsing if AI unavailable

2. **Stock Analyzer** (`stock_analyzer.py`)
   - Fetches real-time market data from multiple sources
   - Calculates technical indicators (RSI, MACD, MAs)
   - Cross-validates TLI recommendations with market data
   - Generates overall recommendations with confidence scores

3. **Database Models** (`models.py`)
   - `StockEvaluation`: Stores complete analysis results
   - `PriceLevel`: Stores extracted price targets/stops from emails
   - `ParsedEmail`: Tracks processed emails to avoid duplicates

4. **Dashboard** (`app.py` + `templates/index.html`)
   - Displays stocks categorized by recommendation strength
   - Shows agreement scores between TLI and technicals
   - Provides detailed analysis modal for each stock
   - One-click refresh for updated analysis

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:

```bash
# Required for AI parsing
GEMINI_API_KEY=your_gemini_api_key

# Optional but recommended for better analysis
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
FINNHUB_API_KEY=your_finnhub_key

# Flask configuration
SECRET_KEY=change_this_in_production
FLASK_DEBUG=True
```

#### Getting API Keys (All Free):

- **Google Gemini**: https://aistudio.google.com/app/apikey
- **Alpha Vantage**: https://www.alphavantage.co/support/#api-key (25 calls/day free)
- **Finnhub**: https://finnhub.io/ (60 calls/minute free)

### 3. Initialize Database
```bash
python app.py
# Or
flask db init
```

The app will automatically create all necessary tables on first run.

### 4. Run the Application
```bash
python app.py
```

Access at: http://localhost:5000

## Usage Workflow

### Option 1: Gmail Integration (Recommended)
1. Set up Gmail API credentials (see `GMAIL_SETUP.md`)
2. Navigate to **Email Parser**
3. Click **Fetch Emails from Gmail**
4. Select TLI emails to parse
5. Dashboard automatically updates with evaluations

### Option 2: Manual Email Parsing
1. Copy email content from TLI
2. Navigate to **Email Parser**
3. Paste content and click **Parse Email**
4. Dashboard automatically updates

### Option 3: Refresh Existing Analysis
1. Go to **Dashboard**
2. Click refresh (↻) button next to any stock
3. Gets latest market data and updates recommendation

## Dashboard Features

### Summary Cards
- **Strong Buys**: Highest confidence opportunities
- **Buys**: Good opportunities
- **Holds**: Wait and monitor
- **Sells**: Consider exiting or avoiding

### Main Table
Shows all analyzed stocks with:
- Current price and 24h change
- TLI target price and upside potential
- **Agreement Score** (0-100%): How well TLI and technicals align
- Risk level (Low/Medium/High)
- Quick actions (Details, Refresh)

### Detail View
Click "Details" on any stock to see:
- **TLI Analysis**: Original recommendation, targets, stop losses
- **Market Data**: Current price, volume, market cap, P/E ratio
- **Technical Indicators**: RSI, MACD, moving averages
- **Analysis Flags**: Warnings and insights
- **Risk/Reward**: Calculated potential gain vs loss

## How the Analysis Works

### 1. Email Parsing
- AI extracts stock symbols, price targets, stop losses, and context
- Data stored in `PriceLevel` table

### 2. TLI Recommendation Extraction
- Determines if TLI suggests buy/sell/hold based on email content
- Extracts confidence level from language used

### 3. Market Data Fetch
- Retrieves current price, volume, market cap
- Falls back through multiple APIs for reliability

### 4. Technical Analysis
- Calculates RSI (oversold/overbought conditions)
- Analyzes MACD signals
- Compares current price to moving averages

### 5. Cross-Validation Scoring
The system uses a 0-100 point scoring system:
- Starts at 50 (neutral)
- **TLI signal**: ±15 points
- **Upside potential**: +10 points (>20% upside)
- **RSI**: ±10 points (oversold/overbought)
- **Moving averages**: ±5 points
- **Risk/reward ratio**: +10 points (>3:1 ratio)

Final Score → Recommendation:
- 75+: **Strong Buy**
- 60-74: **Buy**
- 45-59: **Hold**
- 30-44: **Sell**
- <30: **Strong Sell**

### 6. Flag Generation
System automatically flags:
- Poor risk/reward ratios (<1:1)
- Price above TLI target
- Overbought conditions conflicting with buy signals
- High volatility warnings
- RSI extremes
- Excellent opportunities (high upside + good R/R)

## Best Practices

### For Traders
1. **Focus on Strong Buys** with high agreement scores (>70%)
2. **Check risk levels** - avoid "High" risk unless confident
3. **Review flags** - understand warnings before trading
4. **Refresh regularly** - market data changes throughout the day
5. **Cross-reference** - use dashboard as one input in your decision process

### For Data Quality
1. **Parse emails promptly** - data is most relevant when fresh
2. **Use Gmail integration** - more reliable than manual parsing
3. **Monitor agreement scores** - low scores (<40%) indicate uncertainty
4. **Check detail view** - understand WHY a recommendation was made

### API Rate Limits
- **Alpha Vantage**: 25 calls/day (limit refreshes to important stocks)
- **Finnhub**: 60 calls/minute (generous, but don't spam)
- **Yahoo Finance**: Fallback, no official limit but use responsibly

## Technical Details

### Database Schema
```python
StockEvaluation:
  - TLI data (recommendation, target, stop, notes, confidence)
  - Market data (price, volume, market cap, P/E)
  - Technicals (RSI, MACD, MAs)
  - Analysis results (overall recommendation, agreement score, risk, flags)
```

### Recommendation Logic
See `stock_analyzer.py` → `_cross_validate()` for complete scoring algorithm.

### External API Priority
1. Alpha Vantage (if key provided)
2. Finnhub (if key provided)
3. Yahoo Finance (always available as fallback)

## Troubleshooting

### No evaluations showing
- Parse some emails first via Email Parser
- Check database: `sqlite3 instance/trading.db` → `SELECT * FROM stock_evaluation;`

### External data unavailable
- Check API keys in `.env`
- System gracefully falls back to TLI-only analysis
- Yahoo Finance provides basic data without API key

### Low agreement scores
- Normal! Indicates TLI and technicals disagree
- Review flags to understand why
- Consider as higher risk opportunities

### Parsing errors
- Ensure GEMINI_API_KEY is set
- System falls back to regex parsing
- Check email format matches TLI structure

## Maintenance

### Update Market Data
Click refresh button on dashboard for individual stocks, or:
```bash
# Bulk refresh all stocks (add this route if needed)
curl -X POST http://localhost:5000/refresh-all-analysis
```

### Clean Old Data
```python
# In Python shell
from app import app, db
from models import StockEvaluation
from datetime import datetime, timedelta

with app.app_context():
    # Delete evaluations older than 30 days
    old_date = datetime.utcnow() - timedelta(days=30)
    StockEvaluation.query.filter(
        StockEvaluation.updated_at < old_date
    ).delete()
    db.session.commit()
```

## Future Enhancements

Potential additions:
- [ ] Automated daily email fetching
- [ ] Push notifications for strong buy signals
- [ ] Historical tracking of recommendation accuracy
- [ ] Portfolio simulation based on recommendations
- [ ] Multiple timeframe analysis (daily, weekly, monthly)
- [ ] Sector analysis and correlation
- [ ] Export to CSV/PDF reports

## Support

For issues or questions:
1. Check this documentation
2. Review code comments in `stock_analyzer.py`
3. Check Flask logs for error messages
4. Verify API keys and rate limits

## Credits

- **Email Parsing**: Google Gemini AI
- **Market Data**: Alpha Vantage, Finnhub, Yahoo Finance
- **Frontend**: Custom CSS with responsive design
- **Backend**: Flask + SQLAlchemy

---

**Remember**: This tool provides analysis to support your decisions, not replace your judgment. Always do your own research and understand the risks before trading.
