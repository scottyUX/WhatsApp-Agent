-- Phase 1 Release Rollback

BEGIN;

-- Revert bookings changes
-- Restore payment_status allowed values to prior set ('pending','partial','paid','refunded')
DO $$
DECLARE
    cons_name text;
BEGIN
    FOR cons_name IN
        SELECT conname FROM pg_constraint
        WHERE conrelid='bookings'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%payment_status%'
    LOOP
        EXECUTE format('ALTER TABLE bookings DROP CONSTRAINT %I', cons_name);
    END LOOP;
END $$;

ALTER TABLE bookings
    ADD CONSTRAINT bookings_payment_status_check
    CHECK (payment_status IN ('pending','partial','paid','refunded'));

-- Set currency default back to 'USD'
ALTER TABLE bookings ALTER COLUMN currency SET DEFAULT 'USD';

-- Note: duration_hours column removal is not automatically reversible without data loss; add back nullable
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name='bookings' AND column_name='duration_hours'
    ) THEN
        ALTER TABLE bookings ADD COLUMN duration_hours INTEGER;
    END IF;
END $$;

-- Revert communication_channels channel_type constraint (remove 'zoom')
DO $$
DECLARE
    cons_name text;
BEGIN
    FOR cons_name IN
        SELECT conname FROM pg_constraint
        WHERE conrelid='communication_channels'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%channel_type%'
    LOOP
        EXECUTE format('ALTER TABLE communication_channels DROP CONSTRAINT %I', cons_name);
    END LOOP;
END $$;

ALTER TABLE communication_channels
    ADD CONSTRAINT communication_channels_channel_type_check
    CHECK (channel_type IN ('whatsapp','email','sms','phone','chat'));

-- Revert consultations consultation_type constraint (remove 'zoom')
DO $$
DECLARE
    cons_name text;
BEGIN
    FOR cons_name IN
        SELECT conname FROM pg_constraint
        WHERE conrelid='consultations'::regclass AND contype='c' AND pg_get_constraintdef(oid) ILIKE '%consultation_type%'
    LOOP
        EXECUTE format('ALTER TABLE consultations DROP CONSTRAINT %I', cons_name);
    END LOOP;
END $$;

ALTER TABLE consultations
    ADD CONSTRAINT consultations_consultation_type_check
    CHECK (consultation_type IN ('video','phone','in_person'));

-- Revert leads enrichment fields: drop if exist
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='last_interaction_at') THEN ALTER TABLE leads DROP COLUMN last_interaction_at; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='company') THEN ALTER TABLE leads DROP COLUMN company; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='job_title') THEN ALTER TABLE leads DROP COLUMN job_title; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='country') THEN ALTER TABLE leads DROP COLUMN country; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='city') THEN ALTER TABLE leads DROP COLUMN city; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='age_group') THEN ALTER TABLE leads DROP COLUMN age_group; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='income_group') THEN ALTER TABLE leads DROP COLUMN income_group; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='timezone') THEN ALTER TABLE leads DROP COLUMN timezone; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='deal_value') THEN ALTER TABLE leads DROP COLUMN deal_value; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='work_email') THEN ALTER TABLE leads DROP COLUMN work_email; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='employment_history') THEN ALTER TABLE leads DROP COLUMN employment_history; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='linkedin_url') THEN ALTER TABLE leads DROP COLUMN linkedin_url; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='reddit_handle') THEN ALTER TABLE leads DROP COLUMN reddit_handle; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='x_handle') THEN ALTER TABLE leads DROP COLUMN x_handle; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='facebook_profile') THEN ALTER TABLE leads DROP COLUMN facebook_profile; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='tiktok_profile') THEN ALTER TABLE leads DROP COLUMN tiktok_profile; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='instagram_profile') THEN ALTER TABLE leads DROP COLUMN instagram_profile; END IF;
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='leads' AND column_name='lead_summary') THEN ALTER TABLE leads DROP COLUMN lead_summary; END IF;
END $$;

COMMIT;


