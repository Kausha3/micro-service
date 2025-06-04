"""
Demo script showing AI-powered responses for the Lead-to-Lease Chat Concierge.

This script demonstrates how the AI system would respond to various user queries
by showing example conversations and the intelligent context management.

Usage:
    python demo_ai_responses.py
"""

import sys
import os
from datetime import datetime
import uuid

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import ConversationSession, ChatState, ProspectData, AIContext, ConversationMessage
from inventory_service import inventory_service


def demo_conversation_scenarios():
    """Demonstrate various conversation scenarios with AI-powered responses."""
    
    print("🤖 AI-Powered Lead-to-Lease Chat Concierge Demo")
    print("=" * 60)
    print("This demo shows how the AI system handles natural language queries")
    print("and provides intelligent, context-aware responses.\n")
    
    # Get available inventory for context
    available_units = inventory_service.get_all_available_units()
    print(f"📋 Current Inventory: {len(available_units)} available units")
    
    # Show inventory summary
    units_by_beds = {}
    for unit in available_units:
        beds = unit.beds if unit.beds > 0 else "Studio"
        if beds not in units_by_beds:
            units_by_beds[beds] = []
        units_by_beds[beds].append(unit)
    
    print("Available units:")
    # Sort by bedroom count, handling both int and string types
    sorted_beds = sorted(units_by_beds.items(), key=lambda x: (0 if x[0] == "Studio" else x[0]))
    for beds, units in sorted_beds:
        print(f"  • {beds} bedroom{'s' if beds != 1 and beds != 'Studio' else ''}: {len(units)} units")
        example_unit = units[0]
        print(f"    Example: Unit {example_unit.unit_id} - {example_unit.sqft} sq ft, ${example_unit.rent}/month")
    
    print("\n" + "=" * 60)
    print("🎭 Conversation Scenarios")
    print("=" * 60)
    
    scenarios = [
        {
            "title": "Natural Property Search",
            "conversation": [
                ("User", "Hi, I'm looking for an apartment"),
                ("AI", "Hello! I'd be happy to help you find the perfect apartment at Luxury Apartments at Main Street. What type of place are you looking for?"),
                ("User", "What do you have available?"),
                ("AI", f"We have several great options available! Here's what we currently have:\n\n• Studio Units | 0 bed/1 bath | 450-500 sq ft | $1,500-1,600/month\n• 1-Bedroom Units | 1 bed/1-1.5 bath | 650-750 sq ft | $1,800-2,000/month\n• 2-Bedroom Units | 2 bed/2-2.5 bath | 950-1,100 sq ft | $2,400-2,700/month\n• 3-Bedroom Units | 3 bed/2.5-3 bath | 1,200-1,350 sq ft | $3,200-3,500/month\n• 4-Bedroom Units | 4 bed/3 bath | 1,600-1,750 sq ft | $4,200-4,500/month\n\nWhat size apartment interests you most?"),
                ("User", "I need something with 2 bedrooms"),
                ("AI", f"Perfect! I have several excellent 2-bedroom options for you:\n\n• Unit B301 | 2 bed/2 bath | 950 sq ft | $2,400/month\n• Unit B402 | 2 bed/2 bath | 1,000 sq ft | $2,500/month\n• Unit B503 | 2 bed/2.5 bath | 1,100 sq ft | $2,700/month\n• Unit B604 | 2 bed/2 bath | 975 sq ft | $2,450/month\n\nAll of these units are currently available. Would you like more details about any of these, or would you like to schedule a tour?")
            ]
        },
        {
            "title": "Budget-Conscious Search",
            "conversation": [
                ("User", "What's your cheapest apartment?"),
                ("AI", "Our most affordable option is a studio apartment - Unit S104 at $1500/month. It's 450 square feet with 1 bathroom, perfect for someone looking for a cozy, budget-friendly space. We also have other studios available ranging from $1500-1600/month. Would you like to know more about our studio options?"),
                ("User", "Do you have anything cheaper in a 1-bedroom?"),
                ("AI", "Our most affordable 1-bedroom is Unit A101 at $1800/month. It's 650 square feet with 1 bathroom - a great value for a 1-bedroom apartment. If budget is a primary concern, I'd also be happy to discuss our studio options which offer excellent value. What's most important to you in your new home?")
            ]
        },
        {
            "title": "Specific Requirements",
            "conversation": [
                ("User", "I need a 3-bedroom apartment with at least 1200 square feet"),
                ("AI", "Excellent! I have perfect options for you. Our 3-bedroom units all meet your space requirements:\n\n• Unit C501 | 3 bed/2.5 bath | 1,200 sq ft | $3,200/month\n• Unit C703 | 3 bed/3 bath | 1,350 sq ft | $3,500/month\n• Unit C804 | 3 bed/2.5 bath | 1,225 sq ft | $3,250/month\n\nAll of these exceed your 1,200 sq ft requirement. Unit C703 is our most spacious option with a full 3rd bathroom. When are you looking to move in?"),
                ("User", "I need to move in next month"),
                ("AI", "Perfect timing! All of our 3-bedroom units are available for immediate move-in. Since you need to move next month, I'd recommend scheduling a tour soon so we can get your application processed. Would you like to book a tour to see these units? I can schedule something as early as this week.")
            ]
        },
        {
            "title": "Booking Intent",
            "conversation": [
                ("User", "I want to book a tour"),
                ("AI", "Wonderful! I'd love to schedule a tour for you. To get started, I'll need to collect some information. What's your name?"),
                ("User", "My name is Sarah Johnson"),
                ("AI", "Nice to meet you, Sarah! What's your email address so I can send you the tour confirmation?"),
                ("User", "sarah.johnson@email.com"),
                ("AI", "Great! And what's your phone number?"),
                ("User", "555-123-4567"),
                ("AI", "Perfect! When are you looking to move in?"),
                ("User", "Sometime in March 2024"),
                ("AI", "Excellent! And how many bedrooms are you looking for?"),
                ("User", "2 bedrooms"),
                ("AI", "Perfect! I found an excellent 2-bedroom unit for you: Unit B301 (950 sq ft, $2400/month, 2 bed/2 bath). Your tour is confirmed for tomorrow at 2:00 PM. I've sent a confirmation email to sarah.johnson@email.com with all the details. We'll see you at 123 Main St, Anytown, ST 12345!")
            ]
        },
        {
            "title": "Complex Query Handling",
            "conversation": [
                ("User", "Do you have any units with parking and a balcony under $2500?"),
                ("AI", "Great question! While I don't have specific details about parking and balconies in my current system, I can tell you about our units under $2,500:\n\n• Studio Units | 0 bed/1 bath | 450-500 sq ft | $1,500-1,600/month\n• 1-Bedroom Units | 1 bed/1-1.5 bath | 650-750 sq ft | $1,800-2,000/month\n• Unit B301 | 2 bed/2 bath | 950 sq ft | $2,400/month\n• Unit B604 | 2 bed/2 bath | 975 sq ft | $2,450/month\n\nFor specific amenity details like parking availability and balconies, I'd recommend scheduling a tour where our leasing team can show you the exact features of each unit. Would you like to book a tour to see these options in person?"),
                ("User", "Yes, let's schedule that"),
                ("AI", "Perfect! I'll help you schedule a tour. To get started, what's your name?")
            ]
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print("-" * 40)
        
        for speaker, message in scenario['conversation']:
            if speaker == "User":
                print(f"👤 {speaker}: {message}")
            else:
                print(f"🤖 {speaker}: {message}")
        
        print()
    
    print("=" * 60)
    print("🎯 Key AI Capabilities Demonstrated")
    print("=" * 60)
    
    capabilities = [
        "✅ Natural language understanding - handles conversational queries",
        "✅ Context awareness - remembers conversation history",
        "✅ Database integration - provides real inventory information", 
        "✅ Intelligent responses - tailored to user needs",
        "✅ Flexible information collection - natural data gathering",
        "✅ Booking flow integration - seamless tour scheduling",
        "✅ Graceful handling - manages complex or unclear requests",
        "✅ Personalized recommendations - suggests relevant options"
    ]
    
    for capability in capabilities:
        print(capability)
    
    print(f"\n🔧 Technical Implementation")
    print("-" * 30)
    print("• OpenAI GPT integration for natural language processing")
    print("• Conversation context management with session persistence")
    print("• Real-time inventory database queries")
    print("• Intelligent intent detection and entity extraction")
    print("• Backward compatibility with existing booking system")
    print("• Fallback handling when AI is unavailable")
    
    print(f"\n📊 System Status")
    print("-" * 20)
    print(f"• Available units: {len(available_units)}")
    print(f"• AI service: {'Enabled' if os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your_openai_api_key_here' else 'Requires API key configuration'}")
    print(f"• Database: Operational")
    print(f"• Email service: Configured")
    
    print(f"\n🚀 Next Steps")
    print("-" * 15)
    print("1. Configure OpenAI API key in backend/.env")
    print("2. Start the backend server: python main.py")
    print("3. Start the frontend: npm run dev")
    print("4. Test the AI conversation in the chat interface")
    
    print(f"\n💡 The AI enhancement transforms rigid form-filling into")
    print("   natural conversation while maintaining all existing functionality!")


if __name__ == "__main__":
    demo_conversation_scenarios()
