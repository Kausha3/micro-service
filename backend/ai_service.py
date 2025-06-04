"""
AI Service for Lead-to-Lease Chat Concierge

This module provides AI-powered conversation capabilities using OpenAI's GPT models.
Features include:
- Natural language understanding and intent detection
- Contextual conversation management
- Intelligent database query generation
- Dynamic response generation based on property inventory
- Conversation flow optimization

Author: Augment Agent
Version: 1.0.0
"""

import os
import json
import logging
from typing import Optional, Dict, List, Any
from openai import AsyncOpenAI
from models import ConversationSession, AIContext, Unit
from inventory_service import inventory_service

logger = logging.getLogger(__name__)


class AIService:
    """
    AI-powered conversation service using OpenAI GPT models.
    
    Provides natural language understanding, intent detection, and intelligent
    response generation for apartment leasing conversations.
    """

    def __init__(self):
        """Initialize AI service with OpenAI client and configuration."""
        self.client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.property_name = os.getenv("PROPERTY_NAME", "Luxury Apartments at Main Street")
        self.property_address = os.getenv("PROPERTY_ADDRESS", "123 Main St, Anytown, ST 12345")
        
        # Validate API key
        if not os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY") == "your_openai_api_key_here":
            logger.warning("OpenAI API key not configured. AI features will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info(f"AI service initialized with model: {self.model}")

    async def generate_response(
        self, 
        session: ConversationSession, 
        user_message: str
    ) -> str:
        """
        Generate AI-powered response based on conversation context and user message.
        
        Args:
            session: Current conversation session with context
            user_message: User's latest message
            
        Returns:
            str: AI-generated response
        """
        if not self.enabled:
            return "I'm sorry, AI features are currently unavailable. Please ensure the OpenAI API key is configured."

        try:
            # Get available inventory for context
            available_units = inventory_service.get_all_available_units()
            
            # Build conversation context
            conversation_history = self._build_conversation_history(session)
            
            # Create system prompt with property and inventory context
            system_prompt = self._create_system_prompt(available_units, session.prospect_data)
            
            # Generate response using OpenAI
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    *conversation_history,
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # Update AI context
            await self._update_ai_context(session, user_message, ai_response)
            
            return ai_response
            
        except Exception as e:
            logger.error(f"AI response generation failed: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Could you please try again?"

    def _create_system_prompt(self, available_units: List[Unit], prospect_data) -> str:
        """Create comprehensive system prompt with property and inventory context."""
        
        # Format available units for context
        units_context = ""
        if available_units:
            units_by_beds = {}
            for unit in available_units:
                beds = unit.beds if unit.beds > 0 else "Studio"
                if beds not in units_by_beds:
                    units_by_beds[beds] = []
                units_by_beds[beds].append(unit)
            
            units_context = "Available Units:\n"
            # Sort by bedroom count, handling both int and string types
            sorted_beds = sorted(units_by_beds.items(), key=lambda x: (0 if x[0] == "Studio" else x[0]))
            for beds, units in sorted_beds:
                units_context += f"\n{beds} bedroom{'s' if beds != 1 and beds != 'Studio' else ''}:\n"
                for unit in units:
                    units_context += f"- Unit {unit.unit_id}: {unit.sqft} sq ft, ${unit.rent}/month, {unit.baths} bath{'s' if unit.baths != 1 else ''}\n"
        
        # Current prospect data context
        prospect_context = ""
        if prospect_data.name:
            prospect_context += f"Prospect name: {prospect_data.name}\n"
        if prospect_data.email:
            prospect_context += f"Email: {prospect_data.email}\n"
        if prospect_data.phone:
            prospect_context += f"Phone: {prospect_data.phone}\n"
        if prospect_data.move_in_date:
            prospect_context += f"Move-in date: {prospect_data.move_in_date}\n"
        if prospect_data.beds_wanted:
            prospect_context += f"Bedrooms wanted: {prospect_data.beds_wanted}\n"

        return f"""You are an AI-powered leasing assistant for {self.property_name} located at {self.property_address}. 

Your role is to help prospective tenants find the perfect apartment through natural, helpful conversation. You should:

1. **Be conversational and natural** - Respond to users in a friendly, helpful manner without being overly formal
2. **Understand natural language** - Interpret user queries like "What do you have available?", "I need a 2-bedroom", "Show me your cheapest units"
3. **Provide relevant information** - Use the available inventory to answer questions about units, pricing, and availability
4. **Guide toward booking** - Naturally guide interested prospects toward scheduling a tour
5. **Collect information gradually** - Gather name, email, phone, move-in date, and bedroom preference through natural conversation
6. **Handle edge cases gracefully** - If you don't understand something, ask for clarification

{units_context}

Current prospect information collected:
{prospect_context if prospect_context else "No information collected yet."}

IMPORTANT GUIDELINES:
- Always be helpful and informative about available units
- If asked about specific units, provide details from the available inventory
- If someone wants to book a tour, you'll need their name, email, phone, move-in date, and bedroom preference
- Don't be pushy - let the conversation flow naturally
- If inventory doesn't match their needs, be honest but offer alternatives
- Keep responses concise but informative (under 200 words typically)
- Use a warm, professional tone that makes people feel welcome

Remember: You're here to help people find their perfect home!

IMPORTANT EMAIL GUIDANCE:
- When mentioning email confirmations, always remind users to check their spam/junk folder
- If users report not receiving emails, suggest checking spam folder and adding our email to their contacts
- Provide alternative contact methods (phone number) for urgent matters"""

    def _build_conversation_history(self, session: ConversationSession) -> List[Dict[str, str]]:
        """Build conversation history for AI context."""
        history = []
        
        # Include recent messages (last 10 to stay within token limits)
        recent_messages = session.messages[-10:] if len(session.messages) > 10 else session.messages
        
        for msg in recent_messages:
            role = "assistant" if msg.sender == "bot" else "user"
            history.append({"role": role, "content": msg.text})
        
        return history

    async def _update_ai_context(
        self, 
        session: ConversationSession, 
        user_message: str, 
        ai_response: str
    ):
        """Update AI context with conversation insights."""
        try:
            # Extract intents and preferences using a simple analysis
            intents = await self._extract_intents(user_message)
            preferences = await self._extract_preferences(user_message, session.ai_context.user_preferences)
            
            # Update AI context
            session.ai_context.last_ai_response = ai_response
            session.ai_context.extracted_intents.extend(intents)
            session.ai_context.user_preferences.update(preferences)
            
            # Keep only recent intents (last 5)
            session.ai_context.extracted_intents = session.ai_context.extracted_intents[-5:]
            
        except Exception as e:
            logger.error(f"Failed to update AI context: {str(e)}")

    async def _extract_intents(self, user_message: str) -> List[str]:
        """Extract user intents from message."""
        intents = []
        message_lower = user_message.lower()
        
        # Simple intent detection (can be enhanced with AI)
        if any(word in message_lower for word in ["book", "tour", "visit", "schedule", "appointment"]):
            intents.append("booking_intent")
        
        if any(word in message_lower for word in ["apartment", "unit", "bedroom", "available", "show me"]):
            intents.append("search_intent")
        
        if any(word in message_lower for word in ["price", "cost", "rent", "expensive", "cheap", "budget"]):
            intents.append("pricing_inquiry")
        
        if any(word in message_lower for word in ["amenities", "features", "gym", "pool", "parking"]):
            intents.append("amenities_inquiry")
        
        return intents

    async def _extract_preferences(self, user_message: str, existing_preferences: Dict) -> Dict:
        """Extract user preferences from message."""
        preferences = existing_preferences.copy()
        message_lower = user_message.lower()
        
        # Extract bedroom preferences
        import re
        bedroom_match = re.search(r'(\d+)\s*(?:bed|bedroom)', message_lower)
        if bedroom_match:
            preferences["bedrooms"] = int(bedroom_match.group(1))
        
        # Extract budget preferences
        budget_match = re.search(r'\$(\d+(?:,\d+)?)', user_message)
        if budget_match:
            preferences["max_budget"] = int(budget_match.group(1).replace(',', ''))
        
        # Extract move-in timeframe
        if any(word in message_lower for word in ["asap", "immediately", "soon"]):
            preferences["move_in_urgency"] = "immediate"
        elif any(word in message_lower for word in ["month", "months"]):
            preferences["move_in_urgency"] = "flexible"
        
        return preferences

    async def should_collect_information(self, session: ConversationSession, user_message: str) -> Optional[str]:
        """
        Determine if we should collect specific information based on conversation context.
        
        Returns:
            Optional[str]: Field to collect ("name", "email", "phone", "move_in_date", "beds_wanted") or None
        """
        # Check if user expressed booking intent
        if any(intent in session.ai_context.extracted_intents for intent in ["booking_intent"]):
            # Check what information is missing
            if not session.prospect_data.name:
                return "name"
            elif not session.prospect_data.email:
                return "email"
            elif not session.prospect_data.phone:
                return "phone"
            elif not session.prospect_data.move_in_date:
                return "move_in_date"
            elif not session.prospect_data.beds_wanted:
                return "beds_wanted"
        
        return None


# Global service instance
ai_service = AIService()
