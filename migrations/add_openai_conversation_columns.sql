-- Migration: Add OpenAI conversation tracking columns to conversation_states
-- Ensures the backend can persist OpenAI session identifiers per device

BEGIN;

ALTER TABLE conversation_states
    ADD COLUMN IF NOT EXISTS device_id VARCHAR(255);

ALTER TABLE conversation_states
    ADD COLUMN IF NOT EXISTS openai_conversation_id VARCHAR(255);

CREATE INDEX IF NOT EXISTS idx_conversation_states_device_id
    ON conversation_states(device_id);

CREATE INDEX IF NOT EXISTS idx_conversation_states_openai_conversation
    ON conversation_states(openai_conversation_id);

COMMIT;
