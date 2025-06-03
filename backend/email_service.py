import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from models import TourConfirmation
import os
from datetime import datetime, timedelta
import logging
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

    async def send_tour_confirmation(self, confirmation: TourConfirmation) -> bool:
        """
        Send a tour confirmation email to the prospect.
        Returns True if successful, False otherwise.
        """
        try:
            # Validate email configuration
            if not self._validate_email_config():
                logger.error("Email configuration is invalid")
                return False

            # Create email message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"Tour Confirmation - {confirmation.unit_id}"
            message["From"] = self.smtp_email
            message["To"] = confirmation.prospect_email

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

            await aiosmtplib.send(
                message,
                hostname=self.smtp_server,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_email,
                password=self.smtp_password,
                tls_context=context,
            )

            logger.info(
                f"Tour confirmation email sent to {confirmation.prospect_email}"
            )
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
• Valid government-issued photo ID
• Proof of income (recent pay stubs or employment letter)
• Application fee ($50 - if you decide to apply)

CONTACT INFORMATION:
Leasing Office: {self.leasing_office_phone}
Email: {self.smtp_email}

Please arrive 5 minutes early. If you need to reschedule or have any questions, please call our leasing office or reply to this email.

We look forward to showing you your potential new home!

Best regards,
The Leasing Team
{self.property_name}
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
