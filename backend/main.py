"""
Lead-to-Lease Chat Concierge API

A production-ready FastAPI-based microservice that provides an intelligent chat interface
for apartment leasing with AI-powered natural language processing.

## Core Features
- **AI-Powered Conversations**: OpenAI GPT integration for natural language understanding
- **Automated Lead Qualification**: Intelligent data collection (name, email, phone, move-in date, bedroom preference)
- **Real-time Inventory Management**: Dynamic apartment unit availability with realistic simulation
- **Email Notifications**: Professional HTML email confirmations for tour bookings
- **Session Persistence**: SQLite database with comprehensive conversation history
- **Multi-unit Booking**: Support for booking multiple apartments simultaneously
- **Comprehensive Error Handling**: Graceful degradation and detailed logging

## Architecture
This microservice follows a clean architecture pattern with:
- **Presentation Layer**: FastAPI routes and middleware
- **Business Logic Layer**: Service classes for chat, email, inventory, and AI
- **Data Layer**: SQLAlchemy models with SQLite database
- **External Integrations**: OpenAI API and SMTP email services

## API Endpoints
- `GET /`: Health check and API information
- `POST /chat`: Main conversation endpoint with AI processing
- `GET /inventory`: Current apartment availability
- `GET /sessions/{id}`: Session details and conversation history

## Environment Configuration
Requires environment variables for:
- Email service (SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT)
- Property information (PROPERTY_ADDRESS, PROPERTY_NAME, LEASING_OFFICE_PHONE)
- AI service (OPENAI_API_KEY)
- Application settings (ENVIRONMENT, PORT, FRONTEND_URL)
"""

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

import routes
from models import ChatResponse

# Load environment variables from .env file
# This must be called before importing any modules that use environment variables
load_dotenv()

# Configure structured logging with enhanced visibility for production monitoring
# Uses ISO timestamp format and structured message format for log aggregation
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output for Docker/container environments
    ],
)

# Set specific service loggers to INFO level to ensure visibility of business operations
# These loggers provide detailed insights into the application's core functionality
logging.getLogger("email_service").setLevel(logging.INFO)  # Email delivery tracking
logging.getLogger("chat_service").setLevel(logging.INFO)  # Conversation flow monitoring
logging.getLogger("ai_service").setLevel(logging.INFO)  # AI integration status
logging.getLogger("inventory_service").setLevel(
    logging.INFO
)  # Unit availability tracking

logger = logging.getLogger(__name__)
logger.info("🚀 Application starting - logging configured")

# Initialize FastAPI application with comprehensive metadata
app = FastAPI(
    title="Lead-to-Lease Chat Concierge",
    description="""
    ## 🏠 Intelligent Chat Microservice for Apartment Leasing

    A production-ready FastAPI microservice that automates lead qualification and tour booking
    through AI-powered natural language conversation.

    ### 🚀 Key Features
    - **AI-Powered Conversations**: OpenAI GPT integration for natural language understanding
    - **Automated Lead Qualification**: Intelligent data collection and validation
    - **Real-time Inventory Management**: Dynamic apartment availability with realistic simulation
    - **Professional Email Notifications**: HTML email confirmations with retry logic
    - **Multi-unit Booking Support**: Book multiple apartments simultaneously
    - **Session Persistence**: Complete conversation history and state management

    ### 🔧 Technical Stack
    - **Backend**: FastAPI + Python 3.10+
    - **Database**: SQLite with SQLAlchemy ORM
    - **AI Integration**: OpenAI GPT-4 for conversation processing
    - **Email Service**: SMTP with aiosmtplib for reliable delivery
    - **Authentication**: Environment-based configuration

    ### 📚 Documentation
    - **Interactive API Docs**: [/docs](/docs) (Swagger UI)
    - **Alternative Docs**: [/redoc](/redoc) (ReDoc)
    - **Health Check**: [/](/") (API status)

    ### 🌐 Environment
    Configure the following environment variables:
    - `SMTP_EMAIL`, `SMTP_PASSWORD`: Email service credentials
    - `OPENAI_API_KEY`: AI service authentication
    - `PROPERTY_ADDRESS`, `PROPERTY_NAME`: Property information
    """,
    version="1.0.0",
    contact={
        "name": "Augment Agent",
        "email": "dev@augmentcode.com",
        "url": "https://github.com/your-org/lead-to-lease-chat-concierge",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {
            "name": "Health",
            "description": "API health check and status endpoints",
        },
        {
            "name": "Chat",
            "description": "AI-powered conversation endpoints for lead qualification",
        },
        {
            "name": "Inventory",
            "description": "Apartment unit availability and management",
        },
        {
            "name": "Sessions",
            "description": "Conversation session management and history",
        },
    ],
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development frontend
        "http://localhost:3001",  # Alternative frontend port
        "http://127.0.0.1:3000",  # Alternative local address
        "http://127.0.0.1:3001",  # Alternative local address with port 3001
        "https://micro-service-frontend.onrender.com",  # Production deployment
        os.getenv("FRONTEND_URL", "").strip(),  # Custom frontend URL from environment
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


# Register route handlers
app.get("/")(routes.root)
app.post("/chat", response_model=ChatResponse)(routes.chat_endpoint)


app.get("/inventory")(routes.get_inventory)
app.get("/sessions/{session_id}")(routes.get_session)


@app.exception_handler(Exception)
async def global_exception_handler(_request, exc):
    """
    Global exception handler for unhandled errors.

    Catches any unhandled exceptions and returns a standardized error response.
    Logs the full exception details for debugging while providing a safe
    user-friendly message.

    Args:
        request: The incoming request (unused but required by FastAPI)
        exc: The exception that was raised

    Returns:
        JSONResponse: Standardized error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An unexpected error occurred. Please try again.",
            "type": "internal_server_error",
        },
    )


if __name__ == "__main__":
    """
    Application entry point for direct execution.

    Configures and starts the Uvicorn ASGI server with environment-specific settings.
    Supports both development (with hot reload) and production modes.
    """
    import uvicorn

    # Get configuration from environment variables
    port = int(os.getenv("PORT", 8000))
    environment = os.getenv("ENVIRONMENT", "development")

    # Configure server settings based on environment
    server_config = {
        "app": "main:app",
        # nosec B104 - Binding to all interfaces is required for containerized deployment
        "host": "0.0.0.0",  # nosec B104
        "port": port,
        "reload": environment == "development",
        "log_level": "info",
    }

    logger.info(f"Starting server on port {port} in {environment} mode")
    uvicorn.run(**server_config)
