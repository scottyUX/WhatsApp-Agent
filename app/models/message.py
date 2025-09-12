from typing import List, Optional
from fastapi.datastructures import FormData
import requests
import base64
from app.config.settings import settings

class TwilioWebhookData:
    def __init__(self, form: FormData):
        self.body = form.get("Body", "")
        self.from_number = form.get("From", "unknown_user")
        self.num_media = int(form.get("NumMedia", 0))
        self.form = form
    
    def get_image_urls(self) -> List[str]:
        image_urls = []
        auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
        for i in range(self.num_media):
            media_type = self.form.get(f"MediaContentType{i}")
            if media_type and media_type.startswith("image/"):
                image_url = self.form.get(f"MediaUrl{i}")
                response = requests.get(image_url, auth=auth)       
                encoded_image = base64.b64encode(response.content).decode('utf-8')
                encoded_url = f"data:image/jpeg;base64,{encoded_image}"
                image_urls.append(encoded_url)
        return image_urls
    
    def get_audio_urls(self) -> List[str]:
        audio_urls = []
        
        for i in range(self.num_media):
            media_type = self.form.get(f"MediaContentType{i}")
            if media_type and media_type.startswith("audio/"):
                audio_url = self.form.get(f"MediaUrl{i}")
                audio_urls.append(audio_url)
        return audio_urls

class Message:
    def __init__(self, content: str, user_id: str, image_urls: List[str] = None, audio_urls: List[str] = None):
        self.content = content
        self.user_id = user_id
        self.image_urls = image_urls or []
        self.audio_urls = audio_urls or []
