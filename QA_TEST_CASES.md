# QA Test Cases - Simplified Agent Architecture with Enhanced Appointment Management

## Test Environment Setup
- **Branch:** `feature/simplified-agent-architecture`
- **Environment:** Production (Vercel deployment)
- **Test Channel:** WhatsApp
- **Test Phone:** Use your registered WhatsApp number

---

## Test Suite 1: Phone Number Validation

### Test Case 1.1: Valid Phone Numbers
**Objective:** Verify that valid phone numbers are accepted and formatted correctly

**Steps:**
1. Send message: "Hi, I'd like to schedule a consultation"
2. When asked for phone number, provide: "+1 415 555 2671"
3. Verify Anna accepts the number
4. Verify the number is stored in E.164 format

**Expected Result:** Phone number accepted, consultation booking continues

**Test Data:**
- `+1 415 555 2671` (US with country code)
- `+44 20 7946 0958` (UK with country code)
- `+49 160 1234567` (Germany with country code)
- `8312959447` (US without country code - should add +1)

### Test Case 1.2: Invalid Phone Numbers
**Objective:** Verify that invalid phone numbers are rejected with helpful error messages

**Steps:**
1. Send message: "Hi, I'd like to schedule a consultation"
2. When asked for phone number, provide invalid numbers
3. Verify Anna rejects the number with clear error message
4. Verify Anna asks for a valid number

**Expected Result:** Phone number rejected with error message, user prompted to provide valid number

**Test Data:**
- `+1234` (too short)
- `+123456` (too short)
- `invalid` (not a number)
- `123` (too short, no country code)
- `+44 20 7946 0958` (landline - should be rejected for SMS)

---

## Test Suite 2: Patient Questionnaire System

### Test Case 2.1: Complete Questionnaire Flow
**Objective:** Verify the complete questionnaire flow works correctly

**Steps:**
1. Start consultation booking process
2. Provide valid personal information (name, phone, email)
3. When asked about additional information, respond "yes"
4. Answer all questionnaire questions
5. Verify questionnaire completion

**Expected Result:** All questions answered, consultation scheduled successfully

**Questionnaire Categories to Test:**
- **Basic Info:** Country, age, gender
- **Medical Info:** Medical conditions, medications, allergies
- **Hair Loss Info:** Hair loss duration, family history, previous treatments

### Test Case 2.2: Skip Questionnaire Questions
**Objective:** Verify users can skip optional questions

**Steps:**
1. Start consultation booking process
2. Provide valid personal information
3. When asked about additional information, respond "yes"
4. For each question, respond "skip" or "next"
5. Verify Anna moves to next question/category

**Expected Result:** Questions can be skipped, consultation still scheduled

### Test Case 2.3: Decline Additional Information
**Objective:** Verify users can decline the entire questionnaire

**Steps:**
1. Start consultation booking process
2. Provide valid personal information
3. When asked about additional information, respond "no"
4. Verify consultation is scheduled without questionnaire

**Expected Result:** Consultation scheduled without additional questions

---

## Test Suite 3: Appointment Management - Reschedule

### Test Case 3.1: Reschedule Existing Appointment
**Objective:** Verify users can reschedule their appointments

**Steps:**
1. Send message: "I need to reschedule my appointment"
2. Verify Anna shows current appointments
3. Select an appointment to reschedule
4. Choose a new time slot
5. Verify appointment is rescheduled successfully

**Expected Result:** Appointment rescheduled with confirmation

### Test Case 3.2: Reschedule with Specific Time Request
**Objective:** Verify rescheduling works with specific time requests

**Steps:**
1. Send message: "I want to move my consultation to next week"
2. Verify Anna shows current appointments
3. Select appointment to reschedule
4. Choose next week time slot
5. Verify appointment is rescheduled

**Expected Result:** Appointment moved to next week successfully

### Test Case 3.3: Reschedule Non-existent Appointment
**Objective:** Verify error handling for non-existent appointments

