import pytest
from chat_service import ChatService
from models import ChatMessage, ChatState


@pytest.fixture
def chat_service():
    """Create a fresh chat service instance for each test."""
    return ChatService()


@pytest.mark.asyncio
async def test_initial_greeting(chat_service):
    """Test initial greeting message."""
    message = ChatMessage(message="Hello")
    response = await chat_service.process_message(message)

    assert "name" in response.reply.lower()
    assert response.session_id is not None
    assert len(response.session_id) > 0


@pytest.mark.asyncio
async def test_name_collection(chat_service):
    """Test name collection flow."""
    # Start conversation
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    # Provide name
    message2 = ChatMessage(message="John Doe", session_id=session_id)
    response2 = await chat_service.process_message(message2)

    assert "email" in response2.reply.lower()

    # Check session state
    session = chat_service.db_service.load_session(session_id)
    assert session.prospect_data.name == "John Doe"
    assert session.state == ChatState.COLLECTING_EMAIL


@pytest.mark.asyncio
async def test_invalid_name(chat_service):
    """Test invalid name handling."""
    # Start conversation
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    # Provide invalid name
    message2 = ChatMessage(message="123", session_id=session_id)
    response2 = await chat_service.process_message(message2)

    assert "valid name" in response2.reply.lower()

    # Check session state hasn't changed
    session = chat_service.db_service.load_session(session_id)
    assert session.prospect_data.name is None
    assert session.state == ChatState.COLLECTING_NAME


@pytest.mark.asyncio
async def test_email_validation(chat_service):
    """Test email validation."""
    # Setup: get to email collection state
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    message2 = ChatMessage(message="John Doe", session_id=session_id)
    await chat_service.process_message(message2)

    # Test invalid email
    message3 = ChatMessage(message="invalid-email", session_id=session_id)
    response3 = await chat_service.process_message(message3)

    assert "valid email" in response3.reply.lower()

    # Test valid email
    message4 = ChatMessage(message="john@example.com", session_id=session_id)
    response4 = await chat_service.process_message(message4)

    assert "phone" in response4.reply.lower()

    # Check session state
    session = chat_service.db_service.load_session(session_id)
    assert session.prospect_data.email == "john@example.com"
    assert session.state == ChatState.COLLECTING_PHONE


@pytest.mark.asyncio
async def test_phone_validation(chat_service):
    """Test phone number validation."""
    # Setup: get to phone collection state by going through the flow
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    message2 = ChatMessage(message="John Doe", session_id=session_id)
    await chat_service.process_message(message2)

    message3 = ChatMessage(message="john@example.com", session_id=session_id)
    await chat_service.process_message(message3)

    # Test invalid phone
    message4 = ChatMessage(message="123", session_id=session_id)
    response4 = await chat_service.process_message(message4)

    assert "valid" in response4.reply.lower() and "phone" in response4.reply.lower()

    # Test valid phone
    message5 = ChatMessage(message="5551234567", session_id=session_id)
    response5 = await chat_service.process_message(message5)

    assert "move" in response5.reply.lower()


@pytest.mark.asyncio
async def test_booking_intent_detection(chat_service):
    """Test enhanced booking intent detection."""
    # Test various booking keywords from the enhanced list
    booking_messages = [
        "book", "yes", "schedule tour", "I want it", "interested in booking",
        "tour", "visit", "appointment", "reserve", "confirm", "sure", "okay",
        "want to book", "book a tour", "schedule a tour"
    ]

    for msg in booking_messages:
        assert chat_service._is_booking_intent(msg.lower())

    # Test non-booking messages
    non_booking_messages = ["hello", "maybe", "no thanks", "tell me more", "what", "how", "interested"]

    for msg in non_booking_messages:
        assert not chat_service._is_booking_intent(msg.lower())


@pytest.mark.asyncio
async def test_apartment_search_intent_detection(chat_service):
    """Test enhanced apartment search intent detection."""
    # Test various apartment search keywords
    apartment_messages = [
        "apartment", "looking for", "show me", "bedroom", "2br", "3br",
        "unit", "rent", "lease", "find", "available", "studio", "sqft"
    ]

    for msg in apartment_messages:
        assert chat_service._is_apartment_search_intent(msg.lower())

    # Test non-apartment search messages
    non_apartment_messages = ["hello", "book", "yes", "no", "thanks"]

    for msg in non_apartment_messages:
        assert not chat_service._is_apartment_search_intent(msg.lower())


