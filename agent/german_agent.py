# =============================
# 📂 agent/german_agent.py
# =============================

from dotenv import load_dotenv
load_dotenv()
from agents import Agent, ModelSettings, FileSearchTool, Runner
import os

VECTOR_STORE_ID = os.getenv("VECTOR_STORE_DE")

agent = Agent(
    name="GermanAgent",
    instructions="""
        Beantworte Fragen über IstanbulMedic auf formellem Deutsch.
        Deine Antwort muss maximal 1600 Zeichen lang sein.
        """,
    model="gpt-4o",
    tools=[FileSearchTool(vector_store_ids=[VECTOR_STORE_ID])],
)

async def run_agent(user_input: str) -> str:
    print("🗣️ German agent activated")
    result = await Runner.run(agent, user_input)
    return result.final_output or "Entschuldigung, ich konnte keine Antwort finden."
