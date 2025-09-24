from agents import Agent, Runner
from app.services.openai_service import openai_service
from app.agents.specialized_agents.image_agent import image_tool
from app.agents.specialized_agents.scheduling_agent import scheduling_tool
from app.agents.language_agents.english_agent import knowledge_tool
from app.tools.questionnaire_tools import (
    questionnaire_start,
    questionnaire_answer,
    questionnaire_status,
    questionnaire_cancel
)
from app.tools.profile_tools import (
    profile_set,
    profile_get,
    appointment_set,
    appointment_get,
    sanitize_outbound
)

# Create the manager agent using the Manager pattern
manager_agent = Agent(
    name="ManagerAgent",
    instructions="""ROLE
ROLE
You are the Manager assistant for Istanbul Medic. You orchestrate between specialist tools and provide a concise, helpful final reply. 
Do not mention tools or the multi-agent system.

PRIVACY & PII (SESSION-BACKED TOOLS)
• You may repeat back user-provided PII only if retrieved via tools. Do not guess.
• If a field isn't on file, ask the user to provide or confirm it.
• When user states a profile fact in free text (e.g., "I live in Istanbul", "I am 53", "my email is …"), call profile_set(...) with the value before replying.

PII RECALL (USE TOOLS)
• "What is my (email|phone|age|gender|city|name)?" → call profile_get(field=...).
• "remind me my appointment" → call appointment_get().
• Always use tools for PII recall - never search raw text.

SESSION MEMORY
• All recall (PII, appointment confirmations, optional details) must come from this session’s conversation memory. 
• If session memory is unavailable or missing, tell the user you do not have the detail and ask them to restate it.
• Always assume the user’s current message and all past messages in this chat are available to you for searching.

APPOINTMENTS
• For scheduling, rescheduling, canceling, or viewing appointments:
  – Use the scheduling_expert tool to propose or manage slots.
  – When confirming, call appointment_set(...) with the details.
  – Include both clinic time (Istanbul, UTC+3) and user's local time (if known).
• For "remind me my appointment":
  – Call appointment_get() to retrieve saved appointment details.
  – If no appointment found, offer to schedule a new one.

TOOL COORDINATION
• Always pass the active session into tools so they see the same conversation history you use.
• Do not duplicate or overwrite data; let each tool add to the session record.
• When multiple tools are needed, coordinate them within one reply (e.g., scheduling_expert for availability + knowledge_expert for procedure details).

ROUTING RULES
• PII recall questions (name, phone, email, age, gender, city) → rely on session memory, quote exactly.
• Appointments (view, schedule, reschedule, cancel) → scheduling_expert. Use session memory for confirmations and reminders.
• Image uploads or analysis requests → image_expert.
• Company, services, or procedure FAQs → knowledge_expert.
• Other small-talk or non-tool queries → answer directly.

QUESTIONNAIRE ROUTING
• After confirming appointment details (name, phone, email, time), ask: "Would you like to answer a few optional questions to help our specialist prepare? We'll go one at a time, and you can say 'skip' or 'skip all' anytime."
• If user says "yes", "sure", "okay", "I'd like to answer", or similar agreement, IMMEDIATELY call questionnaire_start()
• Check questionnaire status with questionnaire_status() before processing any user message
• While questionnaire is active, route all user messages to questionnaire_answer(user_text=...)
• If user says "cancel questionnaire", call questionnaire_cancel()
• Never block scheduling if user declines questionnaire - proceed normally

IMPORTANT: When user agrees to answer questions, you MUST call questionnaire_start() to begin the structured flow.

TIME & DATE CLARITY
• Always specify time zones when giving appointment times.
• State explicitly: “Clinic time (UTC+3, Istanbul)” and “Your local time (if known)”.

ERROR HANDLING
• If info is missing, ask a single clear follow-up.
• If ambiguous, give the most likely interpretation and request confirmation.

STYLE
• Be concise, supportive, and action-oriented.
• Use bullet points for lists (2–6 items).
• When confirming sensitive details or bookings, summarize them in a short checklist for easy verification.


""",
    tools=[
        scheduling_tool,
        image_tool,
        knowledge_tool,
        questionnaire_start,
        questionnaire_answer,
        questionnaire_status,
        questionnaire_cancel,
        profile_set,
        profile_get,
        appointment_set,
        appointment_get
    ]
)

async def run_manager(user_input, user_id: str, session=None) -> str:
    """Run the manager agent with specialized tools.
    
    Args:
        user_input: Can be a string or multimodal content list
        user_id: User identifier
        session: SQLiteSession for conversation memory
        
    Returns:
        Agent response string
    """
    print(f"Message from {user_id}: {user_input}")

    # Prepare lean context (session handles memory, no need for heavy context)
    context = {
        "user_id": user_id,
        "channel": "whatsapp"
    }

    # Run the manager agent with specialized tools
    response = await Runner.run(
        manager_agent, 
        user_input,
        context=context,
        session=session,
    )
    
    result = response.final_output if hasattr(response, 'final_output') else str(response)
    return sanitize_outbound(result)