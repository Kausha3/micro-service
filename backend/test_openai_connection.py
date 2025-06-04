#!/usr/bin/env python3
"""
OpenAI Connection Test Script

This script tests the OpenAI API connection with the current configuration.
Use this to verify your setup before deploying to Render.

Usage:
    python test_openai_connection.py

Environment Variables Required:
    OPENAI_API_KEY - Your OpenAI API key
    OPENAI_MODEL - Model to use (default: gpt-3.5-turbo)
    OPENAI_TIMEOUT - Timeout in seconds (default: 60.0)
    OPENAI_MAX_RETRIES - Max retry attempts (default: 3)
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_openai_connection():
    """Test OpenAI API connection with current configuration."""

    print("🔍 Testing OpenAI Connection...")
    print("=" * 50)

    # Check environment variables
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    timeout = float(os.getenv("OPENAI_TIMEOUT", "60.0"))
    max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "3"))

    print(f"📋 Configuration:")
    print(f"   Model: {model}")
    print(f"   Timeout: {timeout}s")
    print(f"   Max Retries: {max_retries}")
    print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")

    if not api_key or api_key == "your_openai_api_key_here":
        print("\n❌ Error: OPENAI_API_KEY not configured")
        print("Please set your OpenAI API key in the .env file")
        return False

    # Test the connection
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=api_key, timeout=timeout, max_retries=max_retries)

        print(f"\n🚀 Testing connection to OpenAI...")

        # Simple test request
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {
                    "role": "user",
                    "content": "Say 'Connection test successful' if you can read this.",
                },
            ],
            max_tokens=50,
            temperature=0.1,
        )

        ai_response = response.choices[0].message.content.strip()
        print(f"✅ Connection successful!")
        print(f"📝 AI Response: {ai_response}")

        # Test usage information
        if hasattr(response, "usage"):
            usage = response.usage
            print(f"📊 Token Usage:")
            print(f"   Prompt: {usage.prompt_tokens}")
            print(f"   Completion: {usage.completion_tokens}")
            print(f"   Total: {usage.total_tokens}")

        return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print(f"\n🔧 Troubleshooting tips:")
        print(f"   1. Verify your API key at https://platform.openai.com/api-keys")
        print(f"   2. Check your OpenAI account billing status")
        print(f"   3. Ensure you have sufficient credits")
        print(f"   4. Try a different model (gpt-3.5-turbo vs gpt-4)")
        return False


def test_ai_service():
    """Test the AI service initialization."""
    print("\n🧠 Testing AI Service...")
    print("=" * 50)

    try:
        from ai_service import AIService

        ai_service = AIService()
        print(f"✅ AI Service initialized")
        print(f"   Enabled: {'✅' if ai_service.enabled else '❌'}")
        print(f"   Model: {ai_service.model}")
        print(f"   Property: {ai_service.property_name}")

        return ai_service.enabled

    except Exception as e:
        print(f"❌ AI Service initialization failed: {str(e)}")
        return False


async def main():
    """Main test function."""
    print("🧪 OpenAI Connection Test Suite")
    print("=" * 50)

    # Test 1: Environment configuration
    print("1️⃣ Testing environment configuration...")
    env_ok = True
    required_vars = ["OPENAI_API_KEY"]
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            print(f"   ❌ {var}: Not configured")
            env_ok = False
        else:
            print(f"   ✅ {var}: Configured")

    if not env_ok:
        print("\n❌ Environment configuration incomplete")
        return False

    # Test 2: Direct OpenAI connection
    print(f"\n2️⃣ Testing direct OpenAI connection...")
    connection_ok = await test_openai_connection()

    # Test 3: AI Service
    print(f"\n3️⃣ Testing AI Service integration...")
    service_ok = test_ai_service()

    # Summary
    print(f"\n📋 Test Summary:")
    print(f"   Environment: {'✅' if env_ok else '❌'}")
    print(f"   OpenAI Connection: {'✅' if connection_ok else '❌'}")
    print(f"   AI Service: {'✅' if service_ok else '❌'}")

    if env_ok and connection_ok and service_ok:
        print(
            f"\n🎉 All tests passed! Your OpenAI integration is ready for deployment."
        )
        return True
    else:
        print(f"\n⚠️ Some tests failed. Please fix the issues before deploying.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
