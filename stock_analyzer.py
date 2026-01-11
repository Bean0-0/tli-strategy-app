"""Stock Analysis Service - Integrates TLI data with external market analysis"""
import os
import requests
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class StockAnalyzer:
    """Analyzes stocks by combining TLI recommendations with external data"""
    
    def __init__(self):
        self.alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        self.finnhub_key = os.getenv('FINNHUB_API_KEY')
        
    def analyze_stock(self, symbol: str, tli_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive stock analysis combining TLI with external data
        
        Args:
            symbol: Stock ticker symbol
            tli_data: Dictionary containing TLI recommendation data
                     {target_price, stop_loss, notes, recommendation}
        
        Returns:
            Complete analysis with recommendation and flags
        """
        try:
            # Get market data
            market_data = self._get_market_data(symbol)
            technical_data = self._get_technical_indicators(symbol, market_data)
            
            # Analyze and cross-validate
            analysis = self._cross_validate(symbol, tli_data, market_data, technical_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return self._fallback_analysis(symbol, tli_data)
    
    def _get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch current market data using free APIs"""
        data = {
            'current_price': None,
            'price_change_pct': None,
            'volume': None,
            'market_cap': None,
            'pe_ratio': None,
            'high_52w': None,
            'low_52w': None
        }
        
        # Try Alpha Vantage (free tier: 25 calls/day)
        if self.alpha_vantage_key:
            try:
                url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_key}'
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    quote = response.json().get('Global Quote', {})
                    if quote:
                        data['current_price'] = float(quote.get('05. price', 0))
                        data['price_change_pct'] = float(quote.get('10. change percent', '0').replace('%', ''))
                        data['volume'] = int(quote.get('06. volume', 0))
                        logger.info(f"Alpha Vantage data retrieved for {symbol}")
            except Exception as e:
                logger.warning(f"Alpha Vantage API error: {e}")
        
        # Try Finnhub (free tier: 60 calls/minute)
        if self.finnhub_key and not data['current_price']:
            try:
                # Get quote
                quote_url = f'https://finnhub.io/api/v1/quote?symbol={symbol}&token={self.finnhub_key}'
                response = requests.get(quote_url, timeout=10)
                if response.status_code == 200:
                    quote = response.json()
                    data['current_price'] = quote.get('c')  # current price
                    data['price_change_pct'] = quote.get('dp')  # percent change
                    data['high_52w'] = quote.get('h')
                    data['low_52w'] = quote.get('l')
                    
                # Get basic financials
                metrics_url = f'https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={self.finnhub_key}'
                response = requests.get(metrics_url, timeout=10)
                if response.status_code == 200:
                    metrics = response.json().get('metric', {})
                    data['pe_ratio'] = metrics.get('peBasicExclExtraTTM')
                    data['market_cap'] = metrics.get('marketCapitalization')
                    
                logger.info(f"Finnhub data retrieved for {symbol}")
            except Exception as e:
                logger.warning(f"Finnhub API error: {e}")
        
        # Fallback: Try Yahoo Finance API (unofficial but works)
        if not data['current_price']:
            try:
                url = f'https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=5d'
                response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                if response.status_code == 200:
                    result = response.json()['chart']['result'][0]
                    meta = result['meta']
                    data['current_price'] = meta.get('regularMarketPrice')
                    data['price_change_pct'] = ((data['current_price'] - meta.get('chartPreviousClose', data['current_price'])) 
                                                / meta.get('chartPreviousClose', data['current_price']) * 100)
                    data['volume'] = meta.get('regularMarketVolume')
                    logger.info(f"Yahoo Finance data retrieved for {symbol}")
            except Exception as e:
                logger.warning(f"Yahoo Finance API error: {e}")
        
        return data
    
    def _get_technical_indicators(self, symbol: str, market_data: Dict) -> Dict[str, Any]:
        """Calculate or fetch technical indicators"""
        indicators = {
            'rsi': None,
            'macd_signal': 'neutral',
            'ma_50': None,
            'ma_200': None,
            'trend': 'neutral'
        }
        
        current_price = market_data.get('current_price')
        if not current_price:
            return indicators
        
        # Try to get technical data from Alpha Vantage
        if self.alpha_vantage_key:
            try:
                # Get RSI
                rsi_url = f'https://www.alphavantage.co/query?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={self.alpha_vantage_key}'
                response = requests.get(rsi_url, timeout=10)
                if response.status_code == 200:
                    rsi_data = response.json().get('Technical Analysis: RSI', {})
                    if rsi_data:
                        latest_date = sorted(rsi_data.keys(), reverse=True)[0]
                        indicators['rsi'] = float(rsi_data[latest_date]['RSI'])
                
                # Get SMA (Simple Moving Average)
                sma_url = f'https://www.alphavantage.co/query?function=SMA&symbol={symbol}&interval=daily&time_period=50&series_type=close&apikey={self.alpha_vantage_key}'
                response = requests.get(sma_url, timeout=10)
                if response.status_code == 200:
                    sma_data = response.json().get('Technical Analysis: SMA', {})
                    if sma_data:
                        latest_date = sorted(sma_data.keys(), reverse=True)[0]
                        indicators['ma_50'] = float(sma_data[latest_date]['SMA'])
                        
            except Exception as e:
                logger.warning(f"Technical indicators API error: {e}")
        
        # Calculate trend based on available data
        if indicators['ma_50'] and current_price:
            if current_price > indicators['ma_50'] * 1.02:
                indicators['trend'] = 'bullish'
            elif current_price < indicators['ma_50'] * 0.98:
                indicators['trend'] = 'bearish'
        
        # Determine MACD signal from trend and RSI
        if indicators['rsi']:
            if indicators['rsi'] > 70:
                indicators['macd_signal'] = 'overbought'
            elif indicators['rsi'] < 30:
                indicators['macd_signal'] = 'oversold'
            elif indicators['trend'] == 'bullish':
                indicators['macd_signal'] = 'bullish'
            elif indicators['trend'] == 'bearish':
                indicators['macd_signal'] = 'bearish'
        
        return indicators
    
    def _cross_validate(self, symbol: str, tli_data: Dict, market_data: Dict, technical_data: Dict) -> Dict[str, Any]:
        """Cross-validate TLI recommendation with market/technical data"""
        
        analysis = {
            'symbol': symbol,
            'tli_recommendation': tli_data.get('recommendation', 'hold'),
            'tli_target_price': tli_data.get('target_price'),
            'tli_stop_loss': tli_data.get('stop_loss'),
            'tli_notes': tli_data.get('notes', ''),
            'tli_confidence': tli_data.get('confidence', 'medium'),
            
            'current_price': market_data.get('current_price'),
            'price_change_pct': market_data.get('price_change_pct'),
            'volume': market_data.get('volume'),
            'market_cap': market_data.get('market_cap'),
            'pe_ratio': market_data.get('pe_ratio'),
            
            'rsi': technical_data.get('rsi'),
            'macd_signal': technical_data.get('macd_signal'),
            'ma_50': technical_data.get('ma_50'),
            'ma_200': technical_data.get('ma_200'),
            
            'flags': [],
            'agreement_score': 50.0,
            'overall_recommendation': 'hold',
            'risk_level': 'medium'
        }
        
        # Scoring system (0-100)
        score = 50  # Start neutral
        flags = []
        
        tli_rec = tli_data.get('recommendation', 'hold').lower()
        current_price = market_data.get('current_price')
        target_price = tli_data.get('target_price')
        stop_loss = tli_data.get('stop_loss')
        
        # TLI Analysis
        if tli_rec in ['buy', 'long']:
            score += 15
        elif tli_rec in ['sell', 'short']:
            score -= 15
        
        # Price Target Analysis
        if current_price and target_price:
            upside_pct = ((target_price - current_price) / current_price) * 100
            if upside_pct > 20:
                score += 10
                flags.append(f"Strong upside potential: {upside_pct:.1f}%")
            elif upside_pct > 10:
                score += 5
            elif upside_pct < -10:
                score -= 10
                flags.append(f"Price above target by {abs(upside_pct):.1f}%")
        
        # RSI Analysis
        rsi = technical_data.get('rsi')
        if rsi:
            if rsi < 30:
                score += 10
                flags.append("RSI indicates oversold conditions (bullish)")
            elif rsi > 70:
                score -= 10
                flags.append("RSI indicates overbought conditions (bearish)")
            elif 40 <= rsi <= 60:
                score += 5  # Neutral zone is good
        
        # Moving Average Analysis
        ma_50 = technical_data.get('ma_50')
        if current_price and ma_50:
            if current_price > ma_50:
                score += 5
            else:
                score -= 5
                flags.append("Price below 50-day MA (bearish)")
        
        # MACD Signal
        macd_signal = technical_data.get('macd_signal', 'neutral')
        if macd_signal == 'bullish':
            score += 5
        elif macd_signal == 'bearish':
            score -= 5
        elif macd_signal == 'oversold' and tli_rec in ['buy', 'long']:
            score += 8
            flags.append("Technical oversold aligns with TLI buy signal")
        elif macd_signal == 'overbought' and tli_rec in ['buy', 'long']:
            score -= 8
            flags.append("WARNING: Overbought conditions conflict with buy signal")
        
        # Risk/Reward Analysis
        if current_price and target_price and stop_loss:
            risk = current_price - stop_loss
            reward = target_price - current_price
            if risk > 0:
                risk_reward_ratio = reward / risk
                if risk_reward_ratio >= 3:
                    score += 10
                    flags.append(f"Excellent risk/reward ratio: {risk_reward_ratio:.1f}:1")
                elif risk_reward_ratio >= 2:
                    score += 5
                    flags.append(f"Good risk/reward ratio: {risk_reward_ratio:.1f}:1")
                elif risk_reward_ratio < 1:
                    score -= 10
                    flags.append(f"WARNING: Poor risk/reward ratio: {risk_reward_ratio:.1f}:1")
        
        # Volatility check
        price_change_pct = market_data.get('price_change_pct')
        if price_change_pct:
            if abs(price_change_pct) > 10:
                flags.append(f"High volatility: {price_change_pct:+.1f}% today")
                analysis['risk_level'] = 'high'
            elif abs(price_change_pct) > 5:
                analysis['risk_level'] = 'medium-high'
        
        # Determine overall recommendation
        if score >= 75:
            analysis['overall_recommendation'] = 'strong_buy'
        elif score >= 60:
            analysis['overall_recommendation'] = 'buy'
        elif score >= 45:
            analysis['overall_recommendation'] = 'hold'
        elif score >= 30:
            analysis['overall_recommendation'] = 'sell'
        else:
            analysis['overall_recommendation'] = 'strong_sell'
        
        # Agreement score (how well TLI and technicals align)
        analysis['agreement_score'] = max(0, min(100, score))
        analysis['flags'] = json.dumps(flags)
        
        return analysis
    
    def _fallback_analysis(self, symbol: str, tli_data: Dict) -> Dict[str, Any]:
        """Fallback analysis when external APIs fail"""
        return {
            'symbol': symbol,
            'tli_recommendation': tli_data.get('recommendation', 'hold'),
            'tli_target_price': tli_data.get('target_price'),
            'tli_stop_loss': tli_data.get('stop_loss'),
            'tli_notes': tli_data.get('notes', ''),
            'tli_confidence': tli_data.get('confidence', 'medium'),
            'current_price': None,
            'price_change_pct': None,
            'volume': None,
            'market_cap': None,
            'pe_ratio': None,
            'rsi': None,
            'macd_signal': 'neutral',
            'ma_50': None,
            'ma_200': None,
            'flags': json.dumps(['External data unavailable - TLI analysis only']),
            'agreement_score': 50.0,
            'overall_recommendation': tli_data.get('recommendation', 'hold'),
            'risk_level': 'medium'
        }


