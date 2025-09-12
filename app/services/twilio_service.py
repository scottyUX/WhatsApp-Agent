from twilio.rest import Client
from fastapi import HTTPException
from app.config.settings import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    def send_message(self, to: str, body: str, media_url: str = None):
        try:
            message = self.client.messages.create(
                from_=settings.TWILIO_PHONE_NUMBER,
                body=body,
                media_url=media_url,
                to=to
            )
            return message.sid
        except Exception as error:
            raise HTTPException(status_code=500, detail=str(error))

twilio_service = TwilioService()
