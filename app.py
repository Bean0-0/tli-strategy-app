"""TLi Trading Strategy Management Tool - Main Application"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
import os
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db, User, Position, PriceLevel, Alert, TLiComment, ParsedEmail
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import helper modules
from email_parser import parse_trading_email
from position_calculator import calculate_position_size
from gmail_client import get_gmail_client


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
            user.last_login = datetime.utcnow()
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
    """Dashboard - Main view"""
    # Show user-specific data
    positions = Position.query.filter_by(user_id=current_user.id).order_by(Position.created_at.desc()).all()
    alerts = Alert.query.filter_by(user_id=current_user.id, triggered=False).order_by(Alert.price).all()
    recent_comments = TLiComment.query.filter_by(user_id=current_user.id).order_by(TLiComment.created_at.desc()).limit(5).all()
    
    # Separate large cap and small cap positions
    large_caps = [p for p in positions if p.is_large_cap]
    small_caps = [p for p in positions if not p.is_large_cap]
    
    return render_template('index.html', 
                         positions=positions,
                         large_caps=large_caps,
                         small_caps=small_caps,
                         alerts=alerts,
                         comments=recent_comments)


@app.route('/positions')
@login_required
def positions():
    """View all positions"""
    all_positions = Position.query.filter_by(user_id=current_user.id).order_by(Position.created_at.desc()).all()
    return render_template('positions.html', positions=all_positions)


@app.route('/positions/add', methods=['GET', 'POST'])
@login_required
def add_position():
    """Add new position"""
    if request.method == 'POST':
        data = request.form
        position = Position(
            user_id=current_user.id,
            symbol=data['symbol'].upper(),
            position_type=data['position_type'],
            entry_price=float(data['entry_price']),
            shares=int(data['shares']),
            notes=data.get('notes', ''),
            is_large_cap=data.get('is_large_cap') == 'on'
        )
        db.session.add(position)
        db.session.commit()
        return redirect(url_for('positions'))
    
    return render_template('add_position.html')


@app.route('/positions/<int:position_id>/update', methods=['POST'])
@login_required
def update_position(position_id):
    """Update position"""
    position = Position.query.filter_by(id=position_id, user_id=current_user.id).first_or_404()
    data = request.json
    
    if 'exit_price' in data:
        position.exit_price = float(data['exit_price'])
        position.status = 'closed'
        position.closed_at = datetime.utcnow()
    if 'notes' in data:
        position.notes = data['notes']
    
    db.session.commit()
    return jsonify({'success': True})


@app.route('/calculator')
@login_required
def calculator():
    """Position sizing calculator"""
    return render_template('calculator.html')


@app.route('/calculator/calculate', methods=['POST'])
@login_required
def calculate():
    """Calculate position size"""
    data = request.json
    account_size = float(data['account_size'])
    risk_percent = float(data['risk_percent'])
    entry_price = float(data['entry_price'])
    stop_loss = float(data['stop_loss'])
    
    result = calculate_position_size(account_size, risk_percent, entry_price, stop_loss)
    return jsonify(result)


@app.route('/alerts')
@login_required
def alerts():
    """View and manage alerts"""
    active_alerts = Alert.query.filter_by(user_id=current_user.id, triggered=False).order_by(Alert.symbol, Alert.price).all()
    triggered_alerts = Alert.query.filter_by(user_id=current_user.id, triggered=True).order_by(Alert.triggered_at.desc()).limit(20).all()
    return render_template('alerts.html', active_alerts=active_alerts, triggered_alerts=triggered_alerts)


@app.route('/alerts/add', methods=['POST'])
@login_required
def add_alert():
    """Add new price alert"""
    data = request.json
    alert = Alert(
        user_id=current_user.id,
        symbol=data['symbol'].upper(),
        price=float(data['price']),
        alert_type=data['alert_type'],
        notes=data.get('notes', '')
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'success': True, 'alert_id': alert.id})


@app.route('/alerts/<int:alert_id>/delete', methods=['POST'])
@login_required
def delete_alert(alert_id):
    """Delete alert"""
    alert = Alert.query.filter_by(id=alert_id, user_id=current_user.id).first_or_404()
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/comments')
@login_required
def comments():
    """View TLi comments and notes"""
    all_comments = TLiComment.query.filter_by(user_id=current_user.id).order_by(TLiComment.created_at.desc()).all()
    return render_template('comments.html', comments=all_comments)


@app.route('/comments/add', methods=['POST'])
@login_required
def add_comment():
    """Add TLi comment/note"""
    data = request.json
    comment = TLiComment(
        user_id=current_user.id,
        symbol=data.get('symbol', '').upper() if data.get('symbol') else None,
        comment_type=data['comment_type'],
        content=data['content']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True, 'comment_id': comment.id})


@app.route('/email-parser')
@login_required
def email_parser_view():
    """Email parser interface"""
    return render_template('email_parser.html')


@app.route('/email-parser/parse', methods=['POST'])
@login_required
def parse_email():
    """Parse email for trading levels"""
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
        
        # Fetch emails sent to the current user
        result = client.get_forwarded_emails(
            max_results=max_results,
            days_back=days_back,
            query_filter=f"to:{current_user.email} -category:promotions -category:social",
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
