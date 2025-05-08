import os
import base64
import imghdr
from openai import OpenAI

def analyze_image_with_gpt4o(prompt: str, image_path: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_type = imghdr.what(None, image_bytes)
    if image_type not in ["jpeg", "png", "gif", "webp"]:
        raise ValueError(f"Unsupported image format: {image_type}")

    mime_type = f"image/{'jpeg' if image_type == 'jpg' else image_type}"
    base64_image = base64.b64encode(image_bytes).decode("utf-8")
    image_data_url = f"data:{mime_type};base64,{base64_image}"

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_data_url}},
            ]}
        ],
        max_tokens=500,
    )

    return response.choices[0].message.content

# Example usage
if __name__ == "__main__":
    prompt = "What is in this image?"
    image_path = "telegram.png"  # Replace with your image path
    try:
        result = analyze_image_with_gpt4o(prompt, image_path)
        print("✅ GPT-4o Result:", result)
    except Exception as e:
        print("❌ Error:", e)

