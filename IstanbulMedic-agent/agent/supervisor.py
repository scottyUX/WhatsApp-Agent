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
        "You are an onboarding agent for IstanbulMedic. Your first task is to collect "
        "the user's first name, last name, and email address. Use the appropriate tool "
        "to gather this information from the user."
    ),
    model="gpt-4o-mini",
    tools=[FileSearchTool(
                max_num_results=3,
                vector_store_ids=["vs_68170479e5588191b21d1bfb32b532c4"],
                include_search_results=True,
            )],
)
