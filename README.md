# WhatsApp Medical Agent

A multilingual medical tourism assistant for IstanbulMedic that handles WhatsApp messages through Twilio webhooks.

## Technologies Used

- **FastAPI** - Web framework
- **OpenAI GPT-4** - Language detection and AI agents
- **Twilio** - WhatsApp integration
- **ElevenLabs** - Audio transcription
- **Python 3.12+** - Runtime

## Setup

1. **Clone and navigate to project**
   ```bash
   git clone <repo-url>
   cd WhatsApp-Agent
   ```

2. **Create Virtual Environment & Install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Required Environment Variables

```bash
# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=your_openai_key
VECTOR_STORE_EN=your_english_vector_store_id
VECTOR_STORE_DE=your_german_vector_store_id
VECTOR_STORE_ES=your_spanish_vector_store_id

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# Testing
TEST_PHONE_NUMBERS=whatsapp:+1234567890,whatsapp:+0987654321
```

## Run

```bash
cd app
python app.py
```

Server runs on `http://localhost:8000`

## API Endpoints

- `POST /api/webhook` - Twilio webhook for WhatsApp messages
- `GET /test/agent` - Test agent with sample data
- `GET /test/message` - Test sending WhatsApp message
- `GET /docs` - FastAPI auto-generated documentation

## Project Structure

```
app/
├── agents/           # AI agents (language & specialized)
├── config/           # Settings and configuration
├── models/           # Data models
├── routers/          # API route handlers
├── services/         # External service integrations
├── utils/            # Utility functions
└── app.py           # Main application
```

## Notes

- Supports English, German, and Spanish
- Handles text, image, and voice messages
- Uses vector stores for medical knowledge
- Image analysis for hair transplant consultations
