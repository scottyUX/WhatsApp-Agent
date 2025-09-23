# Scheduling Agent (Anna) Documentation

## Overview

Anna is the specialized consultation scheduling agent for Istanbul Medic's WhatsApp system. She handles appointment booking, rescheduling, cancellation, and comprehensive patient information collection.

## Table of Contents

- [Agent Profile](#agent-profile)
- [Core Capabilities](#core-capabilities)
- [Conversation Flow](#conversation-flow)
- [Phone Validation](#phone-validation)
- [Appointment Management](#appointment-management)
- [Patient Questionnaire](#patient-questionnaire)
- [Tools Available](#tools-available)
- [Error Handling](#error-handling)
- [Configuration](#configuration)
- [Testing](#testing)

## Agent Profile

### Personality
- **Name**: Anna
- **Role**: Consultation Assistant
- **Personality**: Compassionate, professional, and supportive
- **Communication**: Calm, empathetic, and reassuring
- **Language**: Accessible, avoids medical jargon

### Environment
- **Platform**: WhatsApp messaging and website chat
- **Message Style**: Concise, structured, and easy to read
- **Formatting**: Simple formatting for multiple questions
- **Escalation**: Suggests human coordinator when needed

## Core Capabilities

### 1. Consultation Scheduling
- Books free, no-obligation online consultations
- Collects required personal information
- Schedules appointments with specialists
- Provides Google Meet links for consultations

### 2. Appointment Management
- **View Appointments**: Shows upcoming consultations
- **Reschedule**: Changes appointment times
- **Cancel**: Cancels existing appointments
- **Search**: Finds appointments by title/name

### 3. Patient Information Collection
- **Required Information**: Name, phone, email
- **Optional Information**: Demographics, medical background, hair loss history
- **Validation**: Ensures data quality and completeness

## Conversation Flow

### 1. Initial Contact & Consent
```
Anna: "Hello and welcome! I'm Anna, your consultation assistant at Istanbul Medic. 
I'm here to help you schedule a free, no-obligation online consultation with one of our specialists. 
To get started, I'll need to collect a few basic details so our team can prepare for your appointment. 
Is it okay for me to collect your personal information for this purpose?"
```

### 2. Basic Information Collection (Required)
- **Full Name**: Complete legal name
- **Phone Number**: Mobile number with country code
- **Email Address**: Valid email for confirmations

### 3. Phone Number Validation
Anna enforces strict phone validation rules:

#### Valid Formats
- `+1 415 555 2671` (US)
- `+44 20 7946 0958` (UK)
- `+49 160 1234567` (Germany)
- `+90 555 123 4567` (Turkey)

#### Invalid Formats (Rejected)
- `+1234` (too short)
- `+123456` (too short)
- `1234567890` (missing country code)
- Landline numbers (for SMS reminders)

#### Error Messages
- **Invalid format**: "I need a complete phone number with country code. For example: +1 415 555 2671 (US), +44 20 7946 0958 (UK), or +49 160 1234567 (Germany). Please provide your full international phone number."
- **Landline detected**: "This looks like a landline number. For SMS reminders, could you please provide a mobile number instead? For example: +1 415 555 2671"

### 4. Consultation Scheduling
```
Anna: "Great, thank you. Let's book your consultation. We currently have openings on Tuesday, Wednesday, and Thursday. Which day works best?"
```

### 5. Additional Information Collection (Optional)
After scheduling, Anna confidently collects additional details:

#### Opening Message
```
"To prepare your consultation properly and tailor recommendations to you, I need to collect a few important details. These help our specialists assess suitability, safety, and treatment options before you meet. This step is quick and ensures you get the most value from your consultation. If you prefer not to share something, you can say 'skip', but we recommend providing as much as you're comfortable with."
```

#### Basic Demographics
- **Age**: "What's your age?"
- **Gender**: "What's your gender?"
- **Location**: "What's your location? (city, country)"

#### Medical Background
- **Chronic conditions**: "Do you have any chronic illnesses or medical conditions? This is important for your safety."
- **Medications**: "Are you currently taking any medications? We check for interactions."
- **Allergies**: "Do you have any allergies? This is critical for safety."
- **Surgery history**: "Have you had any surgeries in the past? This informs your medical history."
- **Heart conditions**: "Any heart conditions? This can affect recommendations."
- **Contagious diseases**: "Any contagious diseases? This is for clinic safety."

#### Hair Loss Background
- **Location**: "Where are you experiencing hair loss? (crown, hairline, top, etc.) This helps us determine the best treatment approach."
- **Timeline**: "When did your hair loss start? This helps us understand the progression."
- **Family history**: "Is there a family history of hair loss? This affects our treatment strategy."
- **Previous treatments**: "Have you tried any previous hair loss treatments? This helps us avoid repeating ineffective treatments."

### 6. Closure
```
Anna: "Your free online consultation is now scheduled for:
• Day: Tuesday, September 23
• Time: 2:00–3:00 PM (Turkish time)

You'll receive a confirmation by email and SMS soon. Your consultation will be online, and here's your Google Meet link: https://meet.google.com/kbb-xnko-znu

Thank you, Scott! We look forward to speaking with you and helping you take the first step toward a new you."
```

## Appointment Management

### Rescheduling Process
1. **Show current appointments** using `list_upcoming_events`
2. **Ask which appointment** to reschedule
3. **Offer available time slots** (morning/afternoon, specific days)
4. **Confirm new time** before making changes
5. **Use reschedule tools** to update appointment
6. **Confirm changes** and provide new details

### Cancellation Process
1. **Show current appointments** using `list_upcoming_events`
2. **Ask which appointment** to cancel
3. **Confirm cancellation details**
4. **Use delete tools** to cancel appointment
5. **Confirm cancellation** and offer to reschedule if needed

### Viewing Appointments
- **Use list_upcoming_events** to show all upcoming appointments
- **Display clearly** with date, time, and appointment title
- **Offer help** with changes if needed

## Tools Available

### Calendar Management Tools
- **`create_calendar_event`** - Book new consultation appointments
- **`list_upcoming_events`** - View upcoming appointments and check availability
- **`delete_event`** - Cancel appointments by event ID
- **`delete_event_by_title`** - Cancel appointments by searching for title/name
- **`reschedule_event`** - Change appointment time by event ID
- **`reschedule_event_by_title`** - Change appointment time by searching for title/name

### Tool Usage Examples
- **"I need to reschedule my appointment"** → Show appointments, ask which one, offer new times
- **"Can I cancel my consultation?"** → Show appointments, ask which one, confirm cancellation
- **"What appointments do I have?"** → Use list_upcoming_events, display clearly
- **"I want to change my time"** → Show appointments, ask which one, offer new times
- **"Show me my schedule"** → Use list_upcoming_events, display clearly

## Error Handling

### Validation Rules
- **Time conflicts** - Check before rescheduling
- **Business hours** - Ensure appointments are 9 AM - 6 PM
- **Appointment verification** - Verify exists before changes
- **Error handling** - Graceful handling of edge cases

### Error Recovery
- **Technical difficulties** - "I apologize, but I'm experiencing some technical difficulties. Let me connect you with a human coordinator who can assist you with scheduling your consultation."
- **Missing appointments** - Show available options
- **Invalid times** - Offer alternative slots
- **Confirmation required** - Always confirm before making changes

## Configuration

### Environment Variables
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key

# Google Calendar (for appointment management)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_ID=your_calendar_id

# Phone validation
DEFAULT_PHONE_REGION=US
REQUIRE_MOBILE_NUMBERS=true
```

### Agent Configuration
```python
agent = Agent(
    name="AnnaConsultationAssistant",
    instructions="...",  # See full instructions in scheduling_agent.py
    tools=[
        create_calendar_event,
        list_upcoming_events,
        delete_event,
        reschedule_event,
        reschedule_event_by_title,
        delete_event_by_title
    ]
)
```

## Testing

### Manual Testing Scenarios

#### Phone Validation Tests
1. **Valid numbers**: `+1 415 555 2671`, `+44 20 7946 0958`
2. **Invalid numbers**: `+1234`, `+123456`, `1234567890`
3. **Landline rejection**: `+44 20 7946 0958` (should ask for mobile)

#### Session Memory Tests
1. **Name recall**: Tell Anna your name, then ask "What is my name?"
2. **Appointment recall**: Schedule appointment, then ask "What appointments do I have?"
3. **Context persistence**: Continue conversation across multiple messages

#### Appointment Management Tests
1. **Schedule**: Book new consultation
2. **Reschedule**: Change existing appointment time
3. **Cancel**: Cancel existing appointment
4. **View**: List all upcoming appointments

### Automated Testing
```python
# Example test structure
async def test_phone_validation():
    # Test valid phone numbers
    # Test invalid phone numbers
    # Test landline rejection

async def test_appointment_management():
    # Test scheduling
    # Test rescheduling
    # Test cancellation
    # Test viewing
```

## Integration

### Manager Agent Integration
Anna is integrated as a tool in the Manager Agent:

```python
scheduling_agent.as_tool(
    tool_name="scheduling_expert",
    tool_description="Handles consultation scheduling, appointments, and patient intake questions."
)
```

### Session Memory
- **SQLiteSession** - Local conversation persistence
- **User-specific sessions** - One session per WhatsApp user
- **Context maintenance** - Remembers information across turns

## Best Practices

### For Developers
1. **Maintain Anna's personality** - Keep responses compassionate and professional
2. **Validate all inputs** - Use phone validation and data sanitization
3. **Handle errors gracefully** - Provide helpful error messages
4. **Test thoroughly** - Verify all appointment management flows

### For QA
1. **Test phone validation** - Try various international formats
2. **Verify session memory** - Ensure context persistence
3. **Test appointment flows** - Schedule, reschedule, cancel, view
4. **Check error handling** - Test edge cases and failures

### For Operations
1. **Monitor calendar integration** - Ensure Google Calendar connectivity
2. **Check phone validation** - Verify libphonenumber functionality
3. **Monitor session storage** - Check SQLite database health
4. **Track appointment accuracy** - Verify scheduling precision

## Troubleshooting

### Common Issues

#### Phone Validation Not Working
- **Check libphonenumber installation**: `pip install phonenumbers>=8.13.0`
- **Verify region settings**: Ensure DEFAULT_PHONE_REGION is set
- **Test with known valid numbers**: Use international test numbers

#### Session Memory Issues
- **Check SQLite database**: Verify conversations.db exists and is writable
- **Clear session data**: Delete conversations.db to reset sessions
- **Check user ID format**: Ensure phone numbers are properly formatted

#### Calendar Integration Problems
- **Verify credentials**: Check Google Calendar API credentials
- **Test calendar access**: Ensure calendar ID is correct
- **Check permissions**: Verify calendar write permissions

#### Appointment Management Errors
- **Verify tool availability**: Ensure all calendar tools are properly imported
- **Check time zones**: Verify appointment times are in correct timezone
- **Test calendar connectivity**: Ensure Google Calendar API is accessible

## Support

For technical issues or questions about Anna's functionality:

1. **Check logs** - Review application logs for error details
2. **Test manually** - Use WhatsApp to test specific scenarios
3. **Review configuration** - Verify environment variables and settings
4. **Contact development team** - For complex issues or bugs

---

*Last updated: September 2025*
*Version: 1.0*
