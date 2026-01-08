# Testing Guide for OAuth Login System

This document provides instructions for testing the newly implemented Google OAuth login system.

## Prerequisites for Testing

1. **Google Cloud Platform Setup Required**:
   - You need to create OAuth credentials in Google Cloud Console
   - Follow the complete setup guide in [OAUTH_SETUP.md](OAUTH_SETUP.md)
   - You'll need:
     - `GOOGLE_CLIENT_ID`
     - `GOOGLE_CLIENT_SECRET`

2. **Environment Configuration**:
   - Copy `.env.example` to `.env`
   - Fill in your Google OAuth credentials
   - Generate a secure `SECRET_KEY`

## Quick Start Testing

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your OAuth credentials
```

### 3. Start the Application

```bash
python app.py
```

### 4. Access the Application

Open your browser to: `http://localhost:5000`

You should be redirected to the login page.

## Test Scenarios

### Test 1: Login Flow

**Steps:**
1. Navigate to `http://localhost:5000`
2. Click "Sign in with Google"
3. Choose your Google account
4. Review and grant permissions:
   - View email address and profile
   - Read Gmail messages
5. You should be redirected to the dashboard

**Expected Results:**
- ✓ Redirected to Google OAuth page
- ✓ Successfully authenticated
- ✓ User record created in database
- ✓ OAuth tokens stored
- ✓ Redirected to dashboard
- ✓ User name displayed in navigation
- ✓ Logout button visible

### Test 2: User Data Isolation

**Steps:**
1. Log in as User A
2. Create a position (e.g., AMD, $100, 10 shares)
3. Create an alert (e.g., AMD @ $105)
4. Add a comment
5. Log out
6. Log in as User B (different Google account)
7. Check positions, alerts, and comments

**Expected Results:**
- ✓ User B sees empty dashboard
- ✓ User B cannot see User A's data
- ✓ User B can create their own data
- ✓ Log back in as User A and verify data is still there

### Test 3: Gmail Integration

**Steps:**
1. Log in with a Google account
2. Navigate to Email Parser
3. Click "Fetch from Gmail"
4. Select an email
5. Click "Parse Selected"

**Expected Results:**
- ✓ Emails fetched using user's OAuth token
- ✓ Email content parsed correctly
- ✓ Price levels saved to user's account
- ✓ Data visible in Price Levels page

### Test 4: Session Persistence

**Steps:**
1. Log in successfully
2. Close browser
3. Reopen browser
4. Navigate to `http://localhost:5000`

**Expected Results:**
- ✓ Still logged in (session persists)
- ✓ Can access protected pages without re-authenticating

### Test 5: Logout

**Steps:**
1. Log in successfully
2. Click "Logout" button
3. Try to access `http://localhost:5000/positions` directly

**Expected Results:**
- ✓ Logged out successfully
- ✓ Redirected to login page
- ✓ Cannot access protected pages
- ✓ Must log in again to access application

### Test 6: Token Refresh

**Steps:**
1. Log in successfully
2. Wait for token to expire (or manually set short expiry in code)
3. Use Gmail integration feature

**Expected Results:**
- ✓ Token automatically refreshed
- ✓ Gmail access still works
- ✓ No re-authentication required

### Test 7: Error Handling

**Test 7.1: Invalid OAuth Credentials**
- Set incorrect `GOOGLE_CLIENT_ID` in `.env`
- Try to log in
- Expected: Error message displayed

**Test 7.2: Missing Gmail Permissions**
- Remove Gmail scope from OAuth consent screen
- Try to fetch emails
- Expected: Appropriate error message

**Test 7.3: Database Error**
- Manually corrupt database
- Try to access application
- Expected: Graceful error handling

## Manual Testing Checklist

- [ ] Login with Google works
- [ ] User profile information displayed correctly
- [ ] Logout functionality works
- [ ] Positions are user-specific
- [ ] Alerts are user-specific
- [ ] Price levels are user-specific
- [ ] Comments are user-specific
- [ ] Gmail integration uses user's credentials
- [ ] Multiple users can use app simultaneously
- [ ] Session persists across browser restarts
- [ ] Protected routes require authentication
- [ ] Unauthenticated users redirected to login
- [ ] OAuth tokens stored securely
- [ ] Token refresh works automatically
- [ ] Error messages are user-friendly
- [ ] No sensitive data exposed in logs

