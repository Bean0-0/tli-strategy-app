"""TLi Trading Strategy Management Tool - Main Application"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta, timezone
import os
import requests
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db, User, PriceLevel, ParsedEmail, StockEvaluation
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Import helper modules
from email_parser import parse_trading_email
from gmail_client import get_gmail_client
from stock_analyzer import StockAnalyzer, extract_tli_recommendation


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Generate username from email
        username = email.split('@')[0]
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('register'))
        
        # Ensure username is unique
        base_username = username
        counter = 1
        while User.query.filter_by(username=username).first():
            username = f"{base_username}{counter}"
            counter += 1
            
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return redirect(url_for('register'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            created_at=datetime.utcnow()
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
        
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page with username/password or Google OAuth"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            login_user(user)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('index'))
        else:
            flash('Email not registered', 'error')
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Stock Evaluation Dashboard - Main view"""
    # Get recent stock evaluations
    evaluations = StockEvaluation.query.filter_by(
        user_id=current_user.id
    ).order_by(StockEvaluation.updated_at.desc()).limit(20).all()
    
    # Categorize by recommendation
    strong_buys = [e for e in evaluations if e.overall_recommendation == 'strong_buy']
    buys = [e for e in evaluations if e.overall_recommendation == 'buy']
    holds = [e for e in evaluations if e.overall_recommendation == 'hold']
    sells = [e for e in evaluations if e.overall_recommendation in ['sell', 'strong_sell']]
    
    # Get latest parsed emails count
    recent_emails = ParsedEmail.query.filter_by(user_id=current_user.id).count()
    
    # Convert evaluations to dictionaries for JSON serialization
    evaluations_dict = [e.to_dict() for e in evaluations]
    
    return render_template('index.html',
                         evaluations=evaluations,
                         evaluations_dict=evaluations_dict,
                         strong_buys=strong_buys,
                         buys=buys,
                         holds=holds,
                         sells=sells,
                         recent_emails=recent_emails)


