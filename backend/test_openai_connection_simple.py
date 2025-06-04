#!/usr/bin/env python3
"""
Simple OpenAI Connection Test Script

This script tests the OpenAI API connection with various configurations
to diagnose connectivity issues.
"""

import asyncio
import os
import sys
import time

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_basic_connectivity():
    """Test basic internet connectivity using socket connection"""
    import socket

    try:
        # Test DNS resolution and basic connectivity using socket
        socket.setdefaulttimeout(10)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(("api.openai.com", 443))
        sock.close()

        if result == 0:
            print("✅ Basic connectivity to api.openai.com: OK")
            return True
        else:
            print("❌ Basic connectivity to api.openai.com: FAILED")
            print(f"   Connection error code: {result}")
            return False
    except Exception as e:
        print(f"❌ Connectivity test failed: {e}")
        return False


def test_api_key_format():
    """Test if API key has correct format"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment")
        return False

    if not api_key.startswith("sk-"):
        print("❌ API key doesn't start with 'sk-'")
        return False

    if len(api_key) < 40:
        print("❌ API key seems too short")
        return False

    print(f"✅ API key format looks correct (length: {len(api_key)})")
    return True


async def test_openai_simple():
    """Test OpenAI connection with minimal configuration"""
    try:
        from openai import AsyncOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        client = AsyncOpenAI(api_key=api_key, timeout=30.0, max_retries=1)

        print("🔄 Testing OpenAI connection...")

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": 'Say "Hello" in one word.'}],
            max_tokens=5,
            temperature=0,
        )

        print("✅ OpenAI connection successful!")
        print(f"   Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        return False


async def test_openai_with_retries():
    """Test OpenAI connection with retry logic"""
    try:
        from openai import AsyncOpenAI
        from openai._exceptions import APIConnectionError, APITimeoutError

        api_key = os.getenv("OPENAI_API_KEY")
        client = AsyncOpenAI(api_key=api_key, timeout=45.0, max_retries=3)

        print("🔄 Testing OpenAI connection with retries...")

        for attempt in range(3):
            try:
                response = await client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test message"}],
                    max_tokens=10,
                    temperature=0,
                )

                print(f"✅ OpenAI connection successful on attempt {attempt + 1}!")
                print(f"   Response: {response.choices[0].message.content}")
                return True

            except (APIConnectionError, APITimeoutError) as e:
                print(f"⚠️  Attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

        print("❌ All retry attempts failed")
        return False

    except Exception as e:
        print(f"❌ OpenAI test with retries failed: {e}")
        return False


async def main():
    """Run all connectivity tests"""
    print("🚀 OpenAI Connection Diagnostic Tool")
    print("=" * 50)

    # Test 1: Basic connectivity
    print("\n1. Testing basic connectivity...")
    connectivity_ok = test_basic_connectivity()

    # Test 2: API key format
    print("\n2. Testing API key format...")
    api_key_ok = test_api_key_format()

    if not api_key_ok:
        print("\n❌ Cannot proceed without valid API key")
        return

    # Test 3: Simple OpenAI connection
    print("\n3. Testing simple OpenAI connection...")
    simple_ok = await test_openai_simple()

    # Test 4: OpenAI with retries
    if not simple_ok:
        print("\n4. Testing OpenAI connection with retries...")
        retry_ok = await test_openai_with_retries()
    else:
        retry_ok = True

    # Summary
    print("\n" + "=" * 50)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 50)
    print(f"Basic Connectivity: {'✅ PASS' if connectivity_ok else '❌ FAIL'}")
    print(f"API Key Format:     {'✅ PASS' if api_key_ok else '❌ FAIL'}")
    print(f"Simple Connection:  {'✅ PASS' if simple_ok else '❌ FAIL'}")
    print(f"Retry Connection:   {'✅ PASS' if retry_ok else '❌ FAIL'}")

    if simple_ok or retry_ok:
        print("\n🎉 OpenAI connection is working!")
        print("   The issue might be in the application configuration.")
    else:
        print("\n🔧 RECOMMENDATIONS:")
        if not connectivity_ok:
            print("   - Check your internet connection")
            print("   - Check if firewall is blocking api.openai.com")
        if not simple_ok and not retry_ok:
            print("   - Verify your OpenAI API key is valid and has credits")
            print("   - Check OpenAI service status at status.openai.com")
            print("   - Try using gpt-3.5-turbo instead of gpt-4")


if __name__ == "__main__":
    asyncio.run(main())