**Steps:**
1. Send message: "Reschedule my 3 PM appointment"
2. Verify Anna shows available appointments
3. Verify Anna asks for clarification if no 3 PM appointment exists

**Expected Result:** Anna shows available appointments and asks for clarification

---

## Test Suite 4: Appointment Management - Cancel

### Test Case 4.1: Cancel Existing Appointment
**Objective:** Verify users can cancel their appointments

**Steps:**
1. Send message: "I want to cancel my consultation"
2. Verify Anna shows current appointments
3. Select an appointment to cancel
4. Confirm cancellation
5. Verify appointment is cancelled successfully

**Expected Result:** Appointment cancelled with confirmation

### Test Case 4.2: Cancel Specific Appointment
**Objective:** Verify cancellation works with specific appointment requests

**Steps:**
1. Send message: "Cancel my 2 PM appointment"
2. Verify Anna shows appointments around 2 PM
3. Select the correct appointment
4. Confirm cancellation
5. Verify appointment is cancelled

**Expected Result:** Specific appointment cancelled successfully

### Test Case 4.3: Cancel Non-existent Appointment
**Objective:** Verify error handling for non-existent appointments

**Steps:**
1. Send message: "Cancel my 5 PM appointment"
2. Verify Anna shows available appointments
3. Verify Anna asks for clarification if no 5 PM appointment exists

**Expected Result:** Anna shows available appointments and asks for clarification

---

## Test Suite 5: View Appointments

### Test Case 5.1: View All Appointments
**Objective:** Verify users can view their upcoming appointments

**Steps:**
1. Send message: "What appointments do I have?"
2. Verify Anna shows all upcoming appointments
3. Verify appointments are displayed with clear formatting
4. Verify dates, times, and titles are shown

**Expected Result:** All appointments displayed in clear format

### Test Case 5.2: View Schedule
**Objective:** Verify alternative ways to view appointments

**Steps:**
1. Send message: "Show me my schedule"
2. Verify Anna shows upcoming appointments
3. Verify appointments are displayed clearly

**Expected Result:** Schedule displayed with all appointments

---

## Test Suite 6: Session Memory

### Test Case 6.1: Remember User Information
**Objective:** Verify Anna remembers user information across turns

**Steps:**
1. Start conversation: "Hi, I'd like to schedule a consultation"
2. Provide name: "My name is John Smith"
3. In next message, ask: "What is my name?"
4. Verify Anna remembers the name

**Expected Result:** Anna correctly recalls "John Smith"

### Test Case 6.2: Remember Appointment Details
**Objective:** Verify Anna remembers appointment details

**Steps:**
1. Schedule an appointment
2. In next message, ask: "What time is my appointment?"
3. Verify Anna provides correct appointment time

**Expected Result:** Anna provides correct appointment details

### Test Case 6.3: Context Across Different Topics
**Objective:** Verify context is maintained across different conversation topics

**Steps:**
1. Schedule an appointment
2. Ask general question: "What services do you offer?"
3. Ask: "What time is my appointment?"
4. Verify Anna remembers appointment details

**Expected Result:** Anna maintains context across different topics

---

## Test Suite 7: Error Handling

### Test Case 7.1: Invalid Input Handling
**Objective:** Verify graceful handling of invalid inputs

**Steps:**
1. Send message: "I want to reschedule my appointment"
2. When asked which appointment, send: "asdfasdf"
3. Verify Anna asks for clarification
4. Verify Anna shows available appointments

**Expected Result:** Anna handles invalid input gracefully

### Test Case 7.2: Network Error Handling
**Objective:** Verify handling of network/API errors

**Steps:**
1. Try to schedule appointment during potential API downtime
2. Verify Anna provides helpful error message
3. Verify Anna offers to try again

**Expected Result:** Graceful error handling with retry option

---

## Test Suite 8: Integration Testing

