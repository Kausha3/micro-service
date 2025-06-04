#!/bin/bash

# Lead-to-Lease Chat Concierge Development Script with Visible Logs
# This script runs the backend with visible logs for debugging

set -e

echo "🏠 Lead-to-Lease Chat Concierge - Development with Logs"
echo "======================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Please stop the service using that port."
        return 1
    fi
    return 0
}

# Check if required ports are available
echo "🔍 Checking port availability..."
if ! check_port 8000; then
    echo "Backend port 8000 is in use."
    exit 1
fi

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "✅ Backend setup complete!"
echo ""
echo "🚀 Starting backend server with visible logs..."
echo "📋 All application logs will be displayed below"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Email Configuration Status:"
echo "   SMTP_EMAIL: $(grep SMTP_EMAIL .env | cut -d'=' -f2)"
echo "   SMTP_SERVER: $(grep SMTP_SERVER .env | cut -d'=' -f2)"
echo ""
echo "🛑 To stop the server, press Ctrl+C"
echo "=" * 60

# Start backend with visible logs
uvicorn main:app --reload --port 8000 --log-level info
