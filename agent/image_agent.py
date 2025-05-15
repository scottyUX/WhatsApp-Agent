from dotenv import load_dotenv
import os
import httpx
import base64
from openai import OpenAI
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



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

    except Exception as e:
        print(f"❌ Error in image agent: {e}")
        return "I apologize, but I'm having trouble analyzing the image. Please try sending the image again or describe your hair loss situation in text."

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