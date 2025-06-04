#!/usr/bin/env python3
"""
Test script to verify the parsing logic fix for the chat service.
This script tests the specific issue where "My name is Kausha, patermanav45@gmail.com 7272727272, Next month"
was incorrectly parsing name as "Next month" instead of "Kausha".
"""

import sys
import os
import re

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the necessary classes
from models import ProspectData, ConversationSession
from chat_service import ChatService

def test_parsing_logic():
    """Test the improved parsing logic with the problematic input."""
    
    print("🧪 Testing Chat Service Parsing Logic Fix")
    print("=" * 50)
    
    # Create a test session
    session = ConversationSession(
        session_id="test-session",
        prospect_data=ProspectData()
    )
    
    # Create chat service instance
    chat_service = ChatService()
    
    # Test the problematic input
    test_message = "My name is Kausha, patermanav45@gmail.com 7272727272, Next month"
    
    print(f"📝 Input message: '{test_message}'")
    print()
    
    # Parse the message
    chat_service._parse_multiple_fields_from_message(session, test_message)
    
    # Check the results
    print("📊 Parsing Results:")
    print(f"   Name: '{session.prospect_data.name}'")
    print(f"   Email: '{session.prospect_data.email}'")
    print(f"   Phone: '{session.prospect_data.phone}'")
    print(f"   Move-in Date: '{session.prospect_data.move_in_date}'")
    print()
    
    # Validate the results
    success = True
    expected_results = {
        'name': 'Kausha',
        'email': 'patermanav45@gmail.com',
        'phone': '7272727272',
        'move_in_date': 'Next month'
    }
    
    print("✅ Validation:")
    
    if session.prospect_data.name == expected_results['name']:
        print(f"   ✅ Name correctly parsed: '{session.prospect_data.name}'")
    else:
        print(f"   ❌ Name incorrectly parsed: expected '{expected_results['name']}', got '{session.prospect_data.name}'")
        success = False
    
    if session.prospect_data.email == expected_results['email']:
        print(f"   ✅ Email correctly parsed: '{session.prospect_data.email}'")
    else:
        print(f"   ❌ Email incorrectly parsed: expected '{expected_results['email']}', got '{session.prospect_data.email}'")
        success = False
    
    if session.prospect_data.phone == expected_results['phone']:
        print(f"   ✅ Phone correctly parsed: '{session.prospect_data.phone}'")
    else:
        print(f"   ❌ Phone incorrectly parsed: expected '{expected_results['phone']}', got '{session.prospect_data.phone}'")
        success = False
    
    if session.prospect_data.move_in_date == expected_results['move_in_date']:
        print(f"   ✅ Move-in date correctly parsed: '{session.prospect_data.move_in_date}'")
    else:
        print(f"   ❌ Move-in date incorrectly parsed: expected '{expected_results['move_in_date']}', got '{session.prospect_data.move_in_date}'")
        success = False
    
    print()
    
    if success:
        print("🎉 ALL TESTS PASSED! The parsing logic fix is working correctly.")
        print("   The issue where 'Next month' was assigned as the name has been resolved.")
        print("   Email confirmations will now use the correct prospect name.")
    else:
        print("❌ TESTS FAILED! The parsing logic still has issues.")
    
    return success

def test_additional_cases():
    """Test additional edge cases to ensure robustness."""
    
    print("\n🧪 Testing Additional Edge Cases")
    print("=" * 50)
    
    chat_service = ChatService()
    
    test_cases = [
        {
            'input': 'I am John Smith, john.smith@email.com, 5551234567, January 2025',
            'expected': {'name': 'John Smith', 'email': 'john.smith@email.com', 'phone': '5551234567', 'move_in_date': 'January 2025'}
        },
        {
            'input': 'Call me Sarah, sarah@test.com 9876543210, ASAP',
            'expected': {'name': 'Sarah', 'email': 'sarah@test.com', 'phone': '9876543210', 'move_in_date': 'ASAP'}
        },
        {
            'input': 'My name is Alex Johnson, alex@domain.org, (555) 123-4567, Next year',
            'expected': {'name': 'Alex Johnson', 'email': 'alex@domain.org', 'phone': '5551234567', 'move_in_date': 'Next year'}
        }
    ]
    
    all_passed = True
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: '{test_case['input']}'")
        
        # Create fresh session
        session = ConversationSession(
            session_id=f"test-session-{i}",
            prospect_data=ProspectData()
        )
        
        # Parse the message
        chat_service._parse_multiple_fields_from_message(session, test_case['input'])
        
        # Check results
        case_passed = True
        for field, expected_value in test_case['expected'].items():
            actual_value = getattr(session.prospect_data, field)
            if actual_value == expected_value:
                print(f"   ✅ {field}: '{actual_value}'")
            else:
                print(f"   ❌ {field}: expected '{expected_value}', got '{actual_value}'")
                case_passed = False
                all_passed = False
        
        if case_passed:
            print(f"   🎉 Test Case {i} PASSED")
        else:
            print(f"   ❌ Test Case {i} FAILED")
    
    return all_passed

if __name__ == "__main__":
    print("🚀 Starting Chat Service Parsing Logic Tests")
    print()
    
    # Test the main issue
    main_test_passed = test_parsing_logic()
    
    # Test additional cases
    additional_tests_passed = test_additional_cases()
    
    print("\n" + "=" * 50)
    print("📋 FINAL RESULTS:")
    
    if main_test_passed and additional_tests_passed:
        print("🎉 ALL TESTS PASSED! The parsing logic fix is working correctly.")
        sys.exit(0)
    else:
        print("❌ SOME TESTS FAILED! Please review the parsing logic.")
        sys.exit(1)
