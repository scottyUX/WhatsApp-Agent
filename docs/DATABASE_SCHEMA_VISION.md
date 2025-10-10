# Database Schema Vision for Istanbul Medic Medical Tourism Platform

## Overview

This document outlines a comprehensive database schema designed to support the complete patient journey in medical tourism, from initial discovery through post-procedure recovery. The schema is designed to be implemented incrementally, starting with core functionality and expanding to support advanced features.

## Core Principles

1. **Patient-Centric Design**: Every table and relationship serves the patient experience
2. **Journey Tracking**: Complete visibility into patient touchpoints and interactions
3. **Marketing Intelligence**: Rich data for targeting and personalization
4. **Sales Enablement**: Tools and data to close deals effectively
5. **Scalability**: Architecture that grows with the business
6. **Privacy & Compliance**: GDPR, HIPAA, and medical data protection built-in

## Patient Journey Phases

```
Discovery → Research → Consultation → Booking → Travel → Procedure → Recovery → Follow-up
```

## Database Schema Design

### 1. Core Identity & Authentication

```sql
-- Users: Central identity management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    phone_number TEXT UNIQUE,
    auth_provider TEXT NOT NULL DEFAULT 'email', -- 'email', 'google', 'facebook', 'apple'
    auth_provider_id TEXT, -- External provider ID
    user_type TEXT NOT NULL DEFAULT 'patient' CHECK (user_type IN ('patient', 'provider', 'admin', 'staff')),
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'suspended', 'pending_verification')),
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE,
    deleted BOOLEAN DEFAULT FALSE
);

-- User profiles: Extended information
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    nationality TEXT, -- Country code
    preferred_language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    profile_picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id)
);
```

### 2. Patient Journey & Medical Data

```sql
-- Patient profiles: Medical tourism specific
CREATE TABLE patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id TEXT UNIQUE NOT NULL, -- Human-readable ID like "PAT-2024-001"
    medical_condition TEXT NOT NULL, -- Primary condition (hair loss, dental, etc.)
    procedure_interest TEXT[], -- Array of interested procedures
    budget_range TEXT, -- '$5k-10k', '$10k-20k', etc.
    preferred_timeline TEXT, -- 'immediate', '1-3_months', '3-6_months', etc.
    travel_preferences JSONB, -- Flight preferences, accommodation, etc.
    emergency_contact JSONB, -- Name, phone, relationship
    insurance_info JSONB, -- Optional: patient-provided insurance details when relevant
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id)
);

-- Medical history: Comprehensive medical background
CREATE TABLE medical_histories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    current_medications JSONB DEFAULT '[]',
    allergies JSONB DEFAULT '[]',
    chronic_conditions JSONB DEFAULT '[]',
    previous_surgeries JSONB DEFAULT '[]',
    family_medical_history JSONB DEFAULT '[]',
    lifestyle_factors JSONB DEFAULT '{}', -- Smoking, exercise, diet, etc.
    additional_notes TEXT,
    last_updated_by TEXT, -- 'patient', 'doctor', 'system'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(patient_profile_id)
);

-- Hair loss specific data (for hair transplant patients)
CREATE TABLE hair_loss_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    hair_loss_type TEXT, -- 'male_pattern', 'female_pattern', 'alopecia', etc.
    norwood_scale INTEGER, -- 1-7 for male pattern baldness
    ludwig_scale INTEGER, -- 1-3 for female pattern baldness
    hair_loss_duration TEXT, -- 'less_than_1_year', '1_2_years', etc.
    previous_treatments JSONB DEFAULT '[]',
    donor_area_quality TEXT, -- 'excellent', 'good', 'fair', 'poor'
    expectations TEXT,
    photos JSONB DEFAULT '[]', -- Array of photo URLs
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(patient_profile_id)
);
```

### 3. Provider & Service Management

