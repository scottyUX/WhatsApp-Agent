# =============================
# agent/english_agent.py
# =============================

from dotenv import load_dotenv
load_dotenv()
from agents import Agent, ModelSettings, FileSearchTool, Runner
import os

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_EN")

agent = Agent(
    name="EnglishAgent",
    instructions="""
        Answer questions related to IstanbulMedic in English using formal tone.
        Your answer must be maximum 1600 characters.
        """,
    model="gpt-4o",
    tools=[FileSearchTool(vector_store_ids=[VECTOR_STORE_ID])],
)

async def run_agent(user_input: str) -> str:
    print("🗣️ English agent activated")
    result = await Runner.run(agent, user_input)
    return result.final_output or "Sorry, I couldn't find an English answer."

