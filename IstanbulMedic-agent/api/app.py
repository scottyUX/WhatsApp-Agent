import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, Request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import asyncio
from agent.supervisor import supervisor_agent, Runner

# Load environment variables from .env file
load_dotenv()

# Initialize Twilio client with environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

app = FastAPI()

GOOD_BOY_URL = (
    "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?ixlib=rb-1.2.1"
    "&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=1350&q=80"
)

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
            media_url= 'https://raw.githubusercontent.com/dianephan/flask_upload_photos/main/UPLOADS/DRAW_THE_OWL_MEME.png',
            to='whatsapp:+18312959447'
        )
        return {"sid": message.sid}
    except Exception as error:
        print('Twilio error:', error)
        raise HTTPException(status_code=500, detail=str(error))

from fastapi import Request, Response
from agents import Runner, supervisor_agent  # adjust as needed
import httpx

@app.post("/api/istanbulMedic-agent")
async def istanbulMedic_agent(request: Request):
    try:
        # Parse the form data sent by Twilio
        form_data = await request.form()
        user_input = form_data.get("Body", "")
        num_media = int(form_data.get("NumMedia", "0"))

        image_url = None
        if num_media > 0:
            image_url = form_data.get("MediaUrl0")
            content_type = form_data.get("MediaContentType0")
            # Optionally: Download the image if needed
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                image_bytes = response.content  # you can pass this to your agent

            # You can now pass the image to the agent however needed:
            # Example: augment the input
            user_input += "\n[Image attached]"

        # Call the agent with user_input and optionally the image
        result = await Runner.run(supervisor_agent, user_input)

        # Respond with TwiML
        xml_response = f"""
        <Response>
            <Message>{result.final_output}</Message>
        </Response>
        """
        return Response(content=xml_response, media_type="text/xml")

    except Exception as e:
        print(f"Error: {e}")
        error_response = """
        <Response>
            <Message>Üzgünüz, bir hata oluştu.</Message>
        </Response>
        """
        return Response(content=error_response, media_type="text/xml")


@app.post("api/image-reply")
async def image_reply(request: Request):
    form_data = await request.form()
    try:
        num_media = int(form_data.get("NumMedia", 0))
    except (ValueError, TypeError):
        return Response(content="Invalid request: invalid or missing NumMedia parameter", status_code=400)

    response = MessagingResponse()
    if not num_media:
        msg = response.message("Send us an image!")
    else:
        msg = response.message("Thanks for the image. Here's one for you!")
        msg.media(GOOD_BOY_URL)

    return Response(content=str(response), media_type="application/xml")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 