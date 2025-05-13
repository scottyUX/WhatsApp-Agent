import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, Request, Response
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import asyncio
import requests
import base64
#from agent.supervisor import supervisor_agent, Runner
from agent.manager_agent import run_manager
# Load environment variables from .env file
load_dotenv()

# Initialize Twilio client with environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
print("client", client)

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Hello": "World"}


    
@app.get("/api/istanbulMedic-agent")
async def istanbulMedic_agent():
    print("istanbulMedic_agent")
    try:
        # 🔧 Hardcoded test input
        user_input = "Good morning, I am interested in hair transplantation."
        user_id = "test_user"
        #If image url is none it use other agents. If not none it uses image agent.
        image_url = "https://pedmer.com.tr/wp-content/uploads/2022/09/sac_ekimi.jpg"

        print(f"📩 Testing message from {user_id}: {user_input}")

        result = await run_manager(user_input, user_id, image_url=image_url)
        print(result)

        xml_response = f"""
        <Response>
            <Message>{result}</Message>
        </Response>
        """
        return Response(content=xml_response.strip(), media_type="text/xml")

    except Exception as e:
        print(f"❌ Error: {e}")
        error_response = """
        <Response>
            <Message>Üzgünüz, bir hata oluştu. Lütfen tekrar deneyin2.</Message>
        </Response>
        """
        return Response(content=error_response.strip(), media_type="text/xml")

@app.get("/api/message")
async def send_whatsapp_message():
    try:
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body='Greetings from Istanbul Medic!',
            media_url= 'https://raw.githubusercontent.com/dianephan/flask_upload_photos/main/UPLOADS/DRAW_THE_OWL_MEME.png',
            to='whatsapp:+905538589024'
        )
        return {"sid": message.sid}
    except Exception as error:
        print('Twilio error:', error)
        raise HTTPException(status_code=500, detail=str(error))


    
@app.post("/api/webhook")
async def istanbulMedic_agent(request: Request):
    try:
        form = await request.form()
        print("form", form)
        user_input = form.get("Body", "")
        user_id = form.get("From", "unknown_user")
        
        media_num = int(form.get("NumMedia",0))
        image_url = None
        for i in range(media_num):
            media_type = form.get(f"MediaContentType{i}")
            if media_type.startswith("image/"):
                image_url = form.get(f"MediaUrl{i}")
                break
        
        data_url = None 
        if image_url:
            print("Image getting requested")
            auth = (account_sid, auth_token)
            response = requests.get(image_url, auth=auth)       
            encoded_image = base64.b64encode(response.content).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{encoded_image}"
            print("Image request is succesful: ",data_url)

        print(image_url)
        print(f"📩 WhatsApp message from {user_id}: {user_input}")

        result = await run_manager(user_input, user_id,image_url=data_url)

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
            <Message>Üzgünüz, bir hata oluştu. Lütfen tekrar deneyin.</Message>
        </Response>
        """.strip(), media_type="text/xml")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
