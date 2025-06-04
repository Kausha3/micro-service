# 🛠 Development Guide

This guide provides comprehensive information for developers working on the Lead-to-Lease Chat Concierge project.

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Git

### Automated Setup

```bash
# Clone the repository
git clone <repository-url>
cd lead-to-lease-chat-concierge

# Run automated setup
./scripts/setup-dev-environment.sh
```

## 📁 Project Architecture

### Backend Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── models.py              # Pydantic data models and validation
├── routes.py              # API route definitions
├── chat_service.py        # Core conversation logic
├── email_service.py       # Email notification service
├── inventory_service.py   # Apartment unit management
├── session_db_service.py  # Database operations
├── ai_service.py          # OpenAI integration
├── database.py            # SQLAlchemy models
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Python project configuration
```

### Frontend Structure

```
frontend/
├── src/
│   ├── App.jsx           # Main application component
│   ├── ChatWidget.jsx    # Chat interface component
│   └── main.jsx          # Application entry point
├── package.json          # Node.js dependencies and scripts
├── vite.config.js        # Vite build configuration
├── .eslintrc.cjs         # ESLint configuration
└── .prettierrc.json      # Prettier configuration
```

## 🔧 Development Workflow

### 1. Environment Setup

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### 2. Configuration

Create `backend/.env`:

```bash
# AI Configuration (Required for AI features)
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Email Configuration
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Property Information
PROPERTY_ADDRESS=123 Main St, Anytown, ST 12345
PROPERTY_NAME=Luxury Apartments
LEASING_OFFICE_PHONE=(555) 123-4567

# Application Settings
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### 3. Running the Application

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 🧪 Testing Strategy

### Backend Testing

```bash
cd backend

# Run all tests
pytest -v

# Run with coverage
pytest --cov=. --cov-report=html

# Test AI integration specifically
python test_ai_integration.py

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests

# Run specific test file
pytest test_chat_service.py -v
```

### Frontend Testing

```bash
cd frontend

# Run tests
npm run test

# Interactive test UI
npm run test:ui

# Coverage report
npm run test:coverage
```

## 📝 Code Quality Standards

### Python Standards

- **Formatting**: Black with 88-character line length
- **Import Sorting**: isort with Black profile
- **Linting**: flake8 with custom configuration
- **Type Checking**: mypy for static type analysis
- **Security**: bandit for security vulnerability scanning

### JavaScript Standards

- **Linting**: ESLint with React and accessibility plugins
- **Formatting**: Prettier with consistent configuration
- **Code Style**: Modern ES6+ with React hooks

### Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

## 🔄 Git Workflow

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Individual feature development
- `hotfix/*`: Critical production fixes

### Commit Convention

```bash
# Format: type(scope): description
feat(chat): add multi-unit booking support
fix(email): resolve SMTP timeout issues
docs(readme): update deployment instructions
test(inventory): add unit availability tests
refactor(models): simplify data validation
```

### Pull Request Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run quality checks: `pre-commit run --all-files`
4. Push branch and create PR
5. Ensure CI passes
6. Request code review
7. Merge after approval

## 🐛 Debugging

### Backend Debugging

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG

# Run with debugger
python -m pdb main.py

# Use logging for debugging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

### Frontend Debugging

```bash
# Development mode with hot reload
npm run dev

# Build and preview
npm run build
npm run preview

# Analyze bundle
npm run analyze
```

### Common Issues

1. **Email not sending**: Check SMTP credentials and Gmail app passwords
2. **CORS errors**: Verify FRONTEND_URL in backend .env
3. **Database errors**: Delete conversations.db and restart
4. **Import errors**: Ensure virtual environment is activated

## 📊 Performance Monitoring

### Backend Metrics

- Response time monitoring
- Database query performance
- Email delivery success rates
- Error rate tracking

### Frontend Metrics

- Bundle size analysis
- Component render performance
- User interaction tracking
- Load time optimization

## 🚀 Deployment

### Development Deployment

```bash
# Docker development
docker-compose up --build

# Manual deployment
cd backend && uvicorn main:app --reload
cd frontend && npm run dev
```

### Production Deployment

```bash
# Build production assets
cd frontend && npm run build

# Run production server
cd backend && uvicorn main:app --host 0.0.0.0 --port 8000
```

## 📚 Additional Resources

### Documentation

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://reactjs.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

### Tools

- [Postman Collection](./postman_collection.json) - API testing
- [VS Code Settings](./.vscode/settings.json) - IDE configuration
- [Docker Compose](../docker-compose.yml) - Container orchestration

### Support

- Create GitHub issues for bugs
- Use discussions for questions
- Check existing documentation first
- Follow coding standards and conventions
