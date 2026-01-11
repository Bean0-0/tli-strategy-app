# Stock Evaluation Dashboard - Quick Start Guide

## What This Dashboard Does

This tool helps you make smarter trading decisions by combining **TLI subscription insights** with **real-time market analysis**.

### The Problem It Solves
You get great stock picks from TLI, but you want to know:
- 📊 Is the market confirming this signal?
- ⚠️ What are the risks?
- 💰 What's the potential reward?
- 🚦 Should I buy NOW, or wait?

### The Solution
This dashboard automatically:
1. Reads your TLI emails
2. Gets current market data
3. Calculates technical indicators
4. Cross-checks everything
5. Gives you a clear recommendation with explanation

## How To Use It

### Step 1: Parse TLI Emails
Go to the **Email Parser** tab and either:
- Connect your Gmail and fetch TLI emails automatically, OR
- Copy/paste email content manually

The system extracts stock symbols, target prices, and stop losses.

### Step 2: Review Dashboard
The main dashboard shows all analyzed stocks with:
- **Strong Buys** 🚀 - Best opportunities
- **Buys** ✅ - Good opportunities  
- **Holds** ⏸️ - Wait and watch
- **Sells** ⚠️ - Avoid or exit

### Step 3: Check Details
Click **"Details"** on any stock to see:
- TLI's recommendation and price targets
- Current market conditions
- Technical indicator readings
- Specific warnings or confirmations
- Risk/reward calculations

### Step 4: Make Informed Decisions
Look for:
- ✅ High agreement scores (70%+) = TLI and market agree
- ✅ Good risk/reward ratios (2:1 or better)
- ✅ Low to medium risk levels
- ⚠️ Pay attention to flags and warnings

## Understanding the Dashboard

### Agreement Score
**What it means:**
- 75%+ = Strong alignment between TLI and market
- 50-75% = Moderate alignment
- Below 50% = Conflicting signals (proceed with caution)

**Why it matters:**
Higher scores mean more confirmation from multiple data sources.

### Risk Levels
- **Low**: Stable conditions, clear signals
- **Medium**: Normal market conditions
- **High**: Volatile or conflicting indicators

### Flags
The system automatically warns you about:
- 🚨 Buying into overbought conditions
- 💸 Poor risk/reward setups
- 📈 Price already above target
- ⚡ High volatility
- ✅ Exceptional opportunities

## Best Practices

### Do:
1. ✅ Parse emails promptly (data is freshest)
2. ✅ Focus on Strong Buys with high agreement
3. ✅ Read the flags and understand warnings
4. ✅ Refresh analysis before trading (click ↻ button)
5. ✅ Use this as ONE tool in your decision process

### Don't:
1. ❌ Ignore risk levels
2. ❌ Trade on low agreement scores without understanding why
3. ❌ Forget to check the detailed analysis
4. ❌ Rely solely on this tool - do your own research

## Quick Example

**Stock: NVDA**
- **TLI**: Buy, Target $150, Current $140
- **Agreement**: 82%
- **Risk**: Medium
- **Flags**: "RSI indicates oversold (bullish)" + "Good R/R ratio 3:1"

**What this means:**
TLI recommends buying, market data confirms it's oversold (good entry), and the risk/reward is favorable. High confidence trade.

---

**VS**

**Stock: XYZ**
- **TLI**: Buy, Target $50, Current $48
- **Agreement**: 35%
- **Risk**: High
- **Flags**: "WARNING: Overbought conditions conflict with buy signal"

**What this means:**
TLI says buy, but technical indicators show it's overbought. Lower confidence - proceed with caution or wait for a pullback.

## Setup (First Time Only)

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Get free API keys (optional but recommended):
   - Google Gemini: https://aistudio.google.com/app/apikey
   - Alpha Vantage: https://www.alphavantage.co/support/#api-key
   - Finnhub: https://finnhub.io/

3. Create `.env` file with your keys:
   ```
   GEMINI_API_KEY=your_key_here
   ALPHA_VANTAGE_API_KEY=your_key_here
   FINNHUB_API_KEY=your_key_here
   ```

4. Run the app:
   ```bash
   python app.py
   ```

5. Open http://localhost:5000 in your browser

## Getting Help

- 📖 Full documentation: See `DASHBOARD_GUIDE.md`
- 🔧 Technical details: See `IMPLEMENTATION_SUMMARY.md`
- ❓ Issues: Check Flask logs for error messages

## Remember

**This tool helps you make better decisions, but it doesn't make decisions for you.**

Always:
- Understand what you're buying and why
- Consider your risk tolerance
- Diversify your portfolio
- Never invest more than you can afford to lose
- Do additional research beyond this tool

---

**Happy Trading! 📈**
