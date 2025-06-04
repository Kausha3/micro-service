# 🏠 Lead-to-Lease Chat Concierge

> **Production-Ready Intelligent Chat Microservice for Apartment Leasing**

A FastAPI-based microservice that automates lead qualification and tour booking through natural language conversation. Features intelligent conversation flow, real-time inventory management, email notifications, and comprehensive session persistence.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

---

## ✨ **Key Features**

### 🤖 **AI-Powered Conversation Intelligence**

- **OpenAI GPT Integration**: Advanced natural language understanding using GPT-3.5-turbo/GPT-4
- **Contextual Conversations**: Maintains conversation history and context throughout sessions
- **Intelligent Intent Detection**: Automatically understands user goals (searching, booking, inquiring)
- **Smart Data Extraction**: Naturally collects name, email, phone, move-in date, and preferences
- **Fuzzy Date Parsing**: Accepts natural language dates like "January 2024", "next month", "ASAP"
- **Dynamic Response Generation**: AI responses based on real-time inventory and user context
- **Graceful Fallback**: Maintains functionality even when AI services are unavailable

### 🏢 **Advanced Inventory System**

- **Realistic Simulation**: 15% unavailability rate to demonstrate real-world scenarios
- **Diverse Unit Portfolio**: Studio through 4-bedroom apartments with market-rate pricing
- **Smart Alternatives**: Offers other options when preferred units aren't available
- **Automatic Reservation**: Reserves units immediately after tour confirmation
- **Comprehensive Details**: Square footage, bathrooms, rent, and availability status

### 📧 **Professional Email Notifications**

- **Beautiful HTML Templates**: Mobile-responsive tour confirmations with property branding
- **Complete Information**: Tour date/time, property address, contact information
- **Helpful Guidance**: What to bring checklist (ID, income proof, application fee)
- **Graceful Fallback**: Works seamlessly with or without email configuration
- **Production Ready**: Supports Gmail, Outlook, and professional email services

### 💾 **Enterprise-Grade Persistence**

- **SQLite Database**: Reliable conversation storage with full message history
- **Session Continuity**: Maintains context across page refreshes and browser sessions
- **Data Validation**: Comprehensive input validation with user-friendly error messages
- **Audit Trail**: Complete conversation tracking for compliance and analytics

---

## 🏗️ **Architecture Overview**

```text
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  SQLite Database │
│                 │◄──►│                 │◄──►│                 │
│  - Chat Widget  │    │  - AI Service   │    │  - Sessions     │
│  - Real-time UI │    │  - Chat Service │    │  - Messages     │
│  - Responsive   │    │  - Email Service│    │  - AI Context   │
└─────────────────┘    │  - Inventory    │    │  - Prospect Data│
                       └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  OpenAI GPT API │    │  Email Service  │
                       │                 │    │                 │
                       │  - GPT-3.5/4    │    │  - SMTP Support │
                       │  - Context Mgmt │    │  - HTML Templates│
                       │  - Intent Detection│  │  - Fallback Mode│
                       └─────────────────┘    └─────────────────┘
```

---

## 🚀 **Quick Start**

### **Prerequisites**

- Python 3.10+
- Node.js 18+
- npm or yarn
- Docker (optional)

### **Option 1: Docker Compose (Recommended)**

```bash
git clone <your-repo-url>
cd micro-service

# Start in production mode
docker-compose up

# Start in development mode with hot reload
docker-compose --profile dev up
```

### **Option 2: Manual Setup**

#### **Backend Setup**

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start server
uvicorn main:app --reload --port 8000
```

#### **Frontend Setup**

```bash
cd frontend
npm install
npm run dev
```

---

## 📁 **Project Structure**

```text
micro-service/
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── models.py           # Pydantic data models
│   ├── chat_service.py     # Conversation logic
│   ├── email_service.py    # Email notifications
│   ├── inventory_service.py # Unit management
│   ├── session_db_service.py # Database operations
│   ├── database.py         # Database models
│   ├── requirements.txt    # Python dependencies
│   └── .env.example       # Environment template
├── frontend/               # React frontend
│   ├── src/
│   │   ├── App.jsx        # Main application
│   │   └── ChatWidget.jsx # Chat interface
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Build configuration
├── docker-compose.yml     # Container orchestration
├── Dockerfile            # Production container
└── README.md            # This file
```

---

## ⚙️ **Configuration**

### **Environment Variables**

Create a `.env` file in the `backend` directory:

```bash
# AI Configuration (Required for AI features)
OPENAI_API_KEY=your_actual_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo  # Options: gpt-3.5-turbo, gpt-4, gpt-4-turbo-preview

