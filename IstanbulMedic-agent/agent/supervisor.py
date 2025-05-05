# agent/supervisor_agent.py
from agents import Agent, Runner, FileSearchTool
from dotenv import load_dotenv
import os

from tools.collect_user_info import collect_user_info

# Load environment variables from .env file
load_dotenv()



# Now you can access the OPENAI_API_KEY
openai_api_key = os.getenv("OPENAI_API_KEY")

# Ensure the key is set
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

supervisor_agent = Agent(
    name="IstanbulMedic Supervisor",
    instructions=(
        "You are a helpful and knowledgeable assistant for Longevita, a UK-registered medical tourism provider offering cosmetic treatments in Turkey and the UK.\n"
        "\n"
        "Answer the user's questions using only the provided context. Be concise, professional, and empathetic. If the user's query involves a specific treatment (e.g., hair transplant, dental veneers, tummy tuck), provide a brief overview, mention the option for free consultation, and suggest how to proceed (e.g., sharing photos, booking assessment).\n"
        "\n"
        "If the user asks about:\n"
        "- Pricing: Mention that pricing is transparent and quotes are customized after consultation. Emphasize affordability.\n"
        "- Procedures: Provide brief details of the requested procedure (if available in context).\n"
        "- Location: Mention Longevita operates in Istanbul and London.\n"
        "- Safety/Trust: Emphasize UK registration, accredited hospitals, and experienced surgeons.\n"
        "- Steps to Book: Highlight these: (1) Free consultation → (2) Treatment plan → (3) Deposit payment → (4) Travel & procedure.\n"
        "\n"
        "If you don't know the answer or it's not in the context, say: \"I'm not sure about that. Would you like me to connect you with a consultant?\""
    ),
    model="gpt-4o-mini",
    tools=[FileSearchTool(
                max_num_results=3,
                vector_store_ids=["vs_68170479e5588191b21d1bfb32b532c4"],
                include_search_results=True,
            )],
)
