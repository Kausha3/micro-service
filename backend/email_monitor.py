#!/usr/bin/env python3
"""
Real-time Email Delivery Monitor

This script monitors email delivery in real-time and provides detailed
feedback about the email sending process.
"""

import asyncio
import sys
import os
from datetime import datetime
from dotenv import load_dotenv
from email_service import email_service
from models import TourConfirmation

# Load environment variables
load_dotenv()

class EmailMonitor:
    def __init__(self):
        self.email_service = email_service
        
    async def test_real_time_delivery(self, recipient_email: str):
        """Test real-time email delivery with detailed monitoring."""
        
        print("🚀 REAL-TIME EMAIL DELIVERY TEST")
        print("=" * 60)
        print(f"📧 Recipient: {recipient_email}")
        print(f"⏰ Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # Create test confirmation
        confirmation = TourConfirmation(
            prospect_name="Test User",
            prospect_email=recipient_email,
            unit_id="TEST-101",
            property_address=self.email_service.property_address,
            tour_date="Tomorrow",
            tour_time="2:00 PM"
        )
        
        print("📋 Test Configuration:")
        print(f"   SMTP Server: {self.email_service.smtp_server}:{self.email_service.smtp_port}")
        print(f"   From Email: {self.email_service.smtp_email}")
        print(f"   Timeout: {self.email_service.email_timeout} seconds")
        print(f"   Property: {self.email_service.property_name}")
        print()
        
        # Monitor the sending process
        print("🔄 Starting email delivery process...")
        start_time = datetime.now()
        
        try:
            result = await self.email_service.send_tour_confirmation(confirmation)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print()
            print("📊 DELIVERY RESULTS:")
            print("=" * 40)
            print(f"✅ Success: {'YES' if result else 'NO'}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"🏁 End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if result:
                print()
                print("🎉 EMAIL SENT SUCCESSFULLY!")
                print("📬 Next Steps:")
                print("   1. Check recipient's inbox immediately")
                print("   2. Check spam/junk folder")
                print("   3. Email should arrive within 1-5 minutes")
                print("   4. If not received, check server logs above")
                
                # Provide real-time guidance
                print()
                print("🔍 TROUBLESHOOTING CHECKLIST:")
                print("   ✅ SMTP connection successful")
                print("   ✅ Authentication successful") 
                print("   ✅ Message sent to server")
                print("   ⏳ Waiting for delivery...")
                print()
                print("   If email not received:")
                print("   • Check spam/junk folder first")
                print("   • Verify email address spelling")
                print("   • Wait up to 5 minutes for delivery")
                print("   • Check recipient's email provider settings")
                
            else:
                print()
                print("❌ EMAIL SENDING FAILED!")
                print("🔍 Check the error messages above for details")
                print("💡 Common issues:")
                print("   • SMTP authentication problems")
                print("   • Network connectivity issues")
                print("   • Invalid email configuration")
                
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print()
            print("💥 EXCEPTION OCCURRED:")
            print("=" * 40)
            print(f"❌ Error: {str(e)}")
            print(f"⏱️  Duration: {duration:.2f} seconds")
            print(f"🏁 End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
        print()
        print("=" * 60)
        
    async def monitor_email_config(self):
        """Monitor and validate email configuration."""
        
        print("🔧 EMAIL CONFIGURATION MONITOR")
        print("=" * 50)
        
        # Check all configuration values
        config_items = [
            ("SMTP Email", self.email_service.smtp_email),
            ("SMTP Password", "***" if self.email_service.smtp_password else "Not Set"),
            ("SMTP Server", self.email_service.smtp_server),
            ("SMTP Port", self.email_service.smtp_port),
            ("Email Timeout", f"{self.email_service.email_timeout} seconds"),
            ("Property Name", self.email_service.property_name),
            ("Property Address", self.email_service.property_address),
            ("Leasing Phone", self.email_service.leasing_office_phone),
        ]
        
        print("📋 Current Configuration:")
        for name, value in config_items:
            status = "✅" if value and str(value) != "Not Set" else "❌"
            print(f"   {status} {name}: {value}")
        
        print()
        
        # Validate configuration
        is_valid = self.email_service._validate_email_config()
        print(f"🔍 Configuration Valid: {'✅ YES' if is_valid else '❌ NO'}")
        
        if not is_valid:
            print()
            print("⚠️  CONFIGURATION ISSUES DETECTED:")
            print("   Please check your .env file and ensure all email settings are correct")
            
        return is_valid

async def main():
    """Main function to run email monitoring."""
    
    monitor = EmailMonitor()
    
    # Check configuration first
    print("🔍 Checking email configuration...")
    config_valid = await monitor.monitor_email_config()
    
    if not config_valid:
        print("\n❌ Email configuration is invalid. Please fix before testing.")
        return
    
    print("\n" + "=" * 60)
    
    # Get recipient email
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = input("\nEnter recipient email address for testing: ").strip()
    
    if not recipient or "@" not in recipient:
        print("❌ Invalid email address")
        return
    
    # Run real-time delivery test
    await monitor.test_real_time_delivery(recipient)

if __name__ == "__main__":
    asyncio.run(main())
