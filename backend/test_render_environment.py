#!/usr/bin/env python3
"""
Render Environment Test Module

This module provides tests to diagnose environment variable and OpenAI connectivity issues
specifically for Render deployment.

Tests:
1. Check all required environment variables
2. Test OpenAI connectivity with production-like settings
3. Validate Render deployment readiness
"""

import asyncio
import os
import sys
from typing import Dict

import pytest
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def check_environment_variables() -> Dict[str, bool]:
    """Check all required environment variables."""
    print("🔍 Checking Environment Variables...")
    print("=" * 50)

    required_vars = {
        "OPENAI_API_KEY": "OpenAI API key for AI features",
        "SMTP_EMAIL": "Email address for notifications",
        "SMTP_PASSWORD": "Email password/app password",
        "PROPERTY_NAME": "Property name for branding",
        "PROPERTY_ADDRESS": "Property address for context",
    }

    optional_vars = {
        "OPENAI_MODEL": "OpenAI model (defaults to gpt-3.5-turbo)",
        "OPENAI_TIMEOUT": "API timeout in seconds (defaults to 30)",
        "OPENAI_MAX_RETRIES": "Max retry attempts (defaults to 2)",
        "ENVIRONMENT": "Environment setting (development/production)",
        "PORT": "Server port (defaults to 8000)",
        "FRONTEND_URL": "Frontend URL for CORS",
    }

    results = {}

    print("📋 Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print(f"   ✅ {var}: Set ({description})")
            results[var] = True
        else:
            print(f"   ❌ {var}: Missing or placeholder ({description})")
            results[var] = False

    print("\n📋 Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value} ({description})")
            results[var] = True
        else:
            print(f"   ⚠️  {var}: Using default ({description})")
            results[var] = False

    return results


async def check_openai_connectivity():
    """Test OpenAI connectivity with Render-optimized settings."""
    print("\n🚀 Testing OpenAI with Render Settings...")
    print("=" * 50)

    try:
        from openai import AsyncOpenAI
        from openai._exceptions import (
            APIConnectionError,
            APITimeoutError,
            RateLimitError,
        )

        # Use production-like settings
        api_key = os.getenv("OPENAI_API_KEY")
        model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        timeout = float(os.getenv("OPENAI_TIMEOUT", "30.0"))  # Render-optimized
        max_retries = int(os.getenv("OPENAI_MAX_RETRIES", "2"))  # Render-optimized

        print(f"📋 Configuration:")
        print(f"   Model: {model}")
        print(f"   Timeout: {timeout}s (Render-optimized)")
        print(f"   Max Retries: {max_retries} (Render-optimized)")
        print(f"   API Key: {'✅ Set' if api_key else '❌ Missing'}")

        if not api_key or api_key == "your_openai_api_key_here":
            print("\n❌ Error: OPENAI_API_KEY not configured")
            return False

        # Initialize client with Render-optimized settings
        client = AsyncOpenAI(
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )

        print(f"\n🔗 Testing connection to OpenAI...")

        # Test with a simple request
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Test connection. Respond with 'Connection successful.'",
                }
            ],
            max_tokens=10,
            temperature=0.1,
        )

        ai_response = response.choices[0].message.content.strip()
        print(f"✅ Connection successful!")
        print(f"📝 AI Response: {ai_response}")
        print(f"📊 Token Usage:")
        print(f"   Prompt: {response.usage.prompt_tokens}")
        print(f"   Completion: {response.usage.completion_tokens}")
        print(f"   Total: {response.usage.total_tokens}")

        return True

    except (APIConnectionError, APITimeoutError) as e:
        print(f"❌ Connection Error: {str(e)}")
        print("\n🔧 Troubleshooting Tips:")
        print("   1. Check if your OpenAI API key is valid")
        print("   2. Verify you have sufficient OpenAI credits")
        print("   3. Check Render's network connectivity")
        print("   4. Try reducing timeout settings")
        return False

    except RateLimitError as e:
        print(f"⚠️  Rate Limit Error: {str(e)}")
        print("   Your API key is working but you've hit rate limits")
        return False

    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        return False


