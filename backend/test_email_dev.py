#!/usr/bin/env python3
"""
Development Email Testing Script

This script tests the email functionality in the same way it would be called
during the actual booking flow to identify discrepancies between test and
development environments.
"""

import asyncio
import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to match main application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ]
)

# Set specific loggers to INFO level
logging.getLogger("email_service").setLevel(logging.INFO)
logging.getLogger("chat_service").setLevel(logging.INFO)

from models import TourConfirmation, ChatMessage, ProspectData, ConversationSession, ChatState
from email_service import EmailService
from chat_service import ChatService
import uuid

async def test_email_in_dev_context():
    """Test email functionality in development context."""
    print("🧪 Testing Email in Development Context")
    print("=" * 60)
    
    # Initialize services like the main application does
    email_service = EmailService()
    chat_service = ChatService()
    
    print(f"📧 Email Service Configuration:")
    print(f"   SMTP Email: {email_service.smtp_email}")
    print(f"   SMTP Server: {email_service.smtp_server}:{email_service.smtp_port}")
    print(f"   Configuration Valid: {email_service._validate_email_config()}")
    print()
    
    # Test 1: Direct email service call
    print("🔬 Test 1: Direct Email Service Call")
    print("-" * 40)
    
    confirmation = TourConfirmation(
        prospect_name="Dev Test User",
        prospect_email=email_service.smtp_email,  # Send to self
        unit_id="DEV-TEST-101",
        property_address=email_service.property_address,
        tour_date="Tomorrow",
        tour_time="2:00 PM"
    )
    
    print(f"Sending test email to: {confirmation.prospect_email}")
    result = await email_service.send_tour_confirmation(confirmation)
    print(f"Direct email result: {'✅ SUCCESS' if result else '❌ FAILED'}")
    print()
    
    # Test 2: Complete booking flow simulation
    print("🔬 Test 2: Complete Booking Flow Simulation")
    print("-" * 40)
    
    # Create a session with complete prospect data
    session = ConversationSession(
        session_id=str(uuid.uuid4()),
        state=ChatState.READY_TO_BOOK,
        prospect_data=ProspectData(
            name="Dev Test User",
            email=email_service.smtp_email,
            phone="555-123-4567",
            move_in_date="Next month",
            beds_wanted=2
        ),
        messages=[],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    print(f"Session created with prospect data:")
    print(f"   Name: {session.prospect_data.name}")
    print(f"   Email: {session.prospect_data.email}")
    print(f"   Phone: {session.prospect_data.phone}")
    print(f"   Beds: {session.prospect_data.beds_wanted}")
    print()
    
    # Test data completeness first
    print(f"Data completeness check: {chat_service._is_data_complete(session.prospect_data)}")
    missing_fields = chat_service._get_missing_fields(session.prospect_data)
    print(f"Missing fields: {missing_fields}")

    # Test direct booking intent call
    print("\n🔬 Test 2a: Direct Booking Intent Call")
    print("-" * 40)
    try:
        booking_result = await chat_service._handle_booking_intent(session)
        print(f"Direct booking result: {booking_result[:200]}...")
        print(f"Session state after direct booking: {session.state}")

        # Check if email was mentioned in response
        if "email" in booking_result.lower():
            print("✅ Direct booking mentions email")
        else:
            print("⚠️  Direct booking doesn't mention email")
    except Exception as e:
        print(f"❌ Direct booking failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n🔬 Test 2b: Chat Message Processing")
    print("-" * 40)

    # Simulate booking intent message
    booking_message = ChatMessage(
        session_id=session.session_id,
        message="Yes, I'd like to book a tour please!"
    )

    print("Simulating booking intent...")
    try:
        response = await chat_service.process_message(booking_message)
        print(f"Chat response: {response.reply[:200]}...")
        print(f"Session state after chat: {session.state}")

        # Check if email was mentioned in response
        if "email" in response.reply.lower():
            print("✅ Chat response mentions email")
        else:
            print("⚠️  Chat response doesn't mention email")

    except Exception as e:
        print(f"❌ Chat processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🎯 Development Test Summary:")
    print("=" * 60)
    print("1. ✅ Email service initializes correctly")
    print("2. ✅ Configuration validation works")
    print(f"3. {'✅' if result else '❌'} Direct email sending works")
    print("4. Check booking flow logs above for email service calls")
    print()
    print("💡 If direct email works but booking flow doesn't send emails,")
    print("   check the chat service logs for email service call patterns.")

if __name__ == "__main__":
    asyncio.run(test_email_in_dev_context())
