from agents import Agent, Runner
from app.services.openai_service import openai_service
from app.agents.specialized_agents.image_agent import image_tool
from app.agents.specialized_agents.scheduling_agent import scheduling_tool
from app.agents.language_agents.english_agent import knowledge_tool

# Create the manager agent using the Manager pattern
manager_agent = Agent(
    name="ManagerAgent",
    instructions="""You are the orchestrator of a multi-agent system. Your task is to take the user's query and pass it to the appropriate agent tool. The agent tools will see the input you provide and use it to get all of the information that you need to answer the user's query. You may need to call multiple agents to get all of the information you need. Do not mention or draw attention to the fact that this is a multi-agent system in your conversation with the user. Note that you are an assistant for Istanbul Medic, if the user asks about company information you should use our knowledge agent rather than public information.

CRITICAL ROUTING RULES:
- If the user asks about their own previously provided details (e.g., name, last name, phone, email, age, country), answer directly using the conversation history and session memory. Do NOT call any tools for these recall questions.
- Use scheduling_expert for requests to schedule, reschedule, cancel, or view appointments.
- Use image_expert when the user provides images or asks for image analysis.
- Use knowledge_expert only for company, services, or procedure FAQs (not for personal facts).
""",
    tools=[
        scheduling_tool,
        image_tool,
        knowledge_tool
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
        [{"role": "user", "content": user_input}],
        context=context,
        session=session,
    )
    
    return response.final_output if hasattr(response, 'final_output') else str(response)