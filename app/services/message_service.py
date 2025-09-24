from typing import List, Optional
from fastapi import Request
import json
from datetime import datetime

from app.services.history_service import HistoryService
from app.agents.manager_agent import run_manager, run_manager_streaming
from app.database.entities import Message
from app.models.chat_message import ChatStreamChunk
from app.utils import transcribe_twilio_media, RequestUtils


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
        connection = self.history_service.get_or_create_connection(
            channel="whatsapp",
            phone_number=phone_number
        )
        user = connection.user
        conversation = self.history_service.get_or_create_conversation(
            user_id=user.id,
            connection_id=connection.id
        )

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
            conversation_id=conversation.id,
            content=user_input,
            media_url=media_url
        )

        # Get message history for context
        message_history = self.history_service.get_message_history(conversation_id=conversation.id, limit=10)
        message_history.append(current_message)
        formatted_history = self._format_message_history(message_history)

        print(f"WhatsApp message from {phone_number}: {user_input}")

        # Process the message through the agent manager
        result = await run_manager(formatted_history, phone_number, image_urls=image_urls or [])

        # Log the outgoing response
        self.history_service.log_outgoing_message(
            conversation_id=conversation.id,
            content=result
        )

        return result


    async def handle_incoming_chat_message(
        self,
        request: Request,
        message: str,
        media_urls: Optional[List[str]] = None,
        audio_urls: Optional[List[str]] = None
    ) -> str:
        device_id = RequestUtils.get_device_id_from_headers(request)
        ip_address = RequestUtils.get_ip_address_from_headers(request)
        connection = self.history_service.get_or_create_connection(
            channel="chat",
            device_id=device_id,
            ip_address=ip_address
        )
        user = connection.user
        conversation = self.history_service.get_or_create_conversation(
            user_id=user.id,
            connection_id=connection.id
        )

        # Log the incoming message
        current_message = self.history_service.log_incoming_message(
            conversation_id=conversation.id,
            content=message,
            # media_url=media_url
        )

        # Get message history for context
        message_history = self.history_service.get_message_history(conversation_id=conversation.id, limit=10)
        message_history.append(current_message)
        formatted_history = self._format_message_history(message_history)

        print(f"Website message from {user.id}: {message}")
        
        # Process the message through the agent manager
        result = await run_manager(formatted_history, user.id, [])

        # Log the outgoing response
        self.history_service.log_outgoing_message(
            conversation_id=conversation.id,
            content=result
        )
        
        return result


    async def handle_incoming_chat_message_streaming(
        self,
        request: Request,
        message: str,
        media_urls: Optional[List[str]] = None,
        audio_urls: Optional[List[str]] = None
    ):
        """
        Handle an incoming chat message with streaming response formatted as SSE.

        Args:
            request: FastAPI request object
            message: Text message content
            media_urls: List of media URLs if any
            audio_urls: List of audio URLs if any

        Yields:
            Server-Sent Events formatted streaming response chunks
        """
        try:
            device_id = RequestUtils.get_device_id_from_headers(request)
            ip_address = RequestUtils.get_ip_address_from_headers(request)
            connection = self.history_service.get_or_create_connection(
                channel="chat",
                device_id=device_id,
                ip_address=ip_address
            )
            user = connection.user
            conversation = self.history_service.get_or_create_conversation(
                user_id=user.id,
                connection_id=connection.id
            )

            # Log the incoming message
            current_message = self.history_service.log_incoming_message(
                conversation_id=conversation.id,
                content=message,
                # media_url=media_url
            )

            # Get message history for context
            message_history = self.history_service.get_message_history(conversation_id=conversation.id, limit=10)
            message_history.append(current_message)
            formatted_history = self._format_message_history(message_history)

            print(f"Website message from {user.id} (streaming): {message}")

            # Collect the full response for logging
            full_response = ""

            # Process the message through the agent manager with streaming
            async for chunk in run_manager_streaming(formatted_history, user.id):
                full_response += chunk
                
                # Create a streaming chunk
                stream_chunk = ChatStreamChunk(
                    content=chunk,
                    timestamp=datetime.now().isoformat(),
                    is_final=False
                )
                
                # Send as Server-Sent Events format
                yield f"data: {json.dumps(stream_chunk.__dict__)}\n\n"

            # Send final chunk to indicate completion
            final_chunk = ChatStreamChunk(
                content="",
                timestamp=datetime.now().isoformat(),
                is_final=True
            )
            yield f"data: {json.dumps(final_chunk.__dict__)}\n\n"

            # Log the complete outgoing response
            self.history_service.log_outgoing_message(
                conversation_id=conversation.id,
                content=full_response
            )

        except Exception as e:
            # Send error chunk
            error_chunk = ChatStreamChunk(
                content=f"Error: {str(e)}",
                timestamp=datetime.now().isoformat(),
                is_final=True
            )
            yield f"data: {json.dumps(error_chunk.__dict__)}\n\n"
