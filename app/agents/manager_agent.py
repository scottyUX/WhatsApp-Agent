from app.services.openai_service import openai_service
from app.agents.language_agents.english_agent import run_agent as run_english_agent
from app.agents.language_agents.german_agent import run_agent as run_german_agent
from app.agents.language_agents.spanish_agent import run_agent as run_spanish_agent
from app.agents.specialized_agents.image_agent import run_agent as run_image_agent
from app.agents.specialized_agents.scheduling_agent_2 import handle_scheduling_request

async def detect_scheduling_intent(message: str) -> bool:
    """
    Use AI to intelligently detect if the user wants to schedule a consultation.
    Returns True if scheduling intent is detected.
    """
    intent_prompt = f"""
    Analyze the following user message and determine if they want to schedule a consultation or appointment.
    
    User message: "{message}"
    
    Look for:
    - Requests to schedule, book, or arrange a consultation
    - Interest in speaking with a specialist or doctor
    - Questions about availability or appointment times
    - Expressions of wanting to meet or talk with medical professionals
    
    Respond with only "YES" if they want to schedule a consultation, or "NO" if they don't.
    Be conservative - only respond "YES" if it's clearly about scheduling a consultation.
    """
    
    try:
        response = await openai_service.get_completion(intent_prompt)
        print(f"🔍 OpenAI intent detection response: {response}")
        result = response.strip().upper() == "YES"
        print(f"🔍 Intent detection result: {result}")
        return result
    except Exception as e:
        print(f"Error detecting scheduling intent: {e}")
        # Fallback to keyword-based detection
        scheduling_keywords = ["schedule", "book", "appointment", "consultation", "meeting", "available", "time", "date"]
        fallback_result = any(keyword in message.lower() for keyword in scheduling_keywords)
        print(f"🔍 Fallback keyword detection result: {fallback_result}")
        return fallback_result

async def run_manager(user_input: str, user_id: str, image_urls: list = [], message_history: str = None) -> str:
    print(f"Message from {user_id}: {user_input}")

    # Handle images first
    if len(image_urls) > 0:
        return await run_image_agent(user_input, image_urls)
    
    # Check for scheduling intent using AI
    scheduling_intent = await detect_scheduling_intent(user_input)
    print(f"🔍 Scheduling intent detection result: {scheduling_intent}")
    if scheduling_intent:
        print("Scheduling intent detected - routing to Anna")
        return await handle_scheduling_request(user_input, user_id, message_history)
    
    # Detect language and route to appropriate language agent
    lang = openai_service.detect_language(user_input)
    print(f"Detected language: {lang}")

    if lang == "de":
        return await run_german_agent(user_input, message_history)
    elif lang == "es":
        return await run_spanish_agent(user_input, message_history)
    else:
        return await run_english_agent(user_input, message_history)
