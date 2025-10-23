# API Reference

## Overview

The WhatsApp Medical Agent provides REST API endpoints for webhook integration, testing, and health monitoring.

## Base URL

- **Production**: `https://your-vercel-app.vercel.app`
- **Development**: `http://localhost:8000`

## Authentication

No authentication required for webhook endpoints. API keys are managed through environment variables.

## Endpoints

### Webhook Endpoints

#### POST /api/webhook
**Purpose**: Twilio webhook endpoint for incoming WhatsApp messages.

**Request Body** (form-encoded):
```
From=+1234567890&Body=Hello, I'd like to schedule a consultation&MediaUrl0=https://example.com/image.jpg&NumMedia=1
```

**Response** (XML):
```xml
<Response>
    <Message>Hello! I'm Anna, your consultation assistant...</Message>
</Response>
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

### Chat Endpoints

#### POST /chat/
**Purpose**: Direct chat integration for website users.

**Request Body** (JSON):
```json
{
  "content": "Hello, I want to schedule an appointment",
  "media_urls": [],
  "audio_urls": []
}
```

**Response** (JSON):
```json
{
  "content": "Hello! I'm Anna, your consultation assistant..."
}
```

**Status Codes**:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

#### POST /chat/stream
**Purpose**: Streaming chat integration for real-time responses using Server-Sent Events (SSE).

**Request Body** (JSON):
```json
{
  "content": "I need help with my medical consultation",
  "media_urls": [],
  "audio_urls": []
}
```

**Response** (Server-Sent Events):
```
data: {"content": "Hello! I'm Anna, your consultation assistant...", "timestamp": "2025-10-01T14:24:19.941641", "is_final": false}

data: {"content": "", "timestamp": "2025-10-01T14:24:19.941881", "is_final": true}
```

**Response Format**:
- **Content-Type**: `text/plain; charset=utf-8`
- **Transfer-Encoding**: `chunked`
- **Cache-Control**: `no-cache`
- **Connection**: `keep-alive`

**Status Codes**:
- `200` - Success
- `400` - Bad Request
- `500` - Internal Server Error

### Test Endpoints

#### GET /test/agent
**Purpose**: Test the agent system with sample data.

**Query Parameters**:
- `message` (optional): Test message to send to agent
- `phone` (optional): Test phone number

**Example**:
```
GET /test/agent?message=Hi, I want to schedule a consultation&phone=+1234567890
```

**Response**:
```json
{
  "response": "Hello! I'm Anna, your consultation assistant...",
  "agent": "scheduling_expert",
  "session_id": "wa_1234567890"
}
```

#### GET /test/message
**Purpose**: Test sending a WhatsApp message through Twilio.

**Query Parameters**:
- `to` (required): Recipient phone number
- `message` (required): Message to send

**Example**:
```
GET /test/message?to=+1234567890&message=Test message
```

**Response**:
```json
{
  "success": true,
  "message_sid": "SM1234567890abcdef",
  "status": "queued"
}
```

### Health Check Endpoints

#### GET /health
**Purpose**: Basic health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-22T10:30:00Z",
  "version": "1.0.0"
}
```

#### GET /health/detailed
**Purpose**: Detailed health check with service status.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-09-22T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "openai": "healthy",
    "twilio": "healthy",
    "calendar": "healthy"
  }
}
```

### Patient Image Endpoints

#### POST /api/patient-images/
**Purpose**: Upload a bundle of patient photos to Supabase storage and persist metadata.

**Request**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patient_profile_id` | UUID | ✅ | Patient profile identifier associated with the images |
| `files` | File[] | ✅ (3–6 files) | Between three and six image files (`.jpg`, `.png`, `.webp`, `.gif`) |
| `analysis_notes` | string | ❌ | Optional consultant notes about the upload |

