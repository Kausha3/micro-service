#!/usr/bin/env python3
"""
Test Multi-Field Parsing

This script tests the new multi-field parsing functionality.
"""

import asyncio
from datetime import datetime
from models import ChatMessage
from chat_service import chat_service

async def test_multi_field_parsing():
    """Test parsing multiple fields from a single message."""
    
    print("🧪 TESTING MULTI-FIELD PARSING")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test case 1: Studio unit conversation
    print("1️⃣ Testing studio unit conversation...")
    
    # Start conversation
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id
    print(f"   Session ID: {session_id}")
    
    # Express interest in studio
    message2 = ChatMessage(message="studio", session_id=session_id)
    response2 = await chat_service.process_message(message2)
    print(f"   Studio response: {response2.reply[:100]}...")
    
    # Select specific unit
    message3 = ChatMessage(message="Unit S310: 475 sq ft, $1550/month", session_id=session_id)
    response3 = await chat_service.process_message(message3)
    print(f"   Unit selection response: {response3.reply[:100]}...")
    
    # Provide all info at once
    message4 = ChatMessage(
        message="Manav, kaushatrivedi12@outlook.com, 4444444444, winter 2025", 
        session_id=session_id
    )
    response4 = await chat_service.process_message(message4)
    print(f"   Multi-field response: {response4.reply[:100]}...")
    
    # Check session data
    session = chat_service.db_service.load_session(session_id)
    print()
    print("📊 PARSED DATA:")
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
    booking_confirmed = session.state.value == "booking_confirmed"
    print(f"🎯 Booking Confirmed: {'✅ YES' if booking_confirmed else '❌ NO'}")
    
    # Check if email was mentioned in response
    email_mentioned = any(word in response4.reply.lower() for word in [
        "email", "confirmation", "sent", "inbox", "spam"
    ])
    print(f"📧 Email Mentioned: {'✅ YES' if email_mentioned else '❌ NO'}")
    
    print()
    print("=" * 60)
    
    if is_complete and booking_confirmed:
        print("🎉 SUCCESS: Multi-field parsing worked and booking was triggered!")
        return True
    else:
        print("❌ ISSUE: Multi-field parsing or booking trigger failed")
        print(f"   Current state: {session.state}")
        return False

async def test_direct_multi_field():
    """Test direct multi-field parsing without conversation."""
    
    print("\n🎯 TESTING DIRECT MULTI-FIELD PARSING")
    print("=" * 60)
    
    # Create a new session
    message = ChatMessage(message="John Doe, john@example.com, 5551234567, August 2025, 2 bedroom")
    response = await chat_service.process_message(message)
    
    session = chat_service.db_service.load_session(response.session_id)
    
    print("📊 PARSED DATA:")
    print(f"   Name: {session.prospect_data.name}")
    print(f"   Email: {session.prospect_data.email}")
    print(f"   Phone: {session.prospect_data.phone}")
    print(f"   Move-in: {session.prospect_data.move_in_date}")
    print(f"   Bedrooms: {session.prospect_data.beds_wanted}")
    
    # Check if data is complete
    is_complete = chat_service._is_data_complete(session.prospect_data)
    print(f"📋 Data Complete: {'✅ YES' if is_complete else '❌ NO'}")
    
    if not is_complete:
        missing = chat_service._get_missing_fields(session.prospect_data)
        print(f"   Missing: {missing}")
    
    return is_complete

async def main():
    """Run all multi-field parsing tests."""
    
    print("🧪 MULTI-FIELD PARSING TESTS")
    print("=" * 80)
    
    # Test 1: Studio unit conversation
    test1_result = await test_multi_field_parsing()
    
    # Test 2: Direct multi-field parsing
    test2_result = await test_direct_multi_field()
    
    print("\n📊 TEST RESULTS SUMMARY:")
    print("=" * 40)
    print(f"Studio Conversation Test: {'✅ PASS' if test1_result else '❌ FAIL'}")
    print(f"Direct Multi-Field Test: {'✅ PASS' if test2_result else '❌ FAIL'}")
    
    if test1_result and test2_result:
        print("\n🎉 ALL TESTS PASSED!")
        print("Multi-field parsing is working correctly.")
        print("Check server logs for booking and email details.")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Multi-field parsing may need adjustment.")
        print("Check the implementation and server logs.")

if __name__ == "__main__":
    asyncio.run(main())
