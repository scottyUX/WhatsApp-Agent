import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN") 
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")
    
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    VECTOR_STORE_EN: str = os.getenv("VECTOR_STORE_EN")
    VECTOR_STORE_DE: str = os.getenv("VECTOR_STORE_DE")
    VECTOR_STORE_ES: str = os.getenv("VECTOR_STORE_ES")
    
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    WEBHOOK_VERIFY_TOKEN: str = os.getenv("WEBHOOK_VERIFY_TOKEN")
    TEST_PHONE_NUMBERS: List[str] = os.getenv("TEST_PHONE_NUMBERS", "").split(",")
    
    def validate(self):
        required_vars = [
            "TWILIO_ACCOUNT_SID",
            "TWILIO_AUTH_TOKEN", 
            "OPENAI_API_KEY",
            "VECTOR_STORE_EN"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(self, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

settings = Settings()