**Response** (`200 OK`):
```json
{
  "id": "7b652aa2-7d3a-45e7-9c6f-2b4c22d9ae2c",
  "patient_profile_id": "ef21fa6d-0b40-40bc-b84a-1d2d5aacc902",
  "image_urls": [
    "https://xyz.supabase.co/storage/v1/object/public/istanbulmedic_patient_images/ef21fa6d-.../photo_1.jpg",
    "https://xyz.supabase.co/storage/v1/object/public/istanbulmedic_patient_images/ef21fa6d-.../photo_2.jpg"
  ],
  "analysis_notes": "Frontal and crown coverage requested",
  "created_at": "2025-10-23T20:18:11.229Z",
  "updated_at": "2025-10-23T20:18:11.229Z"
}
```

**Status Codes**:
- `200` - Upload succeeded
- `400` - Invalid UUID, missing files, or incorrect image count
- `404` - Patient profile not found
- `500` - Internal error (Supabase/storage failure)

#### GET /api/patient-images/
**Purpose**: List patient image submissions.

**Query Parameters**:
- `patient_profile_id` _(optional)_ — filter submissions to a specific patient

**Response** (`200 OK`):
```json
[
  {
    "id": "7b652aa2-7d3a-45e7-9c6f-2b4c22d9ae2c",
    "patient_profile_id": "ef21fa6d-0b40-40bc-b84a-1d2d5aacc902",
    "image_urls": [
      "https://xyz.supabase.co/storage/v1/object/public/istanbulmedic_patient_images/..."
    ],
    "analysis_notes": null,
    "created_at": "2025-10-23T20:18:11.229Z",
    "updated_at": "2025-10-23T20:18:11.229Z"
  }
]
```

### Image Analysis Endpoints

#### POST /api/image-analysis/analyze
**Purpose**: Run a comprehensive AI analysis over patient scalp photos.

**Request Body**:
```json
{
  "image_urls": [
    "https://xyz.supabase.co/storage/v1/object/public/istanbulmedic_patient_images/.../1.jpg",
    "https://xyz.supabase.co/storage/v1/object/public/istanbulmedic_patient_images/.../2.jpg"
  ],
  "patient_id": "ef21fa6d-0b40-40bc-b84a-1d2d5aacc902",
  "analysis_type": "comprehensive",
  "include_pdf": false
}
```

**Response** (`200 OK`):
```json
{
  "success": true,
  "report_id": "f05b010d-5bde-4c7b-8d63-7a9c739f1d8c",
  "data": {
    "report_id": "f05b010d-5bde-4c7b-8d63-7a9c739f1d8c",
    "timestamp": "2025-10-23T21:02:44.734Z",
    "patient_id": "ef21fa6d-0b40-40bc-b84a-1d2d5aacc902",
    "analysis_type": "comprehensive",
    "images_analyzed": 2,
    "image_urls": ["https://...", "https://..."],
    "analysis": {
      "analysis": "Verbose surgical assessment...",
      "norwood_scale": "5-6",
      "graft_estimate": { "min": 3200, "max": 4400 },
      "cost_estimate": { "min": 1800, "max": 3200, "currency": "USD" },
      "recommendations": ["..."],
      "procedure_type": "FUE/DHI",
      "expected_timeline": "12-18 months for full results"
    }
  }
}
```

**Status Codes**:
- `200` - Success
- `400` - Missing/too many image URLs
- `500` - Agent failure or PDF generation error

Additional routes:
- `POST /api/image-analysis/analyze/quick` — shorthand for `analysis_type="quick"`
- `POST /api/image-analysis/generate-pdf` — returns a PDF stream (`Content-Type: application/pdf`)
- `GET /api/image-analysis/health` — service health probe

### Clinic Management Endpoints

#### GET /api/clinics/
**Purpose**: Paginated clinic listing with optional contract filtering.

**Query Parameters**:
- `page` _(default 1)_
- `limit` _(default 20, max 100)_
- `hasContract` _(optional boolean)_ — filter contracted clinics

