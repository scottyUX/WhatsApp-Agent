import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import asyncio
import requests
import base64
#from agent.supervisor import supervisor_agent, Runner
from agent.manager_agent import run_manager
from data.handle_twilio import handle_image_urls,handle_audio_urls
from data.caching import add_to_cache, get_from_cache, clear_cache
# Load environment variables from .env file
load_dotenv()

# Initialize Twilio client with environment variables
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)
print("client", client)
user_tasks = {}
user_locks = {} 

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
        image_urls = handle_image_urls(form)
        audio_urls = handle_audio_urls(form)

        await add_to_cache(user_id, image_urls, "image")
        await add_to_cache(user_id, audio_urls, "audio")


        if user_id in user_tasks and not user_tasks[user_id].done():
            print(f"🔄 Cancelling previous task for {user_id}...")
        else:
            print("Task created")
            async def wrapped():
                await process_user_requests(user_id, user_input)
            task = asyncio.create_task(wrapped())
            user_tasks[user_id] = task

        xml_response = f"""
        <Response>
            <Message>İsteğiniz İşleniyor...</Message>
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

async def process_user_requests(user_id, user_input):
    if user_id not in user_locks:
        user_locks[user_id] = asyncio.Lock()
    
    async with user_locks[user_id]:
        try:
            print(f"🔄 Processing requests for {user_id}...")
            await asyncio.sleep(1)

            cached_images = await get_from_cache(user_id, "image")
            cached_audios = await get_from_cache(user_id, "audio")

            combined_images = [img for _, img in cached_images]
            combined_audios = [audio for _, audio in cached_audios]

            print(f"🖼️ Combined images: {combined_images}")
            print(f"🎵 Combined audio: {combined_audios}")

            result = await run_manager(user_input, user_id, image_urls=combined_images)

            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=result,
                to=user_id
            )
            
            print(f"✅ Message sent to {user_id}: {result}")

        except asyncio.CancelledError as e:
            print(f"⏹️ Task for {user_id} was cancelled: {e}")
        except Exception as e:
            print(f"❌ Error processing requests for {user_id}: {e}")
        finally:
            clear_cache(user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 
