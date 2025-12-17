#!/bin/bash
# Setup script for scraping with Selenium

echo "🔧 Setting up scraping environment..."
echo ""

# Check if Chromium/Chrome is installed
if command -v chromium-browser &> /dev/null || command -v chromium &> /dev/null || command -v google-chrome &> /dev/null; then
    echo "✅ Chrome/Chromium is installed"
else
    echo "❌ Chrome/Chromium not found"
    echo ""
    echo "Please install Chromium with:"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install -y chromium-browser"
    echo ""
    exit 1
fi

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing Python dependencies..."
pip install selenium webdriver-manager

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run the scraper:"
echo "  source venv/bin/activate"
echo "  python3 scripts/scrape_with_selenium.py"

