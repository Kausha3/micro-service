#!/usr/bin/env python3
"""
Email Delivery Test Tool

This script helps diagnose email delivery issues by testing various aspects
of email sending and providing detailed feedback.
"""

import asyncio
import sys
import os
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiosmtplib
import ssl
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class EmailDeliveryTester:
    def __init__(self):
        self.smtp_email = os.getenv("SMTP_EMAIL")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        
    async def test_basic_email_delivery(self, recipient_email: str):
        """Test basic email delivery to a specific recipient."""
        print(f"\n🧪 Testing Email Delivery to: {recipient_email}")
        print("=" * 60)
        
        try:
            # Create a simple test message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Email Delivery Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            message["From"] = f"Lead-to-Lease Test <{self.smtp_email}>"
            message["To"] = recipient_email
            message["Reply-To"] = self.smtp_email
            
            # Simple text content
            text_content = f"""
Email Delivery Test

This is a test email sent at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.

If you receive this email, the delivery system is working correctly.

From: {self.smtp_email}
To: {recipient_email}
Server: {self.smtp_server}:{self.smtp_port}

Test ID: {datetime.now().timestamp()}
"""
            
            # Simple HTML content
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Email Delivery Test</h1>
        </div>
        <div class="content">
            <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>From:</strong> {self.smtp_email}</p>
            <p><strong>To:</strong> {recipient_email}</p>
            <p><strong>Server:</strong> {self.smtp_server}:{self.smtp_port}</p>
            <p>If you receive this email, the delivery system is working correctly!</p>
            <p><strong>Test ID:</strong> {datetime.now().timestamp()}</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Add both text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Create SSL context
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            print(f"📧 Sending test email...")
            print(f"   From: {self.smtp_email}")
            print(f"   To: {recipient_email}")
            print(f"   Subject: {message['Subject']}")
            print(f"   Server: {self.smtp_server}:{self.smtp_port}")
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_email,
                password=self.smtp_password,
                tls_context=context,
            )
            
            print("✅ Email sent successfully!")
            print("\n📋 Next Steps:")
            print("1. Check the recipient's inbox")
            print("2. Check spam/junk folder")
            print("3. Wait 1-2 minutes for delivery")
            print("4. If not received, there may be delivery issues")
            
            return True
            
        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            return False
    
    async def test_multiple_recipients(self, recipients: list):
        """Test email delivery to multiple recipients."""
        print(f"\n🧪 Testing Email Delivery to Multiple Recipients")
        print("=" * 60)
        
        results = {}
        for recipient in recipients:
            print(f"\nTesting: {recipient}")
            result = await self.test_basic_email_delivery(recipient)
            results[recipient] = result
            
            # Wait between sends to avoid rate limiting
            await asyncio.sleep(2)
        
        print(f"\n📊 Summary:")
        for recipient, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"   {recipient}: {status}")
        
        return results

async def main():
    """Main function to run email delivery tests."""
    print("🚀 Email Delivery Test Tool")
    print("=" * 60)
    
    tester = EmailDeliveryTester()
    
    # Check configuration
    if not tester.smtp_email or not tester.smtp_password:
        print("❌ Email configuration not found!")
        print("Please ensure SMTP_EMAIL and SMTP_PASSWORD are set in your .env file")
        return
    
    print(f"📧 Configuration:")
    print(f"   SMTP Email: {tester.smtp_email}")
    print(f"   SMTP Server: {tester.smtp_server}:{tester.smtp_port}")
    
    # Get recipient email from command line or use default
    if len(sys.argv) > 1:
        recipient = sys.argv[1]
    else:
        recipient = input("\nEnter recipient email address: ").strip()
    
    if not recipient or "@" not in recipient:
        print("❌ Invalid email address")
        return
    
    # Run the test
    await tester.test_basic_email_delivery(recipient)
    
    print(f"\n🔍 Troubleshooting Tips:")
    print("1. If email was sent but not received:")
    print("   - Check spam/junk folder")
    print("   - Verify email address spelling")
    print("   - Check recipient's email provider settings")
    print("2. If sending failed:")
    print("   - Check SMTP credentials")
    print("   - Verify Gmail App Password")
    print("   - Check network connectivity")

if __name__ == "__main__":
    asyncio.run(main())
