-- Core patient tables to support Phase 1 features
-- Creates user_profiles, patient_profiles, medical_histories, hair_loss_profiles if not present

BEGIN;

-- user_profiles
CREATE TABLE IF NOT EXISTS user_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    date_of_birth DATE,
    gender TEXT CHECK (gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
    nationality TEXT,
    preferred_language TEXT DEFAULT 'en',
    timezone TEXT DEFAULT 'UTC',
    profile_picture_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id)
);

-- patient_profiles
CREATE TABLE IF NOT EXISTS patient_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id TEXT UNIQUE NOT NULL,
    medical_condition TEXT NOT NULL,
    procedure_interest TEXT[],
    budget_range TEXT,
    preferred_timeline TEXT,
    travel_preferences JSONB,
    emergency_contact JSONB,
    insurance_info JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(user_id)
);

-- medical_histories (1:1 with patient_profiles)
CREATE TABLE IF NOT EXISTS medical_histories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    current_medications JSONB DEFAULT '[]',
    allergies JSONB DEFAULT '[]',
    chronic_conditions JSONB DEFAULT '[]',
    previous_surgeries JSONB DEFAULT '[]',
    family_medical_history JSONB DEFAULT '[]',
    lifestyle_factors JSONB DEFAULT '{}',
    additional_notes TEXT,
    last_updated_by TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(patient_profile_id)
);

-- hair_loss_profiles (1:1 with patient_profiles)
CREATE TABLE IF NOT EXISTS hair_loss_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    hair_loss_type TEXT,
    norwood_scale INTEGER,
    ludwig_scale INTEGER,
    hair_loss_duration TEXT,
    previous_treatments JSONB DEFAULT '[]',
    donor_area_quality TEXT,
    expectations TEXT,
    photos JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE,
    UNIQUE(patient_profile_id)
);

COMMIT;


