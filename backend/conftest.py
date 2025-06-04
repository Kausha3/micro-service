"""
Test configuration and fixtures for the Lead-to-Lease Chat Concierge.

This file sets up test fixtures and mocks to run tests without requiring
external API keys or services.
"""

import os
import shutil
import tempfile
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Set test environment variables before importing modules
os.environ["OPENAI_API_KEY"] = "test-key-mock"
os.environ["OPENAI_MODEL"] = "gpt-3.5-turbo"
os.environ["PROPERTY_NAME"] = "Test Property"
os.environ["PROPERTY_ADDRESS"] = "123 Test St, Test City, TS 12345"
os.environ["LEASING_OFFICE_PHONE"] = "(555) 123-4567"
os.environ["SMTP_EMAIL"] = "test@example.com"
os.environ["SMTP_PASSWORD"] = "test-password"  # nosec B105 - test password for mocking
os.environ["SMTP_SERVER"] = "smtp.test.com"
os.environ["SMTP_PORT"] = "587"
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Set up test environment variables and configurations."""
    # Create a temporary directory for test databases
    test_dir = tempfile.mkdtemp()
    os.environ["TEST_DB_PATH"] = os.path.join(test_dir, "test_conversations.db")

    yield

    # Cleanup
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)


@pytest.fixture(autouse=True)
def mock_ai_service():
    """Mock the AI service to avoid using real API keys."""
    # Mock the AI service methods directly
    with (
        patch("ai_service.ai_service.generate_response") as mock_generate,
        patch("ai_service.ai_service.should_collect_information") as mock_collect,
        patch("ai_service.ai_service.client") as mock_client,
    ):

        # Mock generate_response to return helpful responses
        async def mock_generate_response(session, user_message):
            message_lower = user_message.lower()

            # Return appropriate responses based on message content
            if any(word in message_lower for word in ["hello", "hi", "hey"]):
                return "Hello! I'm here to help you find your perfect apartment. May I have your name to get started?"
            elif "name" in message_lower or session.state.value == "collecting_name":
                return "Thank you! Could you please provide your email address?"
            elif "email" in message_lower or session.state.value == "collecting_email":
                return "Great! And what's the best phone number to reach you?"
            elif "phone" in message_lower or session.state.value == "collecting_phone":
                return "Perfect! When are you looking to move in?"
            elif "move" in message_lower or "date" in message_lower:
                return "Excellent! How many bedrooms are you looking for?"
            elif "bedroom" in message_lower or "bed" in message_lower:
                return "Great choice! I have several options available. Would you like to book a tour to see them?"
            elif any(word in message_lower for word in ["book", "tour", "yes", "sure"]):
                return "Wonderful! I've scheduled your tour. You'll receive a confirmation email shortly with all the details."
            else:
                return "I'm here to help you find the perfect apartment. What can I assist you with today?"

        mock_generate.side_effect = mock_generate_response

        # Mock should_collect_information to return None (no specific collection needed)
        mock_collect.return_value = None

        # Mock the OpenAI client for any direct calls
        mock_client.chat.completions.create = AsyncMock()
        mock_response = AsyncMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content="NAME: NONE\nEMAIL: NONE\nPHONE: NONE\nMOVE_IN: NONE\nBEDS: NONE\nUNIT: NONE"
                )
            )
        ]
        mock_client.chat.completions.create.return_value = mock_response

        yield mock_generate


@pytest.fixture(autouse=True)
def mock_email_service():
    """Mock the email service to avoid sending real emails."""
    with patch("email_service.aiosmtplib.send") as mock_send:
        mock_send.return_value = AsyncMock()
        yield mock_send


@pytest.fixture
def mock_ai_responses():
    """Provide mock AI responses for different conversation scenarios."""
    return {
        "greeting": "Hello! I'm here to help you find your perfect apartment. May I have your name to get started?",
        "name_request": "Thank you! Could you please provide your email address?",
        "email_request": "Great! And what's the best phone number to reach you?",
        "phone_request": "Perfect! When are you looking to move in?",
        "move_in_date": "Excellent! How many bedrooms are you looking for?",
        "bedroom_preference": "Great choice! I have several options available. Would you like to book a tour to see them?",
        "booking_confirmation": "Wonderful! I've scheduled your tour. You'll receive a confirmation email shortly with all the details.",
        "apartment_search": "I have several great apartments available. Here are some options that might interest you:",
        "pricing_inquiry": "Our apartments range from $1,200 to $2,500 per month, depending on size and amenities.",
        "amenities_inquiry": "Our property features a fitness center, swimming pool, parking garage, and 24/7 concierge service.",
    }


@pytest.fixture
def sample_conversation_data():
    """Provide sample conversation data for testing."""
    return {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567",
        "move_in_date": "2024-02-01",
        "bedrooms": "2",
        "tour_date": "2024-01-15",
        "tour_time": "2:00 PM",
    }


@pytest.fixture
def mock_inventory_data():
    """Provide mock inventory data for testing."""
    return [
        {
            "unit_id": "A101",
            "bedrooms": 1,
            "bathrooms": 1,
            "square_feet": 750,
            "rent": 1200,
            "available_date": "2024-01-01",
            "amenities": ["balcony", "dishwasher"],
        },
        {
            "unit_id": "B205",
            "bedrooms": 2,
            "bathrooms": 2,
            "square_feet": 1100,
            "rent": 1800,
            "available_date": "2024-01-15",
            "amenities": ["balcony", "dishwasher", "in-unit-laundry"],
        },
        {
            "unit_id": "C301",
            "bedrooms": 3,
            "bathrooms": 2,
            "square_feet": 1400,
            "rent": 2500,
            "available_date": "2024-02-01",
            "amenities": ["balcony", "dishwasher", "in-unit-laundry", "walk-in-closet"],
        },
    ]


@pytest.fixture(autouse=True)
def mock_database():
    """Use an in-memory database for all tests."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from database import Base

    # Create in-memory SQLite database for testing
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(test_engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

    # Patch the SessionLocal in session_db_service
    with patch("session_db_service.SessionLocal", TestSessionLocal):
        yield TestSessionLocal


@pytest.fixture
def clean_database():
    """Ensure a clean database for each test."""
    from session_db_service import SessionDatabaseService

    db_service = SessionDatabaseService()

    yield db_service

    # Cleanup is handled by the in-memory database fixture


# pytest_asyncio is configured in pyproject.toml
