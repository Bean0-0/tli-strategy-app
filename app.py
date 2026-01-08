"""TLi Trading Strategy Management Tool - Main Application"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Google OAuth configuration
app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
app.config['GOOGLE_DISCOVERY_URL'] = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize database
from models import db, User, Position, PriceLevel, Alert, TLiComment
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import helper modules
from email_parser import parse_trading_email
from position_calculator import calculate_position_size
from gmail_client import get_gmail_client

# OAuth imports
import requests
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


@app.route('/login')
def login():
    """Login page"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')


@app.route('/login/google')
def login_google():
    """Initiate Google OAuth flow"""
    # Get Google OAuth configuration
    google_provider_cfg = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    
    # Build OAuth request
    redirect_uri = url_for('callback', _external=True)
    
    request_uri = (
        f"{authorization_endpoint}?"
        f"response_type=code&"
        f"client_id={app.config['GOOGLE_CLIENT_ID']}&"
        f"redirect_uri={redirect_uri}&"
        f"scope=openid%20email%20profile%20https://www.googleapis.com/auth/gmail.readonly&"
        f"access_type=offline&"
        f"prompt=consent"
    )
    
    return redirect(request_uri)


@app.route('/login/callback')
def callback():
    """Handle Google OAuth callback"""
    # Get authorization code
    code = request.args.get('code')
    
    if not code:
        return "Error: No authorization code received", 400
    
    # Get Google OAuth configuration
    google_provider_cfg = requests.get(app.config['GOOGLE_DISCOVERY_URL']).json()
    token_endpoint = google_provider_cfg["token_endpoint"]
    
    # Exchange code for tokens
    token_url, headers, body = prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=url_for('callback', _external=True),
        code=code
    )
    
    token_response = requests.post(
        token_endpoint,
        data={
            'code': code,
            'client_id': app.config['GOOGLE_CLIENT_ID'],
            'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
            'redirect_uri': url_for('callback', _external=True),
            'grant_type': 'authorization_code',
        },
        headers={'Content-Type': 'application/x-www-form-urlencoded'}
    )
    
    if token_response.status_code != 200:
        return f"Error getting tokens: {token_response.text}", 400
    
    tokens = token_response.json()
    
    # Verify ID token
    try:
        idinfo = id_token.verify_oauth2_token(
            tokens['id_token'],
            google_requests.Request(),
            app.config['GOOGLE_CLIENT_ID']
        )
    except ValueError as e:
        return f"Error verifying token: {str(e)}", 400
    
    # Extract user info
    google_id = idinfo['sub']
    email = idinfo['email']
    name = idinfo.get('name', '')
    picture = idinfo.get('picture', '')
    
    # Find or create user
    user = User.query.filter_by(google_id=google_id).first()
    
    if not user:
        user = User(
            google_id=google_id,
            email=email,
            name=name,
            profile_pic=picture,
            created_at=datetime.utcnow()
        )
        db.session.add(user)
    
    # Update user info and tokens
    user.name = name
    user.profile_pic = picture
    user.last_login = datetime.utcnow()
    user.access_token = tokens.get('access_token')
    user.refresh_token = tokens.get('refresh_token', user.refresh_token)  # Keep old refresh token if not provided
    
    # Calculate token expiry
    if 'expires_in' in tokens:
        from datetime import timedelta
        user.token_expiry = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
    
    db.session.commit()
    
    # Log in user
    login_user(user)
    
    return redirect(url_for('index'))


def prepare_token_request(token_endpoint, authorization_response, redirect_url, code):
    """Helper function to prepare token request"""
    return token_endpoint, {}, {}


@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('login'))


@app.route('/')
@login_required
def index():
    """Dashboard - Main view"""
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
        # Use user's stored OAuth credentials
        from gmail_client import GmailClient
        client = GmailClient(user_email=current_user.email)
        
        # Set credentials from user's stored tokens
        if current_user.access_token:
            from google.oauth2.credentials import Credentials
            creds = Credentials(
                token=current_user.access_token,
                refresh_token=current_user.refresh_token
            )
            client.creds = creds
            from googleapiclient.discovery import build
            client.service = build('gmail', 'v1', credentials=creds)
            
            success = client.test_connection()
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'Gmail connection successful!',
                    'email': current_user.email
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Failed to connect to Gmail. Please re-authenticate.'
                }), 400
        else:
            return jsonify({
                'success': False,
                'message': 'No Gmail credentials found. Please log in again to grant Gmail access.'
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
        
        # Use user's stored OAuth credentials
        from gmail_client import GmailClient
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        client = GmailClient(user_email=current_user.email)
        
        if not current_user.access_token:
            return jsonify({
                'success': False,
                'message': 'No Gmail access. Please log in again to grant Gmail permissions.'
            }), 401
        
        # Set credentials from user's stored tokens
        creds = Credentials(
            token=current_user.access_token,
            refresh_token=current_user.refresh_token
        )
        client.creds = creds
        client.service = build('gmail', 'v1', credentials=creds)
        
        # Fetch forwarded emails
        emails = client.get_forwarded_emails(
            max_results=max_results,
            days_back=days_back
        )
        
        if not emails:
            return jsonify({
                'success': True,
                'message': 'No forwarded emails found in the specified time range.',
                'emails': []
            })
        
        # Return email list
        return jsonify({
            'success': True,
            'message': f'Found {len(emails)} forwarded emails',
            'emails': [{
                'id': email['id'],
                'subject': email['subject'],
                'sender': email['sender'],
                'date': email['date'],
                'snippet': email['snippet']
            } for email in emails]
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
        # Use user's stored OAuth credentials
        from gmail_client import GmailClient
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        
        client = GmailClient(user_email=current_user.email)
        
        if not current_user.access_token:
            return jsonify({
                'success': False,
                'message': 'No Gmail access. Please log in again.'
            }), 401
        
        # Set credentials from user's stored tokens
        creds = Credentials(
            token=current_user.access_token,
            refresh_token=current_user.refresh_token
        )
        client.creds = creds
        client.service = build('gmail', 'v1', credentials=creds)
        
        # Get email details
        email = client.get_email_by_id(message_id)
        
        if not email:
            return jsonify({
                'success': False,
                'message': 'Email not found'
            }), 404
        
        # Parse email content
        parsed_data = parse_trading_email(email['body'])
        
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
