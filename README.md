# WhatsApp Medical Agent

A multilingual medical tourism assistant for IstanbulMedic that handles WhatsApp messages through Twilio webhooks, featuring a comprehensive consultant dashboard for patient management.

## Technologies Used

### Backend
- **FastAPI** - Web framework
- **OpenAI GPT-4** - Language detection and AI agents
- **Twilio** - WhatsApp integration
- **ElevenLabs** - Audio transcription
- **Python 3.12+** - Runtime
- **SQLAlchemy** - Database ORM
- **Supabase** - Database hosting

### Frontend
- **Next.js 15** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible components
- **React Query** - Data fetching

## Setup

### Backend Setup

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

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd istanbulmedic-website-fe
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   pnpm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env.local
   # Edit .env.local with your API endpoints
   ```

## Required Environment Variables

### Backend (.env)
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

# Database
DATABASE_URL=your_supabase_database_url

# Testing
TEST_PHONE_NUMBERS=whatsapp:+1234567890,whatsapp:+0987654321
```

### Frontend (.env.local)
```bash
# API Configuration
NEXT_PUBLIC_CHAT_SERVICE_BASE_URL=https://your-backend-url.vercel.app
NEXT_PUBLIC_API_BASE=https://your-backend-url.vercel.app
```

## Run

### Backend
```bash
cd app
python app.py
```
Backend server runs on `http://localhost:8000`

### Frontend
```bash
cd istanbulmedic-website-fe
npm run dev
# or
pnpm dev
```
Frontend runs on `http://localhost:3000`

## API Endpoints

### WhatsApp Integration
- `POST /api/webhook` - Twilio webhook for WhatsApp messages
- `GET /test/agent` - Test agent with sample data
- `GET /test/message` - Test sending WhatsApp message

### Consultant Dashboard
- `GET /api/patients/` - Get all patients
- `GET /api/patients/{patient_id}` - Get patient details
- `PUT /api/patients/{patient_id}` - Update patient profile
- `GET /api/consultations/today` - Get today's appointments

### Documentation
- `GET /docs` - FastAPI auto-generated documentation

## Project Structure

```
WhatsApp-Agent/
├── app/                          # Backend FastAPI application
│   ├── agents/                   # AI agents (language & specialized)
│   ├── config/                   # Settings and configuration
│   ├── database/                 # Database entities and migrations
│   ├── models/                   # Data models
│   ├── routers/                  # API route handlers
│   ├── services/                 # External service integrations
│   ├── utils/                    # Utility functions
│   └── app.py                    # Main application
├── istanbulmedic-website-fe/     # Frontend Next.js application
│   ├── src/
│   │   ├── app/                  # Next.js app router
│   │   │   └── consultant/       # Consultant dashboard pages
│   │   ├── components/           # React components
│   │   │   └── consultant/       # Consultant-specific components
│   │   │       ├── dashboard/    # Layout components
│   │   │       └── patient/      # Patient section components
│   │   ├── types/                # TypeScript type definitions
│   │   ├── services/             # API service layer
│   │   ├── hooks/                # Custom React hooks
│   │   ├── utils/                # Utility functions
│   │   └── constants/            # Application constants
│   └── package.json
└── docs/                         # Documentation
    └── CONSULTANT_DASHBOARD_REFACTOR_PLAN.md
```

## Features

### WhatsApp Integration
- Supports English, German, and Spanish
- Handles text, image, and voice messages
- Uses vector stores for medical knowledge
- Image analysis for hair transplant consultations

### Consultant Dashboard
- **Patient Management**: View and edit patient profiles
- **Appointment Scheduling**: Manage today's appointments
- **Medical Records**: Track medical history, allergies, and conditions
- **Hair Loss Profiles**: Document hair loss patterns and treatments
- **Consultation Status**: Track patient journey stages
- **Notes System**: Add and manage consultant notes
- **Real-time Updates**: Live data synchronization
- **Responsive Design**: Optimized for all screen sizes

### Architecture Highlights
- **Modular Components**: Reusable, maintainable React components
- **Type Safety**: Comprehensive TypeScript definitions
- **Clean Data Layer**: Centralized API service and state management
- **Validation**: Client-side form validation with error handling
- **Accessibility**: Radix UI components for screen reader support

## Deployment

### Backend
Deployed on Vercel with automatic deployments from main branch.

### Frontend
Deployed on Vercel with automatic deployments from main branch.

## Development Notes

- Backend and frontend are separate applications with independent deployments
- Frontend is a git submodule within the main repository
- All consultant dashboard functionality is fully integrated and production-ready
