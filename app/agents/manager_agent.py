from agents import Agent, handoff, Runner
from agents.extensions import handoff_filters, handoff_prompt
from app.services.openai_service import openai_service
from app.agents.language_agents.english_agent import agent as english_agent
from app.agents.language_agents.german_agent import agent as german_agent
from app.agents.language_agents.spanish_agent import agent as spanish_agent
from app.agents.specialized_agents.image_agent import image_agent
from app.agents.specialized_agents.scheduling_agent_2 import agent as anna_agent
from app.services.conversation_state_service import conversation_state_service, ConversationAgent

# Create handoff callbacks - must take exactly one argument: context
async def on_handoff_to_anna(context):
    """Handle handoff to Anna (scheduling agent)."""
    user_id = context.get('user_id') if context else None
    if user_id:
        conversation_state_service.set_conversation_state(
            user_id, 
            ConversationAgent.ANNA_SCHEDULING,
            context=context
        )
        print(f"🔄 Handoff to Anna for user {user_id}")

async def on_handoff_to_english(context):
    """Handle handoff to English agent."""
    user_id = context.get('user_id') if context else None
    if user_id:
        conversation_state_service.set_conversation_state(
            user_id, 
            ConversationAgent.ENGLISH,
            context=context
        )
        print(f" Handoff to English agent for user {user_id}")

async def on_handoff_to_german(context):
    """Handle handoff to German agent."""
    user_id = context.get('user_id') if context else None
    if user_id:
        conversation_state_service.set_conversation_state(
            user_id, 
            ConversationAgent.GERMAN,
            context=context
        )
        print(f"🔄 Handoff to German agent for user {user_id}")

async def on_handoff_to_spanish(context):
    """Handle handoff to Spanish agent."""
    user_id = context.get('user_id') if context else None
    if user_id:
        conversation_state_service.set_conversation_state(
            user_id, 
            ConversationAgent.SPANISH,
            context=context
        )
        print(f" Handoff to Spanish agent for user {user_id}")

async def on_handoff_to_image(context):
    """Handle handoff to Image agent."""
    user_id = context.get('user_id') if context else None
    if user_id:
        conversation_state_service.set_conversation_state(
            user_id, 
            ConversationAgent.IMAGE,
            context=context
        )
        print(f"🔄 Handoff to Image agent for user {user_id}")

# Create the manager agent with proper handoffs
manager_agent = Agent(
    name="ManagerAgent",
    instructions=f"""{handoff_prompt.RECOMMENDED_PROMPT_PREFIX}
    
    You are the Manager Agent for Istanbul Medic's WhatsApp system.
    Your job is to intelligently route conversations to the appropriate specialized agent.
    
    ROUTING LOGIC:
    1. If user wants to schedule a consultation → transfer_to_consultation_agent
    2. If user has images → transfer_to_image_agent  
    3. If user speaks German → transfer_to_german_agent
    4. If user speaks Spanish → transfer_to_spanish_agent
    5. Otherwise → transfer_to_english_agent
    
    Always maintain conversation context when transferring.
    Use the handoff tools to delegate to specialized agents when appropriate.
    """,
    handoffs=[
        handoff(
            agent=anna_agent,
            on_handoff=on_handoff_to_anna,
            tool_name_override="transfer_to_consultation_agent",
            tool_description_override="Delegate to Anna for consultation scheduling and patient intake",
            input_filter=handoff_filters.remove_all_tools
        ),
        handoff(
            agent=english_agent,
            on_handoff=on_handoff_to_english,
            tool_name_override="transfer_to_english_agent",
            tool_description_override="Delegate to English language agent for general assistance",
            input_filter=handoff_filters.remove_all_tools
        ),
        handoff(
            agent=german_agent,
            on_handoff=on_handoff_to_german,
            tool_name_override="transfer_to_german_agent",
            tool_description_override="Delegate to German language agent for German speakers",
            input_filter=handoff_filters.remove_all_tools
        ),
        handoff(
            agent=spanish_agent,
            on_handoff=on_handoff_to_spanish,
            tool_name_override="transfer_to_spanish_agent",
            tool_description_override="Delegate to Spanish language agent for Spanish speakers",
            input_filter=handoff_filters.remove_all_tools
        ),
        handoff(
            agent=image_agent,
            on_handoff=on_handoff_to_image,
            tool_name_override="transfer_to_image_agent",
            tool_description_override="Delegate to Image agent for image analysis",
            input_filter=handoff_filters.remove_all_tools
        )
    ]
)

async def run_manager(user_input: str, user_id: str, image_urls: list = [], message_history: str = None) -> str:
    """Run the manager agent with handoff support."""
    print(f"Message from {user_id}: {user_input}")

    # Check if Anna is already handling this conversation
    if conversation_state_service.is_anna_handling_conversation(user_id):
        print("🔄 Anna is already handling this conversation - routing directly to Anna")
        conversation_state_service.update_conversation_activity(user_id)
        return await handle_scheduling_request(user_input, user_id, message_history)

    # Prepare context for handoffs
    context = {
        "user_id": user_id,
        "message_history": message_history,
        "image_urls": image_urls
    }

    # Run the manager agent with handoff support
    response = await Runner.run(
        manager_agent, 
        [{"role": "user", "content": user_input}],
        context=context
    )
    
    return response.final_output if hasattr(response, 'final_output') else str(response)

# Keep the old function for backward compatibility
async def handle_scheduling_request(user_message: str, user_id: str = None, message_history: str = None) -> str:
    """Handle scheduling requests from the manager agent."""
    # This function is now called by the handoff system
    from app.agents.specialized_agents.scheduling_agent_2 import handle_scheduling_request as anna_handle
    return await anna_handle(user_message, user_id, message_history)