#!/usr/bin/env python3
"""
Test script for unit click booking functionality.

This script tests the enhanced booking flow where users can click on apartment
listings to automatically initiate the booking process for specific units.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import ChatMessage
from chat_service import chat_service
from inventory_service import inventory_service


async def test_unit_click_booking():
    """Test the unit click booking functionality."""
    
    print("🧪 TESTING UNIT CLICK BOOKING FUNCTIONALITY")
    print("=" * 60)
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Show available inventory first
    available_units = inventory_service.get_all_available_units()
    print(f"📋 Available Units: {len(available_units)}")
    for unit in available_units[:5]:  # Show first 5 units
        print(f"   • Unit {unit.unit_id} | {unit.beds} bed/{unit.baths} bath | {unit.sqft} sq ft | ${unit.rent:,}/month")
    print()
    
    # Step 1: Start conversation
    print("1️⃣ Starting conversation...")
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id
    print(f"   Response: {response1.reply[:100]}...")
    print(f"   Session ID: {session_id}")
    print()
    
    # Step 2: Simulate apartment listing click (direct unit booking)
    print("2️⃣ Simulating apartment listing click...")
    test_unit = available_units[0]  # Use first available unit
    click_message = f"I want to book {test_unit.unit_id}"
    print(f"   Click message: '{click_message}'")
    
    message2 = ChatMessage(message=click_message, session_id=session_id)
    response2 = await chat_service.process_message(message2)
    print(f"   Response: {response2.reply[:150]}...")
    print()
    
    # Check session state after click
    session = chat_service.db_service.load_session(session_id)
    print("📊 SESSION STATE AFTER CLICK:")
    print(f"   Unit ID: {session.prospect_data.unit_id}")
    print(f"   Bedrooms: {session.prospect_data.beds_wanted}")
    print(f"   State: {session.state}")
    print(f"   Booking Intent: {'booking_intent' in session.ai_context.extracted_intents}")
    print()
    
    # Step 3: Provide name (should be requested)
    print("3️⃣ Providing name...")
    message3 = ChatMessage(message="John Smith", session_id=session_id)
    response3 = await chat_service.process_message(message3)
    print(f"   Response: {response3.reply[:150]}...")
    print()
    
    # Step 4: Provide email
    print("4️⃣ Providing email...")
    message4 = ChatMessage(message="john.smith@example.com", session_id=session_id)
    response4 = await chat_service.process_message(message4)
    print(f"   Response: {response4.reply[:150]}...")
    print()
    
    # Step 5: Provide phone
    print("5️⃣ Providing phone...")
    message5 = ChatMessage(message="(555) 123-4567", session_id=session_id)
    response5 = await chat_service.process_message(message5)
    print(f"   Response: {response5.reply[:150]}...")
    print()
    
    # Step 6: Provide move-in date
    print("6️⃣ Providing move-in date...")
    message6 = ChatMessage(message="Next month", session_id=session_id)
    response6 = await chat_service.process_message(message6)
    print(f"   Response: {response6.reply[:200]}...")
    print()
    
    # Final session state
    final_session = chat_service.db_service.load_session(session_id)
    print("📊 FINAL SESSION STATE:")
    print(f"   Name: {final_session.prospect_data.name}")
    print(f"   Email: {final_session.prospect_data.email}")
    print(f"   Phone: {final_session.prospect_data.phone}")
    print(f"   Move-in: {final_session.prospect_data.move_in_date}")
    print(f"   Bedrooms: {final_session.prospect_data.beds_wanted}")
    print(f"   Unit ID: {final_session.prospect_data.unit_id}")
    print(f"   State: {final_session.state}")
    print()
    
    # Check if booking was completed
    if final_session.state.value == "BOOKING_CONFIRMED":
        print("✅ SUCCESS: Booking completed successfully!")
        print(f"   Unit {final_session.prospect_data.unit_id} reserved for {final_session.prospect_data.name}")
    else:
        print("⚠️  PARTIAL: Booking flow initiated but not completed")
        print(f"   Current state: {final_session.state}")
    
    print("\n" + "=" * 60)
    print("🎯 UNIT CLICK BOOKING TEST COMPLETED")


if __name__ == "__main__":
    asyncio.run(test_unit_click_booking())
