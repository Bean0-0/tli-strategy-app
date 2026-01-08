"""Position sizing calculator"""


def calculate_position_size(account_size, risk_percent, entry_price, stop_loss):
    """
    Calculate position size based on risk management
    
    Args:
        account_size: Total account value
        risk_percent: Percentage of account to risk (e.g., 1.0 for 1%)
        entry_price: Entry price per share
        stop_loss: Stop loss price per share
    
    Returns:
        dict with position sizing details
    """
    # Calculate risk amount in dollars
    risk_amount = account_size * (risk_percent / 100)
    
    # Calculate risk per share
    risk_per_share = abs(entry_price - stop_loss)
    
    # Calculate number of shares
    if risk_per_share == 0:
        return {
            'error': 'Entry price and stop loss cannot be the same'
        }
    
    shares = int(risk_amount / risk_per_share)
    
    # Calculate actual position size
    position_size = shares * entry_price
    
    # Calculate position size as percentage of account
    position_percent = (position_size / account_size) * 100
    
    # Calculate actual risk amount with whole shares
    actual_risk = shares * risk_per_share
    actual_risk_percent = (actual_risk / account_size) * 100
    
    return {
        'shares': shares,
        'position_size': round(position_size, 2),
        'position_percent': round(position_percent, 2),
        'risk_amount': round(actual_risk, 2),
        'risk_percent': round(actual_risk_percent, 2),
        'risk_per_share': round(risk_per_share, 2)
    }


def calculate_fibonacci_levels(high, low):
    """
    Calculate Fibonacci retracement and extension levels
    
    Args:
        high: Swing high price
        low: Swing low price
    
    Returns:
        dict with fib levels
    """
    diff = high - low
    
    # Retracement levels
    retracements = {
        '0%': high,
        '23.6%': high - (diff * 0.236),
        '38.2%': high - (diff * 0.382),
        '50%': high - (diff * 0.5),
        '61.8%': high - (diff * 0.618),
        '78.6%': high - (diff * 0.786),
        '100%': low
    }
    
    # Extension levels
    extensions = {
        '127.2%': high + (diff * 0.272),
        '161.8%': high + (diff * 0.618),
        '200%': high + diff,
        '261.8%': high + (diff * 1.618),
        '423.6%': high + (diff * 3.236)
    }
    
    return {
        'retracements': {k: round(v, 2) for k, v in retracements.items()},
        'extensions': {k: round(v, 2) for k, v in extensions.items()}
    }
