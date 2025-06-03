# 🏠 Lead-to-Lease Chat Concierge

> **Production-Ready Intelligent Chat Microservice for Apartment Leasing**

A FastAPI-based microservice that automates lead qualification and tour booking through natural language conversation. Features intelligent conversation flow, real-time inventory management, email notifications, and comprehensive session persistence.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

---

## ✨ **Key Features**

### 🤖 **Intelligent Conversation Management**
- **Natural Language Processing**: Understands user intent and guides conversations naturally
- **Smart Data Collection**: Automatically collects name, email, phone, move-in date, and bedroom preferences  
- **Fuzzy Date Parsing**: Accepts natural language dates like "January 2024", "next month", "ASAP"
- **Intent Recognition**: Recognizes booking intent with keywords like "book", "schedule", "tour"
- **State Management**: Intelligent conversation state tracking with seamless flow

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

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  FastAPI Backend │    │  SQLite Database │
│                 │◄──►│                 │◄──►│                 │
│  - Chat Widget  │    │  - Chat Service │    │  - Sessions     │
│  - Real-time UI │    │  - Email Service│    │  - Messages     │
│  - Responsive   │    │  - Inventory    │    │  - Prospect Data│
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Email Service  │
                       │                 │
                       │  - SMTP Support │
                       │  - HTML Templates│
                       │  - Fallback Mode│
                       └─────────────────┘
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

```
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

### **Email Setup (Optional)**

For Gmail:
1. Enable 2-Factor Authentication
2. Generate an App Password: [Google Account Settings](https://myaccount.google.com/) → Security → App passwords
3. Use the 16-character app password in your `.env` file

**Note**: The application works perfectly without email configuration in demo mode.

---

### Render Deployment
The application is ready for deployment on Render. Follow these steps:

1. **Push to GitHub**: Commit and push your code to a GitHub repository
2. **Connect to Render**:
   - Go to [render.com](https://render.com)
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
3. **Set Environment Variables** in your Render dashboard:
   - `SMTP_EMAIL`: Your Gmail address
   - `SMTP_PASSWORD`: Your Gmail app password (not your regular password)
   - `PROPERTY_ADDRESS`: Property address for emails

## 🧪 **Testing**

### **Backend Tests**
```bash
cd backend
python -m pytest -v

# With coverage
python -m pytest --cov=. --cov-report=html
```

### **Frontend Tests**
```bash
cd frontend
npm run lint
npm run build  # Tests build process
```

### **Docker Tests**
```bash
# Validate Docker configuration
docker-compose config

# Run tests in container
docker-compose run backend pytest -v
```

---

## 📊 **API Documentation**

Once running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/

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
https://www.loom.com/share/43f885454f4c49f18bc8b487024b4a50?sid=27079bbb-69d8-4251-9016-b24078bc07c8
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

