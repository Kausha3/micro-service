import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import TourConfirmation
import os
import uuid
from datetime import datetime, timedelta
import logging
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service for sending tour confirmation emails.
    Uses SMTP (Gmail by default) to send emails.
    """

    def __init__(self):
        self.smtp_email = os.getenv("SMTP_EMAIL", "your-email@gmail.com")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "your-app-password")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.property_address = os.getenv(
            "PROPERTY_ADDRESS", "123 Main St, Anytown, ST 12345"
        )
        self.leasing_office_phone = os.getenv("LEASING_OFFICE_PHONE", "(555) 123-4567")
        self.property_name = os.getenv(
            "PROPERTY_NAME", "Luxury Apartments at Main Street"
        )
        self.email_timeout = int(os.getenv("EMAIL_TIMEOUT", "30"))  # Default 30 seconds

        # Log initialization details for debugging
        logger.info("🔧 EmailService initialized with configuration:")
        logger.info(f"   SMTP Email: {self.smtp_email}")
        logger.info(f"   SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"   Property: {self.property_name}")
        logger.info(f"   Timeout: {self.email_timeout}s")

        # Validate configuration on startup
        config_valid = self._validate_email_config()
        logger.info(f"   Configuration Valid: {'✅' if config_valid else '❌'}")

    async def send_tour_confirmation(self, confirmation: TourConfirmation) -> bool:
        """
        Send a tour confirmation email to the prospect with retry logic.
        Returns True if successful, False otherwise.
        """
        logger.info("🚀 EMAIL SERVICE CALLED - Starting tour confirmation email process")
        logger.info(f"   📧 Recipient: {confirmation.prospect_email}")
        logger.info(f"   🏠 Unit: {confirmation.unit_id}")
        logger.info(f"   👤 Prospect: {confirmation.prospect_name}")

        # Validate email configuration
        if not self._validate_email_config():
            logger.error("❌ Email configuration is invalid - aborting email send")
            return False

        # Validate recipient email address
        if not confirmation.prospect_email or "@" not in confirmation.prospect_email:
            logger.error(f"❌ Invalid recipient email address: {confirmation.prospect_email}")
            return False

        logger.info("✅ Email configuration and recipient validation passed")

        # Retry logic for real-time delivery
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds

        for attempt in range(max_retries):
            try:
                logger.info(f"📧 Email sending attempt {attempt + 1}/{max_retries}")
                success = await self._send_email_attempt(confirmation)
                if success:
                    logger.info(f"✅ Email sent successfully on attempt {attempt + 1}")
                    return True

            except Exception as e:
                logger.warning(f"⚠️ Email attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        logger.error(f"❌ All {max_retries} email attempts failed")
        return False

    async def _send_email_attempt(self, confirmation: TourConfirmation) -> bool:
        """
        Single attempt to send email with proper error handling.
        """
        try:
            # Log the confirmation details
            logger.info(f"🎯 Processing tour confirmation:")
            logger.info(f"   Prospect: {confirmation.prospect_name}")
            logger.info(f"   Email: {confirmation.prospect_email}")
            logger.info(f"   Unit: {confirmation.unit_id}")
            logger.info(f"   Date: {confirmation.tour_date}")
            logger.info(f"   Time: {confirmation.tour_time}")

            # Create email message with proper headers for better deliverability
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Tour Confirmation - {confirmation.unit_id}"
            message["From"] = f"{self.property_name} <{self.smtp_email}>"
            message["To"] = confirmation.prospect_email
            message["Reply-To"] = self.smtp_email
            message["Message-ID"] = f"<{uuid.uuid4()}@{self.smtp_server}>"
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Add headers to improve deliverability
            message["X-Mailer"] = "Lead-to-Lease Chat Concierge v1.0"
            message["X-Priority"] = "3"  # Normal priority

            # Create email content
            text_content = self._create_text_content(confirmation)
            html_content = self._create_html_content(confirmation)

            # Add both text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send email
            import ssl

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Log email details before sending
            logger.info(f"📧 Attempting to send email:")
            logger.info(f"   From: {self.smtp_email}")
            logger.info(f"   To: {confirmation.prospect_email}")
            logger.info(f"   Subject: Tour Confirmation - {confirmation.unit_id}")
            logger.info(f"   SMTP Server: {self.smtp_server}:{self.smtp_port}")

            # Send email with explicit connection management for reliability
            smtp_client = aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                timeout=self.email_timeout,  # Configurable timeout for real-time delivery
                start_tls=True,
                tls_context=context,
            )

            try:
                # Establish connection
                logger.info("🔌 Connecting to SMTP server...")
                await smtp_client.connect()
                logger.info("✅ SMTP connection established")

                # Authenticate
                logger.info("🔐 Authenticating with SMTP server...")
                await smtp_client.login(self.smtp_email, self.smtp_password)
                logger.info("✅ SMTP authentication successful")

                # Send the message
                logger.info("📤 Sending email message...")
                send_result = await smtp_client.send_message(message)
                logger.info("✅ Email message sent successfully")

                # Log send result for debugging
                if send_result:
                    logger.info(f"📬 SMTP send result: {send_result}")
                else:
                    logger.info("📬 SMTP send completed (no explicit result)")

            finally:
                # Always close the connection
                try:
                    await smtp_client.quit()
                    logger.info("🔌 SMTP connection closed")
                except Exception as close_error:
                    logger.warning(f"⚠️ Error closing SMTP connection: {close_error}")

            # Log successful delivery with timestamp
            delivery_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"🎉 EMAIL DELIVERY SUCCESS at {delivery_time}")
            logger.info(f"   ✅ Recipient: {confirmation.prospect_email}")
            logger.info(f"   ✅ Unit: {confirmation.unit_id}")
            logger.info(f"   ✅ Subject: Tour Confirmation - {confirmation.unit_id}")
            logger.info(f"   ✅ From: {self.smtp_email}")
            logger.info(f"   ✅ SMTP Server: {self.smtp_server}:{self.smtp_port}")

            # Additional verification logging
            logger.info(f"📬 Email content summary:")
            logger.info(f"   Text length: {len(text_content)} characters")
            logger.info(f"   HTML length: {len(html_content)} characters")
            logger.info(f"   Message size: {len(str(message))} bytes")

            # Important delivery notes
            logger.info(f"📧 DELIVERY STATUS: Email successfully submitted to SMTP server")
            logger.info(f"📧 NEXT STEPS: Email should arrive within 1-5 minutes")
            logger.info(f"📧 USER GUIDANCE: Check inbox and spam/junk folder")

            return True

        except aiosmtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication failed: {str(e)}")
            logger.error("Please check your Gmail credentials and ensure:")
            logger.error("1. 2-Factor Authentication is enabled on your Gmail account")
            logger.error("2. You're using an App Password (not your regular password)")
            logger.error("3. The App Password has no spaces")
            logger.error(
                "4. 'Less secure app access' is enabled (if not using App Password)"
            )
            return False
        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def _validate_email_config(self) -> bool:
        """
        Validate email configuration.
        Returns True if configuration is valid, False otherwise.
        """
        if not self.smtp_email or self.smtp_email == "your-email@gmail.com":
            logger.error("SMTP_EMAIL is not configured")
            return False

        if not self.smtp_password or self.smtp_password == "your-app-password":
            logger.error("SMTP_PASSWORD is not configured")
            return False

        if not self.smtp_server:
            logger.error("SMTP_SERVER is not configured")
            return False

        if not self.smtp_port:
            logger.error("SMTP_PORT is not configured")
            return False

        # Check for common App Password format issues
        if " " in self.smtp_password:
            logger.warning(
                "SMTP_PASSWORD contains spaces - this may cause authentication issues"
            )

        return True

    def _create_text_content(self, confirmation: TourConfirmation) -> str:
        """Create enhanced plain text email content."""
        return f"""
