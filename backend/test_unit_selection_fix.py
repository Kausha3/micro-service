#!/usr/bin/env python3
"""
Quick test to verify the unit selection fix works.
"""

import asyncio
import sys
import os
import uuid
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import (
    ConversationSession, 
    ProspectData, 
    ChatState, 
    AIContext,
    ChatMessage
)
from chat_service import chat_service

async def test_unit_selection_commands():
    """Test the unit selection commands that were missing."""
    print("🧪 Testing Unit Selection Commands Fix")
    print("=" * 50)
    
    # Create a test session
    session_id = str(uuid.uuid4())
    session = ConversationSession(
        session_id=session_id,
        state=ChatState.GREETING,
        prospect_data=ProspectData(),
        messages=[],
        ai_context=AIContext(),
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    
    # Test messages that were failing
    test_messages = [
        "Add unit B604 to my selections",
        "Add unit A101 to my selections", 
        "show selected",
        "Remove unit B604 from my selections",
        "show selected"
    ]
    
    for message_text in test_messages:
        print(f"\n📝 Testing: '{message_text}'")
        
        # Create message object
        message = ChatMessage(message=message_text, session_id=session_id)
        
        # Process the message
        try:
            response = await chat_service.process_message(message)
            print(f"   ✅ Response: {response.reply[:100]}...")
            print(f"   📋 Selected Units: {session.prospect_data.selected_units}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_unit_selection_commands())
