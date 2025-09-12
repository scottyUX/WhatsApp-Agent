from openai import OpenAI
from app.config.settings import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def detect_language(self, text: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": f"What is the ISO 639-1 language code for this text?\n{text}"
                    }
                ],
                max_tokens=2
            )
            return response.choices[0].message.content.strip().lower()
        except Exception as e:
            print(f"Language detection failed: {e}")
            return "en"

openai_service = OpenAIService()
