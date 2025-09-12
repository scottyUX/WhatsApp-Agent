from fastapi import APIRouter, HTTPException, Request, Response
from app.agents.manager_agent import run_manager
from app.models.message import TwilioWebhookData
from app.utils.audio_converter import transcribe_twilio_media

router = APIRouter()

@router.get("/")
async def read_root():
    return {"Hello": "World"}

@router.post("/api/webhook")
async def istanbulMedic_webhook(request: Request):
    try:
        form = await request.form()
        webhook_data = TwilioWebhookData(form)
        
        user_input = webhook_data.body
        user_id = webhook_data.from_number
        image_urls = webhook_data.get_image_urls()
        audio_urls = webhook_data.get_audio_urls()
        
        if audio_urls:
            audio_transcript = transcribe_twilio_media(audio_urls[0])
            user_input = f"[Voice Message]: {audio_transcript}"
        
        print(f"📩 WhatsApp message from {user_id}: {user_input}")
        
        result = await run_manager(user_input, user_id, image_urls=image_urls)
        
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
