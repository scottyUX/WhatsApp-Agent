"""
─────────────────────────────────────────────────────────────────────
🤖 Manager Agent – IstanbulMedic Multilingual Coordinator
─────────────────────────────────────────────────────────────────────
This module defines a central agent that:
- Detects the language of incoming WhatsApp messages using OpenAI's GPT-4o.
- Selects the appropriate vector store (currently supports English and German).
- Falls back to the English vector store for unsupported languages.
- Uses the OpenAI Responses API to query assistant knowledge from vector stores.

It supports short-term in-memory caching to avoid redundant language detection.

Usage:
    response = await run_manager(user_input, user_id)

Environment Variables:
    OPENAI_API_KEY
    VECTOR_STORE_EN
    VECTOR_STORE_DE

Author: Scott Davis
─────────────────────────────────────────────────────────────────────
"""


from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Cache to remember language per WhatsApp user session
lang_cache = {}

# Currently supported languages
SUPPORTED_LANGUAGES = {"en", "de"}

# Vector stores for available languages
VECTOR_STORES = {
    "en": "vs_6819bbcefe4c8191b4b045c0f872a4ec",
    "de": "vs_6819bb2e31b88191875a35d19b87eb62",
}

def detect_language_with_model(text: str) -> str:
    """Use OpenAI to detect ISO 639-1 language code (e.g., 'en', 'de')."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "You are a language detection expert. Respond ONLY with the ISO 639-1 code (e.g., en, de) of the input language."
            },
            {"role": "user", "content": text}
        ],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()

def get_user_language(text: str, user_id: str) -> str:
    """Detect or fetch cached user language."""
    if user_id in lang_cache:
        return lang_cache[user_id]
    lang = detect_language_with_model(text)
    lang_cache[user_id] = lang
    return lang

async def run_manager(user_input: str, user_id: str) -> str:
    lang = get_user_language(user_input, user_id)
    print(f"🌍 Detected language: {lang}")

    # Fallback to English vector store if language is unsupported
    vector_store_id = VECTOR_STORES.get(lang, VECTOR_STORES["en"])
    print(f"📂 Using vector store: {vector_store_id}")

    response = client.responses.create(
        model="gpt-4o",
        input=user_input,
        tools=[{
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }]
    )
    print(response)
# ✅ Extract assistant message text from response object
    for item in response.output:
        if hasattr(item, "content") and isinstance(item.content, list):
            for content_block in item.content:
                if hasattr(content_block, "text"):
                    return content_block.text

# ❌ If nothing valid is found
    return "Üzgünüz, bir yanıt alınamadı."  # Optional fallback in Turkish
