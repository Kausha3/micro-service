#!/usr/bin/env python3
"""
Email Delivery Verification Tool

This script helps verify if emails are being delivered by testing
the complete booking flow and providing detailed feedback.
"""

import asyncio
import sys
from datetime import datetime
from models import TourConfirmation
from email_service import email_service
from chat_service import chat_service
from models import ChatMessage, ProspectData, ConversationSession, ChatState
import uuid

async def test_complete_booking_flow(test_email: str):
    """Test the complete booking flow with email delivery."""
    print(f"\n🧪 Testing Complete Booking Flow")
    print("=" * 60)
    print(f"Test Email: {test_email}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Create a test session with complete prospect data
        session = ConversationSession(
            session_id=str(uuid.uuid4()),
            state=ChatState.COLLECTING_INFO,
            prospect_data=ProspectData(
                name="Test User",
                email=test_email,
                phone="555-123-4567",
                move_in_date="May 2025",
                beds_wanted=2,
                property_address="123 Main St, Anytown, ST 12345"
            ),
            conversation_history=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        print("\n📋 Test Session Created:")
        print(f"   Name: {session.prospect_data.name}")
        print(f"   Email: {session.prospect_data.email}")
        print(f"   Phone: {session.prospect_data.phone}")
        print(f"   Move-in: {session.prospect_data.move_in_date}")
        print(f"   Bedrooms: {session.prospect_data.beds_wanted}")
        
        # Test the booking intent handling
        print(f"\n🎯 Testing Booking Intent...")
        booking_message = ChatMessage(
            message="I want to book a tour",
            session_id=session.session_id
        )
        
        # Process the booking message
        response = await chat_service.process_message(booking_message)
        
        print(f"\n📧 Booking Response:")
        print(f"   Response: {response.reply[:100]}...")
        print(f"   Session ID: {response.session_id}")
        
        # Check if email was mentioned in response
        email_mentioned = any(word in response.reply.lower() for word in [
            "email", "confirmation", "sent", "inbox", "spam"
        ])
        
        print(f"\n✅ Results:")
        print(f"   Booking processed: {'✅' if response.reply else '❌'}")
        print(f"   Email mentioned: {'✅' if email_mentioned else '❌'}")
        print(f"   Response length: {len(response.reply)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

async def test_direct_email_sending(test_email: str):
    """Test direct email sending without the chat flow."""
    print(f"\n📧 Testing Direct Email Sending")
    print("=" * 60)
    
    try:
        # Create a test tour confirmation
        confirmation = TourConfirmation(
            prospect_name="Test User",
            prospect_email=test_email,
            unit_id="TEST-101",
            property_address="123 Main St, Anytown, ST 12345",
            tour_date="Tomorrow",
            tour_time="2:00 PM"
        )
        
        print(f"📋 Test Confirmation:")
        print(f"   Name: {confirmation.prospect_name}")
        print(f"   Email: {confirmation.prospect_email}")
        print(f"   Unit: {confirmation.unit_id}")
        print(f"   Date: {confirmation.tour_date}")
        print(f"   Time: {confirmation.tour_time}")
        
        # Send the email
        print(f"\n📤 Sending email...")
        result = await email_service.send_tour_confirmation(confirmation)
        
        print(f"\n✅ Results:")
        print(f"   Email sent: {'✅' if result else '❌'}")
        
        if result:
            print(f"\n📬 Email Details:")
            print(f"   From: {email_service.smtp_email}")
            print(f"   To: {confirmation.prospect_email}")
            print(f"   Subject: Tour Confirmation - {confirmation.unit_id}")
            print(f"   Server: {email_service.smtp_server}:{email_service.smtp_port}")
        
        return result
        
    except Exception as e:
        print(f"❌ Direct email test failed: {str(e)}")
        return False

async def main():
    """Main function to run email delivery verification."""
    print("🚀 Email Delivery Verification Tool")
    print("=" * 60)
    
    # Get test email from command line or user input
    if len(sys.argv) > 1:
        test_email = sys.argv[1]
    else:
        test_email = input("Enter test email address: ").strip()
    
    if not test_email or "@" not in test_email:
        print("❌ Invalid email address")
        return
    
    print(f"📧 Testing email delivery to: {test_email}")
    
    # Test 1: Direct email sending
    print(f"\n" + "="*60)
    print("TEST 1: Direct Email Sending")
    print("="*60)
    direct_result = await test_direct_email_sending(test_email)
    
    # Test 2: Complete booking flow
    print(f"\n" + "="*60)
    print("TEST 2: Complete Booking Flow")
    print("="*60)
    flow_result = await test_complete_booking_flow(test_email)
    
    # Summary
    print(f"\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Direct Email Test: {'✅ PASSED' if direct_result else '❌ FAILED'}")
    print(f"Booking Flow Test: {'✅ PASSED' if flow_result else '❌ FAILED'}")
    
    if direct_result:
        print(f"\n✅ Email system is working correctly!")
        print(f"📋 Next steps:")
        print(f"   1. Check {test_email} inbox")
        print(f"   2. Check spam/junk folder")
        print(f"   3. Wait 1-2 minutes for delivery")
        print(f"   4. If not received, check email provider settings")
    else:
        print(f"\n❌ Email system has issues!")
        print(f"📋 Troubleshooting:")
        print(f"   1. Check SMTP credentials in .env file")
        print(f"   2. Verify Gmail App Password")
        print(f"   3. Check network connectivity")
        print(f"   4. Review server logs for errors")
    
    print(f"\n🔍 Additional Tips:")
    print(f"   - Gmail may delay delivery by 1-2 minutes")
    print(f"   - Check spam folder thoroughly")
    print(f"   - Some email providers block Gmail SMTP")
    print(f"   - Consider using SendGrid or Mailgun for production")

if __name__ == "__main__":
    asyncio.run(main())