```sql
-- Medical providers (clinics, hospitals, doctors)
CREATE TABLE providers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('clinic', 'hospital', 'doctor', 'dental_clinic')),
    specialty TEXT[], -- Array of specialties
    location JSONB NOT NULL, -- Address, coordinates, city, country
    contact_info JSONB NOT NULL, -- Phone, email, website
    credentials JSONB, -- Licenses, certifications, accreditations
    languages_spoken TEXT[],
    rating DECIMAL(3,2), -- Average rating
    review_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Procedures offered by providers
CREATE TABLE procedures (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    name TEXT NOT NULL, -- Human-readable procedure name shown to patients
    category TEXT NOT NULL, -- 'hair_transplant', 'dental', 'cosmetic', etc.
    description TEXT,
    duration_hours INTEGER,
    recovery_time_days INTEGER,
    price_range JSONB, -- Min/max prices
    requirements JSONB, -- Medical requirements, age limits, etc.
    is_active BOOLEAN DEFAULT TRUE, -- Controls visibility/availability for booking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Provider availability and scheduling
CREATE TABLE provider_availability (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    procedure_id UUID REFERENCES procedures(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    is_available BOOLEAN DEFAULT TRUE,
    max_bookings INTEGER DEFAULT 1,
    current_bookings INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

### 4. Consultation & Booking Management

```sql
-- Consultations: Initial meetings with providers
CREATE TABLE consultations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    procedure_id UUID REFERENCES procedures(id) ON DELETE SET NULL,
    consultation_type TEXT NOT NULL DEFAULT 'video' CHECK (consultation_type IN ('video', 'phone', 'in_person', 'zoom')),
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'no_show')),
    scheduled_at TIMESTAMP WITH TIME ZONE NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    meeting_url TEXT,
    meeting_id TEXT,
    notes TEXT,
    outcome TEXT, -- 'qualified', 'not_qualified', 'needs_follow_up'
    follow_up_required BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Bookings: Confirmed procedures
CREATE TABLE bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_reference TEXT UNIQUE NOT NULL, -- Human-readable like "BK-2024-001"
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    procedure_id UUID NOT NULL REFERENCES procedures(id) ON DELETE CASCADE,
    consultation_id UUID REFERENCES consultations(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled', 'completed', 'no_show')),
    procedure_date DATE NOT NULL,
    procedure_time TIME NOT NULL,
    total_cost DECIMAL(10,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'EUR',
    payment_status TEXT NOT NULL DEFAULT 'pending' CHECK (payment_status IN ('pending', 'deposit', 'paid', 'refunded')),
    special_instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Travel arrangements
CREATE TABLE travel_arrangements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    flight_info JSONB, -- Departure, arrival, airline, etc.
    accommodation_info JSONB, -- Hotel, check-in/out dates
    airport_transfer BOOLEAN DEFAULT FALSE,
    visa_assistance BOOLEAN DEFAULT FALSE,
    travel_insurance BOOLEAN DEFAULT FALSE,
    total_cost DECIMAL(10,2),
    currency TEXT DEFAULT 'USD',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

### 5. Communication & Engagement

```sql
-- Communication channels
CREATE TABLE communication_channels (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_type TEXT NOT NULL CHECK (channel_type IN ('whatsapp', 'email', 'sms', 'phone', 'chat', 'zoom')),
    channel_value TEXT NOT NULL, -- Phone number, email, etc.
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Messages: All communication history
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel_id UUID REFERENCES communication_channels(id) ON DELETE SET NULL,
    direction TEXT NOT NULL CHECK (direction IN ('incoming', 'outgoing')),
    message_type TEXT NOT NULL DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'video', 'audio', 'document')),
    content TEXT,
    media_urls TEXT[],
    metadata JSONB, -- Additional message data
    is_read BOOLEAN DEFAULT FALSE,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Conversation sessions
CREATE TABLE conversation_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    channel_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'ended', 'timeout')),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ended_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB, -- Session-specific data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

### 6. Marketing & Analytics

```sql
-- Marketing campaigns
CREATE TABLE marketing_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('email', 'social_media', 'google_ads', 'facebook_ads', 'referral')),
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'active', 'paused', 'completed')),
    target_audience JSONB, -- Demographics, interests, etc.
    budget DECIMAL(10,2),
    currency TEXT DEFAULT 'USD',
    start_date DATE,
    end_date DATE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Lead tracking
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    email TEXT,
    phone TEXT,
    first_name TEXT,
    last_name TEXT,
    source TEXT NOT NULL, -- 'website', 'google_ads', 'facebook', 'referral', etc.
    campaign_id UUID REFERENCES marketing_campaigns(id) ON DELETE SET NULL,
    status TEXT NOT NULL DEFAULT 'new' CHECK (status IN ('new', 'contacted', 'qualified', 'converted', 'lost')),
    lead_score INTEGER DEFAULT 0, -- 0-100 scoring system
    assigned_to UUID REFERENCES users(id), -- Sales rep
    notes TEXT,
    -- Additional enrichment fields
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    company TEXT,
    job_title TEXT,
    country TEXT,
    city TEXT,
    age_group TEXT, -- e.g., '18-24', '25-34', '35-44', etc.
    income_group TEXT, -- e.g., 'low', 'medium', 'high'
    timezone TEXT,
    deal_value DECIMAL(10,2),
    work_email TEXT,
    employment_history JSONB DEFAULT '[]', -- Array of positions/companies
    linkedin_url TEXT,
    reddit_handle TEXT,
    x_handle TEXT, -- formerly Twitter
    facebook_profile TEXT,
    tiktok_profile TEXT,
    instagram_profile TEXT,
    lead_summary TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Patient journey tracking