## Database Verification

### Check User Records

```bash
sqlite3 trading.db "SELECT id, email, name, created_at FROM user;"
```

### Check User-Data Relationships

```bash
# Positions by user
sqlite3 trading.db "SELECT u.email, COUNT(p.id) as positions FROM user u LEFT JOIN position p ON u.id = p.user_id GROUP BY u.id;"

# Alerts by user
sqlite3 trading.db "SELECT u.email, COUNT(a.id) as alerts FROM user u LEFT JOIN alert a ON u.id = a.user_id GROUP BY u.id;"
```

## Security Testing

### Test 1: SQL Injection Prevention
- Try entering `' OR '1'='1` in various input fields
- Expected: Input properly escaped, no SQL injection

### Test 2: XSS Prevention
- Try entering `<script>alert('xss')</script>` in text fields
- Expected: Script not executed, properly escaped

### Test 3: CSRF Protection
- Try making requests without CSRF token
- Expected: Requests rejected (Flask has built-in CSRF protection)

### Test 4: Token Security
- Check that `.env` is not committed to Git
- Check that tokens are not logged
- Check that database file has appropriate permissions

## Performance Testing

### Test 1: Concurrent Users
- Open multiple browsers/incognito windows
- Log in as different users
- Perform operations simultaneously
- Expected: No conflicts, each user's data isolated

### Test 2: Large Dataset
- Create 100+ positions for a user
- Navigate through pages
- Expected: Reasonable load times, no crashes

## Troubleshooting

### Problem: Cannot log in

**Check:**
1. OAuth credentials in `.env` are correct
2. Redirect URI in Google Cloud Console matches
3. Gmail API is enabled
4. User is added as test user (for external apps)

### Problem: Gmail integration not working

**Check:**
1. Gmail API enabled in Google Cloud Console
2. Gmail scope included in OAuth consent screen
3. User granted Gmail permissions during login
4. OAuth tokens are stored in user record

### Problem: Database errors

**Check:**
1. Database file exists and is writable
2. Schema is up to date
3. No orphaned records (positions without users)

## Success Criteria

The OAuth login system is working correctly if:

✅ Users can log in with Google accounts  
✅ User data is completely isolated  
✅ Gmail integration works with user's credentials  
✅ Sessions persist appropriately  
✅ Logout works correctly  
✅ Protected routes are secured  
✅ OAuth tokens are stored and refreshed automatically  
✅ No security vulnerabilities  
✅ Error handling is graceful  
✅ Multiple users can use the app simultaneously

## Next Steps

After successful testing:

1. **Production Deployment**:
   - Use production Google Cloud project
   - Enable HTTPS (required for OAuth)
   - Set production redirect URI
   - Use secure secret keys
   - Enable database backups

2. **Monitoring**:
   - Set up logging
   - Monitor OAuth token refresh rates
   - Track login/logout events
   - Monitor database growth

3. **Documentation**:
   - Update user manual
   - Create deployment guide
   - Document common issues

## Support

For issues:
- Check [OAUTH_SETUP.md](OAUTH_SETUP.md) for setup help
- Review this testing guide for test procedures
- Check application logs for errors
- Verify Google Cloud Console configuration

## Automated Testing

While manual testing is important, consider adding automated tests:

```python
# Example test structure
def test_login_required():
    """Test that protected routes require authentication"""
    with app.test_client() as client:
        response = client.get('/')
        assert response.status_code == 302  # Redirect to login

def test_user_data_isolation():
    """Test that users can only see their own data"""
    # Create two users
    # Add data for each
    # Verify isolation
```

## Conclusion

The OAuth login system provides:
- Secure authentication
- User-specific data isolation
- Automatic Gmail integration
- Professional user experience

Follow this testing guide to ensure everything works correctly before deployment.
