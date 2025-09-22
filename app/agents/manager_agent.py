from agents import Agent, Runner
from app.services.openai_service import openai_service
from app.agents.specialized_agents.image_agent import image_agent
from app.agents.specialized_agents.scheduling_agent import agent as scheduling_agent
from app.agents.language_agents.english_agent import agent as knowledge_agent

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
        scheduling_agent.as_tool(
            tool_name="scheduling_expert",
            tool_description="Handles consultation scheduling, appointments, and patient intake questions."
        ),
        image_agent.as_tool(
            tool_name="image_expert", 
            tool_description="Analyzes and processes images sent by users for hair transplant assessment."
        ),
        knowledge_agent.as_tool(
            tool_name="knowledge_expert",
            tool_description="Answers general questions about Istanbul Medic services, procedures, and information."
        )
    ]
)

async def run_manager(user_input: str, user_id: str, image_urls: list = [], message_history: str = None, session=None) -> str:
    """Run the manager agent with specialized tools.
    If provided, `session` should be an Agents SDK Session (e.g., OpenAIConversationsSession)
    to maintain conversation memory across turns.
    """
    print(f"Message from {user_id}: {user_input}")

    # Prepare context for the manager
    context = {
        "user_id": user_id,
        "message_history": message_history,
        "image_urls": image_urls
    }

    # Run the manager agent with specialized tools
    response = await Runner.run(
        manager_agent, 
        [{"role": "user", "content": user_input}],
        context=context,
        session=session,
    )
    
    return response.final_output if hasattr(response, 'final_output') else str(response)