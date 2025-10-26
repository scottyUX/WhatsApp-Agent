from fastapi import APIRouter, HTTPException, Request, Response, Depends
from sqlalchemy.orm import Session
from app.models.message import TwilioWebhookData
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep
from app.services.consultation_service import ConsultationService
from app.database.db import SessionLocal
from datetime import datetime
import json


router = APIRouter(
    prefix="/api",
    tags=["Webhook"],
)

@router.get("/webhook")
async def webhook_verification(request: Request):
    """Handle webhook verification requests from Twilio."""
    return {"status": "ok", "message": "Webhook is working"}

@router.post("/webhook")
@limiter.limit(RateLimitConfig.WEBHOOK)
async def istanbulMedic_webhook(request: Request, message_service: MessageServiceDep):
    try:
        form = await request.form()
        webhook_data = TwilioWebhookData(form)
        
        user_input = webhook_data.body
        user_id = webhook_data.from_number
        image_urls = webhook_data.get_image_urls()
        audio_urls = webhook_data.get_audio_urls()
        
        print(f"🟣 WEBHOOK: Processing message from {user_id}")
        print(f"🟣 WEBHOOK: User input: {user_input}")
        print(f"🟣 WEBHOOK: Image URLs: {image_urls}")
        print(f"🟣 WEBHOOK: Audio URLs: {audio_urls}")
        
        # Use the message service to handle the incoming WhatsApp message
        result = await message_service.handle_incoming_whatsapp_message(
            phone_number=user_id,
            body=user_input,
            image_urls=image_urls,
            audio_urls=audio_urls
        )
        
        print(f"🟣 WEBHOOK: Message service returned: {result}")
        print(f"🟣 WEBHOOK: Result type: {type(result)}")
        print(f"🟣 WEBHOOK: Result length: {len(str(result)) if result else 0}")
        
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

def get_db():
    """Dependency to get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/cal-webhook")
@limiter.limit(RateLimitConfig.WEBHOOK)
async def cal_webhook(request: Request, message_service: MessageServiceDep, db: Session = Depends(get_db)):
    """Handle Cal.com webhook when user books an appointment."""
    try:
        # Get the webhook payload
        payload = await request.json()
        
        print(f"📅 CAL.COM WEBHOOK: Received booking notification")
        print(f"📅 CAL.COM WEBHOOK: Payload: {json.dumps(payload, indent=2)}")
        
        # Extract booking ID for logging
        booking_data = payload.get("payload", payload.get("data", {}))
        booking_uid = booking_data.get("uid", "UNKNOWN")
        print(f"📅 CAL.COM WEBHOOK: Booking UID: {booking_uid}")
        
        # Process webhook using consultation service
        consultation_service = ConsultationService(db)
        result = consultation_service.process_cal_webhook(payload)
        
        print(f"📅 CAL.COM WEBHOOK: Processing result: {result}")
        
        # Generate confirmation message for BOOKING_CREATED events
        if result.get("action") == "created":
            booking_data = payload.get("data", {})
            
            # Extract actual data (not template placeholders)
            booking_id = booking_data.get("uid", booking_data.get("id", "Unknown"))
            event_title = booking_data.get("title", "Consultation")
            start_time = booking_data.get("startTime", "")
            attendee_name = booking_data.get("attendeeName", "Guest")
            
            # Format the confirmation message
            confirmation_message = f"""
🎉 **Booking Confirmed!**

Thank you, {attendee_name}! Your consultation has been successfully scheduled.

**Booking Details:**
• **Event:** {event_title}
• **Date & Time:** {start_time}
• **Duration:** 15 minutes
• **Booking ID:** {booking_id}

We'll send you a calendar invite shortly. If you need to reschedule or have any questions, please don't hesitate to reach out.

Looking forward to speaking with you!
            """.strip()
            
            print(f"📅 CAL.COM WEBHOOK: Generated confirmation: {confirmation_message}")
        
        return {
            "status": "success", 
            "message": "Webhook processed successfully",
            "result": result
        }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Cal.com webhook error: {e}")
        print(f"❌ Error details: {error_details}")
        return {"status": "error", "message": str(e)}
