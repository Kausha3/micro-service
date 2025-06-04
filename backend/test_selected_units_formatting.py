"""
Test suite for selected units display and email formatting functionality.

This module tests the improvements made to:
- Selected units display formatting with pipe-separated structure
- Email template formatting for mobile responsiveness
- Multiple booking confirmation email content
- Text email formatting with proper bullet points

Tests follow git testing standards with proper mocking and coverage.
"""

from unittest.mock import MagicMock, patch

import pytest

from chat_service import ChatService
from email_service import EmailService
from models import (
    BookedUnit,
    ConversationSession,
    MultipleBookingConfirmation,
    ProspectData,
    TourConfirmation,
    Unit,
)


@pytest.fixture
def chat_service():
    """Create a fresh chat service instance for each test."""
    return ChatService()


@pytest.fixture
def email_service():
    """Create a fresh email service instance for each test."""
    return EmailService()


@pytest.fixture
def sample_session():
    """Create a sample conversation session with selected units."""
    prospect_data = ProspectData(
        name="John Doe",
        email="john@example.com",
        phone="5551234567",
        move_in_date="2025-07-01",
        beds_wanted=2,
        property_address="123 Test St, Test City, TS 12345",
        selected_units=["A101", "B202"],
    )
    return ConversationSession(
        session_id="test-session-123",
        prospect_data=prospect_data,
    )


@pytest.fixture
def sample_units():
    """Create sample units for testing."""
    return [
        Unit(
            unit_id="A101",
            beds=1,
            baths=1,
            sqft=650,
            rent=1800,
            available=True,
        ),
        Unit(
            unit_id="B202",
            beds=2,
            baths=2,
            sqft=950,
            rent=2400,
            available=True,
        ),
        Unit(
            unit_id="S104",
            beds=0,  # Studio
            baths=1,
            sqft=450,
            rent=1500,
            available=True,
        ),
    ]


class TestSelectedUnitsFormatting:
    """Test cases for selected units display formatting."""

    @patch("chat_service.inventory_service.get_unit_by_id")
    def test_show_selected_units_pipe_format(
        self, mock_get_unit, chat_service, sample_session, sample_units
    ):
        """Test that selected units are displayed in pipe-separated format."""

        # Mock inventory service to return sample units
        def mock_unit_lookup(unit_id):
            return next(
                (unit for unit in sample_units if unit.unit_id == unit_id), None
            )

        mock_get_unit.side_effect = mock_unit_lookup

        # Test the selected units display
        result = chat_service._show_selected_units(sample_session)

        # Verify pipe-separated format is used
        assert "• Unit A101 | 1 bed/1 bath | 650 sq ft | $1,800/month" in result
        assert "• Unit B202 | 2 bed/2 bath | 950 sq ft | $2,400/month" in result

        # Verify header and instructions
        assert "📋 Your Selected Units (2 units):" in result
        assert "Ready to book all 2 units?" in result
        assert "Add more units by clicking on listings" in result

    @patch("chat_service.inventory_service.get_unit_by_id")
    def test_show_selected_units_studio_format(
        self, mock_get_unit, chat_service, sample_session, sample_units
    ):
        """Test that studio units are formatted correctly."""
        # Update session to have studio unit
        sample_session.prospect_data.selected_units = ["S104"]

        def mock_unit_lookup(unit_id):
            return next(
                (unit for unit in sample_units if unit.unit_id == unit_id), None
            )

        mock_get_unit.side_effect = mock_unit_lookup

        result = chat_service._show_selected_units(sample_session)

        # Verify studio formatting
        assert "• Unit S104 | Studio/1 bath | 450 sq ft | $1,500/month" in result

    def test_show_selected_units_empty(self, chat_service, sample_session):
        """Test display when no units are selected."""
        sample_session.prospect_data.selected_units = []

        result = chat_service._show_selected_units(sample_session)

        assert "You haven't selected any units yet" in result
        assert "Click on apartment listings" in result

    @patch("chat_service.inventory_service.get_unit_by_id")
    def test_show_selected_units_unavailable(
        self, mock_get_unit, chat_service, sample_session
    ):
        """Test display when selected units are no longer available."""
        mock_get_unit.return_value = None  # Unit not found

        result = chat_service._show_selected_units(sample_session)

        assert "Your selected units are no longer available" in result
        assert "Please make new selections" in result


