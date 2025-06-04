"""
Standalone test suite for formatting improvements.

This module tests the UI formatting improvements without relying on conftest.py
to ensure compatibility with git testing standards.
"""

import os
import unittest
from unittest.mock import MagicMock, patch

# Set test environment variables
os.environ["OPENAI_API_KEY"] = "test-key-mock"
os.environ["PROPERTY_NAME"] = "Test Property"
os.environ["PROPERTY_ADDRESS"] = "123 Test St, Test City, TS 12345"
os.environ["LEASING_OFFICE_PHONE"] = "(555) 123-4567"
os.environ["SMTP_EMAIL"] = "test@example.com"
os.environ["SMTP_PASSWORD"] = "test-password"  # nosec B105 - test password for mocking
os.environ["SMTP_SERVER"] = "smtp.test.com"
os.environ["SMTP_PORT"] = "587"

# Import after setting environment variables
from email_service import EmailService
from models import BookedUnit, MultipleBookingConfirmation


class TestEmailFormattingStandalone(unittest.TestCase):
    """Standalone tests for email formatting improvements."""

    def setUp(self):
        """Set up test fixtures."""
        self.email_service = EmailService()

        # Sample booked units for testing
        self.sample_units = [
            BookedUnit(
                unit_id="A101",
                beds=1,
                baths=1,
                sqft=650,
                rent=1800,
                confirmation_number="CONF-A101-001",
            ),
            BookedUnit(
                unit_id="B202",
                beds=2,
                baths=2,
                sqft=950,
                rent=2400,
                confirmation_number="CONF-B202-002",
            ),
            BookedUnit(
                unit_id="S104",
                beds=0,  # Studio
                baths=1,
                sqft=450,
                rent=1500,
                confirmation_number="CONF-S104-003",
            ),
        ]

        # Sample multiple booking confirmation
        self.sample_booking = MultipleBookingConfirmation(
            prospect_name="Jane Smith",
            prospect_email="jane@example.com",
            booked_units=self.sample_units,
            property_address="123 Test St, Test City, TS 12345",
            tour_date="2025-07-20",
            tour_time="3:00 PM",
            master_confirmation_number="MASTER-12345",
        )

    def test_html_email_mobile_viewport(self):
        """Test that HTML emails include proper mobile viewport meta tag."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check for viewport meta tag
        self.assertIn(
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
            html_content,
        )

    def test_html_email_responsive_css(self):
        """Test that HTML emails include responsive CSS media queries."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check for mobile media query
        self.assertIn("@media only screen and (max-width: 600px)", html_content)

        # Check for responsive adjustments
        self.assertIn(".container { padding: 5px; }", html_content)
        self.assertIn("table { font-size: 12px; }", html_content)

    def test_html_email_modern_styling(self):
        """Test that HTML emails use modern styling elements."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check for modern CSS features
        self.assertIn("linear-gradient", html_content)
        self.assertIn("box-shadow", html_content)
        self.assertIn("border-radius", html_content)

        # Check for improved typography
        self.assertIn("-apple-system, BlinkMacSystemFont", html_content)

    def test_html_email_table_formatting(self):
        """Test improved table formatting in HTML emails."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check table structure
        self.assertIn("<table>", html_content)
        self.assertIn("<thead>", html_content)
        self.assertIn("<tbody>", html_content)

        # Check improved cell styling with colors
        self.assertIn("color: #2c3e50", html_content)  # Unit ID color
        self.assertIn("color: #34495e", html_content)  # Bed/bath color
        self.assertIn("color: #7f8c8d", html_content)  # Sqft color
        self.assertIn("color: #27ae60", html_content)  # Rent color

    def test_html_email_unit_data_formatting(self):
        """Test that unit data is properly formatted in HTML emails."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check regular unit formatting
        self.assertIn("Unit A101", html_content)
        self.assertIn("1 bed / 1 bath", html_content)
        self.assertIn("$1,800/month", html_content)

        # Check studio unit formatting
        self.assertIn("Unit S104", html_content)
        self.assertIn("Studio / 1 bath", html_content)
        self.assertIn("$1,500/month", html_content)

        # Check confirmation numbers
        self.assertIn("CONF-A101-001", html_content)
        self.assertIn("font-family: monospace", html_content)

    def test_html_email_sections_structure(self):
        """Test that HTML email has proper section structure."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )

        # Check main sections
        self.assertIn('<div class="header">', html_content)
        self.assertIn('<div class="content">', html_content)
        self.assertIn('<div class="details">', html_content)
        self.assertIn('<div class="units-table">', html_content)
        self.assertIn('<div class="bring-list">', html_content)
        self.assertIn('<div class="contact-info">', html_content)
        self.assertIn('<div class="footer">', html_content)

    def test_text_email_bullet_structure(self):
        """Test improved bullet point structure in text emails."""
        text_content = self.email_service._create_multiple_booking_text_content(
            self.sample_booking
        )

        # Check bullet point format
        self.assertIn(
            "  • Unit A101: 1 bed/1 bath, 650 sq ft, $1,800/month", text_content
        )
        self.assertIn("    Confirmation #: CONF-A101-001", text_content)

        # Check studio formatting
        self.assertIn(
            "  • Unit S104: Studio/1 bath, 450 sq ft, $1,500/month", text_content
        )
        self.assertIn("    Confirmation #: CONF-S104-003", text_content)

    def test_text_email_section_headers(self):
        """Test section headers in text emails."""
        text_content = self.email_service._create_multiple_booking_text_content(
            self.sample_booking
        )

        # Check all required sections
        self.assertIn("TOUR DETAILS:", text_content)
        self.assertIn("BOOKED UNITS (3 units):", text_content)
        self.assertIn("WHAT TO BRING:", text_content)
        self.assertIn("CONTACT INFORMATION:", text_content)

        # Check master confirmation number
        self.assertIn(
            f"Master Confirmation Number: {self.sample_booking.master_confirmation_number}",
            text_content,
        )

    def test_text_email_formatting_consistency(self):
        """Test formatting consistency in text emails."""
        text_content = self.email_service._create_multiple_booking_text_content(
            self.sample_booking
        )

        # Check consistent indentation
        unit_lines = [
            line
            for line in text_content.split("\n")
            if line.strip().startswith("• Unit")
        ]
        confirmation_lines = [
            line for line in text_content.split("\n") if "Confirmation #:" in line
        ]

        # All unit lines should start with "  • "
        for line in unit_lines:
            self.assertTrue(
                line.startswith("  • Unit"),
                f"Line doesn't start with '  • Unit': {line}",
            )

        # All confirmation lines should start with "    "
        for line in confirmation_lines:
            self.assertTrue(
                line.startswith("    Confirmation #:"),
                f"Line doesn't start with '    Confirmation #:': {line}",
            )

    def test_email_content_encoding(self):
        """Test that email content is properly encoded."""
        html_content = self.email_service._create_multiple_booking_html_content(
            self.sample_booking
        )
        text_content = self.email_service._create_multiple_booking_text_content(
            self.sample_booking
        )

        # Check that content is valid UTF-8 (no encoding errors)
        self.assertIsInstance(html_content, str)
        self.assertIsInstance(text_content, str)

        # Check that special characters are handled properly
        self.assertIn("📅", html_content)  # Emoji should be preserved
        self.assertIn("📋", html_content)
        self.assertIn("📞", html_content)

    def test_empty_units_list(self):
        """Test email formatting with empty units list."""
        empty_booking = MultipleBookingConfirmation(
            prospect_name="Test User",
            prospect_email="test@example.com",
            booked_units=[],
            property_address="123 Test St",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-EMPTY",
        )

        html_content = self.email_service._create_multiple_booking_html_content(
            empty_booking
        )
        text_content = self.email_service._create_multiple_booking_text_content(
            empty_booking
        )

        # Should handle empty list gracefully
        self.assertIn("0 units", html_content)
        self.assertIn("0 units", text_content)

    def test_long_unit_names(self):
        """Test email formatting with long unit names and data."""
        long_unit = BookedUnit(
            unit_id="PENTHOUSE-SUITE-A-VERY-LONG-NAME-101",
            beds=3,
            baths=2,
            sqft=1500,
            rent=5000,
            confirmation_number="CONF-VERY-LONG-CONFIRMATION-NUMBER-12345",
        )

        booking = MultipleBookingConfirmation(
            prospect_name="Test User With Very Long Name",
            prospect_email="test@example.com",
            booked_units=[long_unit],
            property_address="123 Very Long Street Name, Very Long City Name, ST 12345",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-LONG",
        )

        html_content = self.email_service._create_multiple_booking_html_content(booking)
        text_content = self.email_service._create_multiple_booking_text_content(booking)

        # Should handle long content without breaking layout
        self.assertIn(long_unit.unit_id, html_content)
        self.assertIn(long_unit.confirmation_number, html_content)
        self.assertIn(long_unit.unit_id, text_content)
        self.assertIn(long_unit.confirmation_number, text_content)