@pytest.mark.asyncio
async def test_booking_intent_in_greeting_state(chat_service):
    """Test that booking intent is recognized even in greeting state."""
    # Test "book a tour" in greeting state
    message = ChatMessage(message="book a tour")
    response = await chat_service.process_message(message)

    # Should recognize booking intent and ask for name
    assert "book a tour" in response.reply.lower()
    assert "name" in response.reply.lower()
    assert response.session_id is not None

    # Check that session state moved to COLLECTING_NAME
    session = chat_service.db_service.load_session(response.session_id)
    assert session.state == ChatState.COLLECTING_NAME

    # Test other booking phrases in greeting state
    booking_phrases = ["I want to book", "schedule a tour", "book", "interested in booking"]

    for phrase in booking_phrases:
        message = ChatMessage(message=phrase)
        response = await chat_service.process_message(message)

        # Should recognize booking intent and ask for name
        assert ("book" in response.reply.lower() or "tour" in response.reply.lower() or
                "help" in response.reply.lower())
        assert "name" in response.reply.lower()

        # Check session state - should move to COLLECTING_NAME for booking intent
        session = chat_service.db_service.load_session(response.session_id)
        assert session.state == ChatState.COLLECTING_NAME


@pytest.mark.asyncio
async def test_move_in_date_parsing(chat_service):
    """Test enhanced move-in date parsing."""
    # Setup: get to move-in date collection state
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    message2 = ChatMessage(message="John Doe", session_id=session_id)
    await chat_service.process_message(message2)

    message3 = ChatMessage(message="john@example.com", session_id=session_id)
    await chat_service.process_message(message3)

    message4 = ChatMessage(message="5551234567", session_id=session_id)
    await chat_service.process_message(message4)

    # Test strict date format
    message5 = ChatMessage(message="2025-07-01", session_id=session_id)
    response5 = await chat_service.process_message(message5)

    assert "bedroom" in response5.reply.lower()

    # Check that date was stored
    session = chat_service.db_service.load_session(session_id)
    assert session.prospect_data.move_in_date == "2025-07-01"


@pytest.mark.asyncio
async def test_beds_collection_with_alternatives(chat_service):
    """Test beds collection and alternative handling."""
    # Setup: get to beds collection state
    message1 = ChatMessage(message="Hello")
    response1 = await chat_service.process_message(message1)
    session_id = response1.session_id

    # Complete the flow to beds collection
    message2 = ChatMessage(message="John Doe", session_id=session_id)
    await chat_service.process_message(message2)

    message3 = ChatMessage(message="john@example.com", session_id=session_id)
    await chat_service.process_message(message3)

    message4 = ChatMessage(message="5551234567", session_id=session_id)
    await chat_service.process_message(message4)

    message5 = ChatMessage(message="ASAP", session_id=session_id)
    await chat_service.process_message(message5)

    # Test bedroom selection
    message6 = ChatMessage(message="2", session_id=session_id)
    response6 = await chat_service.process_message(message6)

    # Should either find a unit or say none available
    assert ("found" in response6.reply.lower() or "don't currently have" in response6.reply.lower())


@pytest.mark.asyncio
async def test_data_validation_functions(chat_service):
    """Test data validation helper functions."""
    from models import ProspectData

    # Test complete data
    complete_data = ProspectData(
        name="John Doe",
        email="john@example.com",
        phone="5551234567",
        move_in_date="2025-07-01",
        beds_wanted=2
    )

    assert chat_service._is_data_complete(complete_data)
    assert chat_service._get_missing_fields(complete_data) == []

    # Test incomplete data
    incomplete_data = ProspectData(
        name="John Doe",
        email="john@example.com"
    )

    assert not chat_service._is_data_complete(incomplete_data)
    missing = chat_service._get_missing_fields(incomplete_data)
    assert "phone" in missing
    assert "move-in date" in missing
    assert "number of bedrooms" in missing


@pytest.mark.asyncio
async def test_keyword_overlap_handling(chat_service):
    """Test that apartment search keywords in greeting state don't cause redundant prompts."""
    from models import ChatMessage, ChatState

    # Test apartment search keywords in greeting state
    message = ChatMessage(message="I need a 2 bedroom apartment", session_id=None)
    response = await chat_service.process_message(message)

    # Should handle this in greeting and ask for email (since it extracted the name from the message)
    # or ask for name if it didn't extract it properly
    assert ("email" in response.reply.lower() or "name" in response.reply.lower())

    # Test that the same keywords outside greeting state work differently
    # Create a session in a different state
    session = chat_service._get_or_create_session("test-session-overlap")
    session.state = ChatState.COLLECTING_PHONE
    session.prospect_data.name = "John Doe"
    session.prospect_data.email = "john@example.com"
    chat_service.db_service.save_session(session)

    message2 = ChatMessage(message="I'm looking for an apartment", session_id="test-session-overlap")
    response2 = await chat_service.process_message(message2)

    # Should acknowledge apartment search but continue with phone collection
    assert "phone" in response2.reply.lower()
    assert response2.state == ChatState.COLLECTING_PHONE


if __name__ == "__main__":
    pytest.main([__file__])
