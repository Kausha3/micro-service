#!/bin/bash

# Lead-to-Lease Chat Concierge Development Script
# This script helps you run the application in development mode

set -e

echo "🏠 Lead-to-Lease Chat Concierge - Development Setup"
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ and try again."
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

if ! check_port 3000; then
    echo "Frontend port 3000 is in use."
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

# Start backend in background
echo "🚀 Starting backend server on http://localhost:8000..."
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Go back to root directory
cd ..

# Setup frontend
echo "⚛️  Setting up frontend..."
cd frontend

# Install dependencies
echo "Installing Node.js dependencies..."
npm install

# Start frontend in background
echo "🚀 Starting frontend server on http://localhost:3000..."
npm run dev &
FRONTEND_PID=$!

# Go back to root directory
cd ..

echo ""
echo "✅ Application is starting up!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Make sure to set up your environment variables:"
echo "   - Copy .env.example to .env"
echo "   - Configure your Gmail SMTP settings"
echo ""
echo "🛑 To stop the servers, press Ctrl+C"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "✅ Servers stopped."
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop the script
wait
