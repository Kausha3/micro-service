#!/usr/bin/env python3
"""
Test script to verify the improved AI service configuration
"""

import asyncio
import os
import sys

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@pytest.mark.asyncio
async def test_ai_service():
    """Test the improved AI service"""
    try:
        # Import the AI service
        from datetime import datetime

        from ai_service import get_ai_service
        from models import AIContext, ChatState, ConversationSession, ProspectData

        print("🚀 Testing Improved AI Service")
        print("=" * 50)

        # Get AI service instance
        ai_service = get_ai_service()

        # Check if AI service is enabled
        print(f"AI Service Enabled: {'✅' if ai_service.enabled else '❌'}")
        print(f"Model: {ai_service.model}")
        print(f"Max Retries: {ai_service.max_retries}")
        print(f"Retry Delay: {ai_service.retry_delay}s")

        if not ai_service.enabled:
            print("❌ AI service is disabled. Cannot proceed with test.")
            return False

        # Create a test session
        session = ConversationSession(
            session_id="test-session",
            state=ChatState.GREETING,
            prospect_data=ProspectData(),
            messages=[],
            ai_context=AIContext(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        # Test simple message
        print("\n🔄 Testing simple AI response...")
        test_message = "Hello, I'm looking for an apartment."

        try:
            response = await ai_service.generate_response(session, test_message)
            print(f"✅ AI Response received:")
            print(f"   Length: {len(response)} characters")
            print(f"   Preview: {response[:100]}...")
            return True

        except Exception as e:
            print(f"❌ AI response generation failed: {e}")
            return False

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


@pytest.mark.asyncio
async def test_openai_direct():
    """Test OpenAI connection directly"""
    try:
        from openai import AsyncOpenAI

        print("\n🔄 Testing direct OpenAI connection...")

        client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"), timeout=45.0, max_retries=0
        )

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello in one word."}],
            max_tokens=5,
            temperature=0,
        )

        print(f"✅ Direct OpenAI connection successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ Direct OpenAI connection failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🧪 AI Service Fix Verification")
    print("=" * 50)

    # Test 1: Direct OpenAI connection
    direct_ok = await test_openai_direct()

    # Test 2: AI Service
    service_ok = await test_ai_service()

    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Direct OpenAI:  {'✅ PASS' if direct_ok else '❌ FAIL'}")
    print(f"AI Service:     {'✅ PASS' if service_ok else '❌ FAIL'}")

    if direct_ok and service_ok:
        print("\n🎉 All tests passed! AI service should be working now.")
        print("   You can restart the application to apply the fixes.")
    elif direct_ok and not service_ok:
        print("\n⚠️  Direct connection works but AI service has issues.")
        print("   Check the AI service configuration and imports.")
    else:
        print("\n❌ Connection issues detected.")
        print("   Check your API key and network connectivity.")


if __name__ == "__main__":
    asyncio.run(main())
