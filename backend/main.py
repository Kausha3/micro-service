"""
Lead-to-Lease Chat Concierge API

A FastAPI-based microservice that provides an intelligent chat interface
for apartment leasing. Features include:
- Natural language conversation flow
- Automated data collection (name, email, phone, move-in date, bedroom preference)
- Real-time inventory checking with randomized availability
- Email notifications for tour confirmations
- Session persistence with SQLite database
- Comprehensive error handling and validation

Author: Augment Agent
Version: 1.0.0
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from models import ChatResponse
import routes
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application with metadata
app = FastAPI(
    title="Lead-to-Lease Chat Concierge",
    description="Intelligent chat microservice for apartment leasing with automated lead qualification",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development frontend
        "http://127.0.0.1:3000",  # Alternative local address
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
async def global_exception_handler(request, exc):
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
        "host": "0.0.0.0",
        "port": port,
        "reload": environment == "development",
        "log_level": "info",
    }

    logger.info(f"Starting server on port {port} in {environment} mode")
    uvicorn.run(**server_config)
