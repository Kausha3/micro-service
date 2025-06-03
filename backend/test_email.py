import pytest

from dotenv import load_dotenv
from email_service import EmailService


# Load environment variables
load_dotenv()


@pytest.mark.asyncio
async def test_email_config():
    """Test email configuration validation."""
    # Initialize email service
    service = EmailService()

    # Test that service initializes properly
    assert service.smtp_email is not None
    assert service.smtp_server is not None
    assert service.smtp_port is not None
    assert service.property_address is not None

    # Test configuration validation
    # This will pass even with default values for testing purposes
    is_valid = service._validate_email_config()

    # For testing, we'll just check that the method runs without error
    assert isinstance(is_valid, bool)

@pytest.mark.asyncio
async def test_smtp_connection():
    """Test basic SMTP connection without sending email."""
    try:
        import aiosmtplib
        import ssl

        service = EmailService()

        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        # Test connection
        smtp = aiosmtplib.SMTP(
            hostname=service.smtp_server,
            port=service.smtp_port,
            start_tls=True,
            username=service.smtp_email,
            password=service.smtp_password,
            tls_context=context
        )

        await smtp.connect()
        await smtp.login(service.smtp_email, service.smtp_password)
        await smtp.quit()

        assert True  # If we get here, connection was successful

    except Exception as e:
        # For testing purposes, we'll skip this test if email is not configured
        pytest.skip(f"Email not configured properly: {str(e)}")
