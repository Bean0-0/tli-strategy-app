#!/usr/bin/env python
"""Process existing parsed email data and create stock evaluations"""

from app import app, db
from models import PriceLevel, StockEvaluation
from stock_analyzer import StockAnalyzer, extract_tli_recommendation
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_existing_data():
    """Process all existing price levels and create stock evaluations"""
    
    with app.app_context():
        # Get all unique symbols from price levels
        symbols = db.session.query(PriceLevel.symbol).distinct().all()
        symbols = [s[0] for s in symbols]
        
        if not symbols:
            print("❌ No parsed email data found.")
            print("   Parse some TLI emails first via the Email Parser.")
            return
        
        print(f"📊 Found {len(symbols)} unique symbols with parsed data")
        print(f"   Symbols: {', '.join(symbols)}\n")
        
        analyzer = StockAnalyzer()
        created_count = 0
        updated_count = 0
        error_count = 0
        
        for symbol in symbols:
            try:
                print(f"Processing {symbol}...")
                
                # Get all price levels for this symbol
                levels = PriceLevel.query.filter_by(symbol=symbol).all()
                
                # Reconstruct parsed data
                parsed_data = {
                    'symbols': [symbol],
                    'levels': [{
                        'symbol': l.symbol,
                        'type': l.level_type,
                        'price': l.price,
                        'notes': l.notes
                    } for l in levels],
                    'notes': ' | '.join(l.notes for l in levels if l.notes)
                }
                
                # Extract TLI recommendation
                tli_data = extract_tli_recommendation(parsed_data, symbol)
                
                # Analyze with external data
                analysis = analyzer.analyze_stock(symbol, tli_data)
                
                # Check if evaluation already exists
                evaluation = StockEvaluation.query.filter_by(symbol=symbol).first()
                
                if not evaluation:
                    # Create new evaluation
                    evaluation = StockEvaluation(
                        symbol=symbol,
                        user_id=levels[0].user_id if levels else None
                    )
                    created_count += 1
                    action = "Created"
                else:
                    updated_count += 1
                    action = "Updated"
                
                # Update fields
                for key, value in analysis.items():
                    if hasattr(evaluation, key):
                        setattr(evaluation, key, value)
                
                evaluation.updated_at = datetime.now(timezone.utc)
                
                if not evaluation.id:
                    db.session.add(evaluation)
                
                db.session.commit()
                
                print(f"  ✅ {action}: {symbol} - {evaluation.overall_recommendation}")
                print(f"     Target: ${evaluation.tli_target_price if evaluation.tli_target_price else 'N/A'}, "
                      f"Current: ${evaluation.current_price if evaluation.current_price else 'N/A'}, "
                      f"Agreement: {evaluation.agreement_score:.0f}%\n")
                
            except Exception as e:
                error_count += 1
                logger.error(f"  ❌ Error processing {symbol}: {e}\n")
                continue
        
        print("\n" + "="*60)
        print(f"✅ Processing complete!")
        print(f"   Created: {created_count} new evaluations")
        print(f"   Updated: {updated_count} existing evaluations")
        if error_count > 0:
            print(f"   ⚠️  Errors: {error_count}")
        print("="*60)
        print("\n🚀 Go to the dashboard to see your stock evaluations!")

if __name__ == '__main__':
    process_existing_data()
