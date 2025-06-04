"""
Debug email functionality to identify why emails aren't being sent.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from email_service import email_service
from models import TourConfirmation


async def debug_email_service():
    """Debug the email service step by step."""
    
    print("🔍 Debugging Email Service")
    print("=" * 50)
    
    # Check configuration
    print("📧 Email Configuration:")
    print(f"   SMTP Email: {email_service.smtp_email}")
    print(f"   SMTP Server: {email_service.smtp_server}")
    print(f"   SMTP Port: {email_service.smtp_port}")
    print(f"   Property Name: {email_service.property_name}")
    print()
    
    # Validate configuration
    print("✅ Validating Configuration:")
    is_valid = email_service._validate_email_config()
    print(f"   Configuration Valid: {is_valid}")
    
    if not is_valid:
        print("❌ Email configuration is invalid. Please check your .env file.")
        return
    
    print()
    
    # Test email sending
    print("📤 Testing Email Sending:")
    
    # Create test confirmation
    confirmation = TourConfirmation(
        prospect_name="Test User",
        prospect_email=email_service.smtp_email,  # Send to self for testing
        unit_id="B301",
        property_address=email_service.property_address,
        tour_date="Tomorrow",
        tour_time="2:00 PM"
    )
    
    print(f"   Sending test email to: {confirmation.prospect_email}")
    
    try:
        result = await email_service.send_tour_confirmation(confirmation)
        print(f"   Email Send Result: {result}")
        
        if result:
            print("✅ Email sent successfully!")
            print("   Check your inbox (and spam folder) for the confirmation email.")
        else:
            print("❌ Email sending failed.")
            print("   Check the server logs for detailed error messages.")
            
    except Exception as e:
        print(f"❌ Exception occurred: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_smtp_connection():
    """Test SMTP connection separately."""
    
    print("\n🔌 Testing SMTP Connection:")
    print("-" * 30)
    
    try:
        import aiosmtplib
        import ssl
        
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        print(f"   Connecting to {email_service.smtp_server}:{email_service.smtp_port}")
        
        # Test connection
        smtp = aiosmtplib.SMTP(
            hostname=email_service.smtp_server,
            port=email_service.smtp_port,
            start_tls=True,
            tls_context=context,
        )
        
        await smtp.connect()
        print("   ✅ Connected to SMTP server")
        
        await smtp.login(email_service.smtp_email, email_service.smtp_password)
        print("   ✅ SMTP authentication successful")
        
        await smtp.quit()
        print("   ✅ SMTP connection test completed successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ SMTP connection failed: {str(e)}")
        return False


async def check_email_in_booking_flow():
    """Check if email is being called in the booking flow."""
    
    print("\n🔄 Checking Booking Flow:")
    print("-" * 30)
    
    # Import chat service to check booking flow
    from chat_service import chat_service
    from models import ConversationSession, ChatState, ProspectData, AIContext
    from datetime import datetime
    import uuid
    
    # Create a test session with complete data
    session = ConversationSession(
        session_id=str(uuid.uuid4()),
        state=ChatState.READY_TO_BOOK,
        prospect_data=ProspectData(
            name="Test User",
            email=email_service.smtp_email,
            phone="(555) 123-4567",
            move_in_date="Next month",
            beds_wanted=2
        ),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    print("   Testing booking flow with complete prospect data...")
    
    try:
        # Test the booking intent handler
        result = await chat_service._handle_booking_intent(session)
        print(f"   Booking result: {result[:100]}...")
        
        if "confirmation email" in result.lower():
            print("   ✅ Booking flow mentions sending confirmation email")
        else:
            print("   ⚠️  Booking flow doesn't mention email confirmation")
            
    except Exception as e:
        print(f"   ❌ Error in booking flow: {str(e)}")


if __name__ == "__main__":
    print("Starting Email Debug Session...")
    
    # Run all debug tests
    asyncio.run(debug_email_service())
    asyncio.run(test_smtp_connection())
    asyncio.run(check_email_in_booking_flow())
    
    print("\n🎯 Debug Summary:")
    print("=" * 50)
    print("1. Check if email configuration is valid")
    print("2. Test SMTP connection and authentication")
    print("3. Test actual email sending")
    print("4. Verify booking flow calls email service")
    print("\nIf all tests pass but users still don't receive emails,")
    print("check spam folders and Gmail security settings.")
