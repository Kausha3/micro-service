"""
Data Models for Lead-to-Lease Chat Concierge

This module defines all Pydantic models used throughout the application:
- Chat message and response models
- Conversation state management
- Prospect data collection and validation
- Session persistence models
- Inventory and booking models

All models include comprehensive validation and type safety.
"""

import os
import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class ChatState(str, Enum):
    """
    Enumeration of conversation states in the chat flow.

    Each state represents a specific step in the lead qualification process,
    ensuring proper data collection and conversation flow management.
    """

    GREETING = "greeting"  # Initial user greeting
    COLLECTING_NAME = "collecting_name"  # Collecting prospect's name
    COLLECTING_EMAIL = "collecting_email"  # Collecting email address
    COLLECTING_PHONE = "collecting_phone"  # Collecting phone number
    COLLECTING_MOVE_IN = "collecting_move_in"  # Collecting move-in date
    COLLECTING_BEDS = "collecting_beds"  # Collecting bedroom preference
    READY_TO_BOOK = "ready_to_book"  # Ready for tour booking
    BOOKING_CONFIRMED = "booking_confirmed"  # Tour successfully booked


class ChatMessage(BaseModel):
    """
    Incoming chat message from user.

    Attributes:
        message (str): The user's message text
        session_id (Optional[str]): Session ID for conversation continuity
    """

    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """
    Outgoing response from the chat assistant.

    Attributes:
        reply (str): The assistant's response text
        session_id (str): Session ID for tracking conversation
        state (Optional[ChatState]): Current conversation state
    """

    reply: str
    session_id: str
    state: Optional[ChatState] = None


class ProspectData(BaseModel):
    """
    Prospect information collected during conversation.

    This model stores all lead qualification data with validation.
    Property address is automatically populated from environment variables.

    Attributes:
        name (Optional[str]): Prospect's full name
        email (Optional[EmailStr]): Validated email address
        phone (Optional[str]): Phone number (validated format)
        move_in_date (Optional[str]): Desired move-in date
        beds_wanted (Optional[int]): Number of bedrooms desired (1-5)
        unit_id (Optional[str]): Reserved unit ID after booking (legacy - use selected_units)
        selected_units (list[str]): List of selected unit IDs for multiple booking support
        property_address (Optional[str]): Property address (auto-populated)
    """

    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    move_in_date: Optional[str] = None
    beds_wanted: Optional[int] = None
    unit_id: Optional[str] = None  # Legacy field for backward compatibility
    selected_units: list[str] = []  # New field for multiple booking support
    property_address: Optional[str] = None

    def __init__(self, **data):
        """Initialize with auto-populated property address from environment."""
        if "property_address" not in data or data["property_address"] is None:
            data["property_address"] = os.getenv(
                "PROPERTY_ADDRESS", "123 Main St, Anytown, ST 12345"
            )
        super().__init__(**data)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        # Remove all non-digit characters
        phone_digits = re.sub(r"\D", "", v)
        # Check if it's a valid US phone number (10 digits)
        if len(phone_digits) == 10:
            return f"({phone_digits[:3]}) {phone_digits[3:6]}-{phone_digits[6:]}"
        elif len(phone_digits) == 11 and phone_digits[0] == "1":
            return f"({phone_digits[1:4]}) {phone_digits[4:7]}-{phone_digits[7:]}"
        else:
            raise ValueError(
                "Please provide a valid 10-digit phone number (e.g., 555-123-4567)"
            )

    @field_validator("move_in_date")
    @classmethod
    def validate_move_in_date(cls, v):
        if v is None:
            return v

        # Allow any string input for move-in date (natural language is fine)
        # The chat service handles the conversion and validation logic
        # Only validate if it's in strict YYYY-MM-DD format
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            try:
                # Validate it's a real date if in YYYY-MM-DD format
                datetime.strptime(v, "%Y-%m-%d")
                return v
            except ValueError:
                raise ValueError(
                    "Invalid date format. If using YYYY-MM-DD format, please ensure it's a valid date."
                )

        # Allow natural language inputs like "ASAP", "January 2024", "March 15th", etc.
        return v

    @field_validator("beds_wanted")
    @classmethod
    def validate_beds(cls, v):
        if v is None:
            return v
        if v < 0 or v > 5:  # Allow 0 for studio units
            raise ValueError(
                "Number of bedrooms must be between 0 and 5 (0 for studio)"
            )
        return v


