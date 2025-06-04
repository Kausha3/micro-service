import asyncio
import logging
import os
import uuid
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib
from dotenv import load_dotenv

from models import MultipleBookingConfirmation, TourConfirmation

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EmailService:
    """
    Professional email service for apartment tour confirmations and notifications.

    This service handles all email communications for the Lead-to-Lease Chat Concierge,
    providing reliable, professional email delivery with comprehensive error handling
    and retry logic for production environments.

    ## Key Features
    - **Multi-Provider SMTP Support**: Configurable for Gmail, Outlook, and other providers
    - **Professional Templates**: Mobile-responsive HTML emails with property branding
    - **Retry Logic**: Exponential backoff for reliable delivery in production
    - **Multiple Booking Support**: Comprehensive emails for multi-unit bookings
    - **Delivery Tracking**: Detailed logging for monitoring and debugging
    - **Configuration Validation**: Startup validation of email settings

    ## Email Types
    1. **Single Tour Confirmation**: Individual apartment tour booking
    2. **Multiple Tour Confirmation**: Multi-unit tour booking with detailed tables
    3. **Error Notifications**: Internal error reporting (future enhancement)

    ## SMTP Configuration
    Supports standard SMTP providers with environment variables:
    - SMTP_EMAIL: Sender email address
    - SMTP_PASSWORD: App password or SMTP password
    - SMTP_SERVER: SMTP server hostname (default: smtp.gmail.com)
    - SMTP_PORT: SMTP port (default: 587 for TLS)

    ## Template Features
    - **Mobile-Responsive Design**: Optimized for all devices
    - **Professional Branding**: Property name and contact information
    - **Clear Call-to-Actions**: What to bring, contact information
    - **Accessibility**: High contrast, readable fonts
    - **Deliverability**: Proper headers and formatting for spam prevention

    ## Error Handling
    - **Authentication Errors**: Clear guidance for Gmail App Passwords
    - **Network Timeouts**: Configurable timeout with retry logic
    - **SMTP Errors**: Detailed error logging and graceful degradation
    - **Configuration Validation**: Startup checks for missing settings

    Attributes:
        smtp_email (str): Configured sender email address
        smtp_password (str): SMTP authentication password
        smtp_server (str): SMTP server hostname
        smtp_port (int): SMTP server port
        property_address (str): Property address for email content
        leasing_office_phone (str): Contact phone number
        property_name (str): Property name for branding
        email_timeout (int): SMTP timeout in seconds
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
        logger.info(
            "🚀 EMAIL SERVICE CALLED - Starting tour confirmation email process"
        )
        logger.info(f"   📧 Recipient: {confirmation.prospect_email}")
        logger.info(f"   🏠 Unit: {confirmation.unit_id}")
        logger.info(f"   👤 Prospect: {confirmation.prospect_name}")

        # Validate email configuration
        if not self._validate_email_config():
            logger.error("❌ Email configuration is invalid - aborting email send")
            return False

        # Validate recipient email address
        if not confirmation.prospect_email or "@" not in confirmation.prospect_email:
            logger.error(
                f"❌ Invalid recipient email address: {confirmation.prospect_email}"
            )
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
            logger.info(
                f"📧 DELIVERY STATUS: Email successfully submitted to SMTP server"
            )
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

        # nosec B105 - Checking for default placeholder password, not hardcoded secret
        if (
            not self.smtp_password
            or self.smtp_password == "your-app-password"  # nosec B105
        ):
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

    async def send_multiple_booking_confirmation(
        self, confirmation: MultipleBookingConfirmation
    ) -> bool:
        """
        Send a multiple booking confirmation email to the prospect with retry logic.
        Returns True if successful, False otherwise.
        """
        logger.info(
            "🚀 MULTIPLE BOOKING EMAIL SERVICE CALLED - Starting multiple tour confirmation email process"
        )
        logger.info(f"   📧 Recipient: {confirmation.prospect_email}")
        logger.info(
            f"   🏠 Units: {[unit.unit_id for unit in confirmation.booked_units]}"
        )
        logger.info(f"   👤 Prospect: {confirmation.prospect_name}")
        logger.info(
            f"   📋 Master Confirmation: {confirmation.master_confirmation_number}"
        )

        # Validate email configuration
        if not self._validate_email_config():
            logger.error("❌ Email configuration is invalid - aborting email send")
            return False

        # Validate recipient email
        if not confirmation.prospect_email:
            logger.error("❌ Recipient email is empty - aborting email send")
            return False

        logger.info("✅ Email configuration and recipient validation passed")

        # Retry logic for real-time delivery
        max_retries = 3
        retry_delay = 2  # Start with 2 seconds

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"📧 Multiple booking email sending attempt {attempt + 1}/{max_retries}"
                )
                success = await self._send_multiple_booking_email_attempt(confirmation)
                if success:
                    logger.info(
                        f"✅ Multiple booking email sent successfully on attempt {attempt + 1}"
                    )
                    return True

            except Exception as e:
                logger.warning(
                    f"⚠️ Multiple booking email attempt {attempt + 1} failed: {str(e)}"
                )
                if attempt < max_retries - 1:  # Don't sleep on last attempt
                    logger.info(f"🔄 Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff

        logger.error(f"❌ All {max_retries} multiple booking email attempts failed")
        return False

    async def _send_multiple_booking_email_attempt(
        self, confirmation: MultipleBookingConfirmation
    ) -> bool:
        """
        Single attempt to send multiple booking email with proper error handling.
        """
        try:
            # Log the confirmation details
            logger.info(f"🎯 Processing multiple booking confirmation:")
            logger.info(f"   Prospect: {confirmation.prospect_name}")
            logger.info(f"   Email: {confirmation.prospect_email}")
            logger.info(
                f"   Units: {[unit.unit_id for unit in confirmation.booked_units]}"
            )
            logger.info(f"   Date: {confirmation.tour_date}")
            logger.info(f"   Time: {confirmation.tour_time}")
            logger.info(
                f"   Master Confirmation: {confirmation.master_confirmation_number}"
            )

            # Create email message with proper headers for better deliverability
            message = MIMEMultipart("alternative")
            unit_list = ", ".join([unit.unit_id for unit in confirmation.booked_units])
            message["Subject"] = f"Multiple Tour Confirmation - {unit_list}"
            message["From"] = f"{self.property_name} <{self.smtp_email}>"
            message["To"] = confirmation.prospect_email
            message["Reply-To"] = self.smtp_email
            message["Message-ID"] = f"<{uuid.uuid4()}@{self.smtp_server}>"
            message["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %z")

            # Add headers to improve deliverability
            message["X-Mailer"] = "Lead-to-Lease Chat Concierge v1.0"
            message["X-Priority"] = "3"  # Normal priority

            # Create email content
            text_content = self._create_multiple_booking_text_content(confirmation)
            html_content = self._create_multiple_booking_html_content(confirmation)

            # Add both text and HTML parts
            text_part = MIMEText(text_content, "plain")
            html_part = MIMEText(html_content, "html")

            message.attach(text_part)
            message.attach(html_part)

            # Send email using the same SMTP logic as single booking
            import ssl

            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            # Log email details before sending
            logger.info(f"📧 Attempting to send multiple booking email:")
            logger.info(f"   From: {self.smtp_email}")
            logger.info(f"   To: {confirmation.prospect_email}")
            logger.info(f"   Subject: Multiple Tour Confirmation - {unit_list}")
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
                await smtp_client.connect()
                await smtp_client.login(self.smtp_email, self.smtp_password)
                await smtp_client.send_message(message)
                await smtp_client.quit()
            except Exception as smtp_error:
                logger.error(f"SMTP operation failed: {str(smtp_error)}")
                try:
                    await smtp_client.quit()
                except Exception as cleanup_error:
                    logger.debug(f"SMTP cleanup error (ignored): {cleanup_error}")
                raise smtp_error

            # Log successful delivery with timestamp
            delivery_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(
                f"🎉 MULTIPLE BOOKING EMAIL DELIVERY SUCCESS at {delivery_time}"
            )
            logger.info(f"   ✅ Recipient: {confirmation.prospect_email}")
            logger.info(f"   ✅ Units: {unit_list}")
            logger.info(
                f"   ✅ Master Confirmation: {confirmation.master_confirmation_number}"
            )
            logger.info(f"   ✅ From: {self.smtp_email}")
            logger.info(f"   ✅ SMTP Server: {self.smtp_server}:{self.smtp_port}")

            # Additional verification logging
            logger.info(f"📬 Multiple booking email content summary:")
            logger.info(f"   Text length: {len(text_content)} characters")
            logger.info(f"   HTML length: {len(html_content)} characters")
            logger.info(f"   Message size: {len(str(message))} bytes")

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
            logger.error(f"Failed to send multiple booking email: {str(e)}")
            return False

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

    def generate_confirmation_number(self) -> str:
        """
        Generate a unique confirmation number.
        Returns a string like "CONF-ABC123"
        """
        return f"CONF-{uuid.uuid4().hex[:6].upper()}"

    def _create_multiple_booking_text_content(
        self, confirmation: MultipleBookingConfirmation
    ) -> str:
        """Create enhanced plain text email content for multiple bookings."""

        # Create unit details section
        unit_details = []
        for unit in confirmation.booked_units:
            unit_details.append(
                f"  • Unit {unit.unit_id}: {unit.beds} bed/{unit.baths} bath, "
                f"{unit.sqft} sq ft, ${unit.rent:,}/month (Confirmation: {unit.confirmation_number})"
            )

        unit_details_text = "\n".join(unit_details)

        return f"""
