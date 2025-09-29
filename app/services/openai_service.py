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
    
    async def get_completion(self, prompt: str) -> str:
        """Get completion from OpenAI for general prompts"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI completion failed: {e}")
            return "I'm sorry, I'm having trouble processing that request right now."

openai_service = OpenAIService()