# Email Configuration (Gmail recommended for testing)
SMTP_EMAIL=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587

# Property Information
PROPERTY_ADDRESS=123 Main St, Anytown, ST 12345
PROPERTY_NAME=Luxury Apartments at Main Street
LEASING_OFFICE_PHONE=(555) 123-4567

# Application Settings
ENVIRONMENT=development
PORT=8000
FRONTEND_URL=http://localhost:3000
```

### **AI Setup (Required for Full Features)**

1. **Get OpenAI API Key**: Visit [OpenAI's website](https://platform.openai.com/api-keys)
2. **Add to Environment**: Set `OPENAI_API_KEY` in your `.env` file
3. **Choose Model**: Select between `gpt-3.5-turbo` (faster, cheaper) or `gpt-4` (more sophisticated)
4. **Test Integration**: Run `python backend/test_openai_connection.py` to verify your setup

**Note**: The application gracefully falls back to helpful responses if AI is unavailable.

### **Email Setup (Optional)**

For Gmail:

1. Enable 2-Factor Authentication
2. Generate an App Password: [Google Account Settings](https://myaccount.google.com/) → Security → App passwords
3. Use the 16-character app password in your `.env` file

**Note**: The application works perfectly without email configuration in demo mode.

---

## 🧠 **AI Features Deep Dive**

### **Natural Language Conversation**

The AI system understands natural language queries and responds contextually:

```text
User: "Hi, I'm looking for an apartment"
AI: "Hello! I'd be happy to help you find the perfect apartment.
     What type of place are you looking for?"

User: "Something with 2 bedrooms under $2500"
AI: "Great! I have several 2-bedroom units that might interest you.
     We have Unit B301 (950 sq ft, $2400/month) and Unit B604
     (975 sq ft, $2450/month). Would you like to know more about
     either of these?"

User: "Tell me about B301"
AI: "Unit B301 is a lovely 2-bedroom, 2-bathroom apartment with
     950 square feet for $2400/month. It's currently available.
     Would you like to schedule a tour?"
```

### **Intelligent Data Collection**

The AI naturally extracts information without rigid forms:

- **Name, email, phone number**: Collected conversationally
- **Move-in date preferences**: Understands "next month", "ASAP", "January 2024"
- **Bedroom requirements**: Recognizes "studio", "1-bed", "two bedroom"
- **Budget considerations**: Understands "under $2000", "around $2500"

### **Context-Aware Responses**

- **Conversation Memory**: Remembers previous discussion points
- **Inventory Integration**: Responses include real-time availability and pricing
- **Intent Recognition**: Automatically detects booking, searching, or inquiry intents
- **Personalization**: Tailors responses based on user preferences

### **AI Configuration Options**

```bash
# Model Selection
OPENAI_MODEL=gpt-3.5-turbo      # Fast, cost-effective
OPENAI_MODEL=gpt-4              # More sophisticated responses
OPENAI_MODEL=gpt-4-turbo-preview # Latest capabilities

