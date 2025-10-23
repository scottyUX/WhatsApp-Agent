# System Architecture Documentation

## Overview

The WhatsApp Medical Agent system uses a simplified multi-agent architecture with a Manager pattern, where specialized agents are exposed as tools rather than using complex handoff mechanisms.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    WhatsApp User                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 Twilio Webhook                              │
│              POST /api/webhook                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Message Service                                │
│  • Phone number processing                                 │
│  • Database integration (PostgreSQL)                      │
│  • Message history formatting                             │
│  • Session memory management                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Manager Agent                                │
│  • Intent detection and routing                            │
│  • Tool orchestration                                     │
│  • Context management                                     │
│  • Legacy compatibility (run_manager_legacy)              │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
│ Scheduling   │ │ Image  │ │ Knowledge   │
│ Agent (Anna) │ │ Agent  │ │ Agent       │
└──────────────┘ └────────┘ └─────────────┘
        │
        │
┌───────▼────────────┐
│ Image Analysis API │
│ (multi-image GPT)  │
└────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    Chat Users                               │
│              (Website Integration)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Chat Endpoints                               │
│              POST /chat/                                    │
│              POST /chat/stream                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Message Service                                │
│  • User management (chat_{user_id})                        │
│  • Database integration (PostgreSQL)                      │
│  • Streaming response support                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Manager Agent                                │
│  • Same agent logic as WhatsApp                            │
│  • No session memory for chat                              │
└─────────────────────┬───────────────────────────────────────┘
```

## Core Components

### 1. Manager Agent
**File**: `app/agents/manager_agent.py`

**Purpose**: Central orchestrator that routes user queries to appropriate specialized agents.

**Key Features**:
- Intent detection and routing
- Tool-based agent integration
- Context management
- Session memory integration

**Tools Available**:
- `scheduling_expert` - Anna for consultation scheduling
- `image_expert` - Image analysis for hair transplant assessment
- `knowledge_expert` - General information about Istanbul Medic

### 2. Scheduling Agent (Anna)
**File**: `app/agents/specialized_agents/scheduling_agent.py`

**Purpose**: Handles consultation scheduling, appointment management, and patient information collection.

**Key Features**:
- Phone number validation with libphonenumber
- Appointment CRUD operations
- Patient questionnaire system
- Google Calendar integration

### 3. Image Agent & Analysis Service
**Files**: 
- `app/agents/specialized_agents/image_agent.py`
- `app/routers/image_analysis_router.py`
- `app/services/report_generation_service.py`

**Purpose**: Downloads Supabase-hosted photos, calls the enhanced GPT agent, and produces structured reports (JSON + optional PDF).

**Key Features**:
- Multi-image analysis with Norwood staging, graft estimates, donor assessment
- Supabase storage integration for signed/public URLs
- Optional PDF and HTML report generation
- Health endpoint for observability

### 4. Knowledge Agent
**File**: `app/agents/language_agents/english_agent.py`

**Purpose**: Provides general information about Istanbul Medic services and procedures.

**Key Features**:
- FAQ responses
- Service information
- Procedure details
- Company information

## Data Flow

### 1. Message Reception
```
WhatsApp → Twilio Webhook → Message Service → Manager Agent
```

### 2. Intent Detection
```
User Input → Manager Agent → Tool Selection → Specialized Agent
```

### 3. Response Generation
```
Specialized Agent → Manager Agent → Message Service → Twilio → WhatsApp
```

## Session Management

### SQLiteSession Implementation
**File**: `app/services/message_service.py`

**Purpose**: Maintains conversation context across multiple turns.

**Key Features**:
- User-specific session storage
- Conversation history persistence
- Context maintenance
- Local SQLite database

**Session ID Format**: `wa_{clean_phone_number}`

**Database**: `conversations.db`

## Phone Validation

### libphonenumber Integration
**File**: `utils/validators.py`

**Purpose**: Robust international phone number validation.

**Key Features**:
- E.164 formatting
- Country code validation
- Mobile number detection
- Landline rejection for SMS

**Validation Rules**:
- Must include country code
- Minimum 10 digits total
- Mobile numbers only for SMS
- International format support

## Appointment Management

### Google Calendar Integration
**File**: `app/tools/google_calendar_tools.py`

**Purpose**: Full CRUD operations for consultation appointments.

**Available Operations**:
- `create_calendar_event` - Book new appointments
- `list_upcoming_events` - View appointments
- `reschedule_event` - Change appointment times
- `delete_event` - Cancel appointments
- `reschedule_event_by_title` - Reschedule by name
- `delete_event_by_title` - Cancel by name

## Media & Storage Services

### Patient Image Service
**Files**: 
- `app/services/patient_image_service.py`
- `app/services/supabase_storage_service.py`
- `app/routers/patient_image_router.py`

**Responsibilities**:
- Enforce 3–6 image upload rule per submission
- Validate patient existence before storing photos
- Upload files to Supabase buckets (public or signed URLs)
- Return normalized URLs to the frontend

**Workflow**:
```
Frontend Upload → /api/patient-images → Supabase Storage → DB patient_image_submissions
```

### Supabase Storage Configuration
- Environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_KEY`, `SUPABASE_IMAGE_BUCKET`
- Optional flags: `SUPABASE_BUCKET_IS_PUBLIC`, `SUPABASE_SIGNED_URL_TTL`
- Uses Supabase Python v2 client with `ClientOptions` to set auth headers

