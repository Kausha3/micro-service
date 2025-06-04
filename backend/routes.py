"""
FastAPI Route Definitions

This module contains all FastAPI route declarations and handlers,
separated from business logic for better maintainability.
Framework-specific code is isolated here while business logic
remains in dedicated service modules.
"""

import logging

from fastapi import HTTPException

from chat_service import chat_service
from inventory_service import inventory_service
from models import ChatMessage

logger = logging.getLogger(__name__)


async def root():
    """
    API Health Check and Information

    Returns comprehensive API status, version information, and available features.
    This endpoint is used for health monitoring, service discovery, and API documentation.

    **Use Cases:**
    - Health monitoring and uptime checks
    - Service discovery and capability detection
    - API version verification
    - Integration testing and validation

    **Response Format:**
    - `message`: API name and description
    - `status`: Current service health status
    - `version`: API version following semantic versioning
    - `features`: List of available capabilities
    - `endpoints`: Available API endpoints with descriptions
    - `documentation`: Links to API documentation

    **Tags:** Health

    Returns:
        dict: Comprehensive API status and information
    """
    return {
        "message": "Lead-to-Lease Chat Concierge API",
        "status": "healthy",
        "version": "1.0.0",
        "description": "AI-powered chat microservice for apartment leasing with automated lead qualification",
        "features": [
            "AI-powered natural language conversation",
            "Automated lead qualification and data collection",
            "Real-time apartment inventory management",
            "Professional email notifications with retry logic",
            "Multi-unit booking support",
            "Session persistence and conversation history",
            "OpenAPI/Swagger documentation",
        ],
        "endpoints": {
            "/": "API health check and information",
            "/chat": "AI-powered conversation processing",
            "/inventory": "Apartment unit availability",
            "/sessions/{id}": "Conversation session details",
            "/docs": "Interactive API documentation (Swagger UI)",
            "/redoc": "Alternative API documentation (ReDoc)",
        },
        "documentation": {
            "interactive": "/docs",
            "alternative": "/redoc",
            "openapi_spec": "/openapi.json",
        },
        "contact": {
            "name": "Augment Agent",
            "email": "dev@augmentcode.com",
        },
        "license": "MIT",
    }


async def chat_endpoint(message: ChatMessage):
    """
    Main chat endpoint for processing user messages.

    This endpoint handles the complete conversation flow:
    1. Accepts user messages with optional session ID
    2. Processes messages through the intelligent chat service
    3. Manages conversation state and data collection
    4. Returns contextual assistant replies with session tracking

    Args:
        message (ChatMessage): User message with optional session ID

    Returns:
        ChatResponse: Assistant reply with session ID and state

    Raises:
        HTTPException: 500 if message processing fails
    """
    try:
        logger.info(
            f"Processing message: '{message.message[:50]}{'...' if len(message.message) > 50 else ''}'"
        )

        # Process message through intelligent chat service
        response = await chat_service.process_message(message)

        logger.info(
            f"Generated response: '{response.reply[:50]}{'...' if len(response.reply) > 50 else ''}'"
        )

        return response

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message. Please try again.",
        )


async def get_inventory():
    """
    Get current inventory status.

    Returns all available units for administrative purposes.
    Useful for debugging and monitoring inventory state.

    Returns:
        dict: List of available units with details

    Raises:
        HTTPException: 500 if inventory fetch fails
    """
    try:
        units = inventory_service.get_all_available_units()
        return {
            "available_units": units,
            "total_units": len(units),
            "timestamp": "2025-01-03T01:57:00Z",  # Current timestamp would be dynamic
        }
    except Exception as e:
        logger.error(f"Error fetching inventory: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching inventory")


async def get_session(session_id: str):
    """
    Retrieve session details by session ID.

    Provides detailed information about a conversation session
    including state, collected data, and message history.

    Args:
        session_id (str): Unique session identifier

    Returns:
        dict: Session details including state and prospect data

    Raises:
        HTTPException: 404 if session not found, 500 if fetch fails
    """
    try:
        session = chat_service.db_service.load_session(session_id)
        if session:
            return {
                "session_id": session.session_id,
                "state": session.state.value,  # Convert enum to string
                "prospect_data": session.prospect_data.model_dump(),
                "message_count": len(session.messages),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
            }
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error fetching session")