Dear {confirmation.prospect_name},

Thank you for your interest in {self.property_name}! We're excited to confirm your apartment tour.

TOUR DETAILS:
Property: {self.property_name}
Address: {confirmation.property_address}
Unit: {confirmation.unit_id}
Date: {confirmation.tour_date}
Time: {confirmation.tour_time}

WHAT TO BRING:
- Valid government-issued photo ID
- Proof of income (recent pay stubs or employment letter)
- Application fee ($50 - if you decide to apply)

CONTACT INFORMATION:
Leasing Office: {self.leasing_office_phone}
Email: {self.smtp_email}

Please arrive 5 minutes early. If you need to reschedule or have any questions, please call our leasing office or reply to this email.

We look forward to showing you your potential new home!

Best regards,
The Leasing Team
{self.property_name}

---
This email was sent to {confirmation.prospect_email} regarding your tour request.
If you did not request this tour, please contact us at {self.leasing_office_phone}.

{self.property_name}
{confirmation.property_address}
Phone: {self.leasing_office_phone}
Email: {self.smtp_email}
        """.strip()

    def _create_html_content(self, confirmation: TourConfirmation) -> str:
        """Create enhanced HTML email content."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .details {{ background-color: white; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
        .bring-list {{ background-color: white; padding: 15px; border-left: 4px solid #e74c3c; margin: 20px 0; }}
        .contact-info {{ background-color: white; padding: 15px; border-left: 4px solid #27ae60; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Tour Confirmation</h1>
            <p>{self.property_name}</p>
        </div>
        <div class="content">
            <p>Dear {confirmation.prospect_name},</p>
            <p>Thank you for your interest in {self.property_name}! We're excited to confirm your apartment tour.</p>

            <div class="details">
                <h3>📅 Tour Details</h3>
                <p><strong>Property:</strong> {self.property_name}</p>
                <p><strong>Address:</strong> {confirmation.property_address}</p>
                <p><strong>Unit:</strong> {confirmation.unit_id}</p>
                <p><strong>Date:</strong> {confirmation.tour_date}</p>
                <p><strong>Time:</strong> {confirmation.tour_time}</p>
            </div>

            <div class="bring-list">
                <h3>📋 What to Bring</h3>
                <ul>
                    <li>Valid government-issued photo ID</li>
                    <li>Proof of income (recent pay stubs or employment letter)</li>
                    <li>Application fee ($50 - if you decide to apply)</li>
                </ul>
            </div>

            <div class="contact-info">
                <h3>📞 Contact Information</h3>
                <p><strong>Leasing Office:</strong> {self.leasing_office_phone}</p>
                <p><strong>Email:</strong> {self.smtp_email}</p>
            </div>

            <p>Please arrive 5 minutes early. If you need to reschedule or have any questions, please call our leasing office or reply to this email.</p>
            <p><strong>We look forward to showing you your potential new home!</strong></p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Leasing Team<br>{self.property_name}</p>
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #666;">
                This email was sent to {confirmation.prospect_email} regarding your tour request.<br>
                If you did not request this tour, please contact us at {self.leasing_office_phone}.<br><br>
                {self.property_name}<br>
                {confirmation.property_address}<br>
                Phone: {self.leasing_office_phone}<br>
                Email: {self.smtp_email}
            </p>
        </div>
    </div>
</body>
</html>
        """.strip()

    def generate_tour_slot(self) -> tuple[str, str]:
        """
        Generate a suggested tour date and time.
        Returns (date_string, time_string).
        """
        # Suggest tomorrow at 2 PM
        tomorrow = datetime.now() + timedelta(days=1)
        date_str = tomorrow.strftime("%A, %B %d, %Y")
        time_str = "2:00 PM"

        return date_str, time_str


# Global instance
email_service = EmailService()
