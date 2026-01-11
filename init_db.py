#!/usr/bin/env python
"""Initialize database with all models"""

from app import app, db

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully!")
        print("📊 New StockEvaluation model is ready to use.")
        print("\nTables created:")
        print("  - User")
        print("  - PriceLevel")
        print("  - ParsedEmail")
        print("  - StockEvaluation (NEW)")
