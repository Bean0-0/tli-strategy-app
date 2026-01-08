"""Email parser for extracting trading levels from forwarded emails"""
import re
from typing import Dict, List, Any


def parse_trading_email(email_content: str) -> Dict[str, Any]:
    """
    Parse trading email to extract symbols, levels, and notes
    
    Args:
        email_content: Raw email content
    
    Returns:
        dict containing parsed data
    """
    result = {
        'symbols': [],
        'levels': [],
        'notes': '',
        'raw_content': email_content
    }
    
    # Extract stock symbols (e.g., $AMD, NVDA, etc.)
    # Look for $SYMBOL pattern first (most reliable)
    dollar_symbols = re.findall(r'\$([A-Z]{2,5})\b', email_content)
    
    # Filter common words and technical indicators that might be false positives
    excluded = {'THE', 'AND', 'OR', 'BUT', 'FOR', 'NOT', 'ARE', 'WAS', 'WE', 'YOU', 'ALL', 
                'CAN', 'HER', 'WAS', 'ONE', 'OUR', 'OUT', 'DAY', 'GET', 'HAS', 'HIM',
                'HIS', 'HOW', 'MAN', 'NEW', 'NOW', 'OLD', 'SEE', 'TWO', 'WAY', 'WHO',
                'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 'TOO', 'USE', 'FROM',
                'DATE', 'SUBJECT', 'REPLY', 'TO', 'EMAIL', 'VIEW', 'APP', 'LIKE', 'SHARE',
                'COMMENT', 'POST', 'SENT', 'BEGIN', 'MESSAGE', 'FORWARDED', 'DCA', 'WAVE',
                'FEB', 'JAN', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT',
                'NOV', 'DEC', 'THIS', 'HAVE', 'BEEN', 'ONCE', 'THAT', 'WITH', 'WILL',
                'MUST', 'JUST', 'BACK', 'THEN', 'NEXT', 'MORE', 'ALSO', 'HERE', 'VERY',
                'MA', 'WMA', 'PT', 'FIB', 'NYC', 'US', 'OK', 'SF', 'CA'}  # Exclude technical indicators
    
    # Prioritize dollar-sign symbols
    result['symbols'] = [s for s in dollar_symbols if s not in excluded]
    
    # If no symbols found, look for commodities
    if not result['symbols']:
        commodities = ['PALLADIUM', 'GOLD', 'SILVER', 'PLATINUM', 'COPPER', 'OIL', 'CRUDE']
        for commodity in commodities:
            if commodity in email_content.upper():
                # Check if it's actually the subject (appears early or in context)
                if email_content.upper().find(commodity) < 500:  # Within first 500 chars
                    result['symbols'].append(commodity)
                    break  # Only add the first commodity found
    
    # Remove duplicates and sort
    result['symbols'] = sorted(list(set(result['symbols'])))
    
    # Extract levels with better context awareness
    for symbol in result['symbols']:
        # Look for price targets (PT) - be more specific
        pt_pattern = rf'PT.*?(?:is|for\s+\d{{4}}.*?is)\s+\$(\d+\.?\d*)\b'
        pt_matches = re.finditer(pt_pattern, email_content, re.IGNORECASE)
        for match in pt_matches:
            try:
                price = float(match.group(1))
                if 0.01 < price < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'target',
                        'price': price,
                        'notes': f"PT: ${price}"
                    })
            except (ValueError, IndexError):
                continue
        
        # Look for Wave targets - more specific pattern
        wave_pattern = rf'Wave\s+\d+.*?(?:target|moves)\s+(?:at|to)\s+\$(\d+\.?\d*)\b'
        wave_matches = re.finditer(wave_pattern, email_content, re.IGNORECASE)
        for match in wave_matches:
            try:
                price = float(match.group(1))
                if 0.01 < price < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'target',
                        'price': price,
                        'notes': match.group(0).strip()
                    })
            except (ValueError, IndexError):
                continue
        
        # Look for Fibonacci levels with $ sign
        fib_patterns = [
            (r'0\.5\s+Fib.*?(?:at|level)\s+\$(\d+\.?\d*)', 'fib_0.5'),
            (r'0\.38\s+Fib', None),  # Just mark the position, extract price nearby
            (r'0\.618?\s+Fib', None),
            (r'1\.618\s+Fib\s+at\s+\$(\d+\.?\d*)', 'fib_1.618'),
            (r'50\s+Day\s+MA.*?(?:at|hold\s+at)\s+\$(\d+\.?\d*)', 'ma_50d'),
            (r'200\s+Day\s+MA.*?at\s+\$(\d+\.?\d*)', 'ma_200d'),
            (r'50\s+WMA.*?(?:at|converted\s+to\s+support\s+at)\s+\$(\d+\.?\d*)', 'ma_50w'),
            (r'200\s+WMA\s+at\s+\$(\d+\.?\d*)', 'ma_200w'),
        ]
        
        for pattern, level_type in fib_patterns:
            if level_type:
                matches = re.finditer(pattern, email_content, re.IGNORECASE)
                for match in matches:
                    try:
                        price = float(match.group(1))
                        if 0.01 < price < 100000:
                            result['levels'].append({
                                'symbol': symbol,
                                'type': level_type,
                                'price': price,
                                'notes': match.group(0).strip()
                            })
                    except (ValueError, IndexError):
                        continue
        
        # Look for buy zones and ranges - more specific
        range_pattern = rf'(?:buy\s+zone.*?range|range).*?between\s+\$(\d+\.?\d*).*?(?:and|to)\s+.*?\$(\d+\.?\d*)'
        range_matches = re.finditer(range_pattern, email_content, re.IGNORECASE)
        for match in range_matches:
            try:
                price1 = float(match.group(1))
                price2 = float(match.group(2))
                if 0.01 < price1 < 100000 and 0.01 < price2 < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'buy_zone',
                        'price': min(price1, price2),
                        'notes': f"Buy Zone: ${min(price1, price2)} - ${max(price1, price2)}"
                    })
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'buy_zone',
                        'price': max(price1, price2),
                        'notes': f"Buy Zone: ${min(price1, price2)} - ${max(price1, price2)}"
                    })
            except (ValueError, IndexError):
                continue
        
        # Look for specific price mentions with context
        # "breakout level between $X - $Y"
        breakout_range_pattern = rf'breakout\s+level\s+between\s+\$(\d+\.?\d*)\s*-\s*\$(\d+\.?\d*)'
        breakout_matches = re.finditer(breakout_range_pattern, email_content, re.IGNORECASE)
        for match in breakout_matches:
            try:
                price1 = float(match.group(1))
                price2 = float(match.group(2))
                if 0.01 < price1 < 100000 and 0.01 < price2 < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'breakout',
                        'price': price1,
                        'notes': f"Breakout level: ${price1} - ${price2}"
                    })
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'breakout',
                        'price': price2,
                        'notes': f"Breakout level: ${price1} - ${price2}"
                    })
            except (ValueError, IndexError):
                continue
        
        # "bounced from $X to $Y"
        bounce_pattern = rf'bounced?\s+from\s+\$(\d+\.?\d*)\s+to\s+\$(\d+\.?\d*)'
        bounce_matches = re.finditer(bounce_pattern, email_content, re.IGNORECASE)
        for match in bounce_matches:
            try:
                price1 = float(match.group(1))
                price2 = float(match.group(2))
                if 0.01 < price1 < 100000 and 0.01 < price2 < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'support',
                        'price': price1,
                        'notes': f"Bounced from ${price1}"
                    })
            except (ValueError, IndexError):
                continue
        
        # "resistance back up to $X"
        resistance_to_pattern = rf'resistance\s+(?:back\s+)?up\s+to\s+\$(\d+\.?\d*)'
        resistance_matches = re.finditer(resistance_to_pattern, email_content, re.IGNORECASE)
        for match in resistance_matches:
            try:
                price = float(match.group(1))
                if 0.01 < price < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'resistance',
                        'price': price,
                        'notes': match.group(0).strip()
                    })
            except (ValueError, IndexError):
                continue
        
        # "high of $X"
        high_pattern = rf'high\s+of\s+\$(\d+\.?\d*)'
        high_matches = re.finditer(high_pattern, email_content, re.IGNORECASE)
        for match in high_matches:
            try:
                price = float(match.group(1))
                if 0.01 < price < 100000:
                    result['levels'].append({
                        'symbol': symbol,
                        'type': 'resistance',
                        'price': price,
                        'notes': f"High of ${price}"
                    })
            except (ValueError, IndexError):
                continue
    
    # Extract key strategic notes
    strategic_lines = []
    for line in email_content.split('\n'):
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Look for lines with important keywords
        if any(keyword in line_stripped.lower() for keyword in [
            'plan:', 'strategy', 'objective', 'low risk entry', 'accumulate',
            'wave 3', 'wave 5', 'long term', 'short term', 'must', 'should consider'
        ]):
            strategic_lines.append(line_stripped)
    
    if strategic_lines:
        result['notes'] = '\n'.join(strategic_lines)
    
    # Remove duplicate levels
    seen = set()
    unique_levels = []
    for level in result['levels']:
        key = (level['symbol'], level['type'], level['price'])
        if key not in seen:
            seen.add(key)
            unique_levels.append(level)
    
    result['levels'] = unique_levels
    
    return result


