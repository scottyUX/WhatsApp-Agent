from fastapi import APIRouter, HTTPException, Request, Response
from app.models.message import TwilioWebhookData
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep


router = APIRouter()

@router.get("/api/webhook")
async def webhook_verification(request: Request):
    """Handle webhook verification requests from Twilio."""
    return {"status": "ok", "message": "Webhook is working"}

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
        
        print(f"📤 Webhook result: {result}")
        print(f"📤 Result type: {type(result)}")
        print(f"📤 Result length: {len(str(result)) if result else 0}")
        
        xml_response = f"""
        <Response>
            <Message>{result}</Message>
        </Response>
        """
        print(f"📤 XML response: {xml_response}")
        return Response(content=xml_response.strip(), media_type="text/xml")

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Webhook error: {e}")
        print(f"❌ Error details: {error_details}")
        return Response(content=f"""
        <Response>
            <Message>Sorry, an error occurred. Please try again. Error: {str(e)}</Message>
        </Response>
        """.strip(), media_type="text/xml")
