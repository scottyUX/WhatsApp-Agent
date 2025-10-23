import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PORT: int = int(os.getenv("PORT", 8000))
    
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN") 
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "whatsapp:+14155238886")
    
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    
    # Vector Store IDs (OpenAI Vector Store)
    VECTOR_STORE_EN: str = "vs_68e499ece62c81918ec6d98221c1722a"  # Istanbul Medic specific knowledge base
    VECTOR_STORE_DE: str = os.getenv("VECTOR_STORE_DE")
    VECTOR_STORE_ES: str = os.getenv("VECTOR_STORE_ES")
    
    # Legacy vector store ID (kept for reference)
    SIMPLIFIED_VECTOR_STORE_ID: str = "vs_68e42f2ab970819194ba16b0e0699bcb"
    
    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")
    
    # Google Calendar
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "primary")
    
    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    SUPABASE_IMAGE_BUCKET: str = os.getenv(
        "SUPABASE_IMAGE_BUCKET", "istanbulmedic_patient_images"
    )
    
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    WEBHOOK_VERIFY_TOKEN: str = os.getenv("WEBHOOK_VERIFY_TOKEN")
    TEST_PHONE_NUMBERS: List[str] = [num.strip() for num in os.getenv("TEST_PHONE_NUMBERS", "").split(",") if num.strip()]
    
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
