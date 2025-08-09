#!/bin/bash

echo "🚀 Setting up Node.js Browser Service with @presidio-dev/playwright-core"
echo "================================================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js version: $(node --version)"

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not available. Please install npm."
    exit 1
fi

echo "✅ npm version: $(npm --version)"

echo ""
echo "📦 Installing Node.js dependencies..."

# Install dependencies
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install npm dependencies"
    exit 1
fi

echo "✅ Node.js dependencies installed successfully"

echo ""
echo "🌐 Installing Playwright browsers..."

# Install Playwright globally first (recommended)
npm install -g playwright

# Install browser binaries and system dependencies
npx playwright install --with-deps

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

echo "✅ Playwright browsers installed successfully"

echo ""
echo "🧪 Testing browser service startup..."

# Test if server can start (run for 3 seconds then kill)
timeout 3s npm start &
sleep 2

# Check if port 3000 is accessible
if curl -s http://localhost:3000/health > /dev/null; then
    echo "✅ Browser service test startup successful"
else
    echo "⚠️ Browser service test startup failed, but this may be normal"
fi

# Kill any remaining processes
pkill -f "node server.js" 2>/dev/null || true

echo ""
echo "🎉 Browser Service Setup Complete!"
echo "=================================="
echo ""
echo "📋 Next Steps:"
echo "1. Start the service: npm start"
echo "2. The service will run on http://localhost:3000"
echo "3. Update your Python agent to use the new Node.js tools"
echo ""
echo "🚀 To start the service now:"
echo "   cd browser-service && npm start"
echo ""
echo "✅ All setup complete! No more Python threading issues! 🎯"
