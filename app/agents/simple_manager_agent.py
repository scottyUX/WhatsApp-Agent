"""
Simplified Manager Agent for Istanbul Medic
- Direct Q&A responses only
- No complex routing or scheduling
- Fast, reliable responses with streaming support
"""

from __future__ import annotations
import logging
from typing import Any, Dict, Optional, AsyncGenerator

# Import the simple knowledge agent
from app.agents.simple_knowledge_agent import simple_knowledge_agent

log = logging.getLogger("simple_manager")
log.setLevel(logging.INFO)

def _extract_text(user_input: Any) -> str:
    """Extract text content from various input formats."""
    if isinstance(user_input, str):
        return user_input
    if isinstance(user_input, list):
        for item in user_input:
            if isinstance(item, dict) and item.get("type") == "message":
                c = item.get("content")
                if isinstance(c, str):
                    return c
    return str(user_input or "")

async def run_simple_manager(user_input: Any, context: Dict[str, Any], session: Optional[Any] = None) -> Any:
    """
    Simplified manager that directly handles Q&A without complex routing.
    
    Args:
        user_input: The user's message
        context: Context including user_id and channel
        session: Optional session for conversation memory
    
    Returns:
        Direct response from knowledge agent
    """
    wa_id = (context or {}).get("user_id", "unknown")
    text = _extract_text(user_input)
    
    log.info("🔵 SIMPLE MANAGER: user_id=%s", wa_id)
    log.info("🔵 SIMPLE MANAGER: Input: %r", text)
    
    try:
        # Direct call to knowledge agent - no complex routing
        from agents import Runner
        
        result = await Runner.run(
            simple_knowledge_agent,
            user_input,
            context=context,
            session=session,
        )
        
        log.info("✅ SIMPLE MANAGER: Response generated successfully")
        return result
        
    except Exception as e:
        log.error(f"❌ SIMPLE MANAGER: Error processing request: {e}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly."

async def run_simple_manager_streaming(user_input: str, user_id: str, image_urls: list = [], session = None) -> AsyncGenerator[str, None]:
    """
    Stream the simple manager response for real-time output.
    
    Args:
        user_input: The user's message
        user_id: User identifier
        image_urls: List of image URLs (not used in simplified version)
        session: Optional session for conversation memory
    
    Yields:
        Chunks of the response as they are generated
    """
    context = {
        "user_id": user_id,
        "channel": "chat"
    }
    
    log.info("🔵 SIMPLE MANAGER STREAMING: user_id=%s", user_id)
    log.info("🔵 SIMPLE MANAGER STREAMING: Input: %r", user_input)
    
    try:
        # Use the knowledge agent's streaming capability
        from agents import Runner
        
        # Stream the response directly from the knowledge agent
        async for chunk in Runner.run_streamed(
            simple_knowledge_agent,
            user_input,
            context=context,
            session=session,
        ):
            yield chunk
            
        log.info("✅ SIMPLE MANAGER STREAMING: Response streamed successfully")
        
    except Exception as e:
        log.error(f"❌ SIMPLE MANAGER STREAMING: Error streaming response: {e}")
        yield "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly."

# Legacy compatibility functions for existing code
async def run_manager_legacy(user_input, user_id: str, session=None) -> str:
    """
    Legacy wrapper for backward compatibility with message_service.py
    """
    context = {
        "user_id": user_id,
        "channel": "whatsapp"
    }
    
    result = await run_simple_manager(user_input, context, session)
    
    # Extract final output from result
    if hasattr(result, 'final_output'):
        return str(result.final_output)
    else:
        return str(result)

async def run_manager_streaming(user_input: str, user_id: str, image_urls: list = [], session = None) -> AsyncGenerator[str, None]:
    """
    Legacy wrapper for streaming compatibility
    """
    async for chunk in run_simple_manager_streaming(user_input, user_id, image_urls, session):
        yield chunk
