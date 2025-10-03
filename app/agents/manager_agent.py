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

# Import session service for persistent session management
from app.services.session_service import SessionService
from app.database.db import SessionLocal

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

# ---------- Persistent session management ----------
def _get_session_service() -> SessionService:
    """Get a session service instance with database connection."""
    db = SessionLocal()
    return SessionService(db)

def _get_lock(wa_id: str) -> Optional[str]:
    """Get the active agent for a device's conversation session."""
    try:
        session_service = _get_session_service()
        return session_service.get_session_lock(wa_id)
    except Exception as e:
        log.error(f"Error getting session lock for {wa_id}: {e}")
        return None

def _set_lock(wa_id: str, agent_key: str) -> None:
    """Set a session lock for a device to a specific agent."""
    try:
        session_service = _get_session_service()
        success = session_service.set_session_lock(wa_id, agent_key)
        if not success:
            log.error(f"Failed to set session lock for {wa_id} to {agent_key}")
    except Exception as e:
        log.error(f"Error setting session lock for {wa_id}: {e}")

def _clear_lock(wa_id: str) -> None:
    """Clear the session lock for a device."""
    try:
        session_service = _get_session_service()
        success = session_service.clear_session_lock(wa_id)
        if not success:
            log.error(f"Failed to clear session lock for {wa_id}")
    except Exception as e:
        log.error(f"Error clearing session lock for {wa_id}: {e}")

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

    # 1) Reset handling: user wants out → clear lock and provide reset response
    if RESET_KEYWORDS.search(text):
        _clear_lock(wa_id)
        log.info("🔄 MANAGER ROUTER: Reset keywords detected, cleared lock")
        return "I've reset our conversation. How can I help you today? You can ask about scheduling appointments, our services, or anything else."

    # 2) If there is an active lock, honor it (sticky routing)
    active = _get_lock(wa_id)
    if active and active in AGENTS:
        log.info("🔒 MANAGER ROUTER: Sticky route to %s", active)
        result = await _run_leaf(AGENTS[active], user_input, context, session)
        _maybe_release_lock(wa_id, result)
        return result

    # 3) No lock → detect intent once and lock
    intent = _detect_intent(text)
    _set_lock(wa_id, intent)
    log.info("🔐 MANAGER ROUTER: New lock set: %s", intent)
    result = await _run_leaf(AGENTS[intent], user_input, context, session)
    _maybe_release_lock(wa_id, result)
    return result

async def _run_leaf(agent_obj: Any, user_input: Any, context: Dict[str, Any], session: Optional[Any]) -> Any:
    return await Runner.run(
        agent_obj,
        user_input,
        context=context,
        session=session,
    )

def _maybe_release_lock(wa_id: str, leaf_result: Any) -> None:
    """
    Convention: if the leaf agent returns a dict with {"router_done": True}
    OR {"booking_confirmed": True}, we release the lock.
    You can extend this with whatever your agents already return.
    """
    try:
        if isinstance(leaf_result, dict):
            if leaf_result.get("router_done") or leaf_result.get("booking_confirmed"):
                _clear_lock(wa_id)
                log.info("🔓 MANAGER ROUTER: Lock released due to completion signal")
                return
        # You can also detect special strings if you don't return dicts:
        if isinstance(leaf_result, str) and "Booking confirmed" in leaf_result:
            _clear_lock(wa_id)
            log.info("🔓 MANAGER ROUTER: Lock released due to completion string")
    except Exception:
        pass

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