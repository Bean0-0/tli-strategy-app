#!/usr/bin/env python3
"""
Example usage script demonstrating Gmail API integration with the TLi Trading Tool

This script shows how to:
1. Connect to Gmail API
2. Fetch forwarded emails
3. Parse trading levels from emails
4. Save data to the database
"""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gmail_client import get_gmail_client
from email_parser import parse_trading_email


def main():
    """Demonstrate the complete email analysis workflow"""
    
    print("=" * 70)
    print("TLi Trading Tool - Gmail API Integration Example")
    print("=" * 70)
    print()
    
    # Step 1: Initialize Gmail client
    print("Step 1: Initializing Gmail client...")
    print("-" * 70)
    client = get_gmail_client()
    print(f"✓ Gmail client configured for: {client.user_email}")
    print()
    
    # Step 2: Test connection
    print("Step 2: Testing Gmail API connection...")
    print("-" * 70)
    if not client.test_connection():
        print("❌ Failed to connect to Gmail")
        print("Please run 'python gmail_client.py' to authenticate first")
        return
    print()
    
    # Step 3: Fetch forwarded emails
    print("Step 3: Fetching forwarded emails...")
    print("-" * 70)
    print("Searching for emails with 'Fwd:' in subject from the last 30 days...")
    emails = client.get_forwarded_emails(max_results=5, days_back=30)
    
    if not emails:
        print("No forwarded emails found.")
        print()
        print("Tips:")
        print("- Make sure emails are forwarded to tli.strategy.app@gmail.com")
        print("- Check that forwarded emails have 'Fwd:' in the subject")
        print("- Try increasing days_back parameter")
        return
    
    print(f"✓ Found {len(emails)} forwarded emails")
    print()
    
    # Step 4: Display emails
    print("Step 4: Email summaries...")
    print("-" * 70)
    for i, email in enumerate(emails, 1):
        print(f"\n{i}. {email['subject']}")
        print(f"   From: {email['sender']}")
        print(f"   Date: {email['date']}")
        print(f"   Snippet: {email['snippet'][:80]}...")
    print()
    
    # Step 5: Parse first email
    print("Step 5: Parsing first email for trading data...")
    print("-" * 70)
    first_email = emails[0]
    print(f"Parsing: {first_email['subject']}")
    print()
    
    parsed_data = parse_trading_email(first_email['body'])
    
    # Display parsed results
    print("📊 Parsed Results:")
    print()
    
    if parsed_data['symbols']:
        print(f"Symbols Found ({len(parsed_data['symbols'])}):")
        for symbol in parsed_data['symbols']:
            print(f"  • ${symbol}")
        print()
    else:
        print("  No symbols found")
        print()
    
    if parsed_data['levels']:
        print(f"Price Levels Extracted ({len(parsed_data['levels'])}):")
        for level in parsed_data['levels']:
            print(f"  • ${level['symbol']} - {level['type']} @ ${level['price']:.2f}")
            if level.get('notes'):
                print(f"    Note: {level['notes']}")
        print()
    else:
        print("  No price levels found")
        print()
    
    if parsed_data['notes']:
        print("Strategic Notes:")
        for line in parsed_data['notes'].split('\n'):
            print(f"  {line}")
        print()
    
    # Step 6: Demonstrate database integration
    print("Step 6: Database Integration Example...")
    print("-" * 70)
    print("In the Flask app, parsed levels are automatically saved to the database:")
    print()
    print("  from models import db, PriceLevel")
    print("  for level_data in parsed_data['levels']:")
    print("      level = PriceLevel(")
    print("          symbol=level_data['symbol'],")
    print("          level_type=level_data['type'],")
    print("          price=level_data['price'],")
    print("          notes=level_data.get('notes', '')")
    print("      )")
    print("      db.session.add(level)")
    print("  db.session.commit()")
    print()
    
    # Summary
    print("=" * 70)
    print("✅ Workflow Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Start the Flask app: python app.py")
    print("2. Navigate to: http://localhost:5000/email-parser")
    print("3. Click 'Fetch from Gmail' to automatically fetch and parse emails")
    print("4. Or use 'Manual Parse' to paste email content directly")
    print()
    print("All parsed data is saved to the database and viewable at:")
    print("  • Dashboard: Overview of recent activity")
    print("  • Price Levels: All extracted price levels")
    print("  • Alerts: Set price alerts for key levels")
    print()


def demo_custom_search():
    """Demonstrate custom email search"""
    print("\n" + "=" * 70)
    print("Bonus: Custom Email Search")
    print("=" * 70)
    print()
    
    client = get_gmail_client()
    
    if not client.authenticate():
        print("Authentication required")
        return
    
    # Example: Search for emails from a specific sender
    print("Example: Search for emails with 'trading' in subject...")
    results = client.search_emails("subject:trading", max_results=3)
    
    print(f"Found {len(results)} emails")
    for i, email in enumerate(results, 1):
        print(f"{i}. {email['subject']}")
    print()


if __name__ == '__main__':
    try:
        main()
        
        # Uncomment to see custom search demo
        # demo_custom_search()
        
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
