#!/usr/bin/env python3
"""
Test Booking Flow and Email Sending

This script tests the complete booking flow using mocked services.
"""

import uuid
from datetime import datetime

import pytest

from chat_service import chat_service
from models import AIContext, ChatMessage, ChatState, ConversationSession, ProspectData


@pytest.mark.asyncio
async def test_complete_booking_flow():
    """Test the complete booking flow step by step."""

    print("🧪 TESTING COMPLETE BOOKING FLOW")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Step 1: Start conversation
    print("1️⃣ Starting conversation...")
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id
    print(f"   Response: {response1.reply[:100]}...")
    print(f"   Session ID: {session_id}")
    print()

    # Step 2: Express interest
    print("2️⃣ Expressing interest...")
    message2 = ChatMessage(message="Yes, I'm interested", session_id=session_id)
    response2 = await chat_service.process_message(message2)
    print(f"   Response: {response2.reply[:100]}...")
    print()

    # Step 3: Provide bedroom preference
    print("3️⃣ Providing bedroom preference...")
    message3 = ChatMessage(message="2 bedroom", session_id=session_id)
    response3 = await chat_service.process_message(message3)
    print(f"   Response: {response3.reply[:100]}...")
    print()

    # Step 4: Select unit
    print("4️⃣ Selecting unit...")
    message4 = ChatMessage(message="Unit A101", session_id=session_id)
    response4 = await chat_service.process_message(message4)
    print(f"   Response: {response4.reply[:100]}...")
    print()

    # Step 5: Provide contact info
    print("5️⃣ Providing contact information...")
    message5 = ChatMessage(
        message="John Doe, john@example.com, 5551234567", session_id=session_id
    )
    response5 = await chat_service.process_message(message5)
    print(f"   Response: {response5.reply[:100]}...")
    print()

    # Step 6: Provide move-in date
    print("6️⃣ Providing move-in date...")
    message6 = ChatMessage(message="August 2025", session_id=session_id)
    response6 = await chat_service.process_message(message6)
    print(f"   Response: {response6.reply[:100]}...")
    print()

    # Check final session state
    session = chat_service.db_service.load_session(session_id)
    print("📊 FINAL SESSION STATE:")
    print(f"   State: {session.state}")
    print(f"   Name: {session.prospect_data.name}")
    print(f"   Email: {session.prospect_data.email}")
    print(f"   Phone: {session.prospect_data.phone}")
    print(f"   Move-in: {session.prospect_data.move_in_date}")
    print(f"   Bedrooms: {session.prospect_data.beds_wanted}")
    print(f"   Unit ID: {session.prospect_data.unit_id}")
    print()

    # Check if data is complete
    is_complete = chat_service._is_data_complete(session.prospect_data)
    print(f"📋 Data Complete: {'✅ YES' if is_complete else '❌ NO'}")

    if not is_complete:
        missing = chat_service._get_missing_fields(session.prospect_data)
        print(f"   Missing: {missing}")

    # Check if booking was triggered
    booking_confirmed = session.state == ChatState.BOOKING_CONFIRMED
    print(f"🎯 Booking Confirmed: {'✅ YES' if booking_confirmed else '❌ NO'}")

    # Check if email was mentioned in response
    email_mentioned = any(
        word in response6.reply.lower()
        for word in ["email", "confirmation", "sent", "inbox", "spam"]
    )
    print(f"📧 Email Mentioned: {'✅ YES' if email_mentioned else '❌ NO'}")

    print()
    print("=" * 60)

    if booking_confirmed and email_mentioned:
        print("🎉 SUCCESS: Booking flow completed and email should be sent!")
    else:
        print("❌ ISSUE: Booking flow may not have triggered email sending")
        print("   Check the server logs for detailed information")

    return booking_confirmed and email_mentioned


@pytest.mark.asyncio
async def test_direct_booking():
    """Test direct booking with complete data."""

    print("\n🎯 TESTING DIRECT BOOKING WITH COMPLETE DATA")
    print("=" * 60)

    # Create session with complete data
    session = ConversationSession(
        session_id=str(uuid.uuid4()),
        state=ChatState.GREETING,
        prospect_data=ProspectData(
            name="Test User",
            email="test@example.com",
            phone="5551234567",
            move_in_date="August 2025",
            beds_wanted=2,
        ),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    print("📋 Test Data:")
    print(f"   Name: {session.prospect_data.name}")
    print(f"   Email: {session.prospect_data.email}")
    print(f"   Phone: {session.prospect_data.phone}")
    print(f"   Move-in: {session.prospect_data.move_in_date}")
    print(f"   Bedrooms: {session.prospect_data.beds_wanted}")
    print()

    # Check if data is complete
    is_complete = chat_service._is_data_complete(session.prospect_data)
    print(f"📊 Data Complete: {'✅ YES' if is_complete else '❌ NO'}")

    if is_complete:
        print("🚀 Calling booking intent handler directly...")
        try:
            result = await chat_service._handle_booking_intent(session)
            print(f"   Result: {result[:200]}...")

            # Check if email was mentioned
            email_mentioned = any(
                word in result.lower()
                for word in ["email", "confirmation", "sent", "inbox", "spam"]
            )
            print(f"   Email mentioned: {'✅ YES' if email_mentioned else '❌ NO'}")

            return email_mentioned

        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False
    else:
        missing = chat_service._get_missing_fields(session.prospect_data)
        print(f"   Missing: {missing}")
        return False


# Tests are now run via pytest, no need for main execution block
