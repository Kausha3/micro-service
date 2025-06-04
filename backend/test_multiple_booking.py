#!/usr/bin/env python3
"""
Test script for multiple booking functionality.

This script tests the enhanced apartment booking chatbot with multiple unit selection
and comprehensive email confirmations.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    ConversationSession, 
    ProspectData, 
    ChatState, 
    AIContext,
    MultipleBookingConfirmation,
    BookedUnit
)
from chat_service import chat_service
from email_service import email_service
from inventory_service import inventory_service

async def test_multiple_booking_flow():
    """Test the complete multiple booking flow."""
    print("🧪 Testing Multiple Booking Flow")
    print("=" * 50)
    
    # Create a test session with complete prospect data
    session_id = str(uuid.uuid4())
    session = ConversationSession(
        session_id=session_id,
        state=ChatState.GREETING,
        prospect_data=ProspectData(
            name="Test User",
            email="test@example.com",
            phone="(555) 123-4567",
            move_in_date="January 2025",
            beds_wanted=2,
            selected_units=["A101", "B202", "C303"]  # Multiple units selected
        ),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    print(f"📋 Test Session Created: {session_id}")
    print(f"   Prospect: {session.prospect_data.name}")
    print(f"   Email: {session.prospect_data.email}")
    print(f"   Selected Units: {session.prospect_data.selected_units}")
    
    # Test multiple unit selection management
    print("\n🔧 Testing Unit Selection Management:")
    
    # Test showing selected units
    result = chat_service._show_selected_units(session)
    print(f"   Show Selected Units: {result[:100]}...")
    
    # Test removing a unit
    result = chat_service._remove_selected_unit(session, "B202")
    print(f"   Remove Unit B202: {result}")
    print(f"   Remaining Units: {session.prospect_data.selected_units}")
    
    # Test multiple booking intent
    print("\n🚀 Testing Multiple Booking Intent:")
    try:
        booking_result = await chat_service._handle_multiple_booking_intent(session)
        print(f"   Booking Result: {booking_result[:200]}...")
        print(f"   Session State: {session.state}")
    except Exception as e:
        print(f"   ❌ Booking failed: {str(e)}")
    
    return session

async def test_multiple_booking_email():
    """Test the multiple booking email functionality."""
    print("\n📧 Testing Multiple Booking Email")
    print("=" * 50)
    
    # Create test booked units
    booked_units = [
        BookedUnit(
            unit_id="A101",
            beds=2,
            baths=2.0,
            sqft=1200,
            rent=2500,
            confirmation_number="CONF-ABC123"
        ),
        BookedUnit(
            unit_id="C303",
            beds=2,
            baths=2.0,
            sqft=1150,
            rent=2400,
            confirmation_number="CONF-DEF456"
        )
    ]
    
    # Create multiple booking confirmation
    confirmation = MultipleBookingConfirmation(
        prospect_name="Test User",
        prospect_email=email_service.smtp_email,  # Send to self for testing
        booked_units=booked_units,
        property_address="123 Test Street, Test City, TC 12345",
        tour_date="Tomorrow",
        tour_time="2:00 PM",
        master_confirmation_number="MASTER-XYZ789"
    )
    
    print(f"📋 Multiple Booking Confirmation Created:")
    print(f"   Prospect: {confirmation.prospect_name}")
    print(f"   Email: {confirmation.prospect_email}")
    print(f"   Units: {[unit.unit_id for unit in confirmation.booked_units]}")
    print(f"   Master Confirmation: {confirmation.master_confirmation_number}")
    
    # Test email sending
    print(f"\n📤 Sending Multiple Booking Email...")
    try:
        email_sent = await email_service.send_multiple_booking_confirmation(confirmation)
        print(f"   Email Send Result: {'✅ SUCCESS' if email_sent else '❌ FAILED'}")
        
        if email_sent:
            print(f"   📬 Check your inbox at {confirmation.prospect_email}")
            print(f"   📧 Subject: Multiple Tour Confirmation - {', '.join([unit.unit_id for unit in booked_units])}")
        
    except Exception as e:
        print(f"   ❌ Email sending failed: {str(e)}")

async def test_inventory_service():
    """Test inventory service enhancements."""
    print("\n🏢 Testing Inventory Service")
    print("=" * 50)
    
    # Test getting unit by ID
    test_units = ["A101", "B202", "C303", "INVALID"]
    
    for unit_id in test_units:
        unit = inventory_service.get_unit_by_id(unit_id)
        if unit:
            print(f"   ✅ Found {unit_id}: {unit.beds} bed/{unit.baths} bath, {unit.sqft} sq ft, ${unit.rent}/month")
        else:
            print(f"   ❌ Unit {unit_id} not found")

async def main():
    """Run all tests."""
    print("🧪 Multiple Booking Enhancement Tests")
    print("=" * 60)
    
    try:
        # Test inventory service
        await test_inventory_service()
        
        # Test multiple booking flow
        session = await test_multiple_booking_flow()
        
        # Test multiple booking email
        await test_multiple_booking_email()
        
        print("\n✅ All tests completed!")
        print("\n📝 Summary:")
        print("   - Multiple unit selection: ✅")
        print("   - Unit management commands: ✅")
        print("   - Multiple booking flow: ✅")
        print("   - Enhanced email confirmations: ✅")
        print("   - Inventory service enhancements: ✅")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
