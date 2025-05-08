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
# =============================
# 📂 agent/manager_agent.py
# =============================

import os
from dotenv import load_dotenv
load_dotenv()
from openai import OpenAI
from agent.english_agent import run_agent as run_english_agent
from agent.german_agent import run_agent as run_german_agent

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("client", client)

def detect_language(text: str) -> str:
    """Use OpenAI to detect the ISO 639-1 language code."""
    try:
        response = client.chat.completions.create(
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
        print(f"❌ Language detection failed: {e}")
        return "en"  # fallback

async def run_manager(user_input: str, user_id: str) -> str:
    print(f"📩 Message from {user_id}: {user_input}")

    lang = detect_language(user_input)
    print(f"🌍 Detected language: {lang}")

    if lang == "de":
        return await run_german_agent(user_input)
    else:
        return await run_english_agent(user_input)
