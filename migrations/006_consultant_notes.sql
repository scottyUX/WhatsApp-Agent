-- Migration: Add consultant_notes table
-- Description: Creates table for consultant notes functionality

CREATE TABLE IF NOT EXISTS consultant_notes (
    id VARCHAR(36) PRIMARY KEY,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    patient_profile_id UUID NOT NULL REFERENCES patient_profiles(id) ON DELETE CASCADE,
    consultant_email VARCHAR(255) NOT NULL,
    note_content TEXT NOT NULL,
    consultation_id VARCHAR(36) REFERENCES "Appoinment"(id) ON DELETE SET NULL,
    note_type VARCHAR(50) DEFAULT 'general',
    is_private BOOLEAN DEFAULT FALSE NOT NULL
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_consultant_notes_patient_profile_id ON consultant_notes(patient_profile_id);
CREATE INDEX IF NOT EXISTS idx_consultant_notes_consultation_id ON consultant_notes(consultation_id);
CREATE INDEX IF NOT EXISTS idx_consultant_notes_consultant_email ON consultant_notes(consultant_email);
CREATE INDEX IF NOT EXISTS idx_consultant_notes_created_at ON consultant_notes("createdAt");

-- Add comments
COMMENT ON TABLE consultant_notes IS 'Stores notes created by consultants for patients';
COMMENT ON COLUMN consultant_notes.id IS 'Unique identifier for the note';
COMMENT ON COLUMN consultant_notes.patient_profile_id IS 'Reference to the patient profile';
COMMENT ON COLUMN consultant_notes.consultant_email IS 'Email of the consultant who created the note';
COMMENT ON COLUMN consultant_notes.note_content IS 'The actual note content';
COMMENT ON COLUMN consultant_notes.consultation_id IS 'Optional reference to a specific consultation';
COMMENT ON COLUMN consultant_notes.note_type IS 'Type of note (general, consultation, follow_up, medical, administrative)';
COMMENT ON COLUMN consultant_notes.is_private IS 'Whether the note is private to the consultant';

