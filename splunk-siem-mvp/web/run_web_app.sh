#!/bin/bash

# Splunk SIEM Web Application - Startup Script

echo "════════════════════════════════════════════════════════════════"
echo "   🛡️  SPLUNK SIEM WEB APPLICATION - STARTUP"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if in correct directory
if [ ! -f "backend/app.py" ]; then
    echo "❌ Error: Please run this script from the 'web' directory"
    echo "   cd splunk-siem-mvp/web"
    echo "   ./run_web_app.sh"
    exit 1
fi

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -q -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "⚠️  Some dependencies may have failed to install"
fi

# Start the web application
echo ""
echo "════════════════════════════════════════════════════════════════"
echo "   🚀 STARTING WEB SERVER"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "   🌐 Web Interface: http://localhost:5000"
echo "   📡 API Endpoint: http://localhost:5000/api"
echo ""
echo "   Press Ctrl+C to stop the server"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

cd backend
python3 app.py
