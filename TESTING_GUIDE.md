# WhatsApp Agent Testing Guide

## Overview
This document provides comprehensive testing guidelines for the Istanbul Medic WhatsApp Agent. The agent handles appointment scheduling, patient intake questionnaires, and general inquiries through WhatsApp messaging.

## Expected Behaviors

### 1. Appointment Scheduling Flow

#### **Initial Contact**
- **User says:** "I want to schedule an appointment" or similar
- **Expected response:** Anna greets warmly, introduces herself, and asks for consent to collect personal information
- **Key phrases to expect:** "Hello and welcome! I'm Anna, your consultation assistant at Istanbul Medic"

#### **Consent Collection**
- **User says:** "yes", "I consent", "okay", etc.
- **Expected response:** Anna thanks for consent and asks for required details
- **Key phrases to expect:** "Thank you for your consent! Let's start with a few required details"

#### **Information Gathering**
- **Required fields:** Full name, phone number (with country code), email address
- **Expected behavior:** Anna asks for each field individually and confirms back
- **Phone validation:** Must include country code (e.g., +1 415 555 2671)
- **Confirmation:** Anna repeats all details back for verification

#### **Appointment Booking**
- **Day selection:** Anna offers Tuesday, Wednesday, Thursday
- **Time selection:** Morning or afternoon preference
- **Specific time:** Anna proposes specific time (e.g., "10:00 to 11:00 AM")
- **Confirmation:** When user confirms time, Anna creates calendar event
- **Success indicators:** 
  - "I'm confirming your appointment now"
  - "You'll receive confirmation by email and SMS"
  - Google Meet link provided

### 2. Session Memory (Sticky Routing)

#### **Context Maintenance**
- **Expected behavior:** Anna remembers all details throughout the conversation
- **Test:** Ask "what is my email?" after providing it earlier
- **Expected response:** Anna recalls the email address correctly

#### **Follow-up Messages**
- **Expected behavior:** Short responses like "yes", "no", "thursday" should be understood in context
- **Test:** After asking for day preference, user says "thursday"
- **Expected response:** Anna understands this refers to day selection

### 3. Questionnaire Flow

#### **Post-Booking Questions**
- **Expected behavior:** After appointment booking, Anna asks for additional details
- **Categories:** Demographics, medical background, hair loss history
- **Skip option:** Users can say "skip" for any question
- **Purpose explanation:** Anna explains why each question matters

#### **Question Types**
1. **Demographics:** Age, gender, location
2. **Medical background:** Chronic conditions, medications, allergies, surgeries, heart conditions, contagious diseases
3. **Hair loss:** Location of hair loss, when it started, family history, previous treatments

### 4. Reset Functionality

#### **Reset Keywords**
- **Keywords:** "cancel", "stop", "menu", "start over", "reset", "quit", "exit"
- **Expected behavior:** Anna resets the conversation and asks how she can help
- **Test:** Say "cancel" during any part of the conversation
- **Expected response:** "I've reset our conversation. How can I help you today?"

## Known Issues

### 1. Session Memory Limitations
- **Issue:** In some cases, very long conversations may lose context
- **Workaround:** If context is lost, user can say "cancel" to reset
- **Status:** Monitoring for improvement

### 2. Time Zone Handling
- **Issue:** All appointments are scheduled in Turkish time (Europe/Istanbul)
- **Expected behavior:** Anna should clarify time zone when user provides time
- **Current behavior:** Anna assumes Turkish time unless specified otherwise

### 3. Calendar Event Details
- **Duration:** All appointments are 15 minutes
- **Format:** "Istanbul Medic Consultation" with Google Meet link
- **Notes:** Includes consultation purpose and no-obligation disclaimer

## Expected User Experience

### 1. Smooth Conversation Flow
- **Natural language:** Users can speak naturally, not just use specific commands
- **Context awareness:** Anna understands follow-up messages without repetition
- **Professional tone:** Warm, helpful, and reassuring throughout

### 2. Clear Instructions
- **Step-by-step guidance:** Anna explains what information is needed and why
- **Confirmation:** Always confirms important details back to user
- **Next steps:** Clear explanation of what happens after booking

### 3. Flexible Interaction
- **Skip options:** Users can skip questions they're uncomfortable with
- **Reset capability:** Users can start over at any time
- **Question clarification:** Anna can rephrase questions if needed

## Testing Scenarios

### 1. Complete Happy Path
```
User: "I want to schedule an appointment"
Anna: [Greeting and consent request]
User: "yes"
Anna: [Asks for name, phone, email]
User: [Provides details]
Anna: [Confirms and asks for day preference]
User: "thursday"
Anna: [Asks for morning/afternoon]
User: "morning"
Anna: [Proposes specific time]
User: "yes, that works"
Anna: [Creates calendar event and confirms]
```

### 2. Reset During Conversation
```
User: "I want to schedule an appointment"
Anna: [Starts process]
User: "cancel"
Anna: "I've reset our conversation. How can I help you today?"
```

