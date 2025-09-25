from app.services.openai_service import openai_service
from app.models.enums import SupportedLanguage
from app.agents.language_agents.english_agent import run_agent as run_english_agent
from app.agents.language_agents.german_agent import run_agent as run_german_agent
from app.agents.language_agents.spanish_agent import run_agent as run_spanish_agent
from app.agents.specialized_agents.image_agent import run_agent as run_image_agent

async def run_manager(user_input: str, user_id: str, image_urls: list = []) -> str:
    if len(image_urls) > 0:
        return await run_image_agent(user_input, image_urls)
    
    lang = openai_service.detect_language(user_input)
    print(f"🌍 Detected language: {lang}")

    if lang == SupportedLanguage.GERMAN.value:
        return await run_german_agent(user_input)
    elif lang == SupportedLanguage.SPANISH.value:
        return await run_spanish_agent(user_input)
    else:  # Default to English for any other case
        return await run_english_agent(user_input)