class ConversationMessage(BaseModel):
    """
    Individual message in a conversation.

    Represents a single message exchange between user and bot
    with timestamp for conversation history tracking.

    Attributes:
        sender (str): Message sender ("user" or "bot")
        text (str): Message content
        timestamp (datetime): When the message was sent
    """

    sender: str  # "user" or "bot"
    text: str
    timestamp: datetime


class AIContext(BaseModel):
    """
    AI conversation context for maintaining intelligent dialogue.

    Stores conversation context, user preferences, and AI-generated insights
    to enable natural, contextual responses throughout the conversation.

    Attributes:
        conversation_summary (str): AI-generated summary of conversation so far
        user_preferences (dict): Extracted user preferences and requirements
        last_ai_response (str): Last response generated by AI for context
        conversation_stage (str): Current stage of the conversation flow
        extracted_intents (list[str]): List of user intents detected by AI
    """

    conversation_summary: str = ""
    user_preferences: dict = {}
    last_ai_response: str = ""
    conversation_stage: str = "greeting"
    extracted_intents: list[str] = []


class ConversationSession(BaseModel):
    """
    Complete conversation session with state and history.

    Manages the entire conversation lifecycle including state tracking,
    prospect data collection, message history persistence, and AI context.

    Attributes:
        session_id (str): Unique session identifier
        state (ChatState): Current conversation state
        prospect_data (ProspectData): Collected prospect information
        messages (list[ConversationMessage]): Conversation history
        ai_context (AIContext): AI conversation context and insights
        created_at (datetime): Session creation timestamp
        updated_at (datetime): Last update timestamp
    """

    session_id: str
    state: ChatState
    prospect_data: ProspectData
    messages: list[ConversationMessage]
    ai_context: AIContext = AIContext()
    created_at: datetime
    updated_at: datetime


class Unit(BaseModel):
    """
    Apartment unit model for inventory management.

    Represents an individual apartment unit with all relevant details
    for prospect matching and booking.

    Attributes:
        unit_id (str): Unique unit identifier (e.g., "A101", "B205")
        beds (int): Number of bedrooms
        baths (float): Number of bathrooms (allows half baths)
        sqft (int): Square footage
        rent (int): Monthly rent amount
        available (bool): Current availability status
    """

    unit_id: str
    beds: int
    baths: float
    sqft: int
    rent: int
    available: bool


class TourConfirmation(BaseModel):
    """
    Tour booking confirmation details.

    Contains all information needed for tour confirmation emails
    and booking management.

    Attributes:
        prospect_name (str): Prospect's full name
        prospect_email (EmailStr): Validated email address
        unit_id (str): Reserved unit identifier
        property_address (str): Property location
        tour_date (str): Scheduled tour date
        tour_time (str): Scheduled tour time
    """

    prospect_name: str
    prospect_email: EmailStr
    unit_id: str
    property_address: str
    tour_date: str
    tour_time: str


class BookedUnit(BaseModel):
    """
    Individual booked unit details for multiple booking confirmations.

    Attributes:
        unit_id (str): Unit identifier
        beds (int): Number of bedrooms
        baths (float): Number of bathrooms
        sqft (int): Square footage
        rent (int): Monthly rent
        confirmation_number (str): Individual confirmation number for this unit
    """

    unit_id: str
    beds: int
    baths: float
    sqft: int
    rent: int
    confirmation_number: str


class MultipleBookingConfirmation(BaseModel):
    """
    Multiple tour booking confirmation details.

    Contains all information needed for multiple unit tour confirmation emails.

    Attributes:
        prospect_name (str): Prospect's full name
        prospect_email (EmailStr): Validated email address
        booked_units (list[BookedUnit]): List of all booked units with details
        property_address (str): Property location
        tour_date (str): Scheduled tour date
        tour_time (str): Scheduled tour time
        master_confirmation_number (str): Master confirmation number for the entire booking
    """

    prospect_name: str
    prospect_email: EmailStr
    booked_units: list[BookedUnit]
    property_address: str
    tour_date: str
    tour_time: str
    master_confirmation_number: str
