from agents import Agent, Runner
import base64
import os

image_agent = Agent(
    name="ImageExplainAgent",
    instructions="""Assume that you are a hair transplant doctor.
    There is an image which shows the top of a person's head.
    Your task is to decide how many hair grafts are needed for a hair transplant.
    """,
    model="gpt-4o",
)

# Export the agent and its tool for use by the manager
image_tool = image_agent.as_tool(
    tool_name="image_expert",
    tool_description="Analyzes and processes images sent by users for hair transplant assessment."
)

# Note: This agent now runs as a tool within the manager's session context
# No standalone run_agent() function needed - session memory is handled automatically

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
