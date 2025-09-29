from typing import List, Optional, AsyncGenerator
from fastapi import Request
import json
from datetime import datetime

from app.services.history_service import HistoryService
from app.agents.manager_agent import run_manager_legacy
from app.database.entities import Message
from app.models.chat_message import ChatStreamChunk
from app.utils import transcribe_twilio_media, RequestUtils
from agents import SQLiteSession
from app.tools.profile_tools import sanitize_outbound


class MessageService:
    def __init__(self, history_service: HistoryService):
        self.history_service = history_service

    def _format_message_history(self, messages: List[Message]) -> str:
        """Format message history for context."""
        formatted = []
        for msg in messages:
            direction = "User" if msg.sender == "user" else "Agent"
            message = msg.content or ""
            media_list = msg.media or []
            for media in media_list:
                message += f" [Media: {media.media_url}]"
            message_information = f"[{direction} | {msg.created_at.strftime('%Y-%m-%d %H:%M:%S')}]: {message}"
            formatted.append(message_information)
        return "\n".join(formatted)

    async def handle_incoming_whatsapp_message(
        self,
        phone_number: str,
        body: str,
        image_urls: List[str] = None,
        audio_urls: List[str] = None,
    ) -> str:
        """
        Handle incoming WhatsApp message with session memory and appointment booking.
        """
        print(f"📩 WhatsApp message from {phone_number}: {body}")
        
        # Create session for conversation memory
        session_id = f"whatsapp_{phone_number}"
        session = None
        
        try:
            import os
            import sqlite3
            
            # Ensure the directory exists
            db_dir = "/tmp/whatsapp_sessions"
            os.makedirs(db_dir, exist_ok=True)
            
            # Use absolute path for SQLite database
            db_path = os.path.join(db_dir, "conversations.db")
            
            # Configure SQLite with WAL mode for better concurrency
            conn = sqlite3.connect(db_path)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=MEMORY")
            conn.close()
            
            session = SQLiteSession(session_id, db_path)
            print(f"✅ SQLite session created: {db_path}")
        except Exception as e:
            print(f"⚠️ SQLite session not available: {e}")
            session = None

        # Process the message through the agent manager with session memory
        # When using session memory, pass a string instead of a list
        # The session will handle conversation history automatically
        content = body or ""
        if image_urls:
            content += f" [Images: {', '.join(image_urls)}]"

        result = await run_manager_legacy(
            content,
            phone_number,
            session=session,
        )

        # Store the message in database
        await self.history_service.store_message(
            phone_number=phone_number,
            content=body,
            direction="incoming",
            media_urls=image_urls or []
        )

        # Store the agent response
        await self.history_service.store_message(
            phone_number=phone_number,
            content=result,
            direction="outgoing",
            media_urls=[]
        )

        # Sanitize the response for WhatsApp
        sanitized_result = sanitize_outbound(result)
        return sanitized_result

    async def handle_incoming_chat_message(
        self,
        user_id: str,
        content: str,
        image_urls: List[str] = None,
    ) -> str:
        """
        Handle incoming chat message (for website integration).
        """
        print(f"📩 Chat message from {user_id}: {content}")
        
        # Process through the manager
        result = await run_manager_legacy(
            content,
            user_id,
            session=None,  # No session memory for chat
        )

        # Store the message in database
        await self.history_service.store_message(
            phone_number=user_id,
            content=content,
            direction="incoming",
            media_urls=image_urls or []
        )

        # Store the agent response
        await self.history_service.store_message(
            phone_number=user_id,
            content=result,
            direction="outgoing",
            media_urls=[]
        )

        return result

    async def get_message_history(self, phone_number: str, limit: int = 10) -> List[Message]:
        """Get message history for a phone number."""
        return await self.history_service.get_message_history(phone_number, limit)

    async def handle_incoming_whatsapp_message_streaming(
        self,
        phone_number: str,
        body: str,
        image_urls: List[str] = None,
        audio_urls: List[str] = None,
    ) -> AsyncGenerator[ChatStreamChunk, None]:
        """
        Handle incoming WhatsApp message with streaming response.
        """
        print(f"📩 WhatsApp streaming message from {phone_number}: {body}")
        
        # For now, return a single chunk (can be enhanced later)
        result = await self.handle_incoming_whatsapp_message(
            phone_number, body, image_urls, audio_urls
        )
        
        yield ChatStreamChunk(
            content=result,
            is_final=True,
            timestamp=datetime.now()
        )

    async def handle_incoming_chat_message_streaming(
        self,
        user_id: str,
        content: str,
        image_urls: List[str] = None,
    ) -> AsyncGenerator[ChatStreamChunk, None]:
        """
        Handle incoming chat message with streaming response.
        """
        print(f"📩 Chat streaming message from {user_id}: {content}")
        
        # For now, return a single chunk (can be enhanced later)
        result = await self.handle_incoming_chat_message(
            user_id, content, image_urls
        )
        
        yield ChatStreamChunk(
            content=result,
            is_final=True,
            timestamp=datetime.now()
        )
