from dotenv import load_dotenv
from agents import Agent, Runner
import os
import base64
import asyncio
load_dotenv()

image_agent = Agent(
    name="ImageExplainAgent",
    instructions="""Assume that you are a hair transplant doctor.
    There is an image which shows the top of a person's head.
    Your task is to decide how many hair grafts are needed for a hair transplant.
    """,
    model="gpt-4.1",
)

async def run_agent(user_input: str,image_url: str) -> str:
    print("🗣️ Image agent activated")
    result = await Runner.run(image_agent,
        input=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"input_text", 
                        "text": user_input
                    },
                    {
                        "type":"input_image",
                        "image_url": image_url
                    }
                ]
            }
        ]
    )
    return result.final_output or "Sorry, I couldn't find an answer."


#To test this agent with a local image
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
if __name__ == "__main__":
    image_path = os.path.join(os.path.dirname(__file__), "images", "photo1.png")
    base64_image = encode_image_to_base64(image_path)
    image_url = f"data:image/png;base64,{base64_image}"
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_agent("What is in this image?",image_url))
    print(result)