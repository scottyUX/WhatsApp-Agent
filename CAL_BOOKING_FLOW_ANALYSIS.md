# Cal.com Booking → Patient Information Flow

## 📋 **Current Flow (Broken)**

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PATIENT BOOKS ON CAL.COM                                     │
│  - Fills out booking form                                        │
│  - Submits booking                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CAL.COM CREATES BOOKING                                      │
│  - Generates booking with ID (e.g., "iufb9wQ9g2MiQiLhgmfopb")   │
│  - Sends webhook to our backend                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. WEBHOOK PROCESSING (BACKEND) ✅                              │
│  - Receives webhook payload                                     │
│  - Extracts attendee info: name, email, phone                  │
│  - Creates User record                                          │
│  - Creates PatientProfile record                                │
│  - Creates Consultation record with booking ID                  │
│  ✅ SUCCESS: Data saved to database                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CAL.COM REDIRECTS TO QUESTIONNAIRE PAGE                     │
│  URL: https://istanbulmedic.com/booking-confirmation/[UID]     │
│  Query Params: ?title={title}&attendeeName={name}...            │
│  ❌ PROBLEM: Query params contain PLACEHOLDERS                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. FRONTEND ATTEMPTS TO FETCH PATIENT DATA                      │
│  - Reads bookingUID from URL                                    │
│  - Calls: GET /api/consultations/{bookingUID}                   │
│  ❌ PROBLEM: If bookingUID is "[bookingUid]" placeholder       │
│  ❌ OR: Consultation not found in database                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. FRONTEND FALLS BACK TO QUERY PARAMS                         │
│  - Uses Cal.com query parameters                                │
│  - These contain {title}, {attendee.name}, etc.                 │
│  ❌ RESULTS IN: Invalid Date, {attendee.name} display          │
└─────────────────────────────────────────────────────────────────┘
```

## ✅ **Desired Flow (Fixed)**

```mermaid
flowchart TD
    A[Patient books on Cal.com<br/>selects slot + answers custom questions] --> B[Cal.com creates booking<br/>bookingId + attendee payload]
    B --> C[Webhook POST /api/cal-webhook<br/>ConsultationService]
    C --> D[Create/find User (phone→email fallback)]
    C --> E[Create/find PatientProfile<br/>link to User]
    C --> F[Create Consultation row<br/>zoom_meeting_id = bookingId]
    B --> G[Cal.com redirect<br/>/booking-confirmation/{bookingId}?title={title}...]
    G --> H[Next.js page resolves real bookingId<br/>ignore placeholder params]
    H --> I[GET /api/consultations/{bookingId}]
    I -->|success| J[Appointment card shows real data]
    I -->|404/failure| K[Warn patient + allow manual entry]
    J --> L[Patient submits questionnaire<br/>POST /api/medical/questionnaire]
    L --> M[MedicalDataService updates PatientProfile]
```

```
┌─────────────────────────────────────────────────────────────────┐
│  1. PATIENT BOOKS ON CAL.COM                                     │
│  - Fills out booking form                                        │
│  - Submits booking                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  2. CAL.COM SENDS WEBHOOK TO OUR BACKEND                         │
│  Webhook URL: /api/cal-webhook                                   │
│  Payload: { triggerEvent: "BOOKING_CREATED", payload: {...} }  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  3. BACKEND PROCESSES WEBHOOK ✅                                  │
│  - Extracts: name, email, phone, location                       │
│  - Creates User record                                          │
│  - Creates PatientProfile record                                │
│  - Creates Consultation record                                  │
│  - Stores Cal.com booking ID in consultation                    │
│  ✅ SUCCESS: All data saved to database                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  4. CAL.COM REDIRECTS TO QUESTIONNAIRE PAGE                      │
│  URL: https://istanbulmedic.com/booking-confirmation/[REAL_ID]  │
│  NOTE: Cal.com should pass REAL booking ID, not [bookingUid]   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  5. FRONTEND FETCHES PATIENT DATA ✅                             │
│  - Reads REAL bookingUID from URL                               │
│  - Calls: GET /api/consultations/{REAL_ID}                       │
│  - Backend finds consultation by booking ID                     │
│  - Returns: { title, start_time, end_time, attendee_name... }   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  6. QUESTIONNAIRE PAGE DISPLAYS CORRECT DATA ✅                 │
│  - Shows real patient name                                       │
│  - Shows real email                                              │
│  - Shows correct appointment time                               │
│  - Shows booking details                                         │
└─────────────────────────────────────────────────────────────────┘
```

## 🔍 **ROOT CAUSE ANALYSIS**

### **Problem 1: Cal.com Redirect Format**
Cal.com is redirecting to: `/booking-confirmation/[bookingUid]` 
- The literal string `[bookingUid]` is being used, not a real booking ID
- This happens when Cal.com custom redirect URL template is not configured properly

### **Problem 2: Query Params Have Placeholders**
Cal.com adds query params like: `?title={title}&attendeeName={attendee.name}`
- These are **template strings** that Cal.com should replace with actual values
- They're not being replaced, so we get literal `{title}` strings

### **Problem 3: Missing Consultation Lookup**
When frontend gets `[bookingUid]`, it can't look up the consultation because:
- It queries `/api/consultations/[bookingUid]` (with literal placeholder)
- Backend returns 404
- Frontend falls back to query params (which have placeholders)

## 💡 **SOLUTION OPTIONS**

### **Option A: Fix Cal.com Redirect Configuration** (Recommended)
**Configure Cal.com to redirect to:**
```
https://istanbulmedic.com/booking-confirmation/{bookingId}
```
Instead of:
```
https://istanbulmedic.com/booking-confirmation/{bookingUid}
```
- This should use the real booking ID in the redirect
- Make sure Cal.com replaces `{bookingId}` with actual ID

### **Option B: Store Booking Data in URL Fragment**
Instead of relying on path parameter, pass data in URL hash:
```
https://istanbulmedic.com/booking-confirmation#uid=iufb9wQ9g2MiQiLhgmfopb
```
- Can't be modified by Cal.com
- Frontend can extract and use it

### **Option C: Use Webhook Callback**
Have our backend create a unique token when processing webhook:
1. Webhook creates consultation
2. Backend generates unique token (e.g., UUID)
3. Backend stores token → booking ID mapping
4. Redirect Cal.com to: `/booking-confirmation?token={unique_token}`
5. Frontend fetches booking using token

### **Option D: Accept Query Params But Validate**
Keep current flow but validate that Cal.com passes real values:
- If query params have placeholders, show warning
- Patient can manually enter details
- Store in database on form submission

## 🎯 **RECOMMENDED SOLUTION**

**Option A + Frontend Enhancement:**

1. **Fix Cal.com redirect** to use real booking ID
2. **Frontend should:**
   - Try to fetch from backend using booking ID from URL
   - If that fails, try query params
   - If query params have placeholders, show manual entry form
   - Always show warning banner when using fallback data

3. **Backend should:**
   - Store consultation with Cal.com booking ID
   - Return complete attendee info when queried
   - Handle both `uid` and `id` fields from Cal.com

## ❓ **QUESTION FOR YOU**

What's the **actual URL** when Cal.com redirects? 
- Is it `https://istanbulmedic.com/booking-confirmation/[bookingUid]` (literal)?
- Or does it have a real booking ID like `https://istanbulmedic.com/booking-confirmation/iufb9wQ9g2MiQiLhgmfopb`?

This will determine our fix approach.
