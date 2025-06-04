"""
Test suite for email formatting improvements.

This module tests the enhanced email templates including:
- Mobile-responsive HTML email design
- Improved CSS styling and layout
- Better table formatting for unit information
- Enhanced text email bullet point formatting
- Cross-platform email compatibility

Tests follow git testing standards with comprehensive coverage.
"""

import re
from unittest.mock import patch

import pytest

from email_service import EmailService
from models import BookedUnit, MultipleBookingConfirmation, TourConfirmation


@pytest.fixture
def email_service():
    """Create a fresh email service instance for each test."""
    return EmailService()


@pytest.fixture
def sample_tour_confirmation():
    """Create a sample tour confirmation for testing."""
    return TourConfirmation(
        prospect_name="John Doe",
        prospect_email="john@example.com",
        unit_id="A101",
        property_address="123 Test St, Test City, TS 12345",
        tour_date="2025-07-15",
        tour_time="2:00 PM",
    )


@pytest.fixture
def sample_multiple_booking():
    """Create a sample multiple booking confirmation for testing."""
    booked_units = [
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

    return MultipleBookingConfirmation(
        prospect_name="Jane Smith",
        prospect_email="jane@example.com",
        booked_units=booked_units,
        property_address="123 Test St, Test City, TS 12345",
        tour_date="2025-07-20",
        tour_time="3:00 PM",
        master_confirmation_number="MASTER-12345",
    )


class TestHTMLEmailFormatting:
    """Test cases for HTML email formatting improvements."""

    def test_html_email_mobile_viewport(self, email_service, sample_multiple_booking):
        """Test that HTML emails include proper mobile viewport meta tag."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for viewport meta tag
        assert (
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            in html_content
        )

    def test_html_email_responsive_css(self, email_service, sample_multiple_booking):
        """Test that HTML emails include responsive CSS media queries."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for mobile media query
        assert "@media only screen and (max-width: 600px)" in html_content

        # Check for responsive adjustments
        assert ".container { padding: 5px; }" in html_content
        assert ".header { padding: 20px 15px; }" in html_content
        assert "table { font-size: 12px; }" in html_content

    def test_html_email_modern_styling(self, email_service, sample_multiple_booking):
        """Test that HTML emails use modern styling elements."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for modern CSS features
        assert "linear-gradient" in html_content
        assert "box-shadow" in html_content
        assert "border-radius" in html_content

        # Check for improved typography
        assert "-apple-system, BlinkMacSystemFont" in html_content
        assert "font-weight: 600" in html_content

    def test_html_email_table_formatting(self, email_service, sample_multiple_booking):
        """Test improved table formatting in HTML emails."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check table structure
        assert "<table>" in html_content
        assert "<thead>" in html_content
        assert "<tbody>" in html_content

        # Check header styling
        assert (
            "background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)"
            in html_content
        )

        # Check cell styling with improved colors
        assert "color: #2c3e50" in html_content  # Unit ID color
        assert "color: #34495e" in html_content  # Bed/bath color
        assert "color: #7f8c8d" in html_content  # Sqft color
        assert "color: #27ae60" in html_content  # Rent color

    def test_html_email_unit_data_formatting(
        self, email_service, sample_multiple_booking
    ):
        """Test that unit data is properly formatted in HTML emails."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check regular unit formatting
        assert "Unit A101" in html_content
        assert "1 bed / 1 bath" in html_content
        assert "$1,800/month" in html_content

        # Check studio unit formatting
        assert "Unit S104" in html_content
        assert "Studio / 1 bath" in html_content
        assert "$1,500/month" in html_content

        # Check confirmation numbers with monospace font
        assert "CONF-A101-001" in html_content
        assert "font-family: monospace" in html_content

    def test_html_email_sections_structure(
        self, email_service, sample_multiple_booking
    ):
        """Test that HTML email has proper section structure."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check main sections
        assert '<div class="header">' in html_content
        assert '<div class="content">' in html_content
        assert '<div class="details">' in html_content
        assert '<div class="units-table">' in html_content
        assert '<div class="bring-list">' in html_content
        assert '<div class="contact-info">' in html_content
        assert '<div class="footer">' in html_content

        # Check section headers
        assert "📅 Tour Details" in html_content
        assert "🏢 Your Booked Units" in html_content
        assert "📋 What to Bring" in html_content
        assert "📞 Contact Information" in html_content

    def test_html_email_accessibility_features(
        self, email_service, sample_multiple_booking
    ):
        """Test accessibility features in HTML emails."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for proper heading structure
        assert "<h1>" in html_content
        assert "<h3>" in html_content

        # Check for semantic HTML
        assert "<table>" in html_content
        assert "<ul>" in html_content
        assert "<li>" in html_content

        # Check for proper contrast colors
        assert "color: #333" in html_content  # Dark text on light background


class TestTextEmailFormatting:
    """Test cases for plain text email formatting improvements."""

    def test_text_email_bullet_structure(self, email_service, sample_multiple_booking):
        """Test improved bullet point structure in text emails."""
        text_content = email_service._create_multiple_booking_text_content(
            sample_multiple_booking
        )

        # Check bullet point format
        assert "  • Unit A101: 1 bed/1 bath, 650 sq ft, $1,800/month" in text_content
        assert "    Confirmation #: CONF-A101-001" in text_content

        # Check studio formatting
        assert "  • Unit S104: Studio/1 bath, 450 sq ft, $1,500/month" in text_content
        assert "    Confirmation #: CONF-S104-003" in text_content

    def test_text_email_section_headers(self, email_service, sample_multiple_booking):
        """Test section headers in text emails."""
        text_content = email_service._create_multiple_booking_text_content(
            sample_multiple_booking
        )

        # Check all required sections
        assert "TOUR DETAILS:" in text_content
        assert "BOOKED UNITS (3 units):" in text_content
        assert "WHAT TO BRING:" in text_content
        assert "CONTACT INFORMATION:" in text_content

        # Check master confirmation number
        assert (
            f"Master Confirmation Number: {sample_multiple_booking.master_confirmation_number}"
            in text_content
        )

    def test_text_email_formatting_consistency(
        self, email_service, sample_multiple_booking
    ):
        """Test formatting consistency in text emails."""
        text_content = email_service._create_multiple_booking_text_content(
            sample_multiple_booking
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
            assert line.startswith("  • Unit")

        # All confirmation lines should start with "    "
        for line in confirmation_lines:
            assert line.startswith("    Confirmation #:")

    def test_text_email_data_accuracy(self, email_service, sample_multiple_booking):
        """Test data accuracy in text emails."""
        text_content = email_service._create_multiple_booking_text_content(
            sample_multiple_booking
        )

        # Check prospect information
        assert sample_multiple_booking.prospect_name in text_content
        assert sample_multiple_booking.tour_date in text_content
        assert sample_multiple_booking.tour_time in text_content

        # Check all units are included
        for unit in sample_multiple_booking.booked_units:
            assert f"Unit {unit.unit_id}" in text_content
            assert f"${unit.rent:,}/month" in text_content
            assert unit.confirmation_number in text_content


class TestEmailCompatibility:
    """Test email compatibility across different clients."""

    def test_html_email_inline_styles(self, email_service, sample_multiple_booking):
        """Test that critical styles are inlined for email client compatibility."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for inline styles on table elements
        assert 'style="padding:' in html_content
        assert 'style="background-color:' in html_content
        assert 'style="color:' in html_content

    def test_html_email_fallback_fonts(self, email_service, sample_multiple_booking):
        """Test that fallback fonts are specified for cross-platform compatibility."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )

        # Check for font fallbacks
        assert "Arial, sans-serif" in html_content
        assert "Monaco, monospace" in html_content

    def test_email_content_encoding(self, email_service, sample_multiple_booking):
        """Test that email content is properly encoded."""
        html_content = email_service._create_multiple_booking_html_content(
            sample_multiple_booking
        )
        text_content = email_service._create_multiple_booking_text_content(
            sample_multiple_booking
        )

        # Check that content is valid UTF-8 (no encoding errors)
        assert isinstance(html_content, str)
        assert isinstance(text_content, str)

        # Check that special characters are handled properly
        assert "📅" in html_content  # Emoji should be preserved
        assert "📋" in html_content
        assert "📞" in html_content


@pytest.mark.unit
class TestEmailFormattingEdgeCases:
    """Test edge cases in email formatting."""

    def test_empty_units_list(self, email_service):
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

        html_content = email_service._create_multiple_booking_html_content(
            empty_booking
        )
        text_content = email_service._create_multiple_booking_text_content(
            empty_booking
        )

        # Should handle empty list gracefully
        assert "0 units" in html_content
        assert "0 units" in text_content

    def test_long_unit_names(self, email_service):
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

        html_content = email_service._create_multiple_booking_html_content(booking)
        text_content = email_service._create_multiple_booking_text_content(booking)

        # Should handle long content without breaking layout
        assert long_unit.unit_id in html_content
        assert long_unit.confirmation_number in html_content
        assert long_unit.unit_id in text_content
        assert long_unit.confirmation_number in text_content