### Test Case 8.1: Complete User Journey
**Objective:** Verify complete user journey from start to finish

**Steps:**
1. Start: "Hi, I'd like to schedule a consultation"
2. Provide all required information
3. Complete questionnaire (optional)
4. Schedule appointment
5. View appointment: "What appointments do I have?"
6. Reschedule appointment
7. Cancel appointment
8. Schedule new appointment

**Expected Result:** Complete journey works smoothly

### Test Case 8.2: Multiple Users
**Objective:** Verify system handles multiple users correctly

**Steps:**
1. Use different phone numbers for testing
2. Schedule appointments for different users
3. Verify each user sees only their appointments
4. Verify context is maintained per user

**Expected Result:** Each user has isolated experience

---

## Test Suite 9: Performance Testing

### Test Case 9.1: Response Time
**Objective:** Verify acceptable response times

**Steps:**
1. Send various messages
2. Measure response time
3. Verify responses are under 10 seconds

**Expected Result:** All responses under 10 seconds

### Test Case 9.2: Concurrent Users
**Objective:** Verify system handles multiple concurrent users

**Steps:**
1. Have multiple testers use the system simultaneously
2. Verify all users get responses
3. Verify no cross-user data leakage

**Expected Result:** System handles concurrent users correctly

---

## Test Suite 10: Edge Cases

### Test Case 10.1: Very Long Messages
**Objective:** Verify handling of very long messages

**Steps:**
1. Send very long message (1000+ characters)
2. Verify Anna responds appropriately
3. Verify no system errors

**Expected Result:** Long messages handled gracefully

### Test Case 10.2: Special Characters
**Objective:** Verify handling of special characters

**Steps:**
1. Send messages with special characters: "I'd like to schedule a consultation @#$%"
2. Verify Anna responds appropriately
3. Verify no system errors

**Expected Result:** Special characters handled correctly

---

## Test Results Template

| Test Case | Status | Notes | Screenshots |
|-----------|--------|-------|-------------|
| 1.1 Valid Phone Numbers | Pass/Fail | | |
| 1.2 Invalid Phone Numbers | Pass/Fail | | |
| 2.1 Complete Questionnaire | Pass/Fail | | |
| 2.2 Skip Questions | Pass/Fail | | |
| 2.3 Decline Questionnaire | Pass/Fail | | |
| 3.1 Reschedule Appointment | Pass/Fail | | |
| 3.2 Specific Time Reschedule | Pass/Fail | | |
| 3.3 Non-existent Reschedule | Pass/Fail | | |
| 4.1 Cancel Appointment | Pass/Fail | | |
| 4.2 Specific Cancel | Pass/Fail | | |
| 4.3 Non-existent Cancel | Pass/Fail | | |
| 5.1 View Appointments | Pass/Fail | | |
| 5.2 View Schedule | Pass/Fail | | |
| 6.1 Remember Name | Pass/Fail | | |
| 6.2 Remember Appointment | Pass/Fail | | |
| 6.3 Context Across Topics | Pass/Fail | | |
| 7.1 Invalid Input | Pass/Fail | | |
| 7.2 Network Errors | Pass/Fail | | |
| 8.1 Complete Journey | Pass/Fail | | |
| 8.2 Multiple Users | Pass/Fail | | |
| 9.1 Response Time | Pass/Fail | | |
| 9.2 Concurrent Users | Pass/Fail | | |
| 10.1 Long Messages | Pass/Fail | | |
| 10.2 Special Characters | Pass/Fail | | |

---

## Test Environment Notes

- **Test Data:** Use consistent test data across all test cases
- **Screenshots:** Take screenshots of any failures or unexpected behavior
- **Logs:** Check Vercel logs for any errors during testing
- **Rollback:** Have rollback plan ready if critical issues found

## Sign-off Criteria

- All test cases must pass
- No critical bugs found
- Performance meets requirements
- User experience is smooth and intuitive
- All edge cases handled gracefully
