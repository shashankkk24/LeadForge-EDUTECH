#!/bin/bash
# LeadForge EDU - Quick Setup Guide
# This script guides you through setting up all integrations

echo "🚀 LeadForge EDU - Integration Setup"
echo "===================================="
echo ""

# Step 1: Python Dependencies
echo "📦 Step 1: Installing Python dependencies..."
cd backend

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python -m venv venv
    
    if [ "$OSTYPE" == "msys" ] || [ "$OSTYPE" == "cygwin" ]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Install all dependencies
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Step 2: Environment Configuration
echo "🔐 Step 2: Setting up .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ Created .env from .env.example"
    echo "⚠️  IMPORTANT: Edit .env with your actual credentials"
else
    echo "✓ .env already exists"
fi
echo ""

# Step 3: Database Setup
echo "🗄️  Step 3: Database setup..."
echo "ℹ️  Update DATABASE_URL in .env to your Neon PostgreSQL"
echo "   Current: $(grep DATABASE_URL .env | cut -d'=' -f2)"
echo ""

# Step 4: Credentials Setup
echo "🔑 Step 4: Setting up credentials..."
echo ""
echo "📧 SMTP (Email) - For sending outreach emails:"
echo "   1. Go to https://myaccount.google.com/apppasswords"
echo "   2. Generate an App Password"
echo "   3. Add to .env:"
echo "      SMTP_USER=your_email@gmail.com"
echo "      SMTP_PASSWORD=your_app_password_here"
echo ""

echo "🔗 LinkedIn - For scraping LinkedIn:"
echo "   1. Add your LinkedIn credentials to .env:"
echo "      LINKEDIN_EMAIL=your_email@linkedin.com"
echo "      LINKEDIN_PASSWORD=your_password"
echo "   2. Optional: Get official API token from LinkedIn Dev Portal"
echo ""

echo "🤖 Apify - For distributed web scraping:"
echo "   1. Go to https://apify.com"
echo "   2. Sign up and get free $5 monthly credit"
echo "   3. Get API token from https://console.apify.com/account/integrations"
echo "   4. Add to .env:"
echo "      APIFY_API_TOKEN=your_token"
echo "      APIFY_ACTOR_ID=jbMR8dEWC5OmBWHJh  # Google Search"
echo ""

echo "📱 Reddit (PRAW) - For Reddit scraping:"
echo "   1. Go to https://www.reddit.com/prefs/apps"
echo "   2. Create a new 'script' app"
echo "   3. Add to .env:"
echo "      REDDIT_CLIENT_ID=your_id"
echo "      REDDIT_CLIENT_SECRET=your_secret"
echo ""

echo "✨ Gemini API - For AI-powered message generation:"
echo "   Your Gemini API Key:"
echo "   GEMINI_API_KEY=AIzaSyAtvoCvIvEwbKJFqNmiMbegs2sPPHtLrUk"
echo ""

# Step 5: Browser Setup
echo "🌐 Step 5: Browser automation (Selenium/Playwright)..."
echo "   Automatic: webdriver-manager will auto-download Chrome/Firefox drivers"
echo "   Manual: Download ChromeDriver from https://chromedriver.chromium.org/"
echo "   Configure in .env:"
echo "      SELENIUM_BROWSER=chrome"
echo "      SELENIUM_HEADLESS=true"
echo "      CHROMEDRIVER_PATH=/path/to/chromedriver"
echo ""

# Step 6: Run tests
echo "🧪 Step 6: Testing setup..."
echo ""
echo "Test SMTP Configuration:"
echo "  python -c \"from services.enhanced_email_service import EnhancedEmailService; \""
echo ""

echo "Test Database:"
echo "  python -c \"from database import engine; import asyncio; asyncio.run(engine.dispose())\""
echo ""

echo "✅ Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update .env with all credentials"
echo "2. Run: python main.py"
echo "3. Frontend: cd ../frontend && npm install && npm run dev"
echo "4. Open: http://localhost:5173"
echo ""
echo "📖 For detailed integration info, see: INTEGRATION_GUIDE.md"
echo ""
