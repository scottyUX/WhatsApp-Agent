"""
Server-Sent Events (SSE) Router for Real-time Notifications
Compatible with Vercel's serverless architecture
"""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import asyncio
import json
import time
from typing import Dict, Set
import logging

log = logging.getLogger("sse_router")

# Store active SSE connections
active_connections: Dict[str, Set[asyncio.Queue]] = {}

router = APIRouter(
    prefix="/sse",
    tags=["SSE"],
)

async def event_generator(user_id: str):
    """Generate SSE events for a specific user"""
    # Create a queue for this connection
    queue = asyncio.Queue()
    
    # Add to active connections
    if user_id not in active_connections:
        active_connections[user_id] = set()
    active_connections[user_id].add(queue)
    
    log.info(f"🔌 SSE connection established for user: {user_id}")
    
    try:
        # Send initial connection event
        yield f"data: {json.dumps({'type': 'connected', 'message': 'SSE connection established'})}\n\n"
        
        # Keep connection alive and listen for events
        while True:
            try:
                # Wait for events in the queue with a timeout
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
            except asyncio.TimeoutError:
                # Send keepalive ping
                yield f"data: {json.dumps({'type': 'ping', 'timestamp': time.time()})}\n\n"
            except Exception as e:
                log.error(f"❌ SSE event generation error: {e}")
                break
                
    except Exception as e:
        log.error(f"❌ SSE connection error for user {user_id}: {e}")
    finally:
        # Clean up connection
        if user_id in active_connections:
            active_connections[user_id].discard(queue)
            if not active_connections[user_id]:
                del active_connections[user_id]
        log.info(f"🔌 SSE connection closed for user: {user_id}")

@router.get("/events/{user_id}")
async def stream_events(user_id: str, request: Request):
    """Stream Server-Sent Events for real-time notifications"""
    return StreamingResponse(
        event_generator(user_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control",
        }
    )

async def send_booking_confirmation(user_id: str, booking_data: Dict[str, any]) -> bool:
    """Send booking confirmation to all connected users"""
    if user_id not in active_connections:
        log.warning(f"⚠️ No SSE connections found for user: {user_id}")
        return False
    
    event = {
        "type": "booking_confirmation",
        "data": booking_data
    }
    
    # Send to all connections for this user
    sent_count = 0
    for queue in list(active_connections[user_id]):
        try:
            await queue.put(event)
            sent_count += 1
        except Exception as e:
            log.error(f"❌ Failed to send SSE event: {e}")
    
    log.info(f"📤 Sent booking confirmation to {sent_count} SSE connections for user: {user_id}")
    return sent_count > 0

def get_connected_users() -> list:
    """Get list of users with active SSE connections"""
    return list(active_connections.keys())

def get_connection_count() -> int:
    """Get total number of active SSE connections"""
    return sum(len(connections) for connections in active_connections.values())
