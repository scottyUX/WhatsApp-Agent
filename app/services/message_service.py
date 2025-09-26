from typing import List, Optional

from app.services.history_service import HistoryService
from agents import SQLiteSession
from app.agents.manager_agent import run_manager_legacy
from app.utils.audio_converter import transcribe_twilio_media
from app.database.entities import Message
from app.tools.profile_tools import sanitize_outbound


class MessageService:
    def __init__(self, history_service: HistoryService):
        self.history_service = history_service

    def format_message_history(self, messages: List[Message]) -> str:
        """Format message history for context."""
        formatted = []
        for msg in messages:
            direction = "User" if msg.direction == "incoming" else "Agent"
            body = msg.body or ""
            if msg.media_url:
                body += f" [Media: {msg.media_url}]"
            message_information = f"[{direction} | {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}]: {body}"
            formatted.append(message_information)
        return "\n".join(formatted)

    async def handle_incoming_message(
        self, 
        phone_number: str,
        body: Optional[str] = None,
        image_urls: Optional[List[str]] = None,
        audio_urls: Optional[List[str]] = None
    ) -> str:
        """
        Handle an incoming message from WhatsApp webhook.
        
        Args:
            phone_number: The sender's phone number
            body: Text message body
            image_urls: List of image URLs if any
            audio_urls: List of audio URLs if any
            
        Returns:
            Response message to send back
        """
        # Get or create user
        user = self.history_service.get_or_create_user(phone_number)
        
        # Process audio if present
        user_input = body or ""
        media_url = None
        
        if audio_urls:
            audio_transcript = transcribe_twilio_media(audio_urls[0])
            user_input = f"[Voice Message]: {audio_transcript}"
            media_url = audio_urls[0]
        elif image_urls:
            media_url = image_urls[0] if image_urls else None
        
        # Log the incoming message
        current_message = self.history_service.log_incoming_message(
            user_id=user.id,
            body=user_input,
            media_url=media_url
        )
        
        print(f"📩 WhatsApp message from {phone_number}: {user_input}")
        
        # Prepare session memory using SQLite (one session per WhatsApp user)
        # Convert phone number to valid session ID format
        clean_phone = phone_number.replace('+', '').replace(':', '').replace('-', '')
        session_id = f"wa_{clean_phone}"
        
        # Create session with SQLite backend - simpler and more reliable
        # In serverless environments, SQLite might not be available
        try:
            session = SQLiteSession(session_id, "conversations.db")
        except Exception as e:
            print(f"⚠️ SQLite session not available: {e}")
            session = None

        # Process the message through the agent manager with session memory
        # Use the correct content format for the agent system
        content = [{"type": "message", "role": "user", "content": user_input or ""}]
        if image_urls:
            content += [{"type": "message", "role": "user", "content": f"[Image: {url}]"} for url in image_urls]

        result = await run_manager_legacy(
            content,
            phone_number,
            session=session,
        )
        
        print(f"Agent response: {result}")
        print(f"Response type: {type(result)}")
        print(f"Response length: {len(str(result)) if result else 0}")
        
        # Sanitize the response
        sanitized_result = sanitize_outbound(result)
        
        # Log the outgoing response
        self.history_service.log_outgoing_message(
            user_id=user.id,
            body=sanitized_result
        )
        
        return sanitized_result
