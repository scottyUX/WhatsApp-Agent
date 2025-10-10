-- Rollback Migration 001: Medical Questionnaire Support
-- This script rolls back the medical questionnaire support changes

BEGIN;

-- Drop indexes first
DROP INDEX IF EXISTS idx_users_user_type;
DROP INDEX IF EXISTS idx_medical_submissions_patient_profile;
DROP INDEX IF EXISTS idx_medical_submissions_booking_uid;
DROP INDEX IF EXISTS idx_patient_profiles_booking_uid;

-- Drop the medical questionnaire submissions table
DROP TABLE IF EXISTS medical_questionnaire_submissions;

-- Remove new columns from existing tables
ALTER TABLE patient_profiles 
DROP COLUMN IF EXISTS booking_uid,
DROP COLUMN IF EXISTS source_channel;

ALTER TABLE users 
DROP COLUMN IF EXISTS user_type;

-- Restore phone as required field
-- Note: This will fail if there are any NULL phone values
-- You may need to update NULL values first
ALTER TABLE patient_profiles 
ALTER COLUMN phone SET NOT NULL;

COMMIT;