def extract_fibonacci_levels(email_content: str) -> List[Dict[str, Any]]:
    """
    Extract Fibonacci levels from email content
    
    Args:
        email_content: Raw email content
    
    Returns:
        list of fibonacci level dictionaries
    """
    fib_levels = []
    
    # Common fibonacci percentages with improved patterns
    fib_patterns = [
        (r'\$(\d+\.?\d*).*?(?:23\.6|236|0\.236)', '23.6%'),
        (r'\$(\d+\.?\d*).*?(?:38\.2|382|0\.382)', '38.2%'),
        (r'\$(\d+\.?\d*).*?(?:50|0\.5|50%)', '50%'),
        (r'\$(\d+\.?\d*).*?(?:61\.8|618|0\.618)', '61.8%'),
        (r'\$(\d+\.?\d*).*?(?:78\.6|786|0\.786)', '78.6%'),
        (r'\$(\d+\.?\d*).*?(?:127|1\.27)', '127%'),
        (r'\$(\d+\.?\d*).*?(?:161\.8|1618|1\.618)', '161.8%'),
        (r'\$(\d+\.?\d*).*?(?:261\.8|2618|2\.618)', '261.8%'),
    ]
    
    for pattern, fib_level in fib_patterns:
        matches = re.finditer(pattern, email_content, re.IGNORECASE)
        for match in matches:
            try:
                price = float(match.group(1))
                if 0.01 < price < 100000:
                    fib_levels.append({
                        'price': price,
                        'fib_level': fib_level,
                        'context': match.group(0)
                    })
            except (ValueError, IndexError):
                continue
    
    return fib_levels



