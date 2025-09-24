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
    
    # === LANGUAGE AGENTS CONFIGURATION ===
    # Model for text-based conversations (English, German, Spanish)
    LANGUAGE_AGENT_MODEL: str = os.getenv("LANGUAGE_AGENT_MODEL", "gpt-4o")
    LANGUAGE_AGENT_TEMPERATURE: float = float(os.getenv("LANGUAGE_AGENT_TEMPERATURE", "0.3"))
    LANGUAGE_AGENT_MAX_TOKENS: int = int(os.getenv("LANGUAGE_AGENT_MAX_TOKENS", "1000"))

    # === IMAGE AGENT CONFIGURATION ===
    # Model for image analysis and processing
    IMAGE_AGENT_MODEL: str = os.getenv("IMAGE_AGENT_MODEL", "gpt-4o")
    IMAGE_AGENT_TEMPERATURE: float = float(os.getenv("IMAGE_AGENT_TEMPERATURE", "0.1"))
    IMAGE_AGENT_MAX_TOKENS: int = int(os.getenv("IMAGE_AGENT_MAX_TOKENS", "500"))

    # === MANAGER AGENT CONFIGURATION ===
    # Model for routing and coordination
    MANAGER_AGENT_MODEL: str = os.getenv("MANAGER_AGENT_MODEL", "gpt-4o-mini")
    MANAGER_AGENT_TEMPERATURE: float = float(os.getenv("MANAGER_AGENT_TEMPERATURE", "0.2"))
    MANAGER_AGENT_MAX_TOKENS: int = int(os.getenv("MANAGER_AGENT_MAX_TOKENS", "300"))

    VECTOR_STORE_EN: str = os.getenv("VECTOR_STORE_EN")
    VECTOR_STORE_DE: str = os.getenv("VECTOR_STORE_DE")
    VECTOR_STORE_ES: str = os.getenv("VECTOR_STORE_ES")

    ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY")

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

        # === LANGUAGE AGENT VALIDATION ===
        if not (0.0 <= self.LANGUAGE_AGENT_TEMPERATURE <= 2.0):
            raise ValueError("LANGUAGE_AGENT_TEMPERATURE must be between 0.0 and 2.0")
        if self.LANGUAGE_AGENT_MAX_TOKENS <= 0:
            raise ValueError("LANGUAGE_AGENT_MAX_TOKENS must be positive")

        # === IMAGE AGENT VALIDATION ===
        if not (0.0 <= self.IMAGE_AGENT_TEMPERATURE <= 2.0):
            raise ValueError("IMAGE_AGENT_TEMPERATURE must be between 0.0 and 2.0")
        if self.IMAGE_AGENT_MAX_TOKENS <= 0:
            raise ValueError("IMAGE_AGENT_MAX_TOKENS must be positive")

        # === MANAGER AGENT VALIDATION ===
        if not (0.0 <= self.MANAGER_AGENT_TEMPERATURE <= 2.0):
            raise ValueError("MANAGER_AGENT_TEMPERATURE must be between 0.0 and 2.0")
        if self.MANAGER_AGENT_MAX_TOKENS <= 0:
            raise ValueError("MANAGER_AGENT_MAX_TOKENS must be positive")

settings = Settings()
