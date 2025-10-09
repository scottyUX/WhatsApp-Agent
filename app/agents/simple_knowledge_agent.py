"""
Simplified Knowledge Agent for Istanbul Medic
- Direct Q&A responses based on knowledge base
- No complex routing or scheduling
- Fast, reliable responses
"""

from agents import Agent, FileSearchTool
from app.config.settings import settings

# Create the simplified knowledge agent
simple_knowledge_agent = Agent(
    name="IstanbulMedicConsultant",
    instructions="""
You are Istanbul Medic's AI consultant for hair transplant procedures in Turkey.

EXPERTISE: Hair transplants (FUE, FUT, DHI), medical tourism, consultation booking.

RESPONSE STYLE: Professional, empathetic, concise. Always recommend professional consultation.

BOOKING: When users ask to book/schedule, provide this HTML button:
<a href="https://cal.com/scott-davis-nmxvsr/15min" target="_blank" style="display: inline-block; background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; margin: 10px 0;">📅 Book Free Consultation</a>

CONTACT: Only provide phone/email/WhatsApp when specifically asked.

Keep responses short and focused. Use knowledge base for accurate information.
""",
    model="gpt-4o",
    tools=[FileSearchTool(
        max_num_results=3,
        vector_store_ids=[settings.VECTOR_STORE_EN]
    )]
)

# Export the agent for use by the simple manager
knowledge_tool = simple_knowledge_agent.as_tool(
    tool_name="istanbul_medic_consultant",
    tool_description="Specialized medical tourism consultant for Istanbul Medic. Provides expert guidance on hair transplant procedures, medical tourism to Turkey/UK, pricing, packages, consultation process, and travel arrangements. Uses knowledge base to answer questions about services, procedures, safety, and next steps."
)

print(f"🟦 ISTANBUL MEDIC CONSULTANT: Created specialized agent '{simple_knowledge_agent.name}' with vector store integration")