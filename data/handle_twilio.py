from fastapi.datastructures import FormData
from dotenv import load_dotenv
import os
import base64
import requests
load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
auth = (account_sid, auth_token)

def handle_image_urls(form: FormData) -> list:
    media_num = int(form.get("NumMedia",0))
    image_urls = []
    for i in range(media_num):
        media_type = form.get(f"MediaContentType{i}")
        if media_type.startswith("image/"):
            image_url = form.get(f"MediaUrl{i}")
            response = requests.get(image_url, auth=auth)       
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            encoded_url = f"data:image/jpeg;base64,{encoded_image}"
            image_urls.append(encoded_url)
    return image_urls

def handle_audio_urls(form: FormData) -> list:
    media_num = int(form.get("NumMedia",0))
    audio_urls = []
    for i in range(media_num):
        media_type = form.get(f"MediaContentType{i}")
        if media_type.startswith("audio/"):
            audio_url = form.get(f"MediaUrl{i}")
            response = requests.get(audio_url, auth=auth)       
            encoded_audio = base64.b64encode(response.content).decode('utf-8')
            encoded_url = f"data:audio/mpeg;base64,{encoded_audio}"
            audio_urls.append(encoded_url)
    return audio_urls