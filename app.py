"""TLi Trading Strategy Management Tool - Main Application"""
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
from models import db, Position, PriceLevel, Alert, TLiComment
db.init_app(app)

# Import helper modules
from email_parser import parse_trading_email
from position_calculator import calculate_position_size
from gmail_client import get_gmail_client


@app.route('/')
def index():
    """Dashboard - Main view"""
    positions = Position.query.order_by(Position.created_at.desc()).all()
    alerts = Alert.query.filter_by(triggered=False).order_by(Alert.price).all()
    recent_comments = TLiComment.query.order_by(TLiComment.created_at.desc()).limit(5).all()
    
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
def positions():
    """View all positions"""
    all_positions = Position.query.order_by(Position.created_at.desc()).all()
    return render_template('positions.html', positions=all_positions)


@app.route('/positions/add', methods=['GET', 'POST'])
def add_position():
    """Add new position"""
    if request.method == 'POST':
        data = request.form
        position = Position(
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
def update_position(position_id):
    """Update position"""
    position = Position.query.get_or_404(position_id)
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
def calculator():
    """Position sizing calculator"""
    return render_template('calculator.html')


@app.route('/calculator/calculate', methods=['POST'])
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
def alerts():
    """View and manage alerts"""
    active_alerts = Alert.query.filter_by(triggered=False).order_by(Alert.symbol, Alert.price).all()
    triggered_alerts = Alert.query.filter_by(triggered=True).order_by(Alert.triggered_at.desc()).limit(20).all()
    return render_template('alerts.html', active_alerts=active_alerts, triggered_alerts=triggered_alerts)


@app.route('/alerts/add', methods=['POST'])
def add_alert():
    """Add new price alert"""
    data = request.json
    alert = Alert(
        symbol=data['symbol'].upper(),
        price=float(data['price']),
        alert_type=data['alert_type'],
        notes=data.get('notes', '')
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify({'success': True, 'alert_id': alert.id})


@app.route('/alerts/<int:alert_id>/delete', methods=['POST'])
def delete_alert(alert_id):
    """Delete alert"""
    alert = Alert.query.get_or_404(alert_id)
    db.session.delete(alert)
    db.session.commit()
    return jsonify({'success': True})


@app.route('/comments')
def comments():
    """View TLi comments and notes"""
    all_comments = TLiComment.query.order_by(TLiComment.created_at.desc()).all()
    return render_template('comments.html', comments=all_comments)


@app.route('/comments/add', methods=['POST'])
def add_comment():
    """Add TLi comment/note"""
    data = request.json
    comment = TLiComment(
        symbol=data.get('symbol', '').upper() if data.get('symbol') else None,
        comment_type=data['comment_type'],
        content=data['content']
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({'success': True, 'comment_id': comment.id})


@app.route('/email-parser')
def email_parser_view():
    """Email parser interface"""
    return render_template('email_parser.html')


@app.route('/email-parser/parse', methods=['POST'])
def parse_email():
    """Parse email for trading levels"""
    data = request.json
    email_content = data['email_content']
    
    parsed_data = parse_trading_email(email_content)
    
    # Save price levels to database
    if parsed_data['levels']:
        for level_data in parsed_data['levels']:
            level = PriceLevel(
                symbol=level_data['symbol'],
                level_type=level_data['type'],
                price=level_data['price'],
                notes=level_data.get('notes', '')
            )
            db.session.add(level)
        db.session.commit()
    
    return jsonify(parsed_data)


@app.route('/levels')
def levels():
    """View price levels"""
    all_levels = PriceLevel.query.order_by(PriceLevel.symbol, PriceLevel.price).all()
    return render_template('levels.html', levels=all_levels)


@app.route('/gmail/test-connection', methods=['POST'])
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
def fetch_gmail_emails():
    """Fetch forwarded emails from Gmail"""
    try:
        data = request.json or {}
        max_results = int(data.get('max_results', 10))
        days_back = int(data.get('days_back', 7))
        
        client = get_gmail_client()
        
        # Authenticate if needed
        if not client.authenticate():
            return jsonify({
                'success': False,
                'message': 'Failed to authenticate with Gmail. Please check credentials.'
            }), 401
        
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
        parsed_data = parse_trading_email(email['body'])
        
        # Save price levels to database
        saved_count = 0
        if parsed_data['levels']:
            for level_data in parsed_data['levels']:
                level = PriceLevel(
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