## Clinic & Package Management

### REST Layer
**Files**:
- `app/routers/clinic_router.py`
- `app/routers/package_router.py`
- `app/routers/patient_router.py` (offers endpoint)

**Capabilities**:
- Paginated clinic listing with contract filter
- Clinic detail + package expansion
- Assign/reassign packages to clinics (`PUT /api/clinics/{id}/packages`)
- Partial updates for clinic metadata (`PATCH /api/clinics/{id}`)
- CRUD for packages (create, list, patch)
- Append clinic offers to patient profiles (`POST /api/patients/{id}/offers`)

### Repositories & Services
**Files**:
- `app/database/repositories/clinic_repository.py`
- `app/database/repositories/package_repository.py`
- `app/database/repositories/patient_profile_repository.py`
- `app/database/repositories/patient_image_submission_repository.py`

Repositories encapsulate Supabase/Postgres access and keep routing logic thin.

## Database Schema

### Current Implementation (Simplified)
In addition to the `messages` table, the system now persists:

#### `patient_image_submissions`
```sql
CREATE TABLE patient_image_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id),
    image_urls TEXT[] NOT NULL,
    analysis_notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE INDEX idx_patient_image_submissions_profile_id
    ON patient_image_submissions (patient_profile_id);
```

#### `packages` / `clinic_packages` / clinic extensions
```sql
CREATE TABLE packages (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    price NUMERIC(12,2),
    currency TEXT NOT NULL DEFAULT 'USD',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now())
);

CREATE TABLE clinic_packages (
    clinic_id UUID NOT NULL REFERENCES clinics(id) ON DELETE CASCADE,
    package_id UUID NOT NULL REFERENCES packages(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT timezone('utc', now()),
    PRIMARY KEY (clinic_id, package_id)
);

ALTER TABLE clinics
    ADD COLUMN IF NOT EXISTS has_contract BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS package_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];

ALTER TABLE patient_profiles
    ADD COLUMN IF NOT EXISTS clinic_offer_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];
```

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    direction VARCHAR(20) NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
    body TEXT,
    media_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### User Types
- **WhatsApp Users**: `phone_number` = actual phone number (e.g., `+1234567890`)
- **Chat Users**: `phone_number` = `chat_{user_id}` format (e.g., `chat_user_123`)

### Database Integration
- **Primary Database**: PostgreSQL (Supabase)
- **Session Storage**: SQLite (local, for WhatsApp conversations only)
- **Connection Pooling**: StaticPool with pre-ping enabled
- **Foreign Keys**: Enforced with SET NULL on delete

## Configuration

### Environment Variables
```bash
# OpenAI
OPENAI_API_KEY=your_openai_key

# Twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+14155238886

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=your_calendar_id

# Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# Phone Validation
DEFAULT_PHONE_REGION=US
REQUIRE_MOBILE_NUMBERS=true
```

## Security Considerations

### Input Validation
- Phone number validation with libphonenumber
- Email format validation
- Name sanitization
- XSS prevention

### Data Protection
- SQLite session encryption
- Secure API key management
- Input sanitization
- Error message sanitization

### Privacy
- User data encryption
- Session isolation
- Secure message storage
- GDPR compliance considerations

## Performance Considerations

### Caching
- Session data caching
- API response caching
- Database connection pooling

### Scalability
- Stateless agent design
- Horizontal scaling support
- Database optimization
- API rate limiting

## Monitoring and Logging

### Application Logs
- Request/response logging
- Error tracking
- Performance metrics
- User interaction logs

### Health Checks
- Database connectivity
- API service availability
- Calendar integration status
- Phone validation service

## Deployment Architecture

### Production Environment
- **Web Server**: Vercel (serverless)
- **Database**: Supabase (PostgreSQL)
- **Session Storage**: Local SQLite
- **File Storage**: Vercel Blob

### Development Environment
- **Local Server**: FastAPI development server
- **Database**: Local PostgreSQL
- **Session Storage**: Local SQLite
- **File Storage**: Local filesystem

## Error Handling

### Graceful Degradation
- Fallback responses for API failures
- Graceful handling of validation errors
- User-friendly error messages
- Escalation to human coordinators

### Error Recovery
- Automatic retry mechanisms
- Circuit breaker patterns
- Fallback service providers
- Manual intervention triggers

## Testing Strategy

### Unit Tests
- Individual component testing
- Mock external dependencies
- Validation logic testing
- Error handling verification

### Integration Tests
- End-to-end workflow testing
- API integration testing
- Database interaction testing
- Session management testing

### End-to-End Tests
- Full user journey testing
- WhatsApp integration testing
- Calendar integration testing
- Phone validation testing

## Maintenance

### Code Quality
- Automated linting
- Type checking
- Code coverage monitoring
- Security scanning

### Documentation
- API documentation
- Architecture documentation
- Deployment guides
- Troubleshooting guides

### Updates
- Dependency updates
- Security patches
- Feature enhancements
- Performance optimizations

---

*Last updated: September 2025*
*Version: 1.0*