@app.route('/refresh-analysis/<symbol>')
@login_required
def refresh_analysis(symbol):
    """Refresh analysis for a specific symbol"""
    try:
        # Get latest price levels for this symbol
        levels = PriceLevel.query.filter_by(
            user_id=current_user.id,
            symbol=symbol
        ).order_by(PriceLevel.created_at.desc()).all()
        
        if not levels:
            return jsonify({'success': False, 'message': 'No TLI data found for this symbol'}), 404
        
        # Reconstruct parsed data from levels
        parsed_data = {
            'symbols': [symbol],
            'levels': [{'symbol': l.symbol, 'type': l.level_type, 'price': l.price, 'notes': l.notes} for l in levels],
            'notes': ' | '.join(l.notes for l in levels if l.notes)
        }
        
        # Extract TLI recommendation
        tli_data = extract_tli_recommendation(parsed_data, symbol)
        
        # Analyze with external data
        analyzer = StockAnalyzer()
        analysis = analyzer.analyze_stock(symbol, tli_data)
        
        # Update or create evaluation
        evaluation = StockEvaluation.query.filter_by(
            user_id=current_user.id,
            symbol=symbol
        ).first()
        
        if not evaluation:
            evaluation = StockEvaluation(user_id=current_user.id, symbol=symbol)
        
        # Update fields
        for key, value in analysis.items():
            if hasattr(evaluation, key):
                setattr(evaluation, key, value)
        
        evaluation.updated_at = datetime.utcnow()
        
        if not evaluation.id:
            db.session.add(evaluation)
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'Analysis refreshed for {symbol}'})
        
    except Exception as e:
        logger.error(f"Error refreshing analysis: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/email-parser')
@login_required
def email_parser_view():
    """Email parser interface"""
    return render_template('email_parser.html')


@app.route('/email-parser/parse', methods=['POST'])
@login_required
def parse_email():
    """Parse email for trading levels and create stock evaluation"""
    data = request.json
    email_content = data['email_content']
    
    parsed_data = parse_trading_email(email_content)
    
    # Save price levels to database
    if parsed_data['levels']:
        for level_data in parsed_data['levels']:
            level = PriceLevel(
                user_id=current_user.id,
                symbol=level_data['symbol'],
                level_type=level_data['type'],
                price=level_data['price'],
                notes=level_data.get('notes', '')
            )
            db.session.add(level)
        db.session.commit()
        
        # Create stock evaluations for each symbol
        analyzer = StockAnalyzer()
        for symbol in parsed_data['symbols']:
            try:
                tli_data = extract_tli_recommendation(parsed_data, symbol)
                analysis = analyzer.analyze_stock(symbol, tli_data)
                
                # Update or create evaluation
                evaluation = StockEvaluation.query.filter_by(
                    user_id=current_user.id,
                    symbol=symbol
                ).first()
                
                if not evaluation:
                    evaluation = StockEvaluation(user_id=current_user.id, symbol=symbol)
                
                for key, value in analysis.items():
                    if hasattr(evaluation, key):
                        setattr(evaluation, key, value)
                
                evaluation.updated_at = datetime.now(timezone.utc)
                
                if not evaluation.id:
                    db.session.add(evaluation)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
        
        db.session.commit()
    
    return jsonify(parsed_data)


@app.route('/levels')
@login_required
def levels():
    """View price levels"""
    all_levels = PriceLevel.query.filter_by(user_id=current_user.id).order_by(PriceLevel.symbol, PriceLevel.price).all()
    return render_template('levels.html', levels=all_levels)


@app.route('/gmail/test-connection', methods=['POST'])
@login_required
def test_gmail_connection():
    """Test Gmail API connection"""
    try:
        client = get_gmail_client()
        success = client.test_connection()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Gmail connection successful!',
                'email': client.user_email
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to Gmail. Please check your credentials.'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@app.route('/gmail/fetch-emails', methods=['POST'])
@login_required
def fetch_gmail_emails():
    """Fetch forwarded emails from Gmail"""
    try:
        data = request.json or {}
        max_results = int(data.get('max_results', 10))
        days_back = int(data.get('days_back', 7))
        page_token = data.get('page_token')
        
        client = get_gmail_client()
        
        # Authenticate if needed
        if not client.authenticate():
            return jsonify({
                'success': False,
                'message': 'Failed to authenticate with Gmail. Please check credentials.'
            }), 401
        
        # Fetch forwarded emails (emails with Fwd: or FW: in subject)
        # Don't filter by recipient - we want all forwarded emails in the inbox
        result = client.get_forwarded_emails(
            max_results=max_results,
            days_back=days_back,
            query_filter="-category:promotions -category:social",
            page_token=page_token
        )
        
        emails = result.get('emails', [])
        next_page_token = result.get('next_page_token')
        
        if not emails and not page_token:
            return jsonify({
                'success': True,
                'message': 'No forwarded emails found in the specified time range.',
                'emails': [],
                'next_page_token': None
            })
            
        # Get list of parsed message IDs
        # We fetch all for simplicity, but could filter by ID list if needed optimization
        parsed_ids = {p.message_id for p in ParsedEmail.query.all()}
        
        # Return email list
        return jsonify({
            'success': True,
            'message': f'Found {len(emails)} forwarded emails',
            'emails': [{
                'id': email['id'],
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date'],
                'snippet': email['snippet'],
                'is_parsed': email['id'] in parsed_ids
            } for email in emails],
            'next_page_token': next_page_token
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error fetching emails: {str(e)}'
        }), 500


@app.route('/gmail/parse-email/<message_id>', methods=['POST'])
@login_required
def parse_gmail_email(message_id):
    """Fetch and parse a specific email from Gmail"""
    try:
        client = get_gmail_client()
        
        # Authenticate if needed
        if not client.authenticate():
            return jsonify({
                'success': False,
                'message': 'Failed to authenticate with Gmail'
            }), 401
        
        # Get email details
        email = client.get_email_by_id(message_id)
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email not found'
            }), 404
        
        # Parse email content
        parsed_data = parse_trading_email(email['body'], email.get('images'))
        
        # Save price levels to database
        saved_count = 0
        if parsed_data['levels']:
            for level_data in parsed_data['levels']:
                level = PriceLevel(
                    user_id=current_user.id,
                    symbol=level_data['symbol'],
                    level_type=level_data['type'],
                    price=level_data['price'],
                    notes=level_data.get('notes', '')
                )
                db.session.add(level)
                saved_count += 1
            db.session.commit()
            
            # Create stock evaluations for each symbol
            analyzer = StockAnalyzer()
            for symbol in parsed_data['symbols']:
                try:
                    tli_data = extract_tli_recommendation(parsed_data, symbol)
                    analysis = analyzer.analyze_stock(symbol, tli_data)
                    
                    # Update or create evaluation
                    evaluation = StockEvaluation.query.filter_by(
                        user_id=current_user.id,
                        symbol=symbol
                    ).first()
                    
                    if not evaluation:
                        evaluation = StockEvaluation(user_id=current_user.id, symbol=symbol)
                    
                    for key, value in analysis.items():
                        if hasattr(evaluation, key):
                            setattr(evaluation, key, value)
                    
                    evaluation.updated_at = datetime.utcnow()
                    
                    if not evaluation.id:
                        db.session.add(evaluation)
                        
                except Exception as e:
                    logger.error(f"Error analyzing {symbol}: {e}")
            
            db.session.commit()
            
        # Record as parsed
        if not ParsedEmail.query.filter_by(message_id=message_id).first():
            db.session.add(ParsedEmail(message_id=message_id, user_id=current_user.id))
            db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Parsed email and saved {saved_count} price levels',
            'email': {
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date']
            },
            'parsed_data': parsed_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error parsing email: {str(e)}'
        }), 500


@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized!")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # Only use debug mode in development
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