**Response**:
```json
{
  "clinics": [
    {
      "id": "f5690c1b-b1c3-4b5d-9c2d-86c2b3c5bd68",
      "title": "Istanbul Medic - Central Hospital",
      "location": "Istanbul",
      "city": "Istanbul",
      "country": "Turkey",
      "packageIds": ["bc90f050-..."],
      "hasContract": true,
      "packages": [
        {
          "id": "bc90f050-...",
          "name": "Premium Hair Transplant",
          "currency": "USD",
          "price": "2500.00",
          "is_active": true,
          "created_at": "2025-10-20T10:41:31.129Z",
          "updated_at": "2025-10-20T10:41:31.129Z"
        }
      ],
      "created_at": "2025-10-18T09:25:57.412Z",
      "updated_at": "2025-10-19T14:07:13.018Z"
    }
  ],
  "total": 12,
  "page": 1,
  "limit": 20,
  "total_pages": 1
}
```

#### GET /api/clinics/{clinic_id}
Returns a single clinic with package metadata. Responds with `404` if the clinic does not exist or `400` for malformed UUIDs.

#### PUT /api/clinics/{clinic_id}/packages
**Purpose**: Overwrite the packages assigned to a clinic.

**Request Body**:
```json
{
  "packageIds": [
    "bc90f050-5f34-4e7d-9bc3-ef0c9b4b1234",
    "76ad0ade-21c8-4017-a54a-2144c663c111"
  ],
  "hasContract": true
}
```

**Response**: Updated clinic object (same shape as GET). Missing packages produce `404`.

#### PATCH /api/clinics/{clinic_id}
Allows partial updates to mutable clinic fields (contact info, metadata, contract flag, etc.). Unknown fields trigger `400`.

### Package Management Endpoints

#### GET /api/packages/
Returns all packages. Use `include_inactive=true` to include archived offerings.

**Response**:
```json
{
  "packages": [
    {
      "id": "bc90f050-5f34-4e7d-9bc3-ef0c9b4b1234",
      "name": "Premium Hair Transplant",
      "description": "All-inclusive stay + surgery",
      "price": "2500.00",
      "currency": "USD",
      "is_active": true,
      "created_at": "2025-10-20T10:41:31.129Z",
      "updated_at": "2025-10-20T10:41:31.129Z"
    }
  ],
  "total": 1
}
```

#### POST /api/packages/
Creates a new reusable package.

**Request Body**:
```json
{
  "name": "Deluxe Hair Transplant",
  "description": "3-night stay, PRP, VIP transfers",
  "price": 2800,
  "currency": "USD",
  "is_active": true
}
```

**Response** (`201 Created`): Package object. Attempts to attach to inherited clinic relationships may trigger validation errors if the schema is out of sync.

#### PATCH /api/packages/{package_id}
Partial update for a package (e.g., deactivate, adjust pricing). Unknown IDs return `404`.

### Patient Offer Management

#### POST /api/patients/{patient_id}/offers
**Purpose**: Append clinic offers to a patient profile.

**Request Body**:
```json
{
  "clinicIds": [
    "f5690c1b-b1c3-4b5d-9c2d-86c2b3c5bd68",
    "b84fcb7c-9a7d-4c63-9af7-1ec889cd8af0"
  ]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Clinic offers updated successfully",
  "data": {
    "id": "ef21fa6d-0b40-40bc-b84a-1d2d5aacc902",
    "clinicOffers": [
      "f5690c1b-b1c3-4b5d-9c2d-86c2b3c5bd68",
      "b84fcb7c-9a7d-4c63-9af7-1ec889cd8af0"
    ]
  }
}
```

**Status Codes**:
- `200` - Success
- `400` - Invalid request payload
- `404` - Patient or clinic IDs not found

## Data Models

### Message
```typescript
interface Message {
  id: string;
  user_id: string;
  direction: "incoming" | "outgoing";
  body: string;
  media_url?: string;
  created_at: string;
}
```

### User
```typescript
interface User {
  id: string;
  phone_number: string;
  created_at: string;
}
```

### Appointment
```typescript
interface Appointment {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  description?: string;
  meet_link?: string;
}
```

## Error Responses

