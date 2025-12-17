#!/bin/bash
# Local Debug Script for Dental Trawler

echo "🔍 Dental Trawler - Local Debug Setup"
echo "======================================"
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo ""
    echo "Please install Node.js first:"
    echo "  sudo apt update"
    echo "  sudo apt install nodejs npm"
    echo ""
    echo "Or use nvm (recommended):"
    echo "  curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash"
    echo "  source ~/.bashrc"
    echo "  nvm install --lts"
    echo ""
    exit 1
fi

echo "✅ Node.js version: $(node --version)"
echo "✅ npm version: $(npm --version)"
echo ""

# Navigate to frontend directory
cd "$(dirname "$0")/dentaltrawler" || exit 1

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🚀 Starting development server..."
echo "   The app will be available at: http://localhost:5173"
echo "   Press Ctrl+C to stop"
echo ""

npm run dev