# Performance Tuning
AI_TEMPERATURE=0.7              # Response creativity (0.0-1.0)
AI_MAX_TOKENS=500              # Response length limit
AI_CONTEXT_LIMIT=10            # Conversation history limit
```

### **AI Setup and Testing**

#### **Quick AI Integration Test**

```bash
cd backend
python test_ai_integration.py
```

This tests:
- AI service initialization
- Conversation scenarios with mocked responses
- Inventory context integration
- Error handling and fallback behavior

#### **Manual Testing Scenarios**

1. **Property Search**: "What apartments do you have?"
2. **Specific Requirements**: "I need a 3-bedroom with parking"
3. **Budget Inquiries**: "What's your cheapest unit?"
4. **Booking Flow**: "I want to schedule a tour"
5. **Edge Cases**: Unclear or ambiguous requests

### **AI Troubleshooting**

#### **Common Issues**

1. **AI Not Responding**
   - Check OpenAI API key in `.env`
   - Verify internet connection and API quota/billing
   - Test key at [OpenAI Playground](https://platform.openai.com/playground)

2. **Import Errors**
   - Ensure dependencies installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.10+)

3. **Performance Issues**
   - AI responses typically take 1-3 seconds
   - Uses efficient prompt engineering and context limiting
   - Configurable model selection for cost optimization

#### **Fallback Behavior**

If AI is unavailable, the system:
- Gracefully falls back to helpful responses
- Maintains core booking functionality
- Provides clear error messages to users

---

### **Render Deployment (Recommended)**

The application is ready for deployment on Render with automatic configuration detection.

#### **Backend Deployment**

1. **Create Web Service**: Create a new Web Service on Render
2. **Connect Repository**: Connect your GitHub repository
3. **Configure Build Settings**:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**:
   ```bash
   # AI Configuration (Required)
   OPENAI_API_KEY=your_actual_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   OPENAI_TIMEOUT=60.0
   OPENAI_MAX_RETRIES=3

   # Email Configuration
   SMTP_EMAIL=your-email@gmail.com
   SMTP_PASSWORD=your-16-character-app-password

   # Property Information
   PROPERTY_ADDRESS=123 Main St, Anytown, ST 12345
   PROPERTY_NAME=Luxury Apartments at Main Street
   LEASING_OFFICE_PHONE=(555) 123-4567

   # Application Settings
   FRONTEND_URL=https://your-frontend-url.onrender.com
   ```

#### **Frontend Deployment**

1. **Create Static Site**: Create a new Static Site on Render
2. **Configure Build Settings**:
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
3. **Set Environment Variable**:
   - `VITE_API_URL`: Your backend URL from above

#### **Post-Deployment Steps**

1. Update backend's `FRONTEND_URL` environment variable with frontend URL
2. Test the complete chat flow end-to-end
3. Monitor logs for any connection errors

#### **Render Troubleshooting**

**OpenAI Connection Issues:**
- Verify `OPENAI_API_KEY` is set correctly in environment variables
- Test your API key at [OpenAI Playground](https://platform.openai.com/playground)
- Check OpenAI account billing and credit balance
- Set `OPENAI_TIMEOUT=60.0` for better reliability on Render
- Monitor Render logs for specific error messages

**Email Issues:**
- Use Gmail app passwords (not regular password)
- Enable 2-Factor Authentication on Gmail account
- Verify SMTP settings match Gmail requirements

## 🧪 **Testing & Code Quality**

### **Automated Development Setup**

```bash
# Quick setup for new developers
./scripts/setup-dev-environment.sh
```

### **Code Quality Tools**

```bash
# Install pre-commit hooks (runs automatically on commit)
pre-commit install

# Run all quality checks manually
pre-commit run --all-files

# Python code formatting and linting
cd backend
black .                    # Format code
isort .                    # Sort imports
flake8 .                   # Lint code
mypy .                     # Type checking
bandit -r .                # Security scanning

# Frontend code quality
cd frontend
npm run lint               # ESLint
npm run lint:fix           # Auto-fix ESLint issues
npm run format             # Prettier formatting
npm run format:check       # Check formatting
```

### **Backend Tests**

```bash
cd backend
python -m pytest -v

# With coverage
python -m pytest --cov=. --cov-report=html

# Run specific test categories
python -m pytest -m unit          # Unit tests only
python -m pytest -m integration   # Integration tests only
python -m pytest -m "not slow"    # Skip slow tests
```

### **Frontend Tests**

```bash
cd frontend
npm run test               # Run tests
npm run test:ui            # Interactive test UI
npm run test:coverage      # Coverage report
npm run build              # Test build process
```

### **Docker Tests**

```bash
# Test Docker builds locally (recommended before pushing)
./scripts/test-docker-builds.sh

# Validate Docker configuration
docker-compose config