class TestChatServiceFormattingStandalone(unittest.TestCase):
    """Standalone tests for chat service formatting improvements."""

    def setUp(self):
        """Set up test fixtures."""
        # Mock the inventory service to avoid database dependencies
        self.mock_units = [
            MagicMock(unit_id="A101", beds=1, baths=1, sqft=650, rent=1800),
            MagicMock(unit_id="B202", beds=2, baths=2, sqft=950, rent=2400),
            MagicMock(unit_id="S104", beds=0, baths=1, sqft=450, rent=1500),  # Studio
        ]

    @patch("chat_service.inventory_service.get_unit_by_id")
    def test_selected_units_pipe_format(self, mock_get_unit):
        """Test that selected units are displayed in pipe-separated format."""
        from datetime import datetime

        from chat_service import ChatService
        from models import ChatState, ConversationSession, ProspectData

        # Setup mock
        def mock_unit_lookup(unit_id):
            return next(
                (unit for unit in self.mock_units if unit.unit_id == unit_id), None
            )

        mock_get_unit.side_effect = mock_unit_lookup

        # Create test session with all required fields
        prospect_data = ProspectData(selected_units=["A101", "B202"])
        session = ConversationSession(
            session_id="test",
            state=ChatState.READY_TO_BOOK,
            prospect_data=prospect_data,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Test the method
        chat_service = ChatService()
        result = chat_service._show_selected_units(session)

        # Verify pipe-separated format is used
        self.assertIn("• Unit A101 | 1 bed/1 bath | 650 sq ft | $1,800/month", result)
        self.assertIn("• Unit B202 | 2 bed/2 bath | 950 sq ft | $2,400/month", result)

        # Verify header and instructions
        self.assertIn("📋 Your Selected Units (2 units):", result)
        self.assertIn("Ready to book all 2 units?", result)

    @patch("chat_service.inventory_service.get_unit_by_id")
    def test_selected_units_studio_format(self, mock_get_unit):
        """Test that studio units are formatted correctly."""
        from datetime import datetime

        from chat_service import ChatService
        from models import ChatState, ConversationSession, ProspectData

        # Setup mock for studio unit
        def mock_unit_lookup(unit_id):
            return next(
                (unit for unit in self.mock_units if unit.unit_id == unit_id), None
            )

        mock_get_unit.side_effect = mock_unit_lookup

        # Create test session with studio unit and all required fields
        prospect_data = ProspectData(selected_units=["S104"])
        session = ConversationSession(
            session_id="test",
            state=ChatState.READY_TO_BOOK,
            prospect_data=prospect_data,
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Test the method
        chat_service = ChatService()
        result = chat_service._show_selected_units(session)

        # Verify studio formatting
        self.assertIn("• Unit S104 | Studio/1 bath | 450 sq ft | $1,500/month", result)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)