CREATE TABLE patient_journey_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL, -- 'website_visit', 'consultation_scheduled', 'booking_made', etc.
    event_data JSONB, -- Event-specific data
    source TEXT, -- Where the event originated
    session_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

### 7. Post-Procedure Care

```sql
-- Procedure outcomes
CREATE TABLE procedure_outcomes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    procedure_notes TEXT,
    complications TEXT,
    photos JSONB DEFAULT '[]', -- Before/after photos
    doctor_notes TEXT,
    patient_feedback TEXT,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Follow-up care
CREATE TABLE follow_up_care (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_id UUID NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    follow_up_type TEXT NOT NULL CHECK (follow_up_type IN ('check_in', 'photo_update', 'satisfaction_survey', 'review_request')),
    scheduled_date DATE,
    completed_date DATE,
    status TEXT NOT NULL DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'completed', 'cancelled', 'overdue')),
    notes TEXT,
    patient_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Reviews and testimonials
CREATE TABLE reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    provider_id UUID NOT NULL REFERENCES providers(id) ON DELETE CASCADE,
    booking_id UUID REFERENCES bookings(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title TEXT,
    content TEXT NOT NULL,
    photos JSONB DEFAULT '[]',
    is_verified BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);
```

## Implementation Phases

### Phase 1: Core Foundation (Current)
- User management
- Basic patient profiles
- Medical history
- Communication channels and messages/conversations
- Hair loss profiles
- Basic booking system

### Phase 2: Enhanced Patient Experience
- Consultation management
- Travel arrangements
- Follow-up care

### Phase 3: Marketing & Sales Intelligence
- Lead tracking
- Journey analytics
- Campaign management
- Review system

### Phase 4: Advanced Features
- AI-powered recommendations
- Predictive analytics
- Advanced reporting
- Integration with external systems

## Concepts: Personas and Relationships

### Personas

- **User**
  - Identity in `users` (authentication and authorization)
  - Properties: `email`, `phone_number`, `auth_provider`, `user_type` (`patient`, `provider`, `admin`, `staff`), verification flags, status
  - Purpose: Access control, communication endpoints, conversation sessions

- **Lead**
  - Prospect in `leads` (marketing/sales funnel)
  - Properties: minimal contact (`email`/`phone`), `source`, `campaign_id`, `status` (e.g., `new`, `contacted`, `qualified`, `converted`, `lost`), `lead_score`, `assigned_to`, notes
  - Purpose: Attribution, funnel tracking, sales operations

- **Patient (Patient Profile)**
  - Clinical persona in `patient_profiles` linked 1:1 to a `user`
  - Properties: `patient_id`, `medical_condition`, `procedure_interest[]`, `preferred_timeline`, `budget_range`, `travel_preferences`, `insurance_info`, emergency contact
  - Related records: `medical_histories`, `hair_loss_profiles`, `consultations`, `bookings`, `procedure_outcomes`, `follow_up_care`, `reviews`

### Relationships

- A `lead` may optionally reference a `user` once identified; many leads can exist without users.
- A `user` may or may not have a `patient_profile`; non-patient roles (admin/staff/provider) do not.
- A `patient_profile` must reference exactly one `user` (enforced via `UNIQUE(user_id)`).

### Lifecycle

1. Lead created (web form, ad click, WhatsApp inquiry)
2. User created/linked on verified interaction; lead retained for attribution
3. Patient profile created when medical intake begins (consultation/booking)

### Messaging & Sessions

- Messages and conversation sessions are tied to `users` for consistency and auditability; patient context is derived via `user → patient_profile`.
- For unknown inbound channels, create a `user` on first message; optionally upsert a `lead` with `source`.

### Permissions & Sensitivity

- Lead: lower sensitivity (sales access)
- User: identity/PII (moderate)
- Patient Profile and medical tables: high sensitivity (GDPR/HIPAA controls, audit trails)

## Key Benefits

### For Patients:
- Seamless journey tracking
- Personalized experience
- Complete medical history
- Easy communication
- Post-procedure support

### For Sales Team:
- Lead scoring and qualification
- Complete customer journey visibility
- Automated follow-up triggers
- Performance analytics

### For Marketing Team:
- Detailed audience insights
- Campaign performance tracking
- Customer lifetime value analysis
- A/B testing capabilities

### For Medical Team:
- Complete patient history
- Procedure tracking
- Outcome analysis
- Quality improvement data

## Data Privacy & Compliance

- **GDPR Compliance**: Right to be forgotten, data portability
- **Medical Data Protection**: Encrypted sensitive data
- **Audit Trails**: Complete change tracking
- **Data Retention**: Configurable retention policies
- **Consent Management**: Granular consent tracking

This schema provides a solid foundation that can grow with your business while maintaining data integrity and supporting all aspects of the medical tourism patient journey.
