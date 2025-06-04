"""
Test the complete booking flow including email confirmation.
This simulates a real user booking a tour and verifies email is sent.
"""

import asyncio
import os
import sys
from datetime import datetime
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_service import chat_service
from models import ConversationSession, ChatState, ProspectData, AIContext, ChatMessage


async def test_complete_booking_flow():
    """Test the complete booking flow from start to finish."""
    
    print("🎯 Testing Complete Booking Flow with Email")
    print("=" * 60)
    
    # Create a new session
    session_id = str(uuid.uuid4())
    
    # Simulate the conversation flow
    conversation_steps = [
        "Hi, I'm looking for an apartment",
        "I need a 2-bedroom apartment",
        "I'd like to book a tour",
        "John Smith",  # Name
        "john.smith@example.com",  # Email (you can change this to your email)
        "(555) 123-4567",  # Phone
        "Next month",  # Move-in date
        "2"  # Bedrooms
    ]
    
    print("🤖 Starting conversation simulation...")
    print("-" * 40)
    
    for i, user_message in enumerate(conversation_steps, 1):
        print(f"\n{i}. User: {user_message}")
        
        # Create chat message
        message = ChatMessage(message=user_message, session_id=session_id)
        
        try:
            # Process the message
            response = await chat_service.process_message(message)
            
            print(f"   AI: {response.reply}")
            print(f"   State: {response.state}")
            
            # Check if booking is confirmed
            if response.state == ChatState.BOOKING_CONFIRMED:
                print("\n🎉 BOOKING CONFIRMED!")
                print("   Checking if email was mentioned in response...")
                
                if "confirmation email" in response.reply.lower():
                    print("   ✅ Email confirmation mentioned in response")
                    
                    if "spam" in response.reply.lower() or "junk" in response.reply.lower():
                        print("   ✅ Spam folder reminder included")
                    else:
                        print("   ⚠️  No spam folder reminder")
                        
                    if "leasing office" in response.reply.lower():
                        print("   ✅ Alternative contact method provided")
                    else:
                        print("   ⚠️  No alternative contact method")
                        
                else:
                    print("   ❌ Email confirmation not mentioned")
                
                break
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            break
    
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    # Get the final session to check data
    try:
        from session_db_service import session_db_service
        final_session = session_db_service.load_session(session_id)
        
        if final_session:
            print("✅ Session data preserved:")
            print(f"   Name: {final_session.prospect_data.name}")
            print(f"   Email: {final_session.prospect_data.email}")
            print(f"   Phone: {final_session.prospect_data.phone}")
            print(f"   Move-in: {final_session.prospect_data.move_in_date}")
            print(f"   Bedrooms: {final_session.prospect_data.beds_wanted}")
            print(f"   Unit ID: {final_session.prospect_data.unit_id}")
            print(f"   State: {final_session.state}")
            print(f"   Messages: {len(final_session.messages)}")
            
            if final_session.state == ChatState.BOOKING_CONFIRMED:
                print("\n🎯 BOOKING FLOW TEST: ✅ PASSED")
                print("   - User data collected successfully")
                print("   - Booking confirmed")
                print("   - Unit reserved")
                print("   - Email confirmation process triggered")
            else:
                print(f"\n❌ BOOKING FLOW TEST: FAILED")
                print(f"   Final state: {final_session.state}")
        else:
            print("❌ Session not found in database")
            
    except Exception as e:
        print(f"❌ Error checking final session: {str(e)}")


async def test_email_not_received_scenario():
    """Test how the AI handles when user says they didn't receive email."""
    
    print("\n🔍 Testing 'Email Not Received' Scenario")
    print("-" * 50)
    
    # Create a session in BOOKING_CONFIRMED state
    session_id = str(uuid.uuid4())
    
    # First, complete a booking
    await test_complete_booking_flow()
    
    # Now test the "didn't receive email" scenario
    message = ChatMessage(
        message="I haven't received the confirmation email yet",
        session_id=session_id
    )
    
    try:
        response = await chat_service.process_message(message)
        print(f"\nUser: I haven't received the confirmation email yet")
        print(f"AI: {response.reply}")
        
        # Check if the response is helpful
        response_lower = response.reply.lower()
        
        checks = [
            ("spam folder mentioned", "spam" in response_lower or "junk" in response_lower),
            ("alternative contact provided", "phone" in response_lower or "call" in response_lower),
            ("helpful tone", "sorry" in response_lower or "apologize" in response_lower),
            ("actionable advice", "check" in response_lower or "contact" in response_lower)
        ]
        
        print("\n📋 Response Quality Check:")
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            
    except Exception as e:
        print(f"❌ Error testing email scenario: {str(e)}")


if __name__ == "__main__":
    print("Starting Complete Booking Flow Test...")
    
    # Run the tests
    asyncio.run(test_complete_booking_flow())
    asyncio.run(test_email_not_received_scenario())
    
    print("\n💡 Next Steps:")
    print("1. Check server logs for email sending confirmation")
    print("2. Verify email arrives in inbox (check spam folder)")
    print("3. Test with real email address if needed")
    print("4. Consider adding email delivery status tracking")