class TestEmailFormatting:
    """Test cases for email formatting improvements."""

    def test_multiple_booking_html_content_structure(self, email_service):
        """Test HTML email structure and mobile responsiveness."""
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
        ]

        confirmation = MultipleBookingConfirmation(
            prospect_name="John Doe",
            prospect_email="john@example.com",
            booked_units=booked_units,
            property_address="123 Test St, Test City, TS 12345",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-001",
        )

        html_content = email_service._create_multiple_booking_html_content(confirmation)

        # Test mobile viewport meta tag
        assert 'name="viewport"' in html_content
        assert "width=device-width, initial-scale=1.0" in html_content

        # Test responsive CSS
        assert "@media only screen and (max-width: 600px)" in html_content

        # Test modern styling
        assert "linear-gradient" in html_content
        assert "box-shadow" in html_content
        assert "border-radius" in html_content

        # Test table structure
        assert "<table>" in html_content
        assert "<thead>" in html_content
        assert "<tbody>" in html_content

        # Test unit data formatting
        assert "Unit A101" in html_content
        assert "1 bed / 1 bath" in html_content
        assert "$1,800/month" in html_content
        assert "CONF-A101-001" in html_content

    def test_multiple_booking_html_studio_formatting(self, email_service):
        """Test studio unit formatting in HTML email."""
        booked_units = [
            BookedUnit(
                unit_id="S104",
                beds=0,  # Studio
                baths=1,
                sqft=450,
                rent=1500,
                confirmation_number="CONF-S104-001",
            ),
        ]

        confirmation = MultipleBookingConfirmation(
            prospect_name="Jane Doe",
            prospect_email="jane@example.com",
            booked_units=booked_units,
            property_address="123 Test St, Test City, TS 12345",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-002",
        )

        html_content = email_service._create_multiple_booking_html_content(confirmation)

        # Test studio formatting
        assert "Studio / 1 bath" in html_content
        assert "Unit S104" in html_content

    def test_multiple_booking_text_content_structure(self, email_service):
        """Test plain text email structure and bullet point formatting."""
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
        ]

        confirmation = MultipleBookingConfirmation(
            prospect_name="John Doe",
            prospect_email="john@example.com",
            booked_units=booked_units,
            property_address="123 Test St, Test City, TS 12345",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-001",
        )

        text_content = email_service._create_multiple_booking_text_content(confirmation)

        # Test bullet point structure
        assert "  • Unit A101: 1 bed/1 bath, 650 sq ft, $1,800/month" in text_content
        assert "    Confirmation #: CONF-A101-001" in text_content
        assert "  • Unit B202: 2 bed/2 bath, 950 sq ft, $2,400/month" in text_content
        assert "    Confirmation #: CONF-B202-002" in text_content

        # Test section headers
        assert "TOUR DETAILS:" in text_content
        assert "BOOKED UNITS (2 units):" in text_content
        assert "WHAT TO BRING:" in text_content
        assert "CONTACT INFORMATION:" in text_content

    def test_multiple_booking_text_studio_formatting(self, email_service):
        """Test studio unit formatting in text email."""
        booked_units = [
            BookedUnit(
                unit_id="S104",
                beds=0,  # Studio
                baths=1,
                sqft=450,
                rent=1500,
                confirmation_number="CONF-S104-001",
            ),
        ]

        confirmation = MultipleBookingConfirmation(
            prospect_name="Jane Doe",
            prospect_email="jane@example.com",
            booked_units=booked_units,
            property_address="123 Test St, Test City, TS 12345",
            tour_date="2025-07-15",
            tour_time="2:00 PM",
            master_confirmation_number="MASTER-002",
        )

        text_content = email_service._create_multiple_booking_text_content(confirmation)

        # Test studio formatting in text
        assert "  • Unit S104: Studio/1 bath, 450 sq ft, $1,500/month" in text_content
        assert "    Confirmation #: CONF-S104-001" in text_content


@pytest.mark.integration
class TestIntegrationFormatting:
    """Integration tests for formatting functionality."""

    @patch("chat_service.inventory_service.get_unit_by_id")
    @patch("chat_service.email_service.send_multiple_booking_confirmation")
    def test_end_to_end_formatting_flow(
        self, mock_email, mock_get_unit, chat_service, sample_session, sample_units
    ):
        """Test complete flow from selection to email formatting."""

        # Setup mocks
        def mock_unit_lookup(unit_id):
            return next(
                (unit for unit in sample_units if unit.unit_id == unit_id), None
            )

        mock_get_unit.side_effect = mock_unit_lookup
        mock_email.return_value = True

        # Test selected units display
        display_result = chat_service._show_selected_units(sample_session)

        # Verify pipe format is used
        assert "|" in display_result
        assert "• Unit A101 |" in display_result
        assert "• Unit B202 |" in display_result

        # Verify the format matches what frontend expects
        lines = display_result.split("\n")
        unit_lines = [line for line in lines if line.startswith("• Unit")]

        for line in unit_lines:
            parts = line.split(" | ")
            assert len(parts) == 4  # unit, bed/bath, sqft, rent
            assert parts[0].startswith("• Unit")
            assert "bed" in parts[1] or "Studio" in parts[1]
            assert "sq ft" in parts[2]
            assert "$" in parts[3] and "/month" in parts[3]
