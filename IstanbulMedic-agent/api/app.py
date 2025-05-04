from fastapi import FastAPI, HTTPException
from twilio.rest import Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Twilio client with environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/send-sms/")
async def send_sms(to: str, body: str):
    try:
        message = client.messages.create(
            body=body,
            from_=os.getenv("TWILIO_PHONE_NUMBER"),
            to=to
        )
        return {"message_sid": message.sid}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/message")
async def send_whatsapp_message():
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body='Greetings from Istanbul Medic!',
            to='whatsapp:+18312959447'
        )
        return {"sid": message.sid}
    except Exception as error:
        print('Twilio error:', error)
        raise HTTPException(status_code=500, detail=str(error))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 