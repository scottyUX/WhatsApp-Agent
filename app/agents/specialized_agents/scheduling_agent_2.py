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
from .questionnaire_manager import create_questionnaire_manager
from .scheduling_models import ConversationState, PatientProfile, SchedulingStep

# Load environment variables
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize questionnaire manager
questionnaire_manager = create_questionnaire_manager()

# Global conversation state for questionnaire - keyed by user_id
conversation_states = {}

# Get today's date for context
now = datetime.datetime.now()
today_str = now.strftime("%A, %B %d, %Y")

# Questionnaire function tool for Anna
@function_tool
def manage_questionnaire(user_message: str, user_id: str = None) -> str:
    """
    Manage the patient intake questionnaire.
    Use this when you need to ask the structured questionnaire questions after scheduling an appointment.
    
    Args:
        user_message: The user's response to a questionnaire question
        user_id: Optional user ID for tracking
        
    Returns:
        The next question to ask or completion message
    """
    global conversation_states
    
    try:
        # Get or create conversation state for this user
        user_key = user_id or "temp_user"
        if user_key not in conversation_states:
            conversation_states[user_key] = ConversationState(
                user_id=user_key,
                phone_number="",  # Will be filled when we have patient info
                current_step=SchedulingStep.QUESTIONNAIRE,
                patient_profile=PatientProfile()
            )
        
        conversation_state = conversation_states[user_key]
        
        # Check if questionnaire has started
        if not conversation_state.questionnaire_started_at:
            # Start questionnaire
            start_message = questionnaire_manager.start_questionnaire(conversation_state)
            return start_message
        
        # Process user response
        print(f"🐛 Questionnaire Debug - User: {user_key}, Question ID: {conversation_state.current_question_id}, Message: {user_message}")
        success, response_message, next_action = questionnaire_manager.process_response(
            conversation_state.current_question_id,
            user_message,
            conversation_state,
            save_to_db=False
        )
        print(f"🐛 Questionnaire Debug - Success: {success}, Next Action: {next_action}, Response: {response_message}")
        
        if next_action == "complete":
            # Questionnaire complete
            return response_message
        elif next_action == "clarify":
            # Ask for clarification
            return response_message
        else:
            # Get next question
            next_question = questionnaire_manager.get_next_question(conversation_state)
            print(f"🐛 Questionnaire Debug - Next question: {next_question}")
            if next_question:
                return next_question["text"]
            else:
                return "Perfect! I've collected all the information. Our specialists will review this before your consultation."
                
    except Exception as e:
        print(f"Error in questionnaire management: {e}")
        return "I apologize, but I'm having trouble with the questionnaire. Let me continue with your consultation."

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

3. CONSULTATION SCHEDULING
- Transition: "Great, thank you. Let's book your consultation"
- Offer appointment options: "We currently have openings on Tuesday, Wednesday, and Thursday. Which day works best?"
- After day selection: "Would you prefer morning or afternoon?"
- Propose specific time: "Perfect, how about 2 to 3 PM on Wednesday?"
- Confirm the time back to the user
- Close with reassurance: "Excellent. I've scheduled your consultation for [day/time]. You'll receive a confirmation by email and SMS"

4. QUESTIONNAIRE (OPTIONAL)
After scheduling, politely offer to collect extra details to help specialists prepare:
- Say: "Great! To help our specialists prepare for your consultation, I'd like to ask you a few optional questions. You can skip any question you're not comfortable with. Let's start with some basic information."
- IMMEDIATELY call manage_questionnaire() to start the questionnaire
- For EVERY user response during questionnaire, call manage_questionnaire(user_response)

QUESTIONNAIRE RULES:
- ALWAYS use the manage_questionnaire tool for questionnaire questions
- Call manage_questionnaire() to start the questionnaire after scheduling
- For each user response during questionnaire, call manage_questionnaire(user_response)
- The tool will handle question flow, skip logic, and completion
- These are OPTIONAL - never block scheduling based on these questions

IMPORTANT: When user says "yes" to optional questions, IMMEDIATELY call manage_questionnaire() to start the questionnaire.

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
- manage_questionnaire: Manage the patient intake questionnaire (MANDATORY after scheduling when user agrees to questions)

CRITICAL: When user says "yes" to optional questions after scheduling, you MUST call manage_questionnaire() immediately.

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
        delete_event_by_title,
        manage_questionnaire
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
        
        if not is_valid and extracted_data:
            # Return validation error to user
            return f"I need to clarify some information:\n\n{error_message}\n\nPlease provide the correct details and I'll help you schedule your consultation."
        
        # Run Anna with the user's message
        print(f"🤖 Anna processing message: {user_message}")
        print(f"🤖 User ID: {user_id}")
        response = await Runner.run(agent, [{"role": "user", "content": user_message}])
        print(f"🤖 Anna response: {response.final_output if hasattr(response, 'final_output') else str(response)}")
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