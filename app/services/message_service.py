from typing import List, Optional, AsyncGenerator
from fastapi import Request
import json
from datetime import datetime

from sqlalchemy.orm import Session
from agents.memory.openai_conversations_session import OpenAIConversationsSession
from app.services.history_service import HistoryService
from app.agents.simple_manager_agent import run_manager_legacy, run_manager_streaming
from app.config.settings import settings
# Note: Using OpenAI managed conversation sessions for persistent memory
from app.database.entities import Message
from app.services.session_service import SessionService
from app.database.db import SessionLocal
from app.models.chat_message import ChatStreamChunk
from app.utils import transcribe_twilio_media, RequestUtils
from app.tools.profile_tools import sanitize_outbound


class MessageService:
    def __init__(self, history_service: HistoryService):
        self.history_service = history_service

    def _prepare_agent_session(self, device_id: str) -> tuple[Optional[Session], Optional[SessionService], Optional[OpenAIConversationsSession]]:
        """Create database-backed session service and OpenAI conversation session."""
        db = None
        session_service: Optional[SessionService] = None
        session: Optional[OpenAIConversationsSession] = None

        try:
            db = SessionLocal()
            session_service = SessionService(db)
            conversation_id = session_service.get_openai_conversation_id(device_id)
        except Exception as exc:
            print(f"⚠️ Failed to initialize session service for {device_id}: {exc}")
            conversation_id = None
            if db is not None:
                db.close()
                db = None

        try:
            session = OpenAIConversationsSession(
                conversation_id=conversation_id,
                context_limit=settings.CONTEXT_LIMIT,
                keep_last_n_turns=settings.KEEP_LAST_N_TURNS,
            )
            print(f"🧠 Memory session created for {device_id}: context_limit={settings.CONTEXT_LIMIT}, keep_last_n_turns={settings.KEEP_LAST_N_TURNS}")
        except Exception as exc:
            print(f"⚠️ OpenAI conversation session unavailable for {device_id}: {exc}")
            session = None

        return db, session_service, session

    async def clear_user_session(self, device_id: str) -> bool:
        """Clear conversation history for a specific user."""
        try:
            db, session_service, session = await self._get_session_components(device_id)
            if session:
                await session.clear_session()
                print(f"🧹 Cleared session for user {device_id}")
                return True
            return False
        except Exception as e:
            print(f"❌ Failed to clear session for {device_id}: {e}")
            return False

    async def get_session_items(self, device_id: str) -> list:
        """Get conversation history for debugging/monitoring."""
        try:
            db, session_service, session = await self._get_session_components(device_id)
            if session:
                items = await session.get_items()
                return items
            return []
        except Exception as e:
            print(f"❌ Failed to get session items for {device_id}: {e}")
            return []

    async def _persist_openai_conversation(
        self,
        session_service: Optional[SessionService],
        device_id: str,
        session: Optional[OpenAIConversationsSession],
    ) -> None:
        if not session_service or not session:
            return

        try:
            conversation_id = await session._get_session_id()
            session_service.set_openai_conversation_id(device_id, conversation_id)
        except Exception as exc:
            print(f"⚠️ Failed to persist OpenAI conversation id for {device_id}: {exc}")

    @staticmethod
    def _close_db(db: Optional[Session]) -> None:
        if db:
            try:
                db.close()
            except Exception as exc:
                print(f"⚠️ Failed to close session database handle: {exc}")

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
        
        # Create OpenAI-backed session for conversation memory
        db_handle, session_service, agent_session = self._prepare_agent_session(phone_number)
        session = agent_session

        # Process the message through the agent manager with session memory
        # When using session memory, pass a string instead of a list
        # The session will handle conversation history automatically
        content = body or ""
        if image_urls:
            content += f" [Images: {', '.join(image_urls)}]"

        try:
            result = await run_manager_legacy(
                content,
                phone_number,
                session=session,
            )
            await self._persist_openai_conversation(session_service, phone_number, agent_session)
        finally:
            self._close_db(db_handle)

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
        Handle incoming chat message with simplified Q&A response.
        """
        print(f"📩 Chat message from {user_id}: {content}")
        
        try:
            # Simplified call to simple manager - no complex session management
            result = await run_manager_legacy(content, user_id, None)
        except Exception as e:
            print(f"❌ Error in chat message handling: {e}")
            result = "I apologize, but I'm experiencing technical difficulties. Please try again or contact our support team directly."

        # Store the message in database using user_id as phone_number for chat users
        # This ensures we can track chat conversations separately from WhatsApp
        chat_phone = f"chat_{user_id}"
        await self.history_service.store_message(
            phone_number=chat_phone,
            content=content,
            direction="incoming",
            media_urls=image_urls or []
        )

        # Store the agent response
        await self.history_service.store_message(
            phone_number=chat_phone,
            content=result,
            direction="outgoing",
            media_urls=[]
        )

        return result

    async def handle_incoming_message(
        self,
        phone_number: str,
        body: str,
        image_urls: List[str] = None,
        audio_urls: List[str] = None,
    ) -> str:
        """
        Handle incoming message (alias for WhatsApp message handling).
        """
        return await self.handle_incoming_whatsapp_message(
            phone_number, body, image_urls, audio_urls
        )

    async def get_message_history(self, phone_number: str, limit: int = 10) -> List[Message]:
        """Get message history for a phone number."""
        return await self.history_service.get_message_history_by_phone(phone_number, limit)

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
    ) -> AsyncGenerator[str, None]:
        """
        Handle incoming chat message with simplified streaming response.
        """
        print(f"📩 Chat streaming message from {user_id}: {content}")
        
        # Store the incoming message in database
        chat_phone = f"chat_{user_id}"
        await self.history_service.store_message(
            phone_number=chat_phone,
            content=content,
            direction="incoming",
            media_urls=image_urls or []
        )

        # Collect the full response for logging
        full_response = ""

        try:
            # Simplified streaming - direct call to simple manager
            async for chunk in run_manager_streaming(content, user_id, image_urls or [], None):
                full_response += chunk
                
                # Create a streaming chunk
                stream_chunk = ChatStreamChunk(
                    content=chunk,
                    timestamp=datetime.now().isoformat(),
                    is_final=False
                )
                
                # Send as Server-Sent Events format
                yield f"data: {json.dumps(stream_chunk.__dict__)}\n\n"

        except Exception as e:
            print(f"❌ Error in streaming: {e}")
            # Send error response
            error_chunk = ChatStreamChunk(
                content="I apologize, but I'm experiencing technical difficulties. Please try again.",
                timestamp=datetime.now().isoformat(),
                is_final=False
            )
            yield f"data: {json.dumps(error_chunk.__dict__)}\n\n"
            full_response = "Error occurred"

        # Send final chunk to indicate completion
        final_chunk = ChatStreamChunk(
            content="",
            timestamp=datetime.now().isoformat(),
            is_final=True
        )
        yield f"data: {json.dumps(final_chunk.__dict__)}\n\n"

        # Store the complete outgoing response
        await self.history_service.store_message(
            phone_number=chat_phone,
            content=full_response,
            direction="outgoing",
            media_urls=[]
        )
