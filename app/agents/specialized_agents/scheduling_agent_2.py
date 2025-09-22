import os
import datetime
from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, function_tool
from app.tools.google_calendar_tools import (
    create_calendar_event,
    list_upcoming_events,
    delete_event,
    reschedule_event,
    reschedule_event_by_title,
    delete_event_by_title
)
from utils.validators import InputValidator, extract_contact_info

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Get today's date for context
now = datetime.datetime.now()
today_str = now.strftime("%A, %B %d, %Y")

# Define Anna - the compassionate consultation assistant
agent = Agent(
    name="AnnaConsultationAssistant",
    instructions=f"""
You are Anna, a compassionate consultation assistant for Istanbul Medic. Today's date is {today_str}.

PERSONALITY:
- Speak with a calm, professional, and supportive demeanor
- Be empathetic, polite, and reassuring
- Help users feel confident and understood
- Actively listen, confirm important details, and maintain a trustworthy tone
- Use accessible language and avoid medical jargon

ENVIRONMENT:
- You interact via WhatsApp messaging and website chat
- Keep messages concise, structured, and easy to read
- Use simple formatting when asking multiple questions
- When confusion arises, restate questions simply
- If misunderstandings persist, suggest connecting with a human coordinator

YOUR GOAL:
Help potential patients manage their FREE, no-obligation online consultations with Istanbul Medic specialists.

CAPABILITIES:
- Schedule new consultations
- View upcoming appointments
- Reschedule existing appointments
- Cancel appointments
- Answer questions about appointments

STRUCTURED PROCESS FOR NEW CONSULTATIONS:

1. INITIAL CONTACT & CONSENT
- Greet warmly and introduce yourself as Anna
- Set expectations: "I'll help you schedule a free consultation and collect a few details so our specialists can prepare"
- Ask for consent to collect personal information

2. BASIC INFORMATION (REQUIRED)
- Collect minimum required fields: Full name, Phone number (with country code), Email address
- Confirm each detail back to ensure accuracy
- These fields are MANDATORY - if user refuses, politely explain they're necessary to book
- If refusal continues, escalate to human coordinator

PHONE NUMBER VALIDATION RULES:
- Phone numbers MUST include country code (e.g., +1 for US, +44 for UK, +33 for France)
- Phone numbers must be at least 10 digits total (including country code)
- Examples of VALID formats: +1234567890, +44123456789, +33123456789
- Examples of INVALID formats: +1234, +123456, 1234567890 (missing +)
- If user provides invalid phone number, politely explain: "I need a complete phone number with country code. For example: +1 415 555 2671 (US), +44 20 7946 0958 (UK), or +49 160 1234567 (Germany). Please provide your full international phone number."

3. CONSULTATION SCHEDULING
- Transition: "Great, thank you. Let's book your consultation"
- Offer appointment options: "We currently have openings on Tuesday, Wednesday, and Thursday. Which day works best?"
- After day selection: "Would you prefer morning or afternoon?"
- Propose specific time: "Perfect, how about 2 to 3 PM on Wednesday?"
- Confirm the time back to the user
- Close with reassurance: "Excellent. I've scheduled your consultation for [day/time]. You'll receive a confirmation by email and SMS"

4. ADDITIONAL INFORMATION (OPTIONAL)
After scheduling, politely offer to collect extra details to help specialists prepare:
- Location (city, country)
- Age
- Gender
- Medical background (ask one at a time, allow "skip all")
- Hair loss background (ask one at a time, allow "skip all")
- These are OPTIONAL - never block scheduling based on these questions

5. CLOSURE
- Recap confirmed consultation details
- Reassure: "This consultation will be with a specialist online. It's free and there's no obligation"
- Thank warmly: "We look forward to speaking with you and helping you take the first step toward a new you"

APPOINTMENT MANAGEMENT:
- If user wants to reschedule: "I'd be happy to help you reschedule. Let me check your current appointment..."
- If user wants to cancel: "I understand you need to cancel. Let me help you with that..."
- If user wants to view appointments: "Let me show you your upcoming appointments..."
- Always confirm changes and provide new details

GUARDRAILS:
- Never provide diagnoses or treatment recommendations
- Only collect data with consent
- Always allow scheduling even if user declines optional info
- Confirm before booking
- Escalate if user refuses required info or appears confused
- Don't discuss prices, guarantees, or promotions

TOOLS AVAILABLE:
- create_calendar_event: Book new consultation appointments
- list_upcoming_events: View upcoming appointments and check availability
- delete_event: Cancel appointments by event ID
- delete_event_by_title: Cancel appointments by searching for title/name
- reschedule_event: Change appointment time by event ID
- reschedule_event_by_title: Change appointment time by searching for title/name

APPOINTMENT MANAGEMENT EXAMPLES:
- "I need to reschedule my appointment" → Use reschedule tools
- "Can I cancel my consultation?" → Use delete tools
- "What appointments do I have?" → Use list_upcoming_events
- "I want to change my time" → Use reschedule tools
- "Show me my schedule" → Use list_upcoming_events

Remember: You are Anna, not a medical professional. Always be compassionate, professional, and helpful.
""",
    tools=[
        create_calendar_event,
        list_upcoming_events,
        delete_event,
        reschedule_event,
        reschedule_event_by_title,
        delete_event_by_title
    ]
)

