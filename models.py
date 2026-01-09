"""Database models for TLi Trading Tool"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User accounts for viewing analyzed emails"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)  # Nullable for Google OAuth users
    email = db.Column(db.String(120), unique=True, nullable=True)
    google_id = db.Column(db.String(255), unique=True, nullable=True)  # For Google OAuth
    name = db.Column(db.String(255), nullable=True)
    profile_pic = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Position(db.Model):
    """Trading positions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for backward compatibility
    symbol = db.Column(db.String(10), nullable=False)
    position_type = db.Column(db.String(10), nullable=False)  # 'long' or 'short'
    entry_price = db.Column(db.Float, nullable=False)
    exit_price = db.Column(db.Float)
    shares = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    is_large_cap = db.Column(db.Boolean, default=False)  # True for AMD, NVDA, etc.
    status = db.Column(db.String(20), default='open')  # 'open' or 'closed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='positions')
    
    def __repr__(self):
        return f'<Position {self.symbol} {self.position_type} @ {self.entry_price}>'
    
    @property
    def current_value(self):
        """Calculate current position value"""
        if self.exit_price:
            return self.shares * self.exit_price
        return self.shares * self.entry_price
    
    @property
    def cost_basis(self):
        """Calculate cost basis"""
        return self.shares * self.entry_price
    
    @property
    def pnl(self):
        """Calculate P&L if position is closed"""
        if not self.exit_price:
            return None
        if self.position_type == 'long':
            return (self.exit_price - self.entry_price) * self.shares
        else:  # short
            return (self.entry_price - self.exit_price) * self.shares
    
    @property
    def pnl_percent(self):
        """Calculate P&L percentage"""
        if not self.exit_price:
            return None
        if self.position_type == 'long':
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:  # short
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100


class PriceLevel(db.Model):
    """Price levels extracted from emails"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for backward compatibility
    symbol = db.Column(db.String(10), nullable=False)
    level_type = db.Column(db.String(20), nullable=False)  # 'support', 'resistance', 'fib', 'target'
    price = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='price_levels')
    
    def __repr__(self):
        return f'<PriceLevel {self.symbol} {self.level_type} @ {self.price}>'


class Alert(db.Model):
    """Price alerts"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for backward compatibility
    symbol = db.Column(db.String(10), nullable=False)
    price = db.Column(db.Float, nullable=False)
    alert_type = db.Column(db.String(20), nullable=False)  # 'buy', 'sell', 'fib_extension'
    notes = db.Column(db.Text)
    triggered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    triggered_at = db.Column(db.DateTime)
    
    user = db.relationship('User', backref='alerts')
    
    def __repr__(self):
        return f'<Alert {self.symbol} @ {self.price} ({self.alert_type})>'


class TLiComment(db.Model):
    """TLi's comments and strategy notes"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Nullable for backward compatibility
    symbol = db.Column(db.String(10))  # Optional, can be general market comment
    comment_type = db.Column(db.String(20), nullable=False)  # 'long_term', 'short_term', 'pullback', 'general'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='comments')
    
    def __repr__(self):
        return f'<TLiComment {self.symbol or "General"} - {self.comment_type}>'


class ParsedEmail(db.Model):
    """Log of parsed emails to avoid reprocessing"""
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    parsed_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ParsedEmail {self.message_id}>'