### Standard Error Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid phone number format",
    "details": {
      "field": "phone_number",
      "value": "+1234",
      "expected_format": "+1 415 555 2671"
    }
  }
}
```

### Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Input validation failed | 400 |
| `PHONE_INVALID` | Invalid phone number format | 400 |
| `EMAIL_INVALID` | Invalid email format | 400 |
| `APPOINTMENT_NOT_FOUND` | Appointment not found | 404 |
| `CALENDAR_ERROR` | Calendar integration error | 500 |
| `OPENAI_ERROR` | OpenAI API error | 500 |
| `TWILIO_ERROR` | Twilio API error | 500 |
| `INTERNAL_ERROR` | Internal server error | 500 |

## Rate Limiting

### Webhook Endpoints
- **Rate Limit**: 100 requests per minute per IP
- **Burst Limit**: 10 requests per second
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

### Test Endpoints
- **Rate Limit**: 10 requests per minute per IP
- **Purpose**: Prevent abuse during testing

## Webhook Security

### Twilio Signature Verification
All webhook requests are verified using Twilio's signature validation:

```python
from twilio.request_validator import RequestValidator

validator = RequestValidator(auth_token)
is_valid = validator.validate(
    request_url,
    request_params,
    signature
)
```

### Request Validation
- **Method**: POST only
- **Content-Type**: `application/x-www-form-urlencoded`
- **Required Fields**: `From`, `Body`
- **Optional Fields**: `MediaUrl0`, `NumMedia`

## Testing

### Webhook Testing with ngrok
```bash
# Install ngrok
npm install -g ngrok

# Start local server
python app/app.py

# Expose local server
ngrok http 8000

# Use ngrok URL in Twilio webhook configuration
```

### cURL Examples

#### Test Webhook
```bash
curl -X POST "http://localhost:8000/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Hello, I want to schedule a consultation"
```

#### Test Agent
```bash
curl "http://localhost:8000/test/agent?message=Hi&phone=+1234567890"
```

#### Test Message Sending
```bash
curl "http://localhost:8000/test/message?to=+1234567890&message=Test message"
```

## Monitoring

### Metrics
- **Request Count**: Total webhook requests
- **Response Time**: Average response time
- **Error Rate**: Percentage of failed requests
- **Agent Usage**: Which agents are being used

### Logs
- **Request Logs**: All incoming webhook requests
- **Response Logs**: All outgoing responses
- **Error Logs**: Detailed error information
- **Agent Logs**: Agent decision making process

### Alerts
- **High Error Rate**: > 5% error rate
- **Slow Response**: > 5 second response time
- **Service Down**: Health check failures
- **Rate Limit Exceeded**: Too many requests

## SDK Examples

### Python
```python
import requests

# Send test message
response = requests.post(
    "http://localhost:8000/api/webhook",
    data={
        "From": "whatsapp:+1234567890",
        "Body": "Hello, I want to schedule a consultation"
    }
)

print(response.json())
```

### JavaScript
```javascript
// Send test message
const response = await fetch('http://localhost:8000/api/webhook', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    From: 'whatsapp:+1234567890',
    Body: 'Hello, I want to schedule a consultation'
  })
});

const data = await response.json();
console.log(data);
```

### cURL
```bash
# Test webhook
curl -X POST "http://localhost:8000/api/webhook" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=whatsapp:+1234567890&Body=Hello, I want to schedule a consultation"
```

## Troubleshooting

### Common Issues

#### Webhook Not Receiving Messages
1. **Check Twilio configuration**: Verify webhook URL is correct
2. **Check ngrok status**: Ensure tunnel is active
3. **Check server logs**: Look for error messages
4. **Verify phone number**: Ensure WhatsApp number is connected to sandbox

#### Agent Not Responding
1. **Check OpenAI API key**: Verify key is valid and has credits
2. **Check session memory**: Ensure SQLite database is accessible
3. **Check agent configuration**: Verify agent tools are properly loaded
4. **Check logs**: Look for agent-specific error messages

#### Calendar Integration Issues
1. **Check Google Calendar credentials**: Verify credentials.json exists
2. **Check calendar permissions**: Ensure write access is granted
3. **Check calendar ID**: Verify correct calendar is being used
4. **Check API quotas**: Ensure Google Calendar API limits aren't exceeded

### Debug Mode
Enable debug logging by setting environment variable:
```bash
export DEBUG=true
```

This will provide detailed logs for troubleshooting.

---

*Last updated: September 2025*
*Version: 1.0*
