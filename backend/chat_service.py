import logging
import re
import uuid
from datetime import datetime
from typing import Optional

import dateparser

from ai_service import ai_service
from email_service import email_service
from inventory_service import inventory_service
from models import (
    AIContext,
    BookedUnit,
    ChatMessage,
    ChatResponse,
    ChatState,
    ConversationMessage,
    ConversationSession,
    MultipleBookingConfirmation,
    ProspectData,
    TourConfirmation,
)

# SMS functionality removed - email-only notifications
from session_db_service import session_db_service

logger = logging.getLogger(__name__)


class ChatService:
    """
    AI-powered chat service that manages conversation flow and state.

    This service is the core business logic component that orchestrates the entire
    conversation experience for apartment leasing. It integrates multiple services
    to provide a seamless, intelligent chat experience.

    ## Key Responsibilities
    - **Conversation Management**: Maintains session state and conversation history
    - **AI Integration**: Leverages OpenAI GPT for natural language understanding
    - **Data Collection**: Intelligently extracts prospect information from conversations
    - **Booking Orchestration**: Manages the complete tour booking workflow
    - **Multi-unit Support**: Handles selection and booking of multiple apartments
    - **Email Coordination**: Triggers appropriate email confirmations

    ## Architecture Integration
    - **Database Layer**: Uses session_db_service for persistent storage
    - **AI Layer**: Integrates with ai_service for natural language processing
    - **Email Layer**: Coordinates with email_service for notifications
    - **Inventory Layer**: Queries inventory_service for unit availability

    ## Conversation Flow
    1. **Greeting**: Initial welcome and intent detection
    2. **Information Collection**: Natural language data gathering
    3. **Unit Selection**: Inventory browsing and selection
    4. **Booking Confirmation**: Tour scheduling and email confirmation
    5. **Post-booking**: Follow-up and additional assistance

    ## State Management
    Uses ChatState enum to track conversation progress:
    - GREETING: Initial conversation state
    - COLLECTING_NAME/EMAIL/PHONE: Data collection states
    - READY_TO_BOOK: All data collected, ready for booking
    - BOOKING_CONFIRMED: Tour successfully scheduled

    Attributes:
        db_service: Database service for session persistence
    """

    def __init__(self):
        """
        Initialize the chat service with database connectivity.

        Sets up the database service connection for session management
        and conversation persistence.
        """
        # Database-backed session storage for conversation persistence
        self.db_service = session_db_service

    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """
        Process incoming chat message using AI-powered conversation logic.
        Main entry point for AI-enhanced chat processing.
        """
        # Get or create session
        session = self._get_or_create_session(message.session_id)

        # Add user message to conversation
        self._add_message(session, "user", message.message)

        # Use AI to generate response
        response_text = await self._process_with_ai(session, message.message)

        # Add assistant response to conversation
        self._add_message(session, "bot", response_text)

        # Update session timestamp
        session.updated_at = datetime.now()

        # Save session to database
        self.db_service.save_session(session)

        return ChatResponse(
            reply=response_text, session_id=session.session_id, state=session.state
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

        # Create new session with AI context
        new_session_id = session_id or str(uuid.uuid4())
        session = ConversationSession(
            session_id=new_session_id,
            state=ChatState.GREETING,
            prospect_data=ProspectData(),
            messages=[],
            ai_context=AIContext(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        return session

    async def _process_with_ai(self, session: ConversationSession, message: str) -> str:
        """
        Process message using AI-powered conversation logic.

        This method replaces the rule-based state machine with intelligent
        AI-driven conversation flow that can handle natural language queries.
        """
        try:
            # PRIORITY: Handle unit selection commands FIRST before any other processing
            if "add unit" in message.lower() and "to my selections" in message.lower():
                add_match = re.search(
                    r"add.*?unit\s+([a-z]\d{2,3}).*?to my selections", message.lower()
                )
                if add_match:
                    unit_id = add_match.group(1).upper()
                    return self._add_selected_unit(session, unit_id)
            elif (
                "remove unit" in message.lower()
                and "from my selections" in message.lower()
            ):
                remove_match = re.search(
                    r"remove.*?unit\s+([a-z]\d{2,3}).*?from my selections",
                    message.lower(),
                )
                if remove_match:
                    unit_id = remove_match.group(1).upper()
                    return self._remove_selected_unit(session, unit_id)
            elif (
                "show selected" in message.lower() or "my selections" in message.lower()
            ):
                return self._show_selected_units(session)
            elif (
                "clear selections" in message.lower() or "remove all" in message.lower()
            ):
                return self._clear_selected_units(session)

            # Check if booking is already confirmed
            if session.state == ChatState.BOOKING_CONFIRMED:
                return await self._handle_post_booking_ai(session, message)

            # Check if we need to collect specific information for booking
            missing_field = await ai_service.should_collect_information(
                session, message
            )
            if missing_field:
                return await self._handle_information_collection(
                    session, message, missing_field
                )

            # Check if user wants to book and we have all required information
            if self._has_booking_intent(message):
                data_complete = self._is_data_complete(session.prospect_data)
                logger.info(
                    f"🎯 BOOKING INTENT DETECTED - Data complete: {'✅' if data_complete else '❌'}"
                )

                if data_complete:
                    logger.info("🚀 All data complete - triggering booking flow")

                    # Check if this is a multiple booking request
                    if len(session.prospect_data.selected_units) > 1 or any(
                        phrase in message.lower()
                        for phrase in ["book all", "all units", "multiple units"]
                    ):
                        logger.info("🎯 Multiple booking detected")
                        return await self._handle_multiple_booking_intent(session)
                    else:
                        logger.info("🎯 Single booking detected")
                        return await self._handle_booking_intent(session)
                else:
                    missing_fields = self._get_missing_fields(session.prospect_data)
                    logger.warning(f"❌ Cannot book - missing fields: {missing_fields}")
                    logger.info(
                        f"   Current data: name='{session.prospect_data.name}', email='{session.prospect_data.email}', phone='{session.prospect_data.phone}', move_in='{session.prospect_data.move_in_date}', beds={session.prospect_data.beds_wanted}"
                    )
                    # Let AI handle the missing data collection

            # CRITICAL FIX: Try to parse multiple fields from user message before AI processing
            self._parse_multiple_fields_from_message(session, message)

            # ENHANCED: Check for direct unit booking requests (e.g., "I want to book Unit B301")
            unit_booking_match = re.search(
                r"(?:book|want|select|choose).*?unit\s+([a-z]\d{2,3})", message.lower()
            )
            if unit_booking_match:
                unit_id = unit_booking_match.group(1).upper()
                logger.info(f"🎯 Direct unit booking request detected: {unit_id}")

                # Get unit details to determine bedroom count
                unit = inventory_service.get_unit_by_id(unit_id)
                if unit and unit.available:
                    # Add to selected units list for multiple booking support
                    if unit_id not in session.prospect_data.selected_units:
                        session.prospect_data.selected_units.append(unit_id)
                        logger.info(
                            f"   ✅ Added {unit_id} to selected units: {session.prospect_data.selected_units}"
                        )

                    # Also maintain legacy unit_id field for backward compatibility
                    session.prospect_data.unit_id = unit_id
                    session.prospect_data.beds_wanted = unit.beds
                    logger.info(
                        f"   ✅ Set unit_id to {unit_id} and beds_wanted to {unit.beds}"
                    )

                    # If this is a direct booking request, set booking intent
                    if any(
                        keyword in message.lower()
                        for keyword in ["book", "want to book"]
                    ):
                        session.ai_context.extracted_intents.append("booking_intent")
                        logger.info("   ✅ Added booking_intent to extracted_intents")

            # ENHANCED: Check for multiple unit selection patterns
            multiple_units_match = re.findall(r"unit\s+([a-z]\d{2,3})", message.lower())
            if len(multiple_units_match) > 1:
                logger.info(
                    f"🎯 Multiple unit selection detected: {multiple_units_match}"
                )
                for unit_id in multiple_units_match:
                    unit_id = unit_id.upper()
                    unit = inventory_service.get_unit_by_id(unit_id)
                    if (
                        unit
                        and unit.available
                        and unit_id not in session.prospect_data.selected_units
                    ):
                        session.prospect_data.selected_units.append(unit_id)
                        logger.info(f"   ✅ Added {unit_id} to selected units")

            # ADDITIONAL FIX: If user selected a studio unit, set beds_wanted to 0
            if not session.prospect_data.beds_wanted and "studio" in message.lower():
                session.prospect_data.beds_wanted = 0  # Studio = 0 bedrooms
                logger.info("   ✅ Set beds_wanted to 0 for studio unit")

            # Generate AI response based on conversation context
            ai_response = await ai_service.generate_response(session, message)

            # Post-process AI response to handle specific actions
            processed_response = await self._post_process_ai_response(
                session, message, ai_response
            )

            # ENHANCED: Extract any missing data from AI response and user message
            await self._extract_data_from_ai_context(session, message, ai_response)

            # CRITICAL FIX: Check if all data is now complete after AI processing
            # If so, automatically trigger booking regardless of explicit booking intent
            if (
                self._is_data_complete(session.prospect_data)
                and session.state != ChatState.BOOKING_CONFIRMED
            ):
                logger.info(
                    "🎯 All prospect data complete - automatically triggering booking flow"
                )

                # Check if this is a multiple booking request
                if len(session.prospect_data.selected_units) > 1:
                    logger.info("🎯 Multiple booking detected in auto-trigger")
                    return await self._handle_multiple_booking_intent(session)
                else:
                    logger.info("🎯 Single booking detected in auto-trigger")
                    return await self._handle_booking_intent(session)

            # ENHANCED: Check if AI response indicates booking completion
            if (
                self._ai_indicates_booking_complete(ai_response)
                and session.state != ChatState.BOOKING_CONFIRMED
            ):
                logger.info("🤖 AI indicates booking complete - forcing booking flow")
                # Try to extract any remaining data from the conversation
                await self._extract_data_from_conversation_history(session)
                if self._is_data_complete(session.prospect_data):
                    # Check if this is a multiple booking request
                    if len(session.prospect_data.selected_units) > 1:
                        logger.info("🎯 Multiple booking detected in AI-triggered flow")
                        return await self._handle_multiple_booking_intent(session)
                    else:
                        logger.info("🎯 Single booking detected in AI-triggered flow")
                        return await self._handle_booking_intent(session)
                else:
                    missing_fields = self._get_missing_fields(session.prospect_data)
                    logger.warning(
                        f"❌ AI claims booking complete but missing: {missing_fields}"
                    )
                    return f"I need a bit more information to complete your booking. Please provide: {', '.join(missing_fields)}"

            return processed_response

        except Exception as e:
            logger.error(f"AI processing failed: {str(e)}")
            # Fallback to basic response
            return "I apologize for the confusion. Could you please tell me what you're looking for in an apartment?"

    async def _handle_information_collection(
        self, session: ConversationSession, message: str, field: str
    ) -> str:
        """Handle collection of specific information fields."""
        if field == "name":
            return self._handle_name_collection(session, message)
        elif field == "email":
            return self._handle_email_collection(session, message)
        elif field == "phone":
            return self._handle_phone_collection(session, message)
        elif field == "move_in_date":
            return self._handle_move_in_collection(session, message)
        elif field == "beds_wanted":
            return self._handle_beds_collection(session, message)
        else:
            return "I need a bit more information to help you. What would you like to know about our apartments?"

    async def _post_process_ai_response(
        self, session: ConversationSession, user_message: str, ai_response: str
    ) -> str:
        """Post-process AI response to handle specific actions and state updates."""

        # Check if AI response indicates we should move to booking
        if any(
            phrase in ai_response.lower()
            for phrase in [
                "book a tour",
                "schedule a tour",
                "ready to book",
                "confirm booking",
            ]
        ):
            if self._is_data_complete(session.prospect_data):
                session.state = ChatState.READY_TO_BOOK

        # Check if AI is asking for specific information
        if (
            "what's your name" in ai_response.lower()
            or "your name" in ai_response.lower()
        ):
            session.state = ChatState.COLLECTING_NAME
        elif "email" in ai_response.lower() and "address" in ai_response.lower():
            session.state = ChatState.COLLECTING_EMAIL
        elif "phone" in ai_response.lower() and "number" in ai_response.lower():
            session.state = ChatState.COLLECTING_PHONE
        elif "move" in ai_response.lower() and "date" in ai_response.lower():
            session.state = ChatState.COLLECTING_MOVE_IN
        elif "bedroom" in ai_response.lower() and (
            "how many" in ai_response.lower() or "looking for" in ai_response.lower()
        ):
            session.state = ChatState.COLLECTING_BEDS

        return ai_response

    def _has_booking_intent(self, message: str) -> bool:
        """Check if message contains booking intent."""
        booking_keywords = [
            "book",
            "tour",
            "visit",
            "appointment",
            "schedule",
            "reserve",
            "confirm",
            "interested in booking",
            "want to book",
            "book a tour",
            "schedule a tour",
            "want it",
            "take it",
            "sign up",
            "yes",
            "sure",
            "okay",
        ]
        message_lower = message.lower()
        has_intent = any(keyword in message_lower for keyword in booking_keywords)

        logger.info(f"🔍 Checking booking intent for message: '{message[:50]}...'")
        logger.info(f"   Booking intent detected: {'✅' if has_intent else '❌'}")
        if has_intent:
            matched_keywords = [kw for kw in booking_keywords if kw in message_lower]
            logger.info(f"   Matched keywords: {matched_keywords}")

        return has_intent

    async def _handle_post_booking_ai(
        self, session: ConversationSession, message: str
    ) -> str:
        """Handle messages after booking is confirmed using AI context."""
        # Generate contextual response for post-booking queries
        return await ai_service.generate_response(session, message)

    def _handle_greeting(self, session: ConversationSession, message: str) -> str:
        GREETING_KEYWORDS = {
            "hi",
            "hello",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
        }
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
        APARTMENT_KEYWORDS = {
            "apartment",
            "bedroom",
            "looking for",
            "need",
            "want",
            "searching",
            "unit",
            "place",
            "home",
        }
        if any(keyword in cleaned for keyword in APARTMENT_KEYWORDS):
            return "Great! I'd love to help you find the perfect apartment. First, what's your name?"

        # 3) Otherwise, treat the message as the actual name.
        #    Validate it just like you do in _handle_name_collection.
        if not re.match(r"^[a-zA-Z\s\-'\.]{2,}$", message.strip()):
            session.state = (
                ChatState.COLLECTING_NAME
            )  # Move to name collection state for invalid names
            return "That doesn’t look like a valid name. Please tell me your full name."

        # 4) If it passes validation, store it and advance state:
        session.prospect_data.name = message.strip()
        session.state = ChatState.COLLECTING_EMAIL
        return f"Nice to meet you, {session.prospect_data.name}! What’s your email address?"

    def _handle_name_collection(
        self, session: ConversationSession, message: str
    ) -> str:
        """Collect and validate prospect's name with regex pattern matching."""
        name = message.strip()
        if len(name) < 2 or not re.match(r"^[a-zA-Z\s\-\'\.]+$", name):
            return "Please provide a valid name (letters only, at least 2 characters)."

        session.prospect_data.name = name
        session.state = ChatState.COLLECTING_EMAIL
        return f"Nice to meet you, {name}! What's your email address?"

    def _handle_email_collection(
        self, session: ConversationSession, message: str
    ) -> str:
        """Collect and validate prospect's email address using regex validation."""
        email = message.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return "Please provide a valid email address (e.g., john@example.com)."

        session.prospect_data.email = email
        session.state = ChatState.COLLECTING_PHONE
        return "Great! What's your phone number?"

    def _handle_phone_collection(
        self, session: ConversationSession, message: str
    ) -> str:
        """Collect and validate prospect's phone number using ProspectData model validation."""
        try:
            # Use the validator from ProspectData model
            temp_data = ProspectData(phone=message.strip())
            session.prospect_data.phone = temp_data.phone
            session.state = ChatState.COLLECTING_MOVE_IN
            return (
                "Great! You'll receive email confirmations for your tour. "
                "When are you looking to move in? "
                "(e.g., 'January 2025', 'ASAP', '2025-07-01')"
            )
        except ValueError:
            return "Please provide a valid 10-digit phone number (e.g., 555-123-4567)."

    # _handle_carrier_collection method removed - SMS functionality disabled

    def _handle_move_in_collection(
        self, session: ConversationSession, message: str
    ) -> str:
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
                return (
                    "Please provide a valid move-in date in YYYY-MM-DD format "
                    "(e.g., 2025-07-01) or describe your timeframe "
                    "(e.g., 'ASAP', 'January 2025')."
                )

        # Try to parse with dateparser for natural language dates
        # Note: dateparser may interpret ambiguous formats like "6/15/25" as
        # MM/DD/YY (US format). For international deployment, consider
        # locale-specific parsing or explicit format validation
        try:
            parsed_date = dateparser.parse(
                move_in_str, settings={"PREFER_DATES_FROM": "future"}
            )
            if parsed_date:
                # Ask for confirmation if it's a fuzzy date
                formatted_date = parsed_date.strftime("%B %d, %Y")
                if not self._is_strict_date_format(move_in_str):
                    # Store the parsed date but ask for confirmation
                    session.prospect_data.move_in_date = parsed_date.date().isoformat()
                    session.state = ChatState.COLLECTING_BEDS
                    return (
                        f"I understood '{move_in_str}' as {formatted_date}. "
                        f"How many bedrooms are you looking for? "
                        f"(1, 2, 3, 4, or 5)"
                    )
                else:
                    session.prospect_data.move_in_date = parsed_date.date().isoformat()
                    session.state = ChatState.COLLECTING_BEDS
                    return "How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"
        except Exception as e:
            # If dateparser fails, fall back to storing as-is for common phrases
            logger.debug(f"Date parsing failed: {e}")

        # Allow natural language for flexibility (ASAP, etc.)
        if len(move_in_str) < 3:
            return (
                "Please provide a more specific move-in timeframe "
                "(e.g., 'ASAP', 'January 2025', or '2025-07-01')."
            )

        session.prospect_data.move_in_date = move_in_str
        session.state = ChatState.COLLECTING_BEDS
        return "How many bedrooms are you looking for? (1, 2, 3, 4, or 5)"

    def _is_strict_date_format(self, date_str: str) -> bool:
        """Check if the date string matches strict YYYY-MM-DD format using regex."""
        import re

        return bool(re.match(r"^\d{4}-\d{2}-\d{2}$", date_str))

    def _handle_beds_collection(
        self, session: ConversationSession, message: str
    ) -> str:
        """Extract bedroom count from message and check inventory for matching units."""
        try:
            # Extract number from message
            beds_match = re.search(r"\b([1-5])\b", message)
            if not beds_match:
                return "Please specify the number of bedrooms (1, 2, 3, 4, or 5)."

            beds = int(beds_match.group(1))
            session.prospect_data.beds_wanted = beds

            # Check inventory - use existing unit_id if available for consistency
            preferred_unit_id = (
                session.prospect_data.unit_id if session.prospect_data.unit_id else None
            )
            available_unit = inventory_service.check_inventory(beds, preferred_unit_id)
            if available_unit:
                session.state = ChatState.READY_TO_BOOK
                session.prospect_data.unit_id = available_unit.unit_id
                return (
                    f"Excellent! I found a {beds}-bedroom unit available: "
                    f"Unit {available_unit.unit_id} ({available_unit.sqft} sq ft, "
                    f"${available_unit.rent}/month). "
                    f"Would you like to book a tour? Just type 'book' or 'yes' to confirm!"
                )
            else:
                return (
                    f"I'm sorry, we don't currently have any {beds}-bedroom units available. "
                    f"Would you like to check availability for a different number of bedrooms?"
                )

        except ValueError:
            return "Please specify a valid number of bedrooms (1-5)."

    async def _handle_booking_intent(self, session: ConversationSession) -> str:
        """Handle the actual booking process."""
        logger.info("🚀 BOOKING INTENT TRIGGERED - Starting booking process")
        logger.info(f"   Session ID: {session.session_id}")
        logger.info(f"   Prospect: {session.prospect_data.name}")
        logger.info(f"   Email: {session.prospect_data.email}")
        logger.info(f"   Selected Units: {session.prospect_data.selected_units}")

        # CRITICAL FIX: Check if this should be a multiple booking
        if len(session.prospect_data.selected_units) > 1:
            logger.info(
                "🎯 Multiple units detected in single booking handler - redirecting to multiple booking"
            )
            return await self._handle_multiple_booking_intent(session)

        if not self._is_data_complete(session.prospect_data):
            missing_fields = self._get_missing_fields(session.prospect_data)
            logger.warning(f"❌ Booking failed - missing data: {missing_fields}")
            return f"I need a bit more information before booking. Missing: {', '.join(missing_fields)}"

        # ENHANCED: Use selected_units if available, otherwise fall back to legacy unit_id
        if session.prospect_data.selected_units:
            # Use the first (and only) selected unit for single booking
            unit_id = session.prospect_data.selected_units[0]
            available_unit = inventory_service.get_unit_by_id(unit_id)
            if not available_unit or not available_unit.available:
                return f"I'm sorry, Unit {unit_id} is no longer available. Let me check for other options."
        else:
            # Fall back to legacy inventory check
            preferred_unit_id = (
                session.prospect_data.unit_id if session.prospect_data.unit_id else None
            )
            available_unit = inventory_service.check_inventory(
                session.prospect_data.beds_wanted, preferred_unit_id
            )
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
            tour_time=tour_time,
        )

        # Send email confirmation
        logger.info("📧 CALLING EMAIL SERVICE - About to send tour confirmation")
        logger.info(f"   Recipient: {confirmation.prospect_email}")
        logger.info(f"   Unit: {confirmation.unit_id}")
        logger.info(f"   Tour Date: {confirmation.tour_date}")
        logger.info(f"   Tour Time: {confirmation.tour_time}")

        email_sent = await email_service.send_tour_confirmation(confirmation)

        logger.info(f"📧 EMAIL SERVICE RESULT: {'SUCCESS' if email_sent else 'FAILED'}")

        # SMS functionality removed - email-only notifications

        if email_sent:
            session.state = ChatState.BOOKING_CONFIRMED
            # Reserve the unit and store unit_id in prospect data
            inventory_service.reserve_unit(available_unit.unit_id)
            session.prospect_data.unit_id = available_unit.unit_id

            # CONSISTENCY FIX: Ensure unit is in selected_units list
            if available_unit.unit_id not in session.prospect_data.selected_units:
                session.prospect_data.selected_units.append(available_unit.unit_id)

            # Create response message with spam folder reminder
            notification_msg = (
                f"I've sent a confirmation email to {session.prospect_data.email}. "
                f"Please check your inbox and spam/junk folder if you don't see it within a few minutes"
            )

            return (
                f"Perfect! Your tour is confirmed for {tour_date} at {tour_time}. "
                f"{notification_msg}. The email contains all the details including what to bring. "
                f"If you have any issues, you can also call our leasing office at {email_service.leasing_office_phone}. "
                f"We'll see you at {session.prospect_data.property_address}!"
            )
        else:
            # Still confirm the booking even if email fails
            session.state = ChatState.BOOKING_CONFIRMED
            inventory_service.reserve_unit(available_unit.unit_id)
            session.prospect_data.unit_id = available_unit.unit_id

            # CONSISTENCY FIX: Ensure unit is in selected_units list
            if available_unit.unit_id not in session.prospect_data.selected_units:
                session.prospect_data.selected_units.append(available_unit.unit_id)

            return (
                f"✅ Your tour is confirmed for {tour_date} at {tour_time}! "
                f"📧 Email notifications are currently unavailable (demo mode), but your booking is secured. "
                f"📍 Location: {email_service.property_address} "
                f"📞 Contact: {email_service.leasing_office_phone} "
                f"💡 Please save these details for your records!"
            )

    def _is_data_complete(self, data: ProspectData) -> bool:
        """
        Check if all required data is collected.

        Validates that all essential prospect information has been gathered
        before allowing booking to proceed.
        """
        return all(
            [
                data.name,
                data.email,
                data.phone,
                # carrier field removed - SMS functionality disabled
                data.move_in_date,
                data.beds_wanted is not None,  # Allow 0 for studio units
            ]
        )

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
        if data.beds_wanted is None:
            missing.append("number of bedrooms")
        return missing

    def _parse_multiple_fields_from_message(
        self, session: ConversationSession, message: str
    ):
        """
        Parse multiple fields from a single user message.
        Handles cases like: "My name is Kausha, patermanav45@gmail.com 7272727272, Next month"
        """
        logger.info(f"🔍 Parsing multiple fields from message: '{message[:100]}...'")

        # Split by common delimiters
        parts = re.split(r"[,;]\s*", message.strip())

        if len(parts) >= 2:  # At least 2 parts to consider multi-field parsing
            logger.info(f"   Found {len(parts)} parts: {parts}")

            # First pass: Extract specific field types with high confidence
            for i, part in enumerate(parts):
                part = part.strip()

                # Handle email detection first (most specific)
                if not session.prospect_data.email and self._looks_like_email(part):
                    session.prospect_data.email = part.lower()
                    logger.info(f"   ✅ Parsed email: {part}")
                    continue

                # Handle combined email+phone parts (e.g., "email@domain.com 1234567890")
                if not session.prospect_data.email or not session.prospect_data.phone:
                    email_phone_match = re.search(
                        r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\s+(\d{10})",
                        part,
                    )
                    if email_phone_match:
                        if not session.prospect_data.email:
                            session.prospect_data.email = email_phone_match.group(
                                1
                            ).lower()
                            logger.info(
                                f"   ✅ Parsed email from combined: {email_phone_match.group(1)}"
                            )
                        if not session.prospect_data.phone:
                            session.prospect_data.phone = email_phone_match.group(2)
                            logger.info(
                                f"   ✅ Parsed phone from combined: {email_phone_match.group(2)}"
                            )
                        continue

                # Handle phone detection (specific pattern)
                if not session.prospect_data.phone and self._looks_like_phone(part):
                    cleaned_phone = re.sub(r"[^\d]", "", part)
                    if len(cleaned_phone) == 10:
                        session.prospect_data.phone = cleaned_phone
                        logger.info(f"   ✅ Parsed phone: {cleaned_phone}")
                        continue

            # Second pass: Extract name and date with improved logic
            for i, part in enumerate(parts):
                part = part.strip()

                # Skip parts that were already processed as email/phone
                if (
                    session.prospect_data.email
                    and session.prospect_data.email in part.lower()
                ) or (
                    session.prospect_data.phone
                    and session.prospect_data.phone in re.sub(r"[^\d]", "", part)
                ):
                    continue

                # Handle name extraction with improved logic
                if not session.prospect_data.name:
                    extracted_name = self._extract_name_from_text(part)
                    if extracted_name:
                        session.prospect_data.name = extracted_name
                        logger.info(f"   ✅ Parsed name: {extracted_name}")
                        continue

                # Handle date detection (only if it doesn't look like a name)
                if not session.prospect_data.move_in_date and self._looks_like_date(
                    part
                ):
                    # Additional check: make sure it's not just a name that happens to contain "month"
                    if not self._looks_like_name_only(part):
                        session.prospect_data.move_in_date = part
                        logger.info(f"   ✅ Parsed move-in date: {part}")
                        continue

                # Handle bedroom count
                if (
                    not session.prospect_data.beds_wanted
                    and self._looks_like_bedroom_count(part)
                ):
                    beds_match = re.search(r"\b([1-5])\b", part)
                    if beds_match:
                        session.prospect_data.beds_wanted = int(beds_match.group(1))
                        logger.info(f"   ✅ Parsed bedrooms: {beds_match.group(1)}")
                        continue

    def _extract_name_from_text(self, text: str) -> str:
        """Extract a person's name from text that might contain phrases like 'My name is John'."""
        text = text.strip()

        # Handle "My name is X" patterns
        name_patterns = [
            r"(?:my\s+name\s+is\s+|i\s+am\s+|call\s+me\s+)([a-zA-Z\s\-\'\.]+)",
            r"^([a-zA-Z\s\-\'\.]+)$",  # Just a plain name
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                potential_name = match.group(1).strip()
                # Validate the extracted name
                if self._looks_like_name(potential_name):
                    return potential_name

        return None

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name."""
        return (
            len(text) >= 2
            and re.match(r"^[a-zA-Z\s\-'\.]+$", text)
            and "@" not in text
            and not re.search(r"\d", text)
            and len(text.split()) <= 4
        )  # Names shouldn't be too long

    def _looks_like_name_only(self, text: str) -> bool:
        """Check if text looks like ONLY a name (stricter validation)."""
        # This is used to prevent date phrases like "Next month" from being treated as names
        text_lower = text.lower().strip()

        # Exclude common date-related phrases
        date_phrases = [
            "next month",
            "this month",
            "last month",
            "asap",
            "soon",
            "winter",
            "spring",
            "summer",
            "fall",
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ]

        if text_lower in date_phrases:
            return False

        # Must look like a name and not contain date keywords
        return self._looks_like_name(text) and not any(
            keyword in text_lower for keyword in ["month", "year", "asap", "soon"]
        )

    def _looks_like_email(self, text: str) -> bool:
        """Check if text looks like an email address."""
        return (
            re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", text)
            is not None
        )

    def _looks_like_phone(self, text: str) -> bool:
        """Check if text looks like a phone number."""
        cleaned = re.sub(r"[^\d]", "", text)
        return len(cleaned) == 10 and cleaned.isdigit()

    def _looks_like_date(self, text: str) -> bool:
        """Check if text looks like a date or move-in timeframe."""
        date_keywords = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
            "asap",
            "soon",
            "winter",
            "spring",
            "summer",
            "fall",
            "month",
        ]
        text_lower = text.lower()
        return bool(
            any(keyword in text_lower for keyword in date_keywords)
            or re.match(r"\d{4}-\d{2}-\d{2}", text)
            or re.search(r"\d{4}", text)
        )

    def _looks_like_bedroom_count(self, text: str) -> bool:
        """Check if text contains bedroom count."""
        return re.search(r"\b([1-5])\s*(bed|bedroom)", text.lower()) is not None

    def _add_message(self, session: ConversationSession, sender: str, text: str):
        """Add a message to the conversation history."""
        message = ConversationMessage(
            sender=sender, text=text, timestamp=datetime.now()
        )
        session.messages.append(message)

    async def _extract_data_from_ai_context(
        self, session: ConversationSession, user_message: str, ai_response: str
    ):
        """Use AI to extract prospect data from conversation context."""
        try:
            # Create a prompt to extract structured data
            extraction_prompt = f"""
            Extract prospect information from this conversation:
            User: {user_message}
            Assistant: {ai_response}

            Current data:
            - Name: {session.prospect_data.name or 'Not provided'}
            - Email: {session.prospect_data.email or 'Not provided'}
            - Phone: {session.prospect_data.phone or 'Not provided'}
            - Move-in date: {session.prospect_data.move_in_date or 'Not provided'}
            - Bedrooms wanted: {session.prospect_data.beds_wanted or 'Not provided'}

            Extract any missing information from the user message. Return ONLY the missing data in this exact format:
            NAME: [extracted name or NONE]
            EMAIL: [extracted email or NONE]
            PHONE: [extracted phone or NONE]
            MOVE_IN: [extracted move-in date or NONE]
            BEDS: [extracted bedroom count or NONE]
            UNIT: [extracted unit ID like A101, B402, C804 or NONE]
            """

            if ai_service.enabled:
                extraction_result = await ai_service.client.chat.completions.create(
                    model=ai_service.model,
                    messages=[{"role": "user", "content": extraction_prompt}],
                    max_tokens=200,
                    temperature=0.1,
                )

                extracted_text = extraction_result.choices[0].message.content
                logger.info(f"🤖 AI extracted data: {extracted_text}")

                # Parse the extracted data
                self._parse_ai_extracted_data(session, extracted_text)

        except Exception as e:
            logger.error(f"AI data extraction failed: {str(e)}")

    def _parse_ai_extracted_data(
        self, session: ConversationSession, extracted_text: str
    ):
        """Parse AI-extracted data and update session."""
        lines = extracted_text.strip().split("\n")

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().upper()
                value = value.strip()

                if value and value.upper() != "NONE":
                    if key == "NAME" and not session.prospect_data.name:
                        session.prospect_data.name = value
                        logger.info(f"🤖 AI extracted name: {value}")
                    elif key == "EMAIL" and not session.prospect_data.email:
                        if "@" in value:
                            session.prospect_data.email = value.lower()
                            logger.info(f"🤖 AI extracted email: {value}")
                    elif key == "PHONE" and not session.prospect_data.phone:
                        # Clean phone number
                        phone_digits = re.sub(r"[^\d]", "", value)
                        if len(phone_digits) == 10:
                            session.prospect_data.phone = f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
                            logger.info(
                                f"🤖 AI extracted phone: {session.prospect_data.phone}"
                            )
                    elif key == "MOVE_IN" and not session.prospect_data.move_in_date:
                        session.prospect_data.move_in_date = value
                        logger.info(f"🤖 AI extracted move-in: {value}")
                    elif key == "BEDS" and session.prospect_data.beds_wanted is None:
                        # Extract number from beds description
                        beds_match = re.search(r"\b([0-5])\b", value)
                        if beds_match:
                            session.prospect_data.beds_wanted = int(beds_match.group(1))
                            logger.info(f"🤖 AI extracted beds: {beds_match.group(1)}")
                    elif key == "UNIT" and not session.prospect_data.unit_id:
                        # Extract unit ID from conversation
                        unit_match = re.search(
                            r"\b([A-Z]\d{3}|[A-Z]\d{2}|Unit\s+[A-Z]\d{3})\b",
                            value,
                            re.IGNORECASE,
                        )
                        if unit_match:
                            unit_id = unit_match.group(1).replace("Unit ", "").upper()
                            session.prospect_data.unit_id = unit_id
                            logger.info(f"🤖 AI extracted unit: {unit_id}")

    def _ai_indicates_booking_complete(self, ai_response: str) -> bool:
        """Check if AI response indicates booking is complete."""
        booking_complete_phrases = [
            "tour is confirmed",
            "tour is scheduled",
            "confirmation email",
            "I've sent",
            "email sent",
            "booking confirmed",
            "tour confirmed",
            "scheduled your tour",
            "booked your tour",
            "reservation confirmed",
        ]

        ai_lower = ai_response.lower()
        indicates_complete = any(
            phrase in ai_lower for phrase in booking_complete_phrases
        )

        if indicates_complete:
            logger.info(
                f"🤖 AI indicates booking complete with phrases: {[p for p in booking_complete_phrases if p in ai_lower]}"
            )

        return indicates_complete

    async def _extract_data_from_conversation_history(
        self, session: ConversationSession
    ):
        """Extract missing data from entire conversation history using AI."""
        try:
            # Get recent conversation context
            recent_messages = session.messages[-10:]  # Last 10 messages
            conversation_text = "\n".join(
                [f"{msg.sender}: {msg.text}" for msg in recent_messages]
            )

            missing_fields = self._get_missing_fields(session.prospect_data)
            if not missing_fields:
                return

            extraction_prompt = f"""
            Extract the following missing information from this conversation history:
            Missing: {', '.join(missing_fields)}

            Conversation:
            {conversation_text}

            Extract ONLY the missing information in this format:
            NAME: [name or NONE]
            EMAIL: [email or NONE]
            PHONE: [phone or NONE]
            MOVE_IN: [move-in date or NONE]
            BEDS: [bedroom count or NONE]
            UNIT: [unit ID like A101, B402, C804 or NONE]
            """

            if ai_service.enabled:
                extraction_result = await ai_service.client.chat.completions.create(
                    model=ai_service.model,
                    messages=[{"role": "user", "content": extraction_prompt}],
                    max_tokens=200,
                    temperature=0.1,
                )

                extracted_text = extraction_result.choices[0].message.content
                logger.info(f"🤖 AI extracted from history: {extracted_text}")

                # Parse the extracted data
                self._parse_ai_extracted_data(session, extracted_text)

        except Exception as e:
            logger.error(f"AI history extraction failed: {str(e)}")

    def _show_selected_units(self, session: ConversationSession) -> str:
        """Show currently selected units for multiple booking."""
        if not session.prospect_data.selected_units:
            return "You haven't selected any units yet. Click on apartment listings or tell me which units you'd like to see!"

        unit_details = []
        for unit_id in session.prospect_data.selected_units:
            unit = inventory_service.get_unit_by_id(unit_id)
            if unit:
                unit_details.append(
                    f"• Unit {unit.unit_id}: {unit.beds} bed/{unit.baths} bath, "
                    f"{unit.sqft} sq ft, ${unit.rent:,}/month"
                )

        if not unit_details:
            return "Your selected units are no longer available. Please make new selections."

        unit_list = "\n".join(unit_details)
        count = len(session.prospect_data.selected_units)

        return f"""📋 Your Selected Units ({count} units):

{unit_list}

Ready to book all {count} units? Just say 'book all' or 'confirm booking'!
You can also:
• Add more units by clicking on listings
• Remove a unit: "remove unit A101"
• Clear all selections: "clear selections"
"""

    def _clear_selected_units(self, session: ConversationSession) -> str:
        """Clear all selected units."""
        count = len(session.prospect_data.selected_units)
        session.prospect_data.selected_units.clear()

        if count > 0:
            return f"✅ Cleared {count} selected units. You can now make new selections!"
        else:
            return "You don't have any units selected."

    def _add_selected_unit(self, session: ConversationSession, unit_id: str) -> str:
        """Add a specific unit to selections."""
        # Check if unit exists and is available
        unit = inventory_service.get_unit_by_id(unit_id)
        if not unit:
            return f"❌ Unit {unit_id} does not exist."

        if not unit.available:
            return f"❌ Unit {unit_id} is not available for booking."

        if unit_id in session.prospect_data.selected_units:
            return f"Unit {unit_id} is already in your selections."

        # Add to selections
        session.prospect_data.selected_units.append(unit_id)
        count = len(session.prospect_data.selected_units)

        return (
            f"✅ Added Unit {unit_id} to your selections! You now have {count} units selected. "
            f"Say 'show selected' to see all your selections or 'book all' when ready to book."
        )

    def _remove_selected_unit(self, session: ConversationSession, unit_id: str) -> str:
        """Remove a specific unit from selections."""
        if unit_id in session.prospect_data.selected_units:
            session.prospect_data.selected_units.remove(unit_id)
            remaining = len(session.prospect_data.selected_units)
            return f"✅ Removed Unit {unit_id} from your selections. You have {remaining} units selected."
        else:
            return f"Unit {unit_id} is not in your current selections."

    async def _handle_multiple_booking_intent(
        self, session: ConversationSession
    ) -> str:
        """Handle booking multiple units simultaneously."""
        logger.info(
            "🚀 MULTIPLE BOOKING INTENT TRIGGERED - Starting multiple booking process"
        )
        logger.info(f"   Session ID: {session.session_id}")
        logger.info(f"   Prospect: {session.prospect_data.name}")
        logger.info(f"   Email: {session.prospect_data.email}")
        logger.info(f"   Selected Units: {session.prospect_data.selected_units}")

        if not self._is_data_complete(session.prospect_data):
            missing_fields = self._get_missing_fields(session.prospect_data)
            logger.warning(
                f"❌ Multiple booking failed - missing data: {missing_fields}"
            )
            return f"I need a bit more information before booking. Missing: {', '.join(missing_fields)}"

        if not session.prospect_data.selected_units:
            return "You haven't selected any units to book. Please select units first by clicking on listings or telling me which units you want."

        # Validate all selected units are still available
        available_units = []
        unavailable_units = []

        for unit_id in session.prospect_data.selected_units:
            unit = inventory_service.get_unit_by_id(unit_id)
            if unit and unit.available:
                available_units.append(unit)
            else:
                unavailable_units.append(unit_id)

        if unavailable_units:
            # Remove unavailable units from selection
            for unit_id in unavailable_units:
                session.prospect_data.selected_units.remove(unit_id)

            if not available_units:
                return f"I'm sorry, none of your selected units are available anymore: {', '.join(unavailable_units)}. Please make new selections."
            else:
                logger.warning(f"Some units became unavailable: {unavailable_units}")

        # Generate tour slot
        tour_date, tour_time = email_service.generate_tour_slot()

        # Create booked units with individual confirmation numbers
        booked_units = []
        for unit in available_units:
            confirmation_number = email_service.generate_confirmation_number()
            booked_unit = BookedUnit(
                unit_id=unit.unit_id,
                beds=unit.beds,
                baths=unit.baths,
                sqft=unit.sqft,
                rent=unit.rent,
                confirmation_number=confirmation_number,
            )
            booked_units.append(booked_unit)

        # Create multiple booking confirmation
        master_confirmation_number = email_service.generate_confirmation_number()
        confirmation = MultipleBookingConfirmation(
            prospect_name=session.prospect_data.name,
            prospect_email=session.prospect_data.email,
            booked_units=booked_units,
            property_address=session.prospect_data.property_address,
            tour_date=tour_date,
            tour_time=tour_time,
            master_confirmation_number=master_confirmation_number,
        )

        # Send multiple booking email confirmation
        logger.info("📧 CALLING MULTIPLE BOOKING EMAIL SERVICE")
        logger.info(f"   Recipient: {confirmation.prospect_email}")
        logger.info(f"   Units: {[unit.unit_id for unit in booked_units]}")
        logger.info(f"   Master Confirmation: {master_confirmation_number}")

        email_sent = await email_service.send_multiple_booking_confirmation(
            confirmation
        )

        logger.info(
            f"📧 MULTIPLE BOOKING EMAIL SERVICE RESULT: {'SUCCESS' if email_sent else 'FAILED'}"
        )

        if email_sent:
            session.state = ChatState.BOOKING_CONFIRMED
            # Reserve all units
            for unit in available_units:
                inventory_service.reserve_unit(unit.unit_id)

            # Update prospect data
            session.prospect_data.unit_id = available_units[0].unit_id  # Legacy field

            unit_list = ", ".join([unit.unit_id for unit in available_units])
            notification_msg = (
                f"I've sent a comprehensive confirmation email to {session.prospect_data.email}. "
                f"Please check your inbox and spam/junk folder if you don't see it within a few minutes"
            )

            return (
                f"🎉 Perfect! Your tours for {len(available_units)} units are confirmed for {tour_date} at {tour_time}. "
                f"Units booked: {unit_list}. "
                f"{notification_msg}. The email contains all the details for each unit including individual confirmation numbers. "
                f"If you have any issues, you can also call our leasing office at {email_service.leasing_office_phone}. "
                f"We'll see you at {session.prospect_data.property_address}!"
            )
        else:
            # Still confirm the booking even if email fails
            session.state = ChatState.BOOKING_CONFIRMED
            for unit in available_units:
                inventory_service.reserve_unit(unit.unit_id)
            session.prospect_data.unit_id = available_units[0].unit_id

            unit_list = ", ".join([unit.unit_id for unit in available_units])
            return (
                f"✅ Your tours for {len(available_units)} units are confirmed for {tour_date} at {tour_time}! "
                f"Units: {unit_list}. "
                f"📧 Email notifications are currently unavailable (demo mode), but your bookings are secured. "
                f"📍 Location: {email_service.property_address} "
                f"📞 Contact: {email_service.leasing_office_phone} "
                f"💡 Please save these details for your records!"
            )


# Global instance
chat_service = ChatService()