### 3. Context Memory Test
```
User: [Complete appointment booking]
User: "what is my email?"
Anna: "Your email address on file is: [email]"
```

### 4. Skip Questions
```
User: [During questionnaire]
Anna: "Are you currently taking any medications?"
User: "skip"
Anna: "No problem, we'll skip that."
```

## Potential Improvements

### 1. Enhanced Time Zone Support
- **Current:** All appointments in Turkish time
- **Improvement:** Detect user location and adjust time zone accordingly
- **Priority:** Medium

### 2. Appointment Management
- **Current:** Only new appointments
- **Improvement:** Reschedule, cancel, view existing appointments
- **Priority:** High

### 3. Multi-language Support
- **Current:** English only
- **Improvement:** Turkish, German, Spanish support
- **Priority:** Medium

### 4. Image Processing
- **Current:** Basic image handling
- **Improvement:** Hair loss photo analysis
- **Priority:** Low

### 5. Appointment Reminders
- **Current:** Email/SMS confirmation
- **Improvement:** Automated reminder system
- **Priority:** Medium

## Testing Checklist

### Pre-Test Setup
- [ ] WhatsApp number configured
- [ ] Calendar integration working
- [ ] Email/SMS notifications enabled
- [ ] Test user account ready

### Core Functionality Tests
- [ ] Appointment scheduling flow
- [ ] Session memory across messages
- [ ] Reset functionality
- [ ] Questionnaire completion
- [ ] Calendar event creation
- [ ] Email confirmation

### Edge Cases
- [ ] Invalid phone number format
- [ ] Missing required information
- [ ] Very long conversations
- [ ] Multiple resets
- [ ] Skip all questions

### User Experience Tests
- [ ] Natural language understanding
- [ ] Context maintenance
- [ ] Professional tone
- [ ] Clear instructions
- [ ] Helpful error messages

## Troubleshooting

### Common Issues

#### "I'm experiencing technical issues"
- **Cause:** Calendar tools not being called
- **Solution:** Check if user confirmed appointment time
- **Expected:** Should not occur with current fixes

#### Lost Context
- **Cause:** Session memory issues
- **Solution:** User can say "cancel" to reset
- **Expected:** Rare occurrence

#### Missing Calendar Event
- **Cause:** Tools not called properly
- **Solution:** Check logs for tool execution
- **Expected:** Should create event automatically

## Streaming Functionality Tests

### 1. Chat Endpoints Testing

#### Regular Chat Endpoint (`/chat/`)
```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I need help with my medical consultation",
    "media_urls": [],
    "audio_urls": []
  }'
```

**Expected Response:**
- Status: `200 OK`
- Content-Type: `application/json`
- Body: `{"content": "Anna's response..."}`

#### Streaming Chat Endpoint (`/chat/stream`)
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "I need help with my medical consultation",
    "media_urls": [],
    "audio_urls": []
  }' \
  --no-buffer
```

**Expected Response:**
- Status: `200 OK`
- Content-Type: `text/plain; charset=utf-8`
- Transfer-Encoding: `chunked`
- Cache-Control: `no-cache`
- Connection: `keep-alive`
- Body: Server-Sent Events format with JSON chunks

### 2. Streaming Response Format

Each chunk should follow this format:
```
data: {"content": "Partial response text", "timestamp": "2025-10-01T14:24:19.941641", "is_final": false}

data: {"content": "", "timestamp": "2025-10-01T14:24:19.941881", "is_final": true}
```

### 3. Database Integration Tests

#### Message Storage Verification
- Incoming messages should be stored with `direction = "incoming"`
- Outgoing messages should be stored with `direction = "outgoing"`
- Chat users should have `phone_number = "chat_{user_id}"`
- Messages should be linked to users via `user_id`

#### Test Database Queries
```sql
-- Check chat user creation
SELECT * FROM users WHERE phone_number LIKE 'chat_%';

-- Check message storage
SELECT u.phone_number, m.direction, m.body, m.created_at
FROM users u
JOIN messages m ON u.id = m.user_id
WHERE u.phone_number LIKE 'chat_%'
ORDER BY m.created_at DESC
LIMIT 10;
```

### 4. Comprehensive Testing Script

Run the comprehensive streaming test suite:
```bash
python test_streaming_comprehensive.py
```

This script tests:
- Regular chat endpoint functionality
- Streaming chat endpoint functionality
- Response headers validation
- Database integration
- Error handling
- Performance with concurrent requests
- Webhook integration

### 5. Expected Test Results

All tests should pass with:
- ✅ Regular Chat Response
- ✅ Streaming Response
- ✅ Streaming Headers
- ✅ Database Integration
- ✅ Error Handling
- ✅ Performance Test
- ✅ Webhook Integration

## Contact Information

For technical issues or questions about testing:
- **Developer:** [Your contact info]
- **Project:** Istanbul Medic WhatsApp Agent
- **Repository:** [GitHub link]
- **Last Updated:** October 1, 2025

---

**Note:** This testing guide is updated regularly. Please check for the latest version before testing.
