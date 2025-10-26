# Cal.com Booking Flow Enhancement - Technical Analysis

## 🎯 **Problem Statement**

Currently, when patients book consultations through Cal.com, **no patient profiles are created** until they complete the medical questionnaire. This creates a gap where consultants cannot see new bookings in their dashboard immediately after booking completion.

## 📊 **Current Flow vs Desired Flow**

### ❌ **Current Flow (Broken)**
1. Patient books via Cal.com → Cal webhook fires
2. `ConsultationService.process_cal_webhook()` creates consultation record
3. **No user or patient profile created** (only consultation exists)
4. Consultant dashboard shows consultation but **no patient details**
5. Patient completes medical questionnaire → User + PatientProfile created
6. **Only then** can consultant see full patient information

### ✅ **Desired Flow (Fixed)**
1. Patient books via Cal.com → Cal webhook fires
2. `ConsultationService.process_cal_webhook()` creates:
   - **User record** (from attendee email/phone)
   - **PatientProfile record** (with attendee details)
   - **Consultation record** (linked to patient profile)
3. Consultant dashboard immediately shows **complete patient information**
4. Patient completes medical questionnaire → Updates existing profile

## 🔍 **Technical Analysis**

### **Current Code Issues**

#### 1. **ConsultationService._handle_consultation_created()**
```python
# Current code (lines 104-110)
patient_profile = self._find_patient_by_email(attendee_email)

# Create consultation
consultation = self.consultation_repository.create(
    patient_profile_id=patient_profile.id if patient_profile else None,  # ❌ Often None
    # ... other fields
)
```

**Problem**: If no existing patient profile found, `patient_profile_id=None`, so consultation is orphaned.

#### 2. **Missing User Creation**
- Cal.com webhook only creates consultation records
- No User records created for new attendees
- PatientProfile requires `user_id` (non-nullable FK)

#### 3. **Limited Data Extraction**
```python
# Current code only extracts basic attendee info
attendee_name = attendee.get("name", "Unknown")
attendee_email = attendee.get("email", "")
attendee_timezone = attendee.get("timeZone")
```

**Missing**: Phone numbers, location, and other custom form responses from Cal.com.

## 🛠️ **Proposed Solution**

### **Enhanced ConsultationService Implementation**

#### 1. **Extract Additional Attendee Data**
```python
def _extract_phone_from_responses(self, booking_data: Dict[str, Any]) -> Optional[str]:
    """Extract phone number from Cal.com responses."""
    responses = booking_data.get("responses", {})
    phone_fields = ["phone", "phone_number", "phoneNumber", "mobile", "telephone"]
    # ... implementation

def _extract_location_from_responses(self, booking_data: Dict[str, Any]) -> Optional[str]:
    """Extract location from Cal.com responses."""
    responses = booking_data.get("responses", {})
    location_fields = ["location", "city", "country", "address", "where_are_you_from"]
    # ... implementation
```

#### 2. **Create User and Patient Profile**
```python
def _create_or_find_user_and_patient(
    self, 
    attendee_name: str, 
    attendee_email: str, 
    attendee_phone: Optional[str] = None,
    attendee_location: Optional[str] = None,
    cal_booking_id: Optional[str] = None
) -> tuple[Optional[User], Optional[PatientProfile]]:
    """Create or find user and patient profile for booking."""
    
    # 1. Create/find User
    user_phone = attendee_phone or attendee_email  # Fallback to email
    user = self.user_repository.get_by_phone_number(user_phone)
    if not user:
        user = self.user_repository.create(phone_number=user_phone, name=attendee_name)
    
    # 2. Create/find PatientProfile
    patient_profile = self._find_patient_by_email(attendee_email)
    if not patient_profile:
        patient_profile = self.patient_profile_repository.create(
            user_id=user.id,
            name=attendee_name,
            phone=attendee_phone or attendee_email,
            email=attendee_email,
            location=attendee_location
        )
    
    return user, patient_profile
```

#### 3. **Enhanced Webhook Processing**
```python
def _handle_consultation_created(self, booking_data: Dict[str, Any], webhook_payload: Dict[str, Any]) -> Dict[str, Any]:
    # Extract enhanced attendee data
    attendee_phone = self._extract_phone_from_responses(booking_data)
    attendee_location = self._extract_location_from_responses(booking_data)
    
    # Create/find user and patient profile
    user, patient_profile = self._create_or_find_user_and_patient(
        attendee_name=attendee_name,
        attendee_email=attendee_email,
        attendee_phone=attendee_phone,
        attendee_location=attendee_location,
        cal_booking_id=cal_booking_id
    )
    
    # Create consultation with proper patient_profile_id
    consultation = self.consultation_repository.create(
        patient_profile_id=patient_profile.id,  # ✅ Always linked
        zoom_meeting_id=cal_booking_id,
        attendee_phone=attendee_phone,  # ✅ Store phone in consultation
        # ... other fields
    )
```

