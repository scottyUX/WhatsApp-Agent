 # main.py

import asyncio
from agents import Runner
from agent.supervisor import supervisor_agent  # Make sure this is the Agent instance from supervisor.py

async def main():
    print("🤖 IstanbulMedic Agent is running...\n")
    
    # Initial input to the agent (could come from WhatsApp later)
    user_input = "Hi, I'm interested in cosmetic surgery in Istanbul."
    
    result = await Runner.run(supervisor_agent, user_input)

    print("\n✅ Final Output:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())
