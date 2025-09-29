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
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│              Message Service                                │
│  • Phone number processing                                 │
│  • SQLiteSession management                               │
│  • Message history formatting                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                Manager Agent                                │
│  • Intent detection and routing                            │
│  • Tool orchestration                                     │
│  • Context management                                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌───▼────┐ ┌──────▼──────┐
│ Scheduling   │ │ Image  │ │ Knowledge   │
│ Agent (Anna) │ │ Agent  │ │ Agent       │
└──────────────┘ └────────┘ └─────────────┘
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

### 3. Image Agent
**File**: `app/agents/specialized_agents/image_agent.py`

**Purpose**: Analyzes images for hair transplant consultations.

**Key Features**:
- Hair graft assessment
- Medical image analysis
- Professional consultation support

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

## Database Schema

### Messages Table
```sql
CREATE TABLE messages (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    direction VARCHAR(20) NOT NULL,
    body TEXT,
    media_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
```

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
