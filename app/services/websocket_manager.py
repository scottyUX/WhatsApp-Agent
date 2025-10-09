"""
WebSocket Manager for Real-time Chat Notifications
Handles WebSocket connections and broadcasting booking confirmations
"""

import json
import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
import logging

log = logging.getLogger("websocket_manager")

class ConnectionManager:
    """Manages WebSocket connections for real-time notifications"""
    
    def __init__(self):
        # Store active connections by user_id
        self.active_connections: Dict[str, WebSocket] = {}
        # Store connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str, device_id: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.connection_metadata[user_id] = {
            "device_id": device_id,
            "connected_at": asyncio.get_event_loop().time()
        }
        log.info(f"🔌 WebSocket connected: user_id={user_id}, device_id={device_id}")
    
    def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.connection_metadata:
            del self.connection_metadata[user_id]
        log.info(f"🔌 WebSocket disconnected: user_id={user_id}")
    
    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            try:
                websocket = self.active_connections[user_id]
                await websocket.send_text(message)
                log.info(f"📤 Message sent to user {user_id}")
                return True
            except Exception as e:
                log.error(f"❌ Failed to send message to user {user_id}: {e}")
                # Remove the connection if it's broken
                self.disconnect(user_id)
                return False
        else:
            log.warning(f"⚠️ User {user_id} not connected")
            return False
    
    async def send_booking_confirmation(self, user_id: str, booking_data: Dict[str, Any]):
        """Send a booking confirmation message to a specific user"""
        confirmation_message = {
            "type": "booking_confirmation",
            "data": {
                "booking_id": booking_data.get("id", "Unknown"),
                "title": booking_data.get("title", "Consultation"),
                "start_time": booking_data.get("startTime", ""),
                "attendee_name": booking_data.get("attendee_name", "Guest"),
                "attendee_email": booking_data.get("attendee_email", ""),
                "message": f"""
🎉 **Booking Confirmed!**

Thank you, {booking_data.get('attendee_name', 'Guest')}! Your consultation has been successfully scheduled.

**Booking Details:**
• **Event:** {booking_data.get('title', 'Consultation')}
• **Date & Time:** {booking_data.get('startTime', 'TBD')}
• **Duration:** 15 minutes
• **Booking ID:** {booking_data.get('id', 'Unknown')}

We'll send you a calendar invite shortly. If you need to reschedule or have any questions, please don't hesitate to reach out.

Looking forward to speaking with you!
                """.strip()
            }
        }
        
        message_json = json.dumps(confirmation_message)
        return await self.send_personal_message(message_json, user_id)
    
    async def broadcast_message(self, message: str):
        """Broadcast a message to all connected users"""
        disconnected_users = []
        for user_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(message)
            except Exception as e:
                log.error(f"❌ Failed to broadcast to user {user_id}: {e}")
                disconnected_users.append(user_id)
        
        # Clean up disconnected users
        for user_id in disconnected_users:
            self.disconnect(user_id)
    
    def get_connection_count(self) -> int:
        """Get the number of active connections"""
        return len(self.active_connections)
    
    def get_connected_users(self) -> Set[str]:
        """Get a set of connected user IDs"""
        return set(self.active_connections.keys())

# Global connection manager instance
manager = ConnectionManager()
