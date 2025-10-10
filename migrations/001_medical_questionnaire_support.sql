-- Migration 001: Medical Questionnaire Support
-- This migration adds support for medical questionnaire data collection
-- while maintaining backward compatibility with existing data

BEGIN;

-- Add new columns to patient_profiles table
ALTER TABLE patient_profiles 
ADD COLUMN booking_uid TEXT,
ADD COLUMN source_channel TEXT DEFAULT 'medical_questionnaire';

-- Add user type to distinguish between different user sources
ALTER TABLE users 
ADD COLUMN user_type TEXT DEFAULT 'whatsapp' CHECK (user_type IN ('whatsapp', 'medical_questionnaire', 'chat'));

-- Make phone optional for medical questionnaire users
-- (This allows medical questionnaire users to use email as primary contact)
ALTER TABLE patient_profiles 
ALTER COLUMN phone DROP NOT NULL;

-- Create medical questionnaire submissions table
-- This tracks all medical questionnaire submissions for audit and analytics
CREATE TABLE medical_questionnaire_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    booking_uid TEXT UNIQUE NOT NULL,
    patient_profile_id UUID REFERENCES patient_profiles(id) ON DELETE SET NULL,
    submission_data JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'submitted' CHECK (status IN ('submitted', 'processed', 'failed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted BOOLEAN DEFAULT FALSE
);

-- Create indexes for performance
CREATE INDEX idx_patient_profiles_booking_uid ON patient_profiles(booking_uid);
CREATE INDEX idx_medical_submissions_booking_uid ON medical_questionnaire_submissions(booking_uid);
CREATE INDEX idx_medical_submissions_patient_profile ON medical_questionnaire_submissions(patient_profile_id);
CREATE INDEX idx_users_user_type ON users(user_type);

-- Add comments for documentation
COMMENT ON COLUMN patient_profiles.booking_uid IS 'Cal.com booking UID for medical questionnaire submissions';
COMMENT ON COLUMN patient_profiles.source_channel IS 'Channel through which patient was acquired (whatsapp, medical_questionnaire, chat)';
COMMENT ON COLUMN users.user_type IS 'Type of user account (whatsapp, medical_questionnaire, chat)';
COMMENT ON TABLE medical_questionnaire_submissions IS 'Tracks medical questionnaire submissions and their processing status';

COMMIT;
