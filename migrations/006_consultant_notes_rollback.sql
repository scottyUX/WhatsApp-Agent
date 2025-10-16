-- Rollback Migration: Remove consultant_notes table
-- Description: Drops the consultant_notes table and related indexes

-- Drop indexes first
DROP INDEX IF EXISTS idx_consultant_notes_created_at;
DROP INDEX IF EXISTS idx_consultant_notes_consultant_email;
DROP INDEX IF EXISTS idx_consultant_notes_consultation_id;
DROP INDEX IF EXISTS idx_consultant_notes_patient_profile_id;

-- Drop the table
DROP TABLE IF EXISTS consultant_notes;
