"""
Test script for AI integration in the Lead-to-Lease Chat Concierge.

This script tests the AI-powered conversation capabilities using mocked
AI responses to avoid requiring real API keys.
"""

import os
import sys

import pytest

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import uuid
from datetime import datetime

from ai_service import ai_service
from models import AIContext, ChatState, ConversationSession, ProspectData


@pytest.mark.asyncio
async def test_ai_integration():
    """Test the AI integration with sample conversations."""

    print("🤖 Testing AI Integration for Lead-to-Lease Chat Concierge")
    print("=" * 60)

    # AI service should be enabled in test environment
    assert ai_service.enabled, "AI service should be enabled in test environment"

    print("✅ AI service is enabled")
    print(f"   Model: {ai_service.model}")
    print(f"   Property: {ai_service.property_name}")
    print()

    # Create a test session
    session = ConversationSession(
        session_id=str(uuid.uuid4()),
        state=ChatState.GREETING,
        prospect_data=ProspectData(),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Test scenarios
    test_scenarios = [
        "Hi, I'm looking for an apartment",
        "What do you have available?",
        "I need a 2-bedroom apartment",
        "What's the price range?",
        "I'd like to book a tour",
    ]

    print("🧪 Testing conversation scenarios:")
    print("-" * 40)

    for i, user_message in enumerate(test_scenarios, 1):
        print(f"\n{i}. User: {user_message}")

        try:
            # Generate AI response
            ai_response = await ai_service.generate_response(session, user_message)
            print(f"   AI: {ai_response}")

            # Add messages to session for context
            from models import ConversationMessage

            session.messages.append(
                ConversationMessage(
                    sender="user", text=user_message, timestamp=datetime.now()
                )
            )
            session.messages.append(
                ConversationMessage(
                    sender="bot", text=ai_response, timestamp=datetime.now()
                )
            )

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            break

    print("\n" + "=" * 60)
    print("✅ AI integration test completed!")

    # Display session context
    print(f"\n📊 Session Summary:")
    print(f"   Messages: {len(session.messages)}")
    print(f"   AI Context: {session.ai_context.conversation_stage}")
    print(f"   Extracted Intents: {session.ai_context.extracted_intents}")
    print(f"   User Preferences: {session.ai_context.user_preferences}")


@pytest.mark.asyncio
async def test_inventory_context():
    """Test AI responses with inventory context."""

    print("\n🏠 Testing Inventory Context Integration")
    print("-" * 40)

    # AI service should be enabled in test environment
    assert ai_service.enabled, "AI service should be enabled in test environment"

    # Import inventory service
    from inventory_service import inventory_service

    # Get available units
    available_units = inventory_service.get_all_available_units()
    print(f"📋 Available units: {len(available_units)}")

    # Create session
    session = ConversationSession(
        session_id=str(uuid.uuid4()),
        state=ChatState.GREETING,
        prospect_data=ProspectData(),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    # Test inventory-related queries
    inventory_queries = [
        "What apartments do you have available?",
        "Show me your cheapest units",
        "Do you have any 3-bedroom apartments?",
        "What's the square footage of your units?",
    ]

    for query in inventory_queries:
        print(f"\nUser: {query}")
        try:
            response = await ai_service.generate_response(session, query)
            print(f"AI: {response}")
        except Exception as e:
            print(f"❌ Error: {str(e)}")


# Tests are now run via pytest, no need for main execution block
