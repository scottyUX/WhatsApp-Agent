from fastapi import FastAPI, Request, Response
from agent.manager_agent import run_manager
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

@app.get("/")
async def root():
    return {"status": "App is running ✅"}

from fastapi import FastAPI, Response
from agent.manager_agent import run_manager

app = FastAPI()

@app.get("/api/istanbulMedic-agent")
async def istanbulMedic_agent():
    try:
        # 🔧 Hardcoded test input
        user_input = "Good morning, I am interested in hair transplantation."
        user_id = "test_user"

        print(f"📩 Testing message from {user_id}: {user_input}")

        result = await run_manager(user_input, user_id)
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
            <Message>Üzgünüz, bir hata oluştu. Lütfen tekrar deneyin.</Message>
        </Response>
        """
        return Response(content=error_response.strip(), media_type="text/xml")

