"""Gmail API client for fetching and analyzing emails"""
import os
import pickle
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.pickle
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    """Client for interacting with Gmail API"""
    
    def __init__(self, credentials_path: str = 'credentials.json', 
                 token_path: str = 'token.pickle',
                 user_email: str = 'tli.strategy.app@gmail.com'):
        """
        Initialize Gmail client
        
        Args:
            credentials_path: Path to credentials.json from Google Cloud Console
            token_path: Path to store OAuth token
            user_email: Gmail account to connect to
        """
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.user_email = user_email
        self.service = None
        self.creds = None
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail API using OAuth 2.0
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        creds = None
        
        # Check if token file exists
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    # If refresh fails, delete token and re-authenticate
                    if os.path.exists(self.token_path):
                        os.remove(self.token_path)
                    return False
            else:
                if not os.path.exists(self.credentials_path):
                    print(f"Error: credentials.json not found at {self.credentials_path}")
                    print("Please download credentials.json from Google Cloud Console")
                    print("See GMAIL_SETUP.md for instructions")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during OAuth flow: {e}")
                    return False
            
            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        self.creds = creds
        
        try:
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except HttpError as error:
            print(f'An error occurred building Gmail service: {error}')
            return False
    
    def get_forwarded_emails(self, max_results: int = 10, 
                            days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Fetch forwarded emails from Gmail
        
        Args:
            max_results: Maximum number of emails to fetch
            days_back: Number of days to look back
        
        Returns:
            List of email dictionaries with parsed content
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            # Calculate date for query (format: YYYY/MM/DD)
            date_from = datetime.now() - timedelta(days=days_back)
            date_str = date_from.strftime('%Y/%m/%d')
            
            # Query for forwarded emails
            # Search for emails with "Fwd:" in subject or forwarded flag
            query = f'after:{date_str} (subject:Fwd OR subject:FW)'
            
            # Call the Gmail API
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            if not messages:
                print('No forwarded emails found.')
                return []
            
            # Fetch full message details
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'An error occurred fetching emails: {error}')
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get full details of a specific email
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Dictionary with email details or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract headers
            headers = message['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract body
            body = self._get_message_body(message['payload'])
            
            # Get internal date (Unix timestamp in milliseconds)
            internal_date = int(message['internalDate']) / 1000
            received_date = datetime.fromtimestamp(internal_date)
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date_str,
                'received_date': received_date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', [])
            }
            
        except HttpError as error:
            print(f'An error occurred getting email details: {error}')
            return None
    
    def _get_message_body(self, payload: Dict[str, Any]) -> str:
        """
        Extract message body from email payload
        
        Args:
            payload: Email payload from Gmail API
        
        Returns:
            Decoded message body
        """
        body = ''
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body += base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                elif part['mimeType'] == 'text/html':
                    # If no plain text, use HTML as fallback
                    if not body and 'data' in part['body']:
                        body += base64.urlsafe_b64decode(
                            part['body']['data']).decode('utf-8')
                elif 'parts' in part:
                    # Nested parts (recursive)
                    body += self._get_message_body(part)
        else:
            # Single part message
            if 'data' in payload.get('body', {}):
                body = base64.urlsafe_b64decode(
                    payload['body']['data']).decode('utf-8')
        
        return body
    
    def search_emails(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search emails with custom query
        
        Args:
            query: Gmail search query (e.g., "from:example@gmail.com subject:trading")
            max_results: Maximum number of results
        
        Returns:
            List of email dictionaries
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for message in messages:
                email_data = self._get_email_details(message['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            print(f'An error occurred searching emails: {error}')
            return []
    
    def get_email_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific email by its message ID
        
        Args:
            message_id: Gmail message ID
        
        Returns:
            Email dictionary or None
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        return self._get_email_details(message_id)
    
    def test_connection(self) -> bool:
        """
        Test Gmail API connection
        
        Returns:
            bool: True if connection successful
        """
        if not self.service:
            if not self.authenticate():
                return False
        
        try:
            # Try to get user profile to test connection
            profile = self.service.users().getProfile(userId='me').execute()
            print(f"Successfully connected to Gmail account: {profile['emailAddress']}")
            print(f"Total messages: {profile.get('messagesTotal', 'N/A')}")
            return True
        except HttpError as error:
            print(f'Connection test failed: {error}')
            return False


def get_gmail_client() -> GmailClient:
    """
    Create and return a configured Gmail client using environment variables
    
    Returns:
        GmailClient instance
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    credentials_path = os.getenv('GMAIL_CREDENTIALS_PATH', 'credentials.json')
    token_path = os.getenv('GMAIL_TOKEN_PATH', 'token.pickle')
    user_email = os.getenv('GMAIL_USER_EMAIL', 'tli.strategy.app@gmail.com')
    
    return GmailClient(
        credentials_path=credentials_path,
        token_path=token_path,
        user_email=user_email
    )


if __name__ == '__main__':
    """Test the Gmail client"""
    print("Testing Gmail API connection...")
    print("-" * 50)
    
    client = get_gmail_client()
    
    # Test authentication and connection
    if client.test_connection():
        print("\n✅ Gmail API connection successful!")
        print("\nFetching recent forwarded emails...")
        print("-" * 50)
        
        emails = client.get_forwarded_emails(max_results=5, days_back=30)
        
        print(f"\nFound {len(emails)} forwarded emails:")
        for i, email in enumerate(emails, 1):
            print(f"\n{i}. {email['subject']}")
            print(f"   From: {email['sender']}")
            print(f"   Date: {email['date']}")
            print(f"   Snippet: {email['snippet'][:100]}...")
    else:
        print("\n❌ Gmail API connection failed")
        print("Please check your credentials and try again")
