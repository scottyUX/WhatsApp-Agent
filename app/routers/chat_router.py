import traceback
from fastapi import APIRouter, HTTPException, Request, Response

from app.models.chat_message import ChatMessageRequest, ChatMessageResponse
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep
from app.utils import ErrorUtils


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
        
        # Use the message service to handle the incoming message
        content = await message_service.handle_incoming_chat_message(
            request=request,
            message=content,
            media_urls=media_urls,
            audio_urls=audio_urls
        )
        return ChatMessageResponse(content=content)
    except Exception as exception:
        traceback.print_exc()
        raise ErrorUtils.toHTTPException(exception)
