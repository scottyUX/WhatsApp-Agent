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

**Request Body**:
```json
{
  "From": "whatsapp:+1234567890",
  "Body": "Hello, I'd like to schedule a consultation",
  "MediaUrl0": "https://example.com/image.jpg",
  "NumMedia": "1"
}
```

**Response**:
```json
{
  "message": "Hello! I'm Anna, your consultation assistant..."
}
```

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
