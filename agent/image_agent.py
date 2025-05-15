from dotenv import load_dotenv
import os
import httpx
import base64
from openai import OpenAI
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def download_image(image_url: str) -> str:
    """Download image from Twilio URL and convert to base64."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            response.raise_for_status()
            return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"❌ Error downloading image: {e}")
        raise

async def run_agent(user_input: str, image_url: str) -> str:
    print("🗣️ Image agent activated")
    try:
        # Download and encode the image
        base64_image = await download_image(image_url)
        
        # Create the API request
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "As a hair transplant doctor, analyze this image of a person's head and determine how many hair grafts would be needed for a hair transplant. Please provide a detailed assessment."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        return response.choices[0].message.content

    except Exception as e:
        print(f"❌ Error in image agent: {e}")
        return "I apologize, but I'm having trouble analyzing the image. Please try sending the image again or describe your hair loss situation in text."

if __name__ == "__main__":
    import asyncio
    # Test with a local image
    def encode_image_to_base64(image_path: str) -> str:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    
    image_path = os.path.join(os.path.dirname(__file__), "images", "photo1.png")
    base64_image = encode_image_to_base64(image_path)
    image_url = f"data:image/png;base64,{base64_image}"
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_agent("What is in this image?", image_url))
    print(result)