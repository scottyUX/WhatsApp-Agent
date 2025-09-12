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

async def run_agent(user_input: str, image_urls: list) -> str:
    print("🗣️ Image agent activated")
    content = [{"type": "input_text", "text": user_input}]
    content += [{"type": "input_image", "image_url": url} for url in image_urls]
    result = await Runner.run(image_agent,
        input=[
            {
                "role": "user",
                "content": content
            }
        ]
    )
    return result.final_output or "Sorry, I couldn't find an answer."

def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
