import traceback
from fastapi import APIRouter, HTTPException, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

from app.models.chat_message import ChatMessageRequest, ChatMessageResponse
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep
from app.utils import ErrorUtils
from app.services.websocket_manager import manager


router = APIRouter(
    prefix="/chat",
    tags=["Chat"],
)


@router.post(
    "/",
    response_model=ChatMessageResponse,
    status_code=200
)
@limiter.limit(RateLimitConfig.CHAT)
async def chat(request: Request,
               chat_message_request: ChatMessageRequest,
               message_service: MessageServiceDep):
    try:
        content = chat_message_request.content
        media_urls = chat_message_request.media_urls or []
        audio_urls = chat_message_request.audio_urls or []

        # Validate content is not None or empty
        if not content or content.strip() == "":
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Extract device ID from headers for conversation state management
        device_id = request.headers.get("X-Device-ID", "default_user")
        user_id = f"chat_{device_id}"

        # Use the message service to handle the incoming message
        content = await message_service.handle_incoming_chat_message(
            user_id=user_id,
            content=content,
            image_urls=media_urls
        )
        return ChatMessageResponse(content=content)
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.post(
    "/stream",
    status_code=200
)
@limiter.limit(RateLimitConfig.CHAT)
async def chat_stream(request: Request,
                     chat_message_request: ChatMessageRequest,
                     message_service: MessageServiceDep):
    try:
        content = chat_message_request.content
        media_urls = chat_message_request.media_urls or []
        audio_urls = chat_message_request.audio_urls or []

        # Validate content is not None or empty
        if not content or content.strip() == "":
            raise HTTPException(status_code=400, detail="Content cannot be empty")

        # Extract device ID from headers for conversation state management
        device_id = request.headers.get("X-Device-ID", "default_user")
        user_id = f"chat_{device_id}"

        return StreamingResponse(
            message_service.handle_incoming_chat_message_streaming(
                user_id=user_id,
                content=content,
                image_urls=media_urls
            ),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )

    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)


@router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, device_id: str = None):
    """WebSocket endpoint for real-time chat notifications"""
    await manager.connect(websocket, user_id, device_id)
    try:
        while True:
            # Keep the connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back any messages received (optional)
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(user_id)
        print(f"🔌 WebSocket disconnected: {user_id}")
