from fastapi import APIRouter, HTTPException, Request, Response
from app.models.message import TwilioWebhookData
from app.config.rate_limits import limiter, RateLimitConfig
from app.dependencies import MessageServiceDep
from app.routers.sse_router import send_booking_confirmation
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

@router.post("/cal-webhook")
@limiter.limit(RateLimitConfig.WEBHOOK)
async def cal_webhook(request: Request, message_service: MessageServiceDep):
    """Handle Cal.com webhook when user books an appointment."""
    try:
        # Verify webhook secret (optional but recommended)
        webhook_secret = request.headers.get("x-cal-signature-256")
        expected_secret = "istanbul-medic-webhook-2025"
        
        # Log the signature for debugging
        if webhook_secret:
            print(f"📅 CAL.COM WEBHOOK: Received signature: {webhook_secret}")
        else:
            print("📅 CAL.COM WEBHOOK: No signature provided")
        
        # Note: Cal.com uses HMAC-SHA256 for signature verification
        # For now, we accept all webhooks but log the signature
        # In production, you might want to verify the signature properly
        
        # Get the webhook payload
        payload = await request.json()
        
        print(f"📅 CAL.COM WEBHOOK: Received booking notification")
        print(f"📅 CAL.COM WEBHOOK: Payload: {json.dumps(payload, indent=2)}")
        
        # Extract booking information
        event_type = payload.get("type", "")
        
        if event_type == "BOOKING_CREATED":
            # Extract booking details
            booking = payload.get("data", {})
            attendee = booking.get("attendees", [{}])[0] if booking.get("attendees") else {}
            
            # Get booking information
            booking_id = booking.get("id", "Unknown")
            event_title = booking.get("title", "Consultation")
            start_time = booking.get("startTime", "")
            end_time = booking.get("endTime", "")
            attendee_name = attendee.get("name", "Guest")
            attendee_email = attendee.get("email", "")
            
            # Extract additional patient information if available
            responses = booking.get("responses", {})
            patient_phone = responses.get("phone", "")
            patient_message = responses.get("message", "")
            patient_age = responses.get("age", "")
            hair_loss_pattern = responses.get("hair_loss_pattern", "")
            time_zone = attendee.get("timeZone", "")
            
            # Prepare booking data for real-time notification
            booking_data = {
                "id": booking_id,
                "title": event_title,
                "startTime": start_time,
                "endTime": end_time,
                "attendee_name": attendee_name,
                "attendee_email": attendee_email,
                "patient_phone": patient_phone,
                "patient_message": patient_message,
                "patient_age": patient_age,
                "hair_loss_pattern": hair_loss_pattern,
                "time_zone": time_zone
            }
            
            print(f"📅 CAL.COM WEBHOOK: Generated booking data: {booking_data}")
            
                    # Add booking to polling system for real-time notifications
                    from app.routers.booking_router import add_booking
                    try:
                        await add_booking(booking_data)
                        print(f"📅 CAL.COM WEBHOOK: Added booking to polling system: {booking_data.get('booking_id')}")
                    except Exception as e:
                        print(f"❌ CAL.COM WEBHOOK: Failed to add booking to polling system: {e}")
            
            # Store the booking confirmation in database
            # You can add logic here to store booking details in your database
            
            return {"status": "success", "message": "Booking confirmation processed and notifications sent"}
        
        elif event_type == "BOOKING_CANCELLED":
            print(f"📅 CAL.COM WEBHOOK: Booking cancelled")
            return {"status": "success", "message": "Booking cancellation processed"}
        
        else:
            print(f"📅 CAL.COM WEBHOOK: Unknown event type: {event_type}")
            return {"status": "success", "message": "Webhook received"}
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Cal.com webhook error: {e}")
        print(f"❌ Error details: {error_details}")
        return {"status": "error", "message": str(e)}