Dear {confirmation.prospect_name},

Thank you for your interest in {self.property_name}! We're excited to confirm your apartment tours for multiple units.

TOUR DETAILS:
Property: {self.property_name}
Address: {confirmation.property_address}
Date: {confirmation.tour_date}
Time: {confirmation.tour_time}
Master Confirmation Number: {confirmation.master_confirmation_number}

BOOKED UNITS ({len(confirmation.booked_units)} units):
{unit_details_text}

WHAT TO BRING:
- Valid government-issued photo ID
- Proof of income (recent pay stubs or employment letter)
- Application fee ($50 per unit - if you decide to apply)

CONTACT INFORMATION:
Leasing Office: {self.leasing_office_phone}
Email: {self.smtp_email}

Please arrive 5 minutes early for your comprehensive tour. We'll show you all {len(confirmation.booked_units)} units during your visit. If you need to reschedule or have any questions, please call our leasing office or reply to this email.

We look forward to showing you your potential new home options!

Best regards,
The Leasing Team
{self.property_name}

---
This email was sent to {confirmation.prospect_email} regarding your multiple unit tour request.
If you did not request these tours, please contact us at {self.leasing_office_phone}.

{self.property_name}
{confirmation.property_address}
Phone: {self.leasing_office_phone}
Email: {self.smtp_email}
        """.strip()

    def _create_multiple_booking_html_content(
        self, confirmation: MultipleBookingConfirmation
    ) -> str:
        """Create enhanced HTML email content for multiple bookings."""

        # Create unit details section
        unit_details_html = []
        for unit in confirmation.booked_units:
            unit_details_html.append(
                f"""
                <tr>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">
                        <strong>Unit {unit.unit_id}</strong>
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">
                        {unit.beds} bed / {unit.baths} bath
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">
                        {unit.sqft} sq ft
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee;">
                        ${unit.rent:,}/month
                    </td>
                    <td style="padding: 10px; border-bottom: 1px solid #eee; font-size: 12px; color: #666;">
                        {unit.confirmation_number}
                    </td>
                </tr>
            """
            )

        unit_table_rows = "".join(unit_details_html)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 700px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .details {{ background-color: white; padding: 15px; border-left: 4px solid #3498db; margin: 20px 0; }}
        .units-table {{ background-color: white; padding: 15px; border-left: 4px solid #9b59b6; margin: 20px 0; }}
        .bring-list {{ background-color: white; padding: 15px; border-left: 4px solid #e74c3c; margin: 20px 0; }}
        .contact-info {{ background-color: white; padding: 15px; border-left: 4px solid #27ae60; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #666; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th {{ background-color: #f8f9fa; padding: 12px; text-align: left; border-bottom: 2px solid #dee2e6; }}
        td {{ padding: 10px; border-bottom: 1px solid #eee; }}
        ul {{ margin: 10px 0; padding-left: 20px; }}
        .highlight {{ background-color: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 Multiple Tour Confirmation</h1>
            <p>{self.property_name}</p>
        </div>
        <div class="content">
            <p>Dear {confirmation.prospect_name},</p>
            <p>Thank you for your interest in {self.property_name}! We're excited to confirm your apartment tours for <strong>{len(confirmation.booked_units)} units</strong>.</p>

            <div class="details">
                <h3>📅 Tour Details</h3>
                <p><strong>Property:</strong> {self.property_name}</p>
                <p><strong>Address:</strong> {confirmation.property_address}</p>
                <p><strong>Date:</strong> {confirmation.tour_date}</p>
                <p><strong>Time:</strong> {confirmation.tour_time}</p>
                <p><strong>Master Confirmation:</strong> <code>{confirmation.master_confirmation_number}</code></p>
            </div>

            <div class="units-table">
                <h3>🏢 Your Booked Units ({len(confirmation.booked_units)} units)</h3>
                <table>
                    <thead>
                        <tr>
                            <th>Unit</th>
                            <th>Bed/Bath</th>
                            <th>Size</th>
                            <th>Rent</th>
                            <th>Confirmation #</th>
                        </tr>
                    </thead>
                    <tbody>
                        {unit_table_rows}
                    </tbody>
                </table>
            </div>

            <div class="bring-list">
                <h3>📋 What to Bring</h3>
                <ul>
                    <li>Valid government-issued photo ID</li>
                    <li>Proof of income (recent pay stubs or employment letter)</li>
                    <li>Application fee ($50 per unit - if you decide to apply)</li>
                </ul>
            </div>

            <div class="contact-info">
                <h3>📞 Contact Information</h3>
                <p><strong>Leasing Office:</strong> {self.leasing_office_phone}</p>
                <p><strong>Email:</strong> {self.smtp_email}</p>
            </div>

            <div class="highlight">
                <p><strong>💡 Tour Information:</strong> Please arrive 5 minutes early for your comprehensive tour. We'll show you all {len(confirmation.booked_units)} units during your visit, allowing you to compare and make the best choice for your needs.</p>
            </div>

            <p>If you need to reschedule or have any questions, please call our leasing office or reply to this email.</p>
            <p><strong>We look forward to showing you your potential new home options!</strong></p>
        </div>
        <div class="footer">
            <p>Best regards,<br>The Leasing Team<br>{self.property_name}</p>
            <hr style="margin: 20px 0; border: none; border-top: 1px solid #ddd;">
            <p style="font-size: 12px; color: #666;">
                This email was sent to {confirmation.prospect_email} regarding your multiple unit tour request.<br>
                If you did not request these tours, please contact us at {self.leasing_office_phone}.<br><br>
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


# Global instance
email_service = EmailService()
