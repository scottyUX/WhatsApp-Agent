from typing import List, Optional

from app.services.history_service import HistoryService
from agents import SQLiteSession
from app.agents.manager_agent import run_manager
from app.utils.audio_converter import transcribe_twilio_media
from app.database.entities import Message


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
        
        # Get message history for context
        message_history = self.history_service.get_message_history(user.id, limit=10)
        message_history.append(current_message)
        formatted_history = self.format_message_history(message_history)
        
        print(f"📩 WhatsApp message from {phone_number}: {user_input}")
        
        # Prepare session memory using SQLite (one session per WhatsApp user)
        # Convert phone number to valid session ID format
        clean_phone = phone_number.replace('+', '').replace(':', '').replace('-', '')
        session_id = f"wa_{clean_phone}"
        
        # Create session with SQLite backend - simpler and more reliable
        session = SQLiteSession(session_id, "conversations.db")

        # Process the message through the agent manager with session memory
        # IMPORTANT: Pass only the current user turn; the session maintains history
        result = await run_manager(
            user_input,
            phone_number,
            image_urls=image_urls or [],
            session=session,
        )
        
        print(f"🤖 Agent response: {result}")
        print(f"🤖 Response type: {type(result)}")
        print(f"🤖 Response length: {len(str(result)) if result else 0}")
        
        # Log the outgoing response
        self.history_service.log_outgoing_message(
            user_id=user.id,
            body=result
        )
        
        return result
