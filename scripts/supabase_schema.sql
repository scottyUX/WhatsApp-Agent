-- Supabase Database Schema for WhatsApp Agent
-- Patient Intake Questionnaire System

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. USERS TABLE (existing)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    phone_number TEXT UNIQUE NOT NULL,
    name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. MESSAGES TABLE (existing)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    direction TEXT CHECK (direction IN ('incoming', 'outgoing')) NOT NULL,
    body TEXT,
    media_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. APPOINTMENTS TABLE
CREATE TABLE appointments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Appointment Details
    scheduled_datetime TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 60,
    time_zone TEXT DEFAULT 'UTC',
    status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'confirmed', 'cancelled', 'completed')),
    
    -- Calendar Integration
    calendar_event_id TEXT UNIQUE,
    google_meet_link TEXT,
    confirmation_code TEXT UNIQUE,
    
    -- Metadata
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. PATIENT PROFILES TABLE (Processed data for specialists)
CREATE TABLE patient_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Basic Info (Required)
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    
    -- Basic Info (Optional)
    location TEXT,
    age INTEGER,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    
    -- Medical Background (Processed from questionnaire)
    medical_conditions TEXT[], -- Array of conditions
    current_medications TEXT[], -- Array of medications
    allergies TEXT[], -- Array of allergies
    recent_surgeries TEXT[], -- Array of surgeries
    recent_stress_events TEXT[], -- Array of stress events
    
    -- Hair Loss Background (Processed from questionnaire)
    hair_loss_locations TEXT[], -- Array of locations
    hair_loss_onset TEXT, -- When it started
    hair_loss_progression TEXT, -- How it progressed
    family_hair_loss_history BOOLEAN,
    previous_treatments TEXT[], -- Array of treatments
    
    -- Questionnaire Status
    questionnaire_completed BOOLEAN DEFAULT FALSE,
    questionnaire_completed_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id) -- One profile per user
);

-- 5. QUESTIONNAIRE RESPONSES TABLE (Raw questionnaire data)
CREATE TABLE questionnaire_responses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    appointment_id UUID REFERENCES appointments(id) ON DELETE SET NULL,
    
    -- Question Details
    question_id TEXT NOT NULL,
    question_text TEXT NOT NULL,
    question_category TEXT NOT NULL, -- 'basic', 'medical', 'hair_loss'
    
    -- Response Details
    answer TEXT,
    skipped BOOLEAN DEFAULT FALSE,
    clarification_attempted BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CONVERSATION STATES TABLE
CREATE TABLE conversation_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Scheduling State
    scheduling_step TEXT DEFAULT 'initial_contact',
    questionnaire_step TEXT DEFAULT 'not_started',
    
    -- Current Question Tracking
    current_question_id TEXT,
    questionnaire_started_at TIMESTAMPTZ,
    questionnaire_completed_at TIMESTAMPTZ,
    
    -- Lead Management
    lead_id TEXT, -- HubSpot lead ID
    crm_synced BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id) -- One state per user
);

-- INDEXES for Performance
CREATE INDEX idx_appointments_user_id ON appointments(user_id);
CREATE INDEX idx_appointments_scheduled_datetime ON appointments(scheduled_datetime);
CREATE INDEX idx_appointments_status ON appointments(status);
CREATE INDEX idx_patient_profiles_user_id ON patient_profiles(user_id);
CREATE INDEX idx_questionnaire_responses_user_id ON questionnaire_responses(user_id);
CREATE INDEX idx_questionnaire_responses_appointment_id ON questionnaire_responses(appointment_id);
CREATE INDEX idx_questionnaire_responses_question_id ON questionnaire_responses(question_id);
CREATE INDEX idx_conversation_states_user_id ON conversation_states(user_id);

-- ROW LEVEL SECURITY (RLS) for Patient Data Privacy
-- Note: RLS policies can be added later when specialist access is needed
-- ALTER TABLE patient_profiles ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE questionnaire_responses ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- FUNCTIONS for Data Processing
CREATE OR REPLACE FUNCTION update_patient_profile_from_questionnaire()
RETURNS TRIGGER AS $$
BEGIN
    -- This function will be called when questionnaire responses are inserted/updated
    -- It will process the raw responses and update the patient_profiles table
    -- Implementation will be added when we build the questionnaire processing logic
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- TRIGGER to automatically update patient profiles
-- CREATE TRIGGER update_patient_profile_trigger
--     AFTER INSERT OR UPDATE ON questionnaire_responses
--     FOR EACH ROW
--     EXECUTE FUNCTION update_patient_profile_from_questionnaire();
