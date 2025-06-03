import uuid
import re
from datetime import datetime
from typing import Optional
from models import (
    ChatState, ChatMessage, ChatResponse, ProspectData,
    ConversationSession, TourConfirmation, ConversationMessage
)
from inventory_service import inventory_service
from email_service import email_service
# SMS functionality removed - email-only notifications
from session_db_service import session_db_service
import logging
import dateparser

logger = logging.getLogger(__name__)


class ChatService:
    """
    Core chat service that manages conversation flow and state.
    Implements structured reasoning for data collection and booking flow.
    Now uses SQLite database for session persistence.
    """

    # Enhanced keyword arrays for better intent detection
    APARTMENT_KEYWORDS = [
        "apartment", "unit", "rent", "looking for", "show me", "bedroom", "bed",
        "searching", "place", "home", "lease", "find", "available",
        "2br", "3br", "1br", "studio", "sqft", "square feet"
    ]

    BOOKING_KEYWORDS = [
        "book", "tour", "visit", "appointment", "schedule", "reserve", "confirm",
        "interested in booking", "want to book", "book a tour", "schedule a tour",
        "want it", "take it", "sign up", "yes", "sure", "okay"
    ]

    def __init__(self):
        # Database-backed session storage
        self.db_service = session_db_service

    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """
        Process incoming chat message and return appropriate response.
        Main entry point for chat logic.
        """
        # Get or create session
        session = self._get_or_create_session(message.session_id)

        # Add user message to conversation
        self._add_message(session, "user", message.message)

        # Process message based on current state
        response_text = await self._process_by_state(session, message.message)

        # Add assistant response to conversation
        self._add_message(session, "bot", response_text)

        # Update session timestamp
        session.updated_at = datetime.now()

        # Save session to database
        self.db_service.save_session(session)

        return ChatResponse(
            reply=response_text,
            session_id=session.session_id,
            state=session.state
        )

    def _get_or_create_session(self, session_id: Optional[str]) -> ConversationSession:
        """
        Get existing session from database or create new one.

        Attempts to load an existing session by ID, creating a fresh session
        with default state if none exists or no ID is provided.
        """
        if session_id:
            # Try to load existing session from database
            existing_session = self.db_service.load_session(session_id)
            if existing_session:
                return existing_session

        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = ConversationSession(
            session_id=new_session_id,
            state=ChatState.GREETING,
            prospect_data=ProspectData(),
            messages=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return session

    def _add_message(self, session: ConversationSession, sender: str, text: str):
        """
        Add message to session history.

        Creates a timestamped conversation message and appends it to the session's
        message history for tracking the complete conversation flow.
        """
        message = ConversationMessage(
            sender=sender,
            text=text,
            timestamp=datetime.now()
        )
        session.messages.append(message)

    async def _process_by_state(self, session: ConversationSession,
                                message: str) -> str:
        """Process message based on current conversation state."""
        message_lower = message.lower().strip()

        # Check for booking intent at any stage (highest priority)
        # But skip if already in BOOKING_CONFIRMED state to avoid duplicates
        if (session.state != ChatState.BOOKING_CONFIRMED and
            self._is_booking_intent(message_lower)):
            return await self._handle_smart_booking_intent(session, message)

        # Special handling for GREETING state to avoid redundant prompts
        if session.state == ChatState.GREETING:
            # If they express apartment search intent in greeting, handle it there
            # to avoid duplicate "What's your name?" prompts
            if self._is_apartment_search_intent(message_lower):
                return self._handle_greeting(session, message)
        else:
            # Check for apartment search intent at any stage (lower priority)
            # If user expresses apartment search intent, acknowledge and guide
            if self._is_apartment_search_intent(message_lower):
                return await self._handle_apartment_search_intent(
                    session, message)

        # State-specific processing
        if session.state == ChatState.GREETING:
            return self._handle_greeting(session, message)

        elif session.state == ChatState.COLLECTING_NAME:
            return self._handle_name_collection(session, message)

        elif session.state == ChatState.COLLECTING_EMAIL:
            return self._handle_email_collection(session, message)

        elif session.state == ChatState.COLLECTING_PHONE:
            return self._handle_phone_collection(session, message)

        # COLLECTING_CARRIER state removed - SMS functionality disabled

        elif session.state == ChatState.COLLECTING_MOVE_IN:
            return self._handle_move_in_collection(session, message)

        elif session.state == ChatState.COLLECTING_BEDS:
            return self._handle_beds_collection(session, message)

        elif session.state == ChatState.READY_TO_BOOK:
            return await self._handle_ready_to_book(session, message)

        elif session.state == ChatState.BOOKING_CONFIRMED:
            return await self._handle_post_booking(session, message)

        return "I'm sorry, I didn't understand. Could you please try again?"

    def _handle_greeting(self, session: ConversationSession, message: str) -> str:
        GREETING_KEYWORDS = {"hi", "hello", "hey", "good morning", "good afternoon", "good evening"}
        """
        If the user typed “hi”/“hello” (any greeting), respond with a welcome prompt but
        do NOT treat that message as their name. Keep session.state = GREETING.
        If the user typed anything else, assume that’s their name, store it, and move to COLLECTING_EMAIL.
        """
        cleaned = message.strip().lower()

        # 1) If they literally said just a greeting, respond and stay in GREETING.
        if any(greet in cleaned for greet in GREETING_KEYWORDS):
            return "Hello there! What’s your name?"

        # 2) If they're talking about apartments/searching, acknowledge but still need their name
        APARTMENT_KEYWORDS = {"apartment", "bedroom", "looking for", "need", "want", "searching", "unit", "place", "home"}
        if any(keyword in cleaned for keyword in APARTMENT_KEYWORDS):
            return "Great! I'd love to help you find the perfect apartment. First, what's your name?"

        # 3) Otherwise, treat the message as the actual name.
        #    Validate it just like you do in _handle_name_collection.
        if not re.match(r"^[a-zA-Z\s\-'\.]{2,}$", message.strip()):
            session.state = ChatState.COLLECTING_NAME  # Move to name collection state for invalid names
            return "That doesn’t look like a valid name. Please tell me your full name."

        # 4) If it passes validation, store it and advance state:
        session.prospect_data.name = message.strip()
        session.state = ChatState.COLLECTING_EMAIL
        return f"Nice to meet you, {session.prospect_data.name}! What’s your email address?"


    def _handle_name_collection(self, session: ConversationSession, message: str) -> str:
        """Collect and validate prospect's name with regex pattern matching."""
        name = message.strip()
        if len(name) < 2 or not re.match(r'^[a-zA-Z\s\-\'\.]+$', name):
            return "Please provide a valid name (letters only, at least 2 characters)."

        session.prospect_data.name = name
        session.state = ChatState.COLLECTING_EMAIL
        return f"Nice to meet you, {name}! What's your email address?"

    def _handle_email_collection(self, session: ConversationSession, message: str) -> str:
        """Collect and validate prospect's email address using regex validation."""
        email = message.strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return "Please provide a valid email address (e.g., john@example.com)."

        session.prospect_data.email = email
        session.state = ChatState.COLLECTING_PHONE
        return "Great! What's your phone number?"

    def _handle_phone_collection(self, session: ConversationSession, message: str) -> str:
        """Collect and validate prospect's phone number using ProspectData model validation."""
        try:
            # Use the validator from ProspectData model
            temp_data = ProspectData(phone=message.strip())
            session.prospect_data.phone = temp_data.phone
            session.state = ChatState.COLLECTING_MOVE_IN
            return ("Great! You'll receive email confirmations for your tour. "
                    "When are you looking to move in? "
                    "(e.g., 'January 2025', 'ASAP', '2025-07-01')")
        except ValueError:
            return "Please provide a valid 10-digit phone number (e.g., 555-123-4567)."

    # _handle_carrier_collection method removed - SMS functionality disabled

    def _handle_move_in_collection(self, session: ConversationSession, message: str) -> str:
        """Parse user's move-in date (YYYY-MM-DD or fuzzy) and confirm if ambiguous."""
        move_in_str = message.strip()

        # Try to parse as strict date format first
        if self._is_strict_date_format(move_in_str):
            try:
                # Validate it's a real date
                parsed_date = datetime.strptime(move_in_str, "%Y-%m-%d")
                session.prospect_data.move_in_date = parsed_date.date().isoformat()
                session.state = ChatState.COLLECTING_BEDS
                return "How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"
            except ValueError:
                return ("Please provide a valid move-in date in YYYY-MM-DD format "
                    "(e.g., 2025-07-01) or describe your timeframe "
                    "(e.g., 'ASAP', 'January 2025').")

        # Try to parse with dateparser for natural language dates
        # Note: dateparser may interpret ambiguous formats like "6/15/25" as
        # MM/DD/YY (US format). For international deployment, consider
        # locale-specific parsing or explicit format validation
        try:
            parsed_date = dateparser.parse(
                move_in_str, settings={'PREFER_DATES_FROM': 'future'})
            if parsed_date:
                # Ask for confirmation if it's a fuzzy date
                formatted_date = parsed_date.strftime("%B %d, %Y")
                if not self._is_strict_date_format(move_in_str):
                    # Store the parsed date but ask for confirmation
                    session.prospect_data.move_in_date = parsed_date.date().isoformat()
                    session.state = ChatState.COLLECTING_BEDS
                    return (f"I understood '{move_in_str}' as {formatted_date}. "
                            f"How many bedrooms are you looking for? "
                            f"(1, 2, 3, 4, or 5)")
                else:
                    session.prospect_data.move_in_date = parsed_date.date().isoformat()
                    session.state = ChatState.COLLECTING_BEDS
                    return "How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"
        except Exception:
            # If dateparser fails, fall back to storing as-is for common phrases
            pass

        # Allow natural language for flexibility (ASAP, etc.)
        if len(move_in_str) < 3:
            return ("Please provide a more specific move-in timeframe "
                    "(e.g., 'ASAP', 'January 2025', or '2025-07-01').")

        session.prospect_data.move_in_date = move_in_str
        session.state = ChatState.COLLECTING_BEDS
        return "How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"

    def _is_strict_date_format(self, date_str: str) -> bool:
        """Check if the date string matches strict YYYY-MM-DD format using regex."""
        import re
        return bool(re.match(r'^\d{4}-\d{2}-\d{2}$', date_str))

    def _handle_beds_collection(self, session: ConversationSession, message: str) -> str:
        """Extract bedroom count from message and check inventory for matching units."""
        try:
            # Extract number from message
            beds_match = re.search(r'\b([1-5])\b', message)
            if not beds_match:
                return "Please specify the number of bedrooms (1, 2, 3, 4, or 5)."

            beds = int(beds_match.group(1))
            session.prospect_data.beds_wanted = beds

            # Check inventory - use existing unit_id if available for consistency
            preferred_unit_id = session.prospect_data.unit_id if session.prospect_data.unit_id else None
            available_unit = inventory_service.check_inventory(beds, preferred_unit_id)
            if available_unit:
                session.state = ChatState.READY_TO_BOOK
                session.prospect_data.unit_id = available_unit.unit_id
                return (f"Excellent! I found a {beds}-bedroom unit available: "
                       f"Unit {available_unit.unit_id} ({available_unit.sqft} sq ft, "
                       f"${available_unit.rent}/month). "
                       f"Would you like to book a tour? Just type 'book' or 'yes' to confirm!")
            else:
                return (f"I'm sorry, we don't currently have any {beds}-bedroom units available. "
                       f"Would you like to check availability for a different number of bedrooms?")

        except ValueError:
            return "Please specify a valid number of bedrooms (1-5)."

    async def _handle_ready_to_book(self, session: ConversationSession, message: str) -> str:
        """Handle booking confirmation when user is ready."""
        message_lower = message.lower().strip()

        if self._is_booking_intent(message_lower):
            return await self._handle_booking_intent(session)
        elif self._is_negative_response(message_lower):
            return await self._handle_show_alternatives(session)
        elif self._is_different_bedroom_request(message_lower):
            return await self._handle_different_bedroom_request(session, message)
        else:
            return "Would you like to book a tour for this unit? Type 'book', 'yes', or 'schedule tour' to confirm! Or say 'no' or 'show other' to see different options."

    def _is_booking_intent(self, message: str) -> bool:
        """Check if message contains booking keywords like 'book', 'tour', 'schedule'."""
        return any(keyword in message for keyword in self.BOOKING_KEYWORDS)

    def _is_apartment_search_intent(self, message: str) -> bool:
        """Check if message contains apartment search keywords like 'apartment', 'bedroom', 'rent'."""
        return any(keyword in message for keyword in self.APARTMENT_KEYWORDS)

    def _is_negative_response(self, message: str) -> bool:
        """Check if message contains negative keywords like 'no', 'not interested', 'pass'."""
        negative_keywords = [
            'no', 'nope', 'not interested', 'pass', 'skip', 'different',
            'other', 'show other', 'show me other', 'alternatives', 'something else'
        ]
        return any(keyword in message for keyword in negative_keywords)

    def _is_different_bedroom_request(self, message: str) -> bool:
        """Check if message requests different bedroom count using regex patterns."""
        # Look for patterns like "2 bedroom", "3 bed", "different size", etc.
        import re
        bedroom_patterns = [
            r'\b([1-5])\s*(bed|bedroom)',
            r'different\s*(size|bedroom|bed)',
            r'bigger|smaller|larger|studio'
        ]
        return any(re.search(pattern, message, re.IGNORECASE) for pattern in bedroom_patterns)

    async def _handle_show_alternatives(self, session: ConversationSession) -> str:
        """Show alternative units with different bedroom counts when user rejects current unit."""
        # Get all available units
        all_units = inventory_service.get_all_available_units()

        if not all_units:
            return "I'm sorry, we don't have any other units available at the moment. Would you like me to put you on a waiting list?"

        # Filter out the current bedroom count to show different options
        current_beds = session.prospect_data.beds_wanted
        different_units = [unit for unit in all_units if unit.beds != current_beds]

        if not different_units:
            # Only units with same bedroom count available
            same_bed_units = [unit for unit in all_units if unit.beds == current_beds]
            if len(same_bed_units) > 1:
                # Show other units with same bedroom count
                other_unit = next((unit for unit in same_bed_units if unit.unit_id != session.prospect_data.unit_id), same_bed_units[0])
                session.prospect_data.unit_id = other_unit.unit_id
                return (f"Here's another {current_beds}-bedroom option: "
                       f"Unit {other_unit.unit_id} ({other_unit.sqft} sq ft, ${other_unit.rent}/month). "
                       f"Would you like to book a tour for this one?")
            else:
                return "That's the only unit we have available with your preferred bedroom count. Would you like to see units with different bedroom counts?"

        # Show summary of different bedroom options
        bedroom_summary = {}
        for unit in different_units:
            if unit.beds not in bedroom_summary:
                bedroom_summary[unit.beds] = []
            bedroom_summary[unit.beds].append(unit)

        response = "Here are our other available options:\n\n"
        for beds, units in sorted(bedroom_summary.items()):
            unit = units[0]  # Show first unit as example
            response += f"• {beds}-bedroom: Unit {unit.unit_id} ({unit.sqft} sq ft, ${unit.rent}/month)\n"

        response += "\nWhich bedroom count interests you? Just tell me the number (1, 2, 3, 4, or 5)."

        # Reset to collecting beds so they can choose a different option
        session.state = ChatState.COLLECTING_BEDS
        return response

    async def _handle_different_bedroom_request(self, session: ConversationSession, message: str) -> str:
        """Extract bedroom count from message and check inventory for that specific count."""
        import re

        # Extract bedroom count from message
        beds_match = re.search(r'\b([1-5])\s*(bed|bedroom)', message, re.IGNORECASE)
        if beds_match:
            beds = int(beds_match.group(1))
            session.prospect_data.beds_wanted = beds

            # Check inventory for this bedroom count - use existing unit_id for consistency
            preferred_unit_id = session.prospect_data.unit_id if session.prospect_data.unit_id else None
            available_unit = inventory_service.check_inventory(beds, preferred_unit_id)
            if available_unit:
                session.state = ChatState.READY_TO_BOOK
                session.prospect_data.unit_id = available_unit.unit_id
                return (f"Great choice! I found a {beds}-bedroom unit: "
                       f"Unit {available_unit.unit_id} ({available_unit.sqft} sq ft, ${available_unit.rent}/month). "
                       f"Would you like to book a tour for this unit?")
            else:
                return f"I'm sorry, we don't have any {beds}-bedroom units available. Would you like to see other options?"

        # If no specific bedroom count found, show alternatives
        return await self._handle_show_alternatives(session)

    async def _handle_apartment_search_intent(self, session: ConversationSession, message: str) -> str:
        """Handle apartment search intent regardless of current state."""
        # If we're in greeting state, acknowledge and ask for name
        if session.state == ChatState.GREETING:
            return "Great! I'd love to help you find the perfect apartment. First, what's your name?"

        # If we're collecting information, acknowledge but continue with current step
        if session.state == ChatState.COLLECTING_NAME:
            return "Perfect! I'm here to help you find an apartment. Let's start with your name. What's your name?"
        elif session.state == ChatState.COLLECTING_EMAIL:
            return "Excellent! I'll help you find the perfect apartment. I just need your email address first so I can send you information. What's your email?"
        elif session.state == ChatState.COLLECTING_PHONE:
            return "Great! I'm excited to help you find an apartment. I just need your phone number first for the booking. What's your phone number?"
        elif session.state == ChatState.COLLECTING_MOVE_IN:
            return "Perfect! I'll help you find the ideal apartment. When are you looking to move in? (e.g., 'January 2025', 'ASAP', '2025-07-01')"
        elif session.state == ChatState.COLLECTING_BEDS:
            return "Excellent! I'm here to help you find the perfect apartment. How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"
        elif session.state == ChatState.READY_TO_BOOK:
            return "Great! I found a perfect apartment for you. Would you like to book a tour? Type 'book' or 'yes' to confirm!"
        elif session.state == ChatState.BOOKING_CONFIRMED:
            return "Your apartment tour is already confirmed! I'm excited to help you find your new home."

        # Fallback
        return "I'd love to help you find the perfect apartment! Let me gather some information first."

    async def _handle_smart_booking_intent(self, session: ConversationSession, message: str) -> str:
        """
        Intelligently handle booking intent based on current state and available data.

        Detects booking intent and either proceeds with booking if all data is collected,
        or guides user through remaining data collection steps before booking.
        """
        # If we have all the data, proceed with booking
        if self._is_data_complete(session.prospect_data):
            return await self._handle_booking_intent(session)

        # If we're missing data, acknowledge the booking intent and guide them
        missing_fields = self._get_missing_fields(session.prospect_data)

        # Acknowledge their booking intent
        response = "Great! I'd love to help you book a tour. "

        # Handle greeting state specifically - we need to start collecting info
        if session.state == ChatState.GREETING:
            response += "I'll need to collect some information first. Let's start with your name. What's your name?"
            session.state = ChatState.COLLECTING_NAME
            return response

        # Guide them to the next step based on current state
        if session.state == ChatState.COLLECTING_NAME:
            response += "I just need your name first. What's your name?"
            return response
        elif session.state == ChatState.COLLECTING_EMAIL:
            response += "I just need your email address first so I can send you the confirmation. What's your email?"
            return response
        elif session.state == ChatState.COLLECTING_PHONE:
            response += "I just need your phone number first for the booking. What's your phone number?"
            return response
        elif session.state == ChatState.COLLECTING_MOVE_IN:
            response += "I just need to know when you're looking to move in. When would you like to move in? (e.g., 'January 2025', 'ASAP', '2025-07-01')"
            return response
        elif session.state == ChatState.COLLECTING_BEDS:
            response += "I just need to know how many bedrooms you're looking for. How many bedrooms? (1, 2, 3, 4, or 5)"
            return response
        else:
            # Fallback - list what we still need
            response += f"I just need a bit more information: {', '.join(missing_fields)}. "
            if 'name' in missing_fields:
                response += "Let's start with your name."
                session.state = ChatState.COLLECTING_NAME
            elif 'email' in missing_fields:
                response += "What's your email address?"
                session.state = ChatState.COLLECTING_EMAIL
            elif 'phone' in missing_fields:
                response += "What's your phone number?"
                session.state = ChatState.COLLECTING_PHONE
            elif 'move-in date' in missing_fields:
                response += "When are you looking to move in?"
                session.state = ChatState.COLLECTING_MOVE_IN
            elif 'number of bedrooms' in missing_fields:
                response += "How many bedrooms are you looking for?"
                session.state = ChatState.COLLECTING_BEDS

            return response

    async def _handle_booking_intent(self, session: ConversationSession) -> str:
        """Handle the actual booking process."""
        if not self._is_data_complete(session.prospect_data):
            missing_fields = self._get_missing_fields(session.prospect_data)
            return f"I need a bit more information before booking. Missing: {', '.join(missing_fields)}"

        # Check inventory again - use existing unit_id for consistency
        preferred_unit_id = session.prospect_data.unit_id if session.prospect_data.unit_id else None
        available_unit = inventory_service.check_inventory(session.prospect_data.beds_wanted, preferred_unit_id)
        if not available_unit:
            return "I'm sorry, that unit is no longer available. Let me check for other options."

        # Generate tour slot
        tour_date, tour_time = email_service.generate_tour_slot()

        # Create confirmation
        confirmation = TourConfirmation(
            prospect_name=session.prospect_data.name,
            prospect_email=session.prospect_data.email,
            unit_id=available_unit.unit_id,
            property_address=session.prospect_data.property_address,
            tour_date=tour_date,
            tour_time=tour_time
        )

        # Send email confirmation
        email_sent = await email_service.send_tour_confirmation(confirmation)

        # SMS functionality removed - email-only notifications

        if email_sent:
            session.state = ChatState.BOOKING_CONFIRMED
            # Reserve the unit and store unit_id in prospect data
            inventory_service.reserve_unit(available_unit.unit_id)
            session.prospect_data.unit_id = available_unit.unit_id

            # Create response message - email-only notifications
            notification_msg = f"I've sent a confirmation email to {session.prospect_data.email}"

            return (f"Perfect! Your tour is confirmed for {tour_date} at {tour_time}. "
                   f"{notification_msg} with all the details. "
                   f"We'll see you at {session.prospect_data.property_address}!")
        else:
            # Still confirm the booking even if email fails
            session.state = ChatState.BOOKING_CONFIRMED
            inventory_service.reserve_unit(available_unit.unit_id)
            session.prospect_data.unit_id = available_unit.unit_id

            return (f"✅ Your tour is confirmed for {tour_date} at {tour_time}! "
                   f"📧 Email notifications are currently unavailable (demo mode), but your booking is secured. "
                   f"📍 Location: {email_service.property_address} "
                   f"📞 Contact: {email_service.leasing_office_phone} "
                   f"💡 Please save these details for your records!")

    async def _handle_post_booking(self, session: ConversationSession, message: str) -> str:
        """Handle messages after booking is confirmed."""
        message_lower = message.lower().strip()

        # Check if they want to book another tour or have other questions
        if any(keyword in message_lower for keyword in ['another', 'different', 'other unit', 'more']):
            return "I'd be happy to help you explore other units! What type of apartment are you looking for?"
        elif any(keyword in message_lower for keyword in ['thank', 'thanks', 'great', 'perfect']):
            return "You're very welcome! We're excited to show you around. If you have any questions before your tour, feel free to ask!"
        elif any(keyword in message_lower for keyword in ['question', 'ask', 'info', 'detail']):
            return "Of course! I'm here to help. What would you like to know about the property or your upcoming tour?"
        elif any(keyword in message_lower for keyword in ['reschedule', 'change', 'cancel']):
            return f"For any changes to your tour, please contact our leasing office at {email_service.leasing_office_phone} or reply to your confirmation email."
        else:
            return "Your tour is all set! Is there anything else I can help you with regarding the property or your visit?"

    def _is_data_complete(self, data: ProspectData) -> bool:
        """
        Check if all required data is collected.

        Validates that all essential prospect information has been gathered
        before allowing booking to proceed.
        """
        return all([
            data.name,
            data.email,
            data.phone,
            # carrier field removed - SMS functionality disabled
            data.move_in_date,
            data.beds_wanted
        ])

    def _get_missing_fields(self, data: ProspectData) -> list[str]:
        """
        Get list of missing required fields.

        Returns a human-readable list of data fields that still need to be
        collected before the booking process can be completed.
        """
        missing = []
        if not data.name:
            missing.append("name")
        if not data.email:
            missing.append("email")
        if not data.phone:
            missing.append("phone")
        # carrier field removed - SMS functionality disabled
        if not data.move_in_date:
            missing.append("move-in date")
        if not data.beds_wanted:
            missing.append("number of bedrooms")
        return missing



# Global instance
chat_service = ChatService()
