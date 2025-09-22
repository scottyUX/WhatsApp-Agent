# QA Quick Reference - Critical Test Scenarios

## Must-Test Scenarios (Priority 1)

### 1. Phone Validation
- **Valid:** `+1 415 555 2671` → Should accept
- **Invalid:** `+1234` → Should reject with error message
- **Landline:** `+44 20 7946 0958` → Should reject (not mobile)

### 2. Appointment Management
- **Reschedule:** "I need to reschedule my appointment" → Should show appointments, allow selection
- **Cancel:** "I want to cancel my consultation" → Should show appointments, allow selection
- **View:** "What appointments do I have?" → Should show all appointments clearly

### 3. Session Memory
- **Test:** Provide name, then ask "What is my name?" → Should remember
- **Test:** Schedule appointment, then ask "What time is my appointment?" → Should remember

### 4. Questionnaire
- **Complete:** Answer all questions → Should work smoothly
- **Skip:** Say "skip" to questions → Should allow skipping
- **Decline:** Say "no" to additional info → Should still schedule

## Test Commands

### Basic Flow
1. "Hi, I'd like to schedule a consultation"
2. Provide: Name, Phone (+1 415 555 2671), Email
3. Say "yes" to additional information
4. Answer or skip questions
5. Schedule appointment

### Appointment Management
1. "What appointments do I have?"
2. "I need to reschedule my appointment"
3. "I want to cancel my consultation"

### Memory Test
1. "What is my name?" (after providing name)
2. "What time is my appointment?" (after scheduling)

## Expected Behaviors

- **Phone validation:** Clear error messages for invalid numbers
- **Appointments:** Always show current appointments before changes
- **Memory:** Remember user info across conversation turns
- **Questionnaire:** Professional, confident tone when collecting info
- **Errors:** Graceful handling with helpful messages

## Red Flags (Report Immediately)

- Anna forgets user information between messages
- Invalid phone numbers are accepted
- Appointment changes don't work
- System crashes or shows errors
- Responses take longer than 10 seconds
- Cross-user data leakage

## Test Environment

- **Branch:** `feature/simplified-agent-architecture`
- **Deployment:** Vercel production
- **Channel:** WhatsApp
- **Test Phone:** Your registered WhatsApp number
