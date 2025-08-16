"""
FastAPI Route Definitions

This module contains all FastAPI route declarations and handlers,
separated from business logic for better maintainability.
Framework-specific code is isolated here while business logic
remains in dedicated service modules.
"""

import logging
import os

from fastapi import HTTPException

from chat_service import chat_service
from inventory_service import inventory_service
from models import ChatMessage
from ai_service import get_ai_service

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
            "/debug/ai-status": "AI service diagnostic information",
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


async def debug_ai_status():
    """
    AI Service Diagnostic Endpoint
    
    Provides detailed information about the AI service configuration and status.
    This endpoint is useful for debugging AI-related issues in production.
    
    **Use Cases:**
    - Debugging AI service initialization failures
    - Verifying AI provider configuration
    - Checking API key presence without exposing it
    - Identifying model configuration issues
    
    **Response Format:**
    - `ai_enabled`: Whether AI features are enabled
    - `provider`: AI provider being used (Gemini/OpenAI)
    - `model`: AI model being used
    - `api_key_present`: Whether API key is configured (without revealing it)
    - `api_key_valid`: Whether API key format is valid
    - `initialization_status`: Status of AI service initialization
    - `configuration`: Additional configuration details
    - `errors`: Any initialization errors encountered
    
    **Tags:** Debug, Health
    
    Returns:
        dict: Comprehensive AI service status and configuration
    """
    try:
        # Get the AI service instance
        ai_svc = get_ai_service()
        
        # Check environment variables
        gemini_key = os.getenv("GEMINI_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        
        # Determine which provider is configured
        provider = None
        api_key_present = False
        api_key_valid = False
        
        if gemini_key:
            provider = "Gemini"
            api_key_present = True
            # Check if it's not a placeholder
            api_key_valid = (
                gemini_key != "your_gemini_api_key_here" 
                and len(gemini_key) > 10
                and gemini_key != "test-key-mock"
            )
        elif openai_key:
            provider = "OpenAI"
            api_key_present = True
            # Check if it's not a placeholder
            api_key_valid = (
                openai_key.startswith("sk-") 
                and len(openai_key) > 20
            )
        
        # Build response
        response = {
            "ai_enabled": ai_svc.enabled if hasattr(ai_svc, 'enabled') else False,
            "provider": provider or "None",
            "model": None,
            "api_key_present": api_key_present,
            "api_key_valid": api_key_valid,
            "initialization_status": "unknown",
            "configuration": {},
            "errors": []
        }
        
        # Get model information based on provider
        if provider == "Gemini" and hasattr(ai_svc, 'model_name'):
            response["model"] = ai_svc.model_name
            response["configuration"]["timeout"] = getattr(ai_svc, 'timeout_seconds', 'not set')
            response["configuration"]["max_retries"] = getattr(ai_svc, 'max_retries', 'not set')
            response["configuration"]["retry_delay"] = getattr(ai_svc, 'retry_delay', 'not set')
        elif provider == "OpenAI" and hasattr(ai_svc, 'model'):
            response["model"] = ai_svc.model
        
        # Check initialization status
        if hasattr(ai_svc, 'model'):
            if ai_svc.model is not None:
                response["initialization_status"] = "success"
            else:
                response["initialization_status"] = "failed"
                response["errors"].append("AI model client is None")
        else:
            response["initialization_status"] = "not_initialized"
            response["errors"].append("AI service does not have model attribute")
        
        # Check for common configuration issues
        if not api_key_present:
            response["errors"].append("No AI API key found in environment")
        elif not api_key_valid:
            response["errors"].append("API key appears to be a placeholder or invalid format")
        
        # Add environment information
        response["configuration"]["environment"] = os.getenv("ENVIRONMENT", "not set")
        response["configuration"]["property_name"] = getattr(ai_svc, 'property_name', 'not set')
        response["configuration"]["property_address"] = getattr(ai_svc, 'property_address', 'not set')
        
        # Add service health check
        if response["ai_enabled"] and response["initialization_status"] == "success":
            response["health_status"] = "healthy"
        else:
            response["health_status"] = "unhealthy"
        
        return response
        
    except Exception as e:
        logger.error(f"Error checking AI status: {str(e)}", exc_info=True)
        return {
            "ai_enabled": False,
            "provider": "Unknown",
            "model": "Unknown",
            "api_key_present": False,
            "api_key_valid": False,
            "initialization_status": "error",
            "configuration": {},
            "errors": [f"Failed to check AI status: {str(e)}"],
            "health_status": "error"
        }
