#!/bin/bash

# Development Environment Setup Script for Lead-to-Lease Chat Concierge
# This script sets up the complete development environment with all tools and dependencies

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main setup function
main() {
    print_status "🚀 Setting up Lead-to-Lease Chat Concierge development environment..."

    # Check prerequisites
    print_status "Checking prerequisites..."

    if ! command_exists python3; then
        print_error "Python 3 is required but not installed. Please install Python 3.10+ and try again."
        exit 1
    fi

    if ! command_exists node; then
        print_error "Node.js is required but not installed. Please install Node.js 18+ and try again."
        exit 1
    fi

    if ! command_exists git; then
        print_error "Git is required but not installed. Please install Git and try again."
        exit 1
    fi

    print_success "Prerequisites check passed"

    # Setup backend environment
    print_status "Setting up Python backend environment..."

    cd backend

    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate

    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip

    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt

    # Install development dependencies
    print_status "Installing development dependencies..."
    pip install black isort flake8 mypy bandit pre-commit pytest-cov

    print_success "Backend environment setup complete"

    # Setup frontend environment
    cd ../frontend
    print_status "Setting up Node.js frontend environment..."

    # Install dependencies
    print_status "Installing Node.js dependencies..."
    npm install

    print_success "Frontend environment setup complete"

    # Setup pre-commit hooks
    cd ..
    print_status "Setting up pre-commit hooks..."

    if command_exists pre-commit; then
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "pre-commit not found. Install with: pip install pre-commit"
    fi

    # Create environment file if it doesn't exist
    if [ ! -f "backend/.env" ]; then
        print_status "Creating environment configuration file..."
        cat > backend/.env << EOF
# Lead-to-Lease Chat Concierge Environment Configuration
# Copy this file and update with your actual values

# AI Configuration (Required for AI features)
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Email Configuration (Gmail recommended for development)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Property Information
PROPERTY_ADDRESS=123 Main St, Anytown, ST 12345
PROPERTY_NAME=Luxury Apartments at Main Street
LEASING_OFFICE_PHONE=(555) 123-4567

# AI Configuration (Optional - for enhanced features)
OPENAI_API_KEY=your_openai_api_key_here

# Application Settings
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:3000

# Email Settings
EMAIL_TIMEOUT=30
EOF
        print_warning "Created .env file. Please update with your actual configuration values."
    fi

    # Setup complete
    print_success "🎉 Development environment setup complete!"

    echo ""
    print_status "📋 Next steps:"
    echo "1. Update backend/.env with your configuration"
    echo "2. Start the backend: cd backend && source venv/bin/activate && python main.py"
    echo "3. Start the frontend: cd frontend && npm run dev"
    echo "4. Visit http://localhost:3000 to see the application"
    echo ""
    print_status "🔧 Development commands:"
    echo "• Run tests: cd backend && pytest -v"
    echo "• Test AI integration: cd backend && python test_ai_integration.py"
    echo "• Lint code: pre-commit run --all-files"
    echo "• Format code: cd backend && black . && isort ."
    echo "• Check types: cd backend && mypy ."
    echo ""
    print_status "📚 Documentation:"
    echo "• API docs: http://localhost:8000/docs"
    echo "• Alternative docs: http://localhost:8000/redoc"
    echo "• Health check: http://localhost:8000/"
}

# Run main function
main "$@"