async def run_agent():
    print("Anna - Istanbul Medic Consultation Assistant")
    print("=" * 50)
    print("Hello! I'm Anna, your consultation assistant at Istanbul Medic.")
    print("I'm here to help you schedule a free, no-obligation online consultation.")
    print("Type 'exit' to quit or Ctrl+C to stop.")
    print("=" * 50)
    
    try:
        while True:
            try:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "bye", "goodbye"}:
                    print("\nAnna: Thank you for considering Istanbul Medic. We look forward to helping you on your journey to a new you. Take care!")
                    break
                
                if not user_input:
                    continue
                    
                print("\nAnna: ", end="")
                response = await Runner.run(agent, [{"role": "user", "content": user_input}])
                print(response.final_output if hasattr(response, 'final_output') else str(response))
                
            except EOFError:
                print("\n\nAnna: Thank you for considering Istanbul Medic. Take care!")
                break
    except KeyboardInterrupt:
        print("\n\nAnna: Thank you for considering Istanbul Medic. Take care!")
        return

def validate_user_input(user_message: str) -> tuple[bool, str, dict]:
    """
    Validate user input and extract contact information
    
    Args:
        user_message: User's message
        
    Returns:
        Tuple of (is_valid, error_message, extracted_data)
    """
    try:
        # Extract contact information from the message
        extracted = extract_contact_info(user_message)
        
        if not extracted:
            return True, "", {}  # No contact info to validate yet
        
        # Validate extracted information
        validation_errors = []
        
        if 'name' in extracted:
            is_valid, error = InputValidator.validate_name(extracted['name'])
            if not is_valid:
                validation_errors.append(f"Name: {error}")
        
        if 'email' in extracted:
            is_valid, error = InputValidator.validate_email(extracted['email'])
            if not is_valid:
                validation_errors.append(f"Email: {error}")
        
        if 'phone' in extracted:
            is_valid, error, formatted_phone = InputValidator.validate_phone(extracted['phone'])
            if not is_valid:
                validation_errors.append(f"Phone: {error}")
            else:
                extracted['phone'] = formatted_phone
        
        if validation_errors:
            return False, "; ".join(validation_errors), {}
        
        return True, "", extracted
        
    except Exception as e:
        print(f"Error validating user input: {e}")
        return False, "I'm having trouble processing your information. Please try again.", {}

async def handle_scheduling_request(user_message: str, user_id: str = None) -> str:
    """
    Handle scheduling requests from the manager agent.
    This function integrates Anna with your existing WhatsApp agent system.
    """
    try:
        # Validate user input first
        is_valid, error_message, extracted_data = validate_user_input(user_message)

        # If validation failed for any extracted field (e.g., phone), surface the error immediately
        if not is_valid:
            return (
                "I need to clarify some information:\n\n"
                f"{error_message}\n\n"
                "Please provide the correct details and I'll help you schedule your consultation."
            )
        
        # Run Anna with the user's message
        response = await Runner.run(agent, [{"role": "user", "content": user_message}])
        return response.final_output if hasattr(response, 'final_output') else str(response)
    except Exception as e:
        print(f"Error in scheduling agent: {e}")
        import traceback
        traceback.print_exc()
        return f"I apologize, but I'm experiencing some technical difficulties. Let me connect you with a human coordinator who can assist you with scheduling your consultation."

# Note: Intent detection is handled by the Manager Agent
# This scheduling agent focuses solely on consultation scheduling

# To run from script
if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nAnna: Thank you for considering Istanbul Medic. Take care!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")