## 🗄️ **Database Schema Considerations**

### **Current Schema**
```sql
-- Users table
users.id (UUID, PK)
users.phone_number (String, unique, not null)
users.name (String, nullable)

-- Patient Profiles table  
patient_profiles.id (UUID, PK)
patient_profiles.user_id (UUID, FK to users.id, not null)
patient_profiles.name (String, not null)
patient_profiles.phone (String, not null)
patient_profiles.email (String, not null)
patient_profiles.location (String, nullable)

-- Consultations table (appointment)
consultation.id (String, PK)
consultation.zoom_meeting_id (String, not null)  -- Stores Cal booking ID
consultation.patient_profile_id (UUID, FK to patient_profiles.id, nullable)
consultation.attendee_phone (String, nullable)
```

### **Cal Booking ID Storage Question**

**Option A**: Add `cal_booking_id` to `patient_profiles` table
```sql
ALTER TABLE patient_profiles ADD COLUMN cal_booking_id VARCHAR(255) NULL;
```

**Option B**: Use existing `consultation.zoom_meeting_id` (Recommended)
- Cal booking ID already stored in `consultation.zoom_meeting_id`
- Can find patient via: `consultation.zoom_meeting_id = cal_booking_id → consultation.patient_profile_id → patient_profile`
- No schema changes needed

**Recommendation**: Use Option B to avoid database migration.

## 🧪 **Testing Strategy**

### **Test Cases**
1. **New Patient Booking**: Should create User + PatientProfile + Consultation
2. **Existing Patient Booking**: Should find existing User + PatientProfile, create new Consultation
3. **Booking with Phone**: Should extract and store phone number
4. **Booking without Phone**: Should fallback to email for user lookup
5. **Booking with Location**: Should extract and store location
6. **Duplicate Booking**: Should handle gracefully without creating duplicates

### **Sample Cal.com Webhook Payload**
```json
{
  "type": "BOOKING_CREATED",
  "data": {
    "id": "cal_booking_12345",
    "title": "Hair Transplant Consultation",
    "startTime": "2025-10-26T15:00:00Z",
    "endTime": "2025-10-26T15:15:00Z",
    "attendees": [
      {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "timeZone": "America/New_York"
      }
    ],
    "responses": {
      "phone": "+1-555-123-4567",
      "location": "New York, NY",
      "age": "35"
    }
  }
}
```

## 🚀 **Implementation Status**

### **Completed**
- ✅ Enhanced ConsultationService with user/patient creation logic
- ✅ Phone and location extraction from Cal.com responses
- ✅ User creation/lookup with phone number fallback
- ✅ PatientProfile creation with proper user linking
- ✅ Deduplication logic for repeat bookings
- ✅ Comprehensive logging for debugging

### **Pending**
- ⏳ Database migration (if using Option A for cal_booking_id)
- ⏳ End-to-end testing with real Cal.com webhooks
- ⏳ Frontend updates to display new patient data immediately

## 🎯 **Expected Outcome**

After implementation:
1. **Every Cal.com booking** creates a complete patient profile
2. **Consultants see new patients** immediately in their dashboard
3. **No more orphaned consultations** without patient details
4. **Seamless integration** between booking and medical questionnaire flows
5. **Better data capture** from Cal.com custom form responses

## ❓ **Questions for Codex**

1. **Database Schema**: Should we add `cal_booking_id` to `patient_profiles` or use existing `consultation.zoom_meeting_id`?

2. **User Phone Field**: The `users.phone_number` field is used for both actual phone numbers and email fallbacks. Is this acceptable or should we add a separate `email` field?

3. **Deduplication Strategy**: Current logic matches by email first, then phone. Should we prioritize phone number matching for better deduplication?

4. **Error Handling**: How should we handle cases where user creation succeeds but patient profile creation fails?

5. **Migration Strategy**: If we need database changes, what's the safest way to deploy this without breaking existing functionality?

---
*Document created: October 26, 2025*
*Status: Ready for Codex review and recommendations*
