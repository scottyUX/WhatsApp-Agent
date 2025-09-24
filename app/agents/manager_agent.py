from typing import AsyncGenerator

from app.services.openai_service import openai_service
from app.models.enums import SupportedLanguage
from app.agents.language_agents import (
    english_agent,
    german_agent,
    spanish_agent,
)
from app.agents.language_agents import run_agent, run_agent_streaming
from app.agents.specialized_agents.image_agent import run_image_agent, run_image_agent_streaming


def _langage_code_to_agent(lang_code: str):
    if lang_code == SupportedLanguage.GERMAN.value:
        return german_agent
    elif lang_code == SupportedLanguage.SPANISH.value:
        return spanish_agent
    else:  # Default to English for any other case
        return english_agent


async def run_manager(user_input: str, user_id: str, image_urls: list = []) -> str:
    if len(image_urls) > 0:
        return await run_image_agent(user_input, image_urls)
    
    lang = openai_service.detect_language(user_input)
    print(f"Detected language: {lang}")
    agent = _langage_code_to_agent(lang)
    return await run_agent(agent, user_input)


async def run_manager_streaming(user_input: str, user_id: str, image_urls: list = []) -> AsyncGenerator[str, None]:
    """Stream the manager response for real-time output"""
    if len(image_urls) > 0:
        async for chunk in run_image_agent_streaming(user_input, image_urls):
            yield chunk
        return

    lang = openai_service.detect_language(user_input)
    print(f"Detected language: {lang} (streaming)")
    agent = _langage_code_to_agent(lang)
    async for chunk in run_agent_streaming(agent, user_input):
        yield chunk