# Run tests in container
docker-compose run backend pytest -v
```

### **Troubleshooting Docker Builds**

If you encounter GitHub Actions cache errors (502 Bad Gateway), see our comprehensive [Docker Troubleshooting Guide](docs/DOCKER_TROUBLESHOOTING.md).

**Quick fixes:**

- Use the no-cache workflow: `.github/workflows/ci-no-cache.yml`
- Test builds locally: `./scripts/test-docker-builds.sh`
- Check [GitHub Status](https://www.githubstatus.com/) for service issues

---

## 📊 **API Documentation**

Once running, visit:

- **Interactive API Docs**: <http://localhost:8000/docs>
- **Alternative Docs**: <http://localhost:8000/redoc>
- **Health Check**: <http://localhost:8000/>

### **Key Endpoints**

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check and API information |
| `/chat` | POST | Main chat processing endpoint |
| `/inventory` | GET | Current unit availability |
| `/sessions/{id}` | GET | Session details and history |

---

## 🚀 **Deployment**

### **Production Deployment**

1. **Environment Setup**:

   ```bash
   export ENVIRONMENT=production
   export FRONTEND_URL=https://your-domain.com
   ```

2. **Docker Production**:

   ```bash
   docker-compose -f docker-compose.yml up -d
   ```

3. **Manual Production**:

   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000

   # Frontend
   cd frontend
   npm run build
   # Serve dist/ with nginx or similar
   ```

## ⚖️ Trade-offs & Design Decisions

### Current Implementation Strengths

- ✅ **Simplicity**: Clean, maintainable codebase with minimal dependencies
- ✅ **Fast Development**: Rapid prototyping and iteration capability
- ✅ **User Experience**: Smooth conversational flow with intelligent error handling
- ✅ **Reliability**: SQLite provides reliable session persistence without external dependencies
- ✅ **Email-Only**: Simplified notification system reduces complexity and costs
- ✅ **Smart Booking Flow**: Handles "no" responses by showing alternatives instead of repeating offers

### Trade-offs Made

- ⚠️ **SMS Removed**: Eliminated SMS functionality to reduce complexity and avoid carrier costs during development
- ⚠️ **In-Memory Inventory**: Simple inventory system suitable for demo/small-scale use
- ✅ **Enhanced NLP**: Upgraded from basic keyword matching to enhanced intent detection with flexible date parsing
- ⚠️ **Single Property**: Designed for single property management (scope limitation)
- ⚠️ **Email Dependency**: Relies on SMTP for notifications (could fail silently)
- ⚠️ **SQLite**: Great for development; would need PostgreSQL for production scale

### Scalability Considerations

- **Database**: Current SQLite approach works for moderate traffic; PostgreSQL recommended for production
- **Session Storage**: In-memory approach limits to single instance; Redis recommended for multi-instance deployment
- **Inventory**: Current in-memory storage needs database backing for real-world use

## 🔮 Next Steps & Roadmap

### Immediate Improvements (1-2 weeks)

1. **Enhanced Error Handling**
   - Retry logic for email sending failures
   - Graceful degradation when services are unavailable
   - Comprehensive logging and monitoring

2. **User Experience Enhancements**
   - Typing indicators during message processing
   - Message timestamps and read receipts
   - Conversation export functionality
   - Mobile responsiveness improvements

3. **Admin Features**
   - Dashboard for viewing active conversations
   - Inventory management interface
   - Basic analytics and reporting

### Medium-term Enhancements (1-2 months)

1. **Advanced NLP Integration**
   - OpenAI GPT integration for better conversation understanding
   - Sentiment analysis for lead scoring
   - Multi-language support

2. **Enhanced Inventory Management**
   - Database-backed inventory with real-time updates
   - Photo galleries and virtual tour integration
   - Dynamic pricing and availability calendars

3. **CRM Integration**
   - Salesforce, HubSpot, or custom CRM connectivity
   - Automated lead scoring and qualification
   - Follow-up sequence automation

### Long-term Vision (3-6 months)

1. **Multi-Property Support**
   - Property selection and comparison features
   - Cross-property availability search
   - Centralized management dashboard

2. **Advanced Features**
   - Video chat integration for virtual tours
   - Document upload and e-signature capabilities
   - Payment processing for deposits and applications

3. **AI & Analytics**
   - Predictive analytics for conversion optimization
   - Personalized unit recommendations
   - Automated lead nurturing campaigns

---

### Demo Video

<https://www.loom.com/share/43f885454f4c49f18bc8b487024b4a50?sid=27079bbb-69d8-4251-9016-b24078bc07c8>

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 **Support**

- **Documentation**: Check this README and API docs
- **Issues**: Open a GitHub issue
- **Email**: Contact the development team