def extract_tli_recommendation(parsed_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
    """Extract TLI recommendation from parsed email data"""
    
    tli_data = {
        'recommendation': 'hold',
        'target_price': None,
        'stop_loss': None,
        'notes': parsed_data.get('notes', ''),
        'confidence': 'medium'
    }
    
    # Extract levels for this symbol
    levels = [l for l in parsed_data.get('levels', []) if l.get('symbol') == symbol]
    
    for level in levels:
        level_type = level.get('type', '').lower()
        price = level.get('price')
        
        if level_type in ['target', 'pt']:
            tli_data['target_price'] = price
        elif level_type in ['stop_loss', 'stop']:
            tli_data['stop_loss'] = price
    
    # Determine recommendation from context
    notes_lower = tli_data['notes'].lower()
    if any(word in notes_lower for word in ['buy', 'long', 'entry', 'bullish', 'accumulate']):
        tli_data['recommendation'] = 'buy'
        if 'strong' in notes_lower or 'aggressive' in notes_lower:
            tli_data['confidence'] = 'high'
    elif any(word in notes_lower for word in ['sell', 'short', 'exit', 'bearish', 'reduce']):
        tli_data['recommendation'] = 'sell'
    elif any(word in notes_lower for word in ['wait', 'watch', 'monitor']):
        tli_data['recommendation'] = 'wait'
    
    return tli_data
