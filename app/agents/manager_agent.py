"""
Manager Router with Sticky Routes (session lock):
- Determine intent (scheduling / image / knowledge / fallback) on first message.
- Once locked to an agent, keep routing to that agent until flow completes.
- Never generate user-facing text.

Integration notes:
- message_service.py should call: await run_manager(user_input, context, session)
- context is expected to include { "user_id": "...", "channel": "whatsapp" } (or similar)
"""

from __future__ import annotations
import re
import time
import logging
from typing import Any, Dict, Optional, Tuple, AsyncGenerator

# Import your SDK runner and specialized agents.
from agents import Runner

# Required agents (adjust to your module paths/names)
from app.agents.specialized_agents.scheduling_agent import agent as scheduling_agent
from app.agents.specialized_agents.image_agent import image_agent

# Optional: if you have a knowledge/general agent; otherwise we route to scheduling by default or raise.
try:
    from app.agents.language_agents.english_agent import agent as knowledge_agent
except Exception:
    knowledge_agent = None

# Note: Session management is now handled by the agents framework
# through the session parameter passed to Runner.run()

log = logging.getLogger("manager_router")
log.setLevel(logging.INFO)

# ---------- Intent regex (used only when no lock exists) ----------
SCHEDULING_INTENT = re.compile(r"\b(schedule|booking|book|appointment|reschedul(e|ing)|consult(ation)?|availability|slot[s]?|times?)\b", re.I)
IMAGE_INTENT = re.compile(r"\b(photo|image|picture|pic|jpeg|png|edit|enhance|retouch|filter|background|remove)\b", re.I)
RESET_KEYWORDS = re.compile(r"\b(cancel|stop|end|menu|main menu|start over|reset|quit|exit)\b", re.I)

# ---------- Agent registry ----------
AGENTS: Dict[str, Any] = {"scheduling": scheduling_agent, "image": image_agent}
if knowledge_agent is not None:
    AGENTS["knowledge"] = knowledge_agent

# ---------- Session management is now handled by the agents framework ----------
# The session parameter passed to Runner.run() automatically maintains conversation state

# ---------- Text extraction ----------
def _extract_text(user_input: Any) -> str:
    if isinstance(user_input, str):
        return user_input
    if isinstance(user_input, list):
        for item in user_input:
            if isinstance(item, dict) and item.get("type") == "message":
                c = item.get("content")
                if isinstance(c, str):
                    return c
    return str(user_input or "")

def _detect_intent(text: str) -> str:
    if SCHEDULING_INTENT.search(text): return "scheduling"
    if IMAGE_INTENT.search(text):      return "image"
    return "knowledge" if "knowledge" in AGENTS else "scheduling"

# ---------- Public entry ----------
async def run_manager(user_input: Any, context: Dict[str, Any], session: Optional[Any] = None) -> Any:
    wa_id = (context or {}).get("user_id") or ""
    text  = _extract_text(user_input)

    log.info("🔵 MANAGER ROUTER: user_id=%s", wa_id)
    log.info("🔵 MANAGER ROUTER: Input: %r", user_input)

    # 1) Reset handling: user wants out → clear session and provide reset response
    if RESET_KEYWORDS.search(text):
        if session:
            await session.clear_session()
        log.info("🔄 MANAGER ROUTER: Reset keywords detected, cleared session")
        # Provide a helpful reset response instead of routing to another agent
        return "I've reset our conversation. How can I help you today? You can ask about scheduling appointments, our services, or anything else."

    # 2) Detect intent and route to appropriate agent
    # The agents framework will handle conversation state through the session parameter
    intent = _detect_intent(text)
    log.info("🔐 MANAGER ROUTER: Routing to %s", intent)
    result = await _run_leaf(AGENTS[intent], user_input, context, session)
    return result

async def _run_leaf(agent_obj: Any, user_input: Any, context: Dict[str, Any], session: Optional[Any]) -> Any:
    return await Runner.run(
        agent_obj,
        user_input,
        context=context,
        session=session,
    )

# Note: Session management is now handled by the agents framework
# The session parameter automatically maintains conversation state

# Legacy compatibility - keep the old function signature for message_service.py
async def run_manager_legacy(user_input, user_id: str, session=None) -> str:
    """
    Legacy wrapper for backward compatibility with message_service.py
    """
    context = {
        "user_id": user_id,
        "channel": "whatsapp"
    }
    
    result = await run_manager(user_input, context, session)
    
    # Extract final output from result
    if hasattr(result, 'final_output'):
        return str(result.final_output)
    else:
        return str(result)

async def run_manager_streaming(user_input: str, user_id: str, image_urls: list = [], session = None) -> AsyncGenerator[str, None]:
    """
    Stream the manager response for real-time output.
    For now, this is a simplified implementation that yields the full response.
    Can be enhanced later with true streaming from the agents.
    """
    context = {
        "user_id": user_id,
        "channel": "chat"
    }
    
    # Get the full response first
    result = await run_manager(user_input, context, session=session)
    
    # Extract final output from result
    if hasattr(result, 'final_output'):
        full_response = str(result.final_output)
    else:
        full_response = str(result)
    
    # For now, yield the full response as a single chunk
    # This can be enhanced to stream word by word or sentence by sentence
    yield full_response