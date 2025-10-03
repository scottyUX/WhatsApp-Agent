-- Migration: Add session lock fields to conversation_states table
-- This migration adds fields needed for persistent session management in serverless environments

-- Make patient_profile_id nullable for chat sessions
ALTER TABLE conversation_states 
ALTER COLUMN patient_profile_id DROP NOT NULL;

-- Add device_id column for chat sessions
ALTER TABLE conversation_states 
ADD COLUMN IF NOT EXISTS device_id VARCHAR(255);

-- Add session lock fields to conversation_states table
ALTER TABLE conversation_states 
ADD COLUMN IF NOT EXISTS active_agent VARCHAR(50),
ADD COLUMN IF NOT EXISTS locked_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS session_ttl INTEGER NOT NULL DEFAULT 86400;

-- Add index for performance on active_agent lookups
CREATE INDEX IF NOT EXISTS idx_conversation_states_active_agent ON conversation_states(active_agent);

-- Add index for performance on locked_at lookups (for cleanup)
CREATE INDEX IF NOT EXISTS idx_conversation_states_locked_at ON conversation_states(locked_at);

-- Update existing records to have default session_ttl
UPDATE conversation_states 
SET session_ttl = 86400 
WHERE session_ttl IS NULL;

-- Add comment to document the purpose
COMMENT ON COLUMN conversation_states.active_agent IS 'Currently active agent for this conversation session';
COMMENT ON COLUMN conversation_states.locked_at IS 'Timestamp when the session was locked to an agent';
COMMENT ON COLUMN conversation_states.session_ttl IS 'Session time-to-live in seconds (default: 24 hours)';
