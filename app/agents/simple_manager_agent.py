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
    # Validate input
    if not user_input or not isinstance(user_input, str) or user_input.strip() == "":
        log.error("❌ SIMPLE MANAGER STREAMING: Invalid input: %r", user_input)
        yield "I apologize, but I didn't receive a valid message. Please try again with a proper question."
        return
    
    context = {
        "user_id": user_id,
        "channel": "chat"
    }
    
    log.info("🔵 SIMPLE MANAGER STREAMING: user_id=%s", user_id)
    log.info("🔵 SIMPLE MANAGER STREAMING: Input: %r", user_input)
    
    try:
        # Use the knowledge agent's streaming capability
        from agents import Runner
        
        # Get the streaming result
        result = Runner.run_streamed(
            simple_knowledge_agent,
            user_input,
            context=context,
            session=session,
        )
        
        # Track whether we've already streamed any delta text to avoid
        # duplicating the final full message from raw_response.
        streamed_any_delta = False

        # Stream the events from the result
        async for event in result.stream_events():
            # 1) Yield incremental deltas ASAP (varies by provider/version)
            try:
                if hasattr(event, 'type') and hasattr(event, 'data'):
                    etype = str(getattr(event, 'type', '') or '')
                    data = getattr(event, 'data', None)

                    # Common delta fields
                    if hasattr(data, 'delta') and isinstance(data.delta, str) and data.delta:
                        streamed_any_delta = True
                        yield data.delta
                        continue
                    if hasattr(data, 'text') and isinstance(data.text, str) and data.text and ('delta' in etype or 'stream' in etype):
                        streamed_any_delta = True
                        yield data.text
                        continue

            except Exception:
                # Ignore delta extraction errors and fall back to raw_response parsing below
                pass

            # 2) Fallback: extract full text from raw response events (end of run)
            if not streamed_any_delta and hasattr(event, 'type') and 'raw_response' in str(event.type):
                if hasattr(event, 'data') and hasattr(event.data, 'response'):
                    response = event.data.response
                    if hasattr(response, 'output') and response.output:
                        for output_item in response.output:
                            if hasattr(output_item, 'content') and output_item.content:
                                for content_item in output_item.content:
                                    if hasattr(content_item, 'text') and content_item.text:
                                        yield content_item.text
            
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
