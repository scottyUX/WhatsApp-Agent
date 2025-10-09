import traceback
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.models.chat_message import ChatMessageRequest, ChatMessageResponse
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep
from app.utils import ErrorUtils
from app.config.settings import settings


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


@router.delete("/memory/{user_id}")
@limiter.limit(RateLimitConfig.ADMIN)
async def clear_user_memory(request: Request, user_id: str, message_service: MessageServiceDep):
    """Clear conversation memory for a specific user (admin endpoint)."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        success = await message_service.clear_user_session(user_id)
        if success:
            return {"status": "success", "message": f"Memory cleared for user {user_id}"}
        else:
            return {"status": "error", "message": f"Failed to clear memory for user {user_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/{user_id}")
@limiter.limit(RateLimitConfig.ADMIN)
async def get_user_memory(request: Request, user_id: str, message_service: MessageServiceDep):
    """Get conversation memory for a specific user (admin endpoint)."""
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not found")
    
    try:
        items = await message_service.get_session_items(user_id)
        return {
            "status": "success", 
            "user_id": user_id,
            "item_count": len(items),
            "items": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
