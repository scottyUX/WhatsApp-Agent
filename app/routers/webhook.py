from fastapi import APIRouter, HTTPException, Request, Response
from app.models.message import TwilioWebhookData
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep


router = APIRouter()

@router.post("/api/webhook")
@limiter.limit(RateLimitConfig.WEBHOOK)
async def istanbulMedic_webhook(request: Request, message_service: MessageServiceDep):
    try:
        form = await request.form()
        webhook_data = TwilioWebhookData(form)
        
        user_input = webhook_data.body
        user_id = webhook_data.from_number
        image_urls = webhook_data.get_image_urls()
        audio_urls = webhook_data.get_audio_urls()
        
        # Use the message service to handle the incoming message
        result = await message_service.handle_incoming_message(
            phone_number=user_id,
            body=user_input,
            image_urls=image_urls,
            audio_urls=audio_urls
        )
        
        xml_response = f"""
        <Response>
            <Message>{result}</Message>
        </Response>
        """
        return Response(content=xml_response.strip(), media_type="text/xml")

    except Exception as e:
        print(f"❌ Webhook error: {e}")
        return Response(content="""
        <Response>
            <Message>Sorry, an error occurred. Please try again.</Message>
        </Response>
        """.strip(), media_type="text/xml")
