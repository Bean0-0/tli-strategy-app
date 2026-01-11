# Share Your TLI Stock Evaluation Dashboard

## 🔗 Your Shareable Link

Your app is currently running on port 5000. To share it with others:

### Quick Share URL:
```
https://didactic-halibut-9wv6gr7r4vqh7g6q-5000.app.github.dev
```

## 📋 How to Share the App

### Option 1: Make Port Public (Recommended)
1. In VS Code, go to the **PORTS** tab (bottom panel)
2. Find port **5000** in the list
3. Right-click on port 5000
4. Select **"Port Visibility"** → **"Public"**
5. Share the URL above with anyone!

### Option 2: Share with GitHub Users Only
- By default, the port is visible to GitHub authenticated users
- They'll need to be signed into GitHub to access it
- This is more secure but requires authentication

## 🔐 Security Notes

⚠️ **Important**: When making the port public, anyone with the link can access your app!

**Before sharing publicly:**
1. ✅ Make sure you're not exposing sensitive data
2. ✅ Consider adding authentication requirements
3. ✅ Review what data is visible in the dashboard
4. ✅ Remember this is a development server (not production-ready)

**Current Security:**
- ✅ User authentication required (login/register)
- ✅ Users can only see their own stock evaluations
- ✅ Each user has isolated data

## 👥 For Your Users

When sharing the link, tell them:

1. **Go to the URL**: `https://didactic-halibut-9wv6gr7r4vqh7g6q-5000.app.github.dev`

2. **Register an account**:
   - Click "Register"
   - Enter their email address
   - Create a password
   - They'll be automatically logged in

3. **Start using the dashboard**:
   - Go to "Email Parser" to add TLI email data
   - View analyzed stocks on the Dashboard
   - Click "Details" for comprehensive analysis

## 🚀 Alternative: Deploy for Production

For a more permanent solution, consider deploying to:

### Heroku (Easy)
```bash
# Install Heroku CLI, then:
heroku create your-tli-dashboard
git push heroku main
heroku open
```

### Railway (Very Easy)
1. Go to railway.app
2. Click "Start a New Project"
3. Connect your GitHub repo
4. Railway auto-deploys!

### Render (Free Tier Available)
1. Go to render.com
2. Create "New Web Service"
3. Connect GitHub repo
4. Auto-deploys on push

### DigitalOcean App Platform
1. Go to DigitalOcean
2. Create new "App"
3. Connect GitHub
4. Configure and deploy

## 🔄 Keeping the App Running

**In Codespaces:**
- The app stops when you close the Codespace
- Restart with: `python app.py`
- Codespaces sleep after inactivity

**For Production:**
Use a proper WSGI server instead of Flask's dev server:

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📧 Sharing Instructions Template

Copy/paste this to send to users:

---

**TLI Stock Evaluation Dashboard Access**

I've set up a stock analysis dashboard that combines TLI insights with real-time market data!

**Access the dashboard:**
https://didactic-halibut-9wv6gr7r4vqh7g6q-5000.app.github.dev

**Getting Started:**
1. Click "Register" to create an account
2. Log in with your credentials
3. Go to "Email Parser" to add TLI email data
4. View the dashboard for AI-powered stock analysis

**Features:**
- 📊 Automated stock evaluation (Buy/Sell/Hold)
- 📈 Real-time market data integration
- ⚖️ Cross-validation with technical indicators
- ⚠️ Automated risk warnings and flags
- 📱 Mobile-responsive design

Let me know if you have any questions!

---

## 🛠️ Troubleshooting

**Link not working?**
- Check if port 5000 is set to "Public" in the PORTS tab
- Restart the Flask app: `python app.py`
- Verify the Codespace is still running

**Users can't register?**
- Make sure the database is initialized: `python init_db.py`
- Check Flask logs for errors

**Need to reset?**
- Delete the database: `rm instance/trading.db`
- Reinitialize: `python init_db.py`
- Reprocess data: `python process_existing_data.py`

## 📝 Notes

- **Codespace URL**: Your current Codespace is `didactic-halibut-9wv6gr7r4vqh7g6q`
- **Port**: App runs on port 5000
- **Access**: Currently requires port to be made public
- **Users**: Each user gets their own isolated data
- **Data**: User data persists in SQLite database at `instance/trading.db`

---

**Ready to share?** Just make port 5000 public and send the URL! 🚀