def provide_render_recommendations(env_results: Dict[str, bool], openai_success: bool):
    """Provide specific recommendations for Render deployment."""
    print("\n🎯 Render Deployment Recommendations...")
    print("=" * 50)

    if not openai_success:
        print("🚨 OpenAI Connection Issues:")
        print("   1. In Render Dashboard → Environment:")
        print("      - Verify OPENAI_API_KEY is set correctly")
        print("      - Ensure no extra spaces or quotes around the key")
        print("      - Set OPENAI_TIMEOUT=30 (shorter for Render)")
        print("      - Set OPENAI_MAX_RETRIES=2 (fewer retries)")
        print("      - Set ENVIRONMENT=production")
        print()
        print("   2. Check OpenAI Account:")
        print(
            "      - Verify API key is active at https://platform.openai.com/api-keys"
        )
        print("      - Check billing and usage limits")
        print("      - Ensure you have sufficient credits")
        print()

    missing_vars = [
        var
        for var, present in env_results.items()
        if not present
        and var
        in [
            "OPENAI_API_KEY",
            "SMTP_EMAIL",
            "SMTP_PASSWORD",
            "PROPERTY_NAME",
            "PROPERTY_ADDRESS",
        ]
    ]

    if missing_vars:
        print("📝 Missing Environment Variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("   → Set these in Render Dashboard → Environment")
        print()

    print("✅ Recommended Render Environment Variables:")
    print("   ENVIRONMENT=production")
    print("   OPENAI_TIMEOUT=30")
    print("   OPENAI_MAX_RETRIES=2")
    print("   OPENAI_MODEL=gpt-3.5-turbo  # Faster and cheaper than gpt-4")
    print()

    if openai_success:
        print("🎉 OpenAI connection is working! Your deployment should work correctly.")
    else:
        print("⚠️  Fix the OpenAI connection issues above before deploying.")


def test_environment_variables():
    """Test that all required environment variables are configured."""
    # Check for critical variables (allow test values for testing)
    critical_vars = ["OPENAI_API_KEY", "SMTP_EMAIL", "SMTP_PASSWORD"]
    missing_vars = []

    for var in critical_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        elif var == "OPENAI_API_KEY" and value == "your_openai_api_key_here":
            missing_vars.append(f"{var} (placeholder value)")

    # Only fail if completely missing (allow test values)
    completely_missing = [var for var in critical_vars if not os.getenv(var)]
    assert (
        not completely_missing
    ), f"Missing required environment variables: {completely_missing}"


@pytest.mark.asyncio
async def test_openai_render_connectivity():
    """Test OpenAI connectivity with Render-optimized settings."""
    api_key = os.getenv("OPENAI_API_KEY")

    # Skip test if using mock/test credentials
    if not api_key or api_key in ["test-key-mock", "your_openai_api_key_here"]:
        pytest.skip("Skipping OpenAI test - no valid API key configured")

    success = await check_openai_connectivity()
    assert success, "OpenAI connection failed with Render settings"


def test_render_deployment_readiness():
    """Test overall readiness for Render deployment."""
    env_results = check_environment_variables()

    required_vars_ok = all(
        env_results.get(var, False)
        for var in ["OPENAI_API_KEY", "SMTP_EMAIL", "SMTP_PASSWORD"]
    )

    assert required_vars_ok, "Not all required environment variables are configured"


async def main():
    """Main function for standalone execution."""
    print("🧪 Render Environment Test Suite")
    print("=" * 50)

    # Test 1: Environment variables
    env_results = check_environment_variables()

    # Test 2: OpenAI connectivity
    openai_success = await check_openai_connectivity()

    # Test 3: Recommendations
    provide_render_recommendations(env_results, openai_success)

    # Summary
    print("\n📊 Test Summary:")
    print("=" * 50)
    required_vars_ok = all(
        env_results.get(var, False)
        for var in ["OPENAI_API_KEY", "SMTP_EMAIL", "SMTP_PASSWORD"]
    )

    if required_vars_ok and openai_success:
        print("🎉 All tests passed! Ready for Render deployment.")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
