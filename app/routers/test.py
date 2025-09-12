from fastapi import APIRouter, Response
from app.services.twilio_service import twilio_service
from app.agents.manager_agent import run_manager
from app.config.settings import settings

router = APIRouter(prefix="/test", tags=["testing"])

@router.get("/agent")
async def test_agent():
    """Test endpoint with hardcoded values for development"""
    print("Testing agent with hardcoded values")
    try:
        user_input = "Good morning, I am interested in hair transplantation."
        user_id = "test_user"
        image_url = "https://pedmer.com.tr/wp-content/uploads/2022/09/sac_ekimi.jpg"

        print(f"📩 Testing message from {user_id}: {user_input}")

        result = await run_manager(user_input, user_id, image_urls=[image_url])
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
            <Message>Sorry, an error occurred. Please try again.</Message>
        </Response>
        """
        return Response(content=error_response.strip(), media_type="text/xml")


@router.get("/message")
async def test_send_message():
    """Test sending a WhatsApp message"""
    try:
        for test_number in settings.TEST_PHONE_NUMBERS:
            message_sid = twilio_service.send_message(
                to=test_number,
                body='Greetings from Istanbul Medic!',
                media_url='https://raw.githubusercontent.com/dianephan/flask_upload_photos/main/UPLOADS/DRAW_THE_OWL_MEME.png'
            )
        return {"sid": message_sid, "status": "sent"}
    except Exception as e:
        return {"error": str(e)}
