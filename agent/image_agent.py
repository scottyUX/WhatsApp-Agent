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
    Your answer must be maximum 1600 characters.
    """,
    model="gpt-4o",
)

async def run_agent(user_input: str,image_urls: list) -> str:
    print("🗣️ Image agent activated")
    content = [{ "type":"input_text", "text": user_input}]
    content += [{"type":"input_image","image_url": url} for url in image_urls]
    result = await Runner.run(image_agent,
        input=[
            {
                "role":"user",
                "content": content
            }
        ]
    )
    return result.final_output or "Sorry, I couldn't find an answer."


#To test this agent with a local image
def encode_image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")
    
if __name__ == "__main__":
    image_path1 = os.path.join(os.path.dirname(__file__), "images", "photo1.png")
    image_path2 = os.path.join(os.path.dirname(__file__), "images", "photo2.png")
    
    base64_image1 = encode_image_to_base64(image_path1)
    base64_image2 = encode_image_to_base64(image_path2)
    image_urls = [f"data:image/png;base64,{base64_image1}", f"data:image/png;base64,{base64_image2}"]
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_agent("What is in this image?",image_urls))
    with open("result.txt", "w") as f:
        f.write(result)
    print(result)