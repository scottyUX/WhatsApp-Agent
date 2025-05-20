import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi import FastAPI, HTTPException, Request, Response, BackgroundTasks
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import asyncio
import time
#from agent.supervisor import supervisor_agent, Runner
from agent.manager_agent import run_manager
from data.handle_twilio import handle_image_urls,handle_audio_urls
from data.caching.redis_client import add_media_to_cache,add_text_to_cache, get_from_redis_cache,get_media_from_redis_cache,clear_redis_cache,get_redis_media_counter
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
        image_urls = handle_image_urls(form)
        audio_urls = handle_audio_urls(form)

        add_media_to_cache(user_id, image_urls, "image")
        add_media_to_cache(user_id, audio_urls, "audio")
        add_text_to_cache(user_id, [user_input], "text")
        media_count_old = get_redis_media_counter(user_id)
        
        await asyncio.sleep(2)
        media_count_new = get_redis_media_counter(user_id)
        
        if media_count_new == media_count_old:
            cached_images = get_media_from_redis_cache(user_id, "image")
            cached_audios = get_media_from_redis_cache(user_id, "audio")
            cached_texts = "".join(get_from_redis_cache(user_id, "text"))
            print("cached_texts", cached_texts)
            print("cached_images", cached_images)

            result = await run_manager(cached_texts, user_id, image_urls=cached_images)

            message = client.messages.create(
                from_='whatsapp:+14155238886',
                body=result,
                to=user_id
            )
            
            xml_response = f"""
            <Response>
                <Message>{result}</Message>
            </Response>
            """
            return Response(content=xml_response.strip(), media_type="text/xml")

        else:
            return Response(content="<Response></Response>", media_type="text/xml")

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
