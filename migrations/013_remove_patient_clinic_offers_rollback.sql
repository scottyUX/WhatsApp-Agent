BEGIN;

-- Restore clinic offer cache column if rollback is required
ALTER TABLE patient_profiles
    ADD COLUMN IF NOT EXISTS clinic_offer_ids UUID[] NOT NULL DEFAULT '{}'::uuid[];

COMMIT;